"""Analyzer for SLURM .out files to identify failure modes."""

import asyncio
import glob
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from inspect_ai.model import get_model, GenerateConfig, Model

from experiments.failure.analyze import (
    estimate_token_count,
    split_transcript_into_segments,
    format_prompt,
    parse_response,
    analyze_with_prompt,
    AnalysisResult
)
from experiments.failure.prompts import ENVIRONMENT_BUGS_PROMPT
from logging_config import get_logger

logger = get_logger(__name__)


def parse_slurm_out_file(file_path: str) -> str:
    """Parse a SLURM .out file and extract the transcript starting from first Assistant message.

    Returns:
        transcript starting from first Assistant message
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find the first Assistant message
        assistant_pattern = r'╭─ Assistant ─+╮'
        match = re.search(assistant_pattern, content)

        if not match:
            logger.warning(f"No Assistant message found in {file_path}")
            return ""

        # Extract everything from the first Assistant message onwards
        transcript = content[match.start():]
        return transcript

    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return ""


async def analyze_slurm_file(
    model_client,
    file_path: str,
    config: GenerateConfig,
    max_tokens_per_segment: int = 400000
) -> Optional[AnalysisResult]:
    """Analyze a single SLURM .out file for environment bugs and issues."""

    transcript = parse_slurm_out_file(file_path)

    if not transcript:
        logger.info(f"Skipping {file_path}: No transcript available")
        return None

    filename = os.path.basename(file_path)
    token_count = estimate_token_count(transcript)

    # Use paper_id as filename for now (required by prompt template)
    paper_id = filename

    expected_tags = ["summary", "bugs"]

    if token_count > max_tokens_per_segment:
        logger.info(f"Transcript for {filename} has ~{token_count:,} tokens - splitting into segments")
        segments = split_transcript_into_segments(transcript, max_tokens_per_segment)

        all_responses = []
        all_parsed = {tag: [] for tag in expected_tags}

        for i, (segment_text, start_token, end_token) in enumerate(segments):
            segment_info = f"{filename} segment {i+1}/{len(segments)}"
            logger.info(f"Analyzing {segment_info}")

            prompt = format_prompt(
                ENVIRONMENT_BUGS_PROMPT,
                paper_id=paper_id,
                transcript=segment_text
            )

            completion, parsed = await analyze_with_prompt(
                model_client, prompt, expected_tags, config
            )

            all_responses.append(completion)
            for tag, value in parsed.items():
                all_parsed[tag].append(value)

        # Keep results from segments as lists
        combined_response = "\n\n".join(all_responses)
        combined_parsed = {
            "summary": all_parsed["summary"],  # Keep as list
            "bugs": all_parsed["bugs"]  # Keep as list
        }

        return AnalysisResult(
            eval_id=filename,
            paper_id=paper_id,
            response=combined_response,
            parsed_data=combined_parsed,
            metadata={"source": "slurm", "token_count": token_count},
            was_segmented=True,
            num_segments=len(segments)
        )
    else:
        logger.info(f"Analyzing {filename} (~{token_count:,} tokens)")

        prompt = format_prompt(
            ENVIRONMENT_BUGS_PROMPT,
            paper_id=paper_id,
            transcript=transcript
        )

        completion, parsed = await analyze_with_prompt(
            model_client, prompt, expected_tags, config
        )

        # Wrap single results in lists for consistency
        parsed_as_lists = {
            "summary": [parsed.get("summary", "")],
            "bugs": [parsed.get("bugs", "")]
        }

        return AnalysisResult(
            eval_id=filename,
            paper_id=paper_id,
            response=completion,
            parsed_data=parsed_as_lists,
            metadata={"source": "slurm", "token_count": token_count},
            was_segmented=False,
            num_segments=1
        )


async def analyze_slurm_directory(
    log_dir: str,
    output_file: str,
    model_name: str = "openai/gpt-4o-mini",
    temperature: float = 0.5,
    max_tokens: Optional[int] = None,
    max_concurrent: int = 10,
    max_tokens_per_segment: int = 400000,
    limit: Optional[int] = None
) -> List[AnalysisResult]:
    """Analyze all .out files in a SLURM log directory."""

    model = get_model(
        model_name,
        config=GenerateConfig(
            temperature=temperature,
            max_tokens=max_tokens
        )
    )

    # Initialize the model client
    model_client = await model.__aenter__()

    try:
        # Find all .out files
        out_files = glob.glob(os.path.join(log_dir, "*.out"))

        if not out_files:
            logger.warning(f"No .out files found in {log_dir}")
            return []

        logger.info(f"Found {len(out_files)} .out files to analyze")

        # Apply limit if specified
        if limit:
            out_files = out_files[:limit]
            logger.info(f"Limiting analysis to {limit} files")

        valid_analyses = []

        # Process files in batches
        for i in range(0, len(out_files), max_concurrent):
            batch = out_files[i:i+max_concurrent]
            tasks = []

            for file_path in batch:
                tasks.append(
                    analyze_slurm_file(
                        model_client,
                        file_path,
                        GenerateConfig(temperature=temperature, max_tokens=max_tokens),
                        max_tokens_per_segment
                    )
                )

            results = await asyncio.gather(*tasks)
            valid_analyses.extend([r for r in results if r])
            logger.info(f"Processed {min(i+max_concurrent, len(out_files))}/{len(out_files)} files")
    finally:
        # Clean up the model client
        await model.__aexit__(None, None, None)

    logger.info(f"Successfully analyzed {len(valid_analyses)} files")

    # Write results to output file
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        for analysis in valid_analyses:
            result = {
                "file": analysis.eval_id,
                "summary": analysis.parsed_data.get("summary", ""),
                "bugs": analysis.parsed_data.get("bugs", ""),
                "was_segmented": analysis.was_segmented,
                "num_segments": analysis.num_segments,
                "metadata": analysis.metadata
            }
            f.write(json.dumps(result) + '\n')

    logger.info(f"Results written to {output_file}")

    # Print summary
    print_failure_summary(valid_analyses)

    return valid_analyses


def print_failure_summary(analyses: List[AnalysisResult]):
    """Print summary of environment bugs and issues from analyses."""

    logger.info("\n" + "="*60)
    logger.info("ENVIRONMENT BUGS AND ISSUES SUMMARY")
    logger.info("="*60)

    # Count files with bugs vs no bugs
    files_with_bugs = 0
    files_without_bugs = 0

    for analysis in analyses:
        bugs_list = analysis.parsed_data.get("bugs", [])
        # Check if any segment has significant bugs
        has_bugs = False
        for bug_text in bugs_list:
            if bug_text and "No significant technical issues identified" not in bug_text:
                has_bugs = True
                break

        if has_bugs:
            files_with_bugs += 1
        else:
            files_without_bugs += 1

    logger.info(f"\nFiles analyzed: {len(analyses)}")
    logger.info(f"Files with bugs/issues: {files_with_bugs} ({files_with_bugs/len(analyses)*100:.1f}%)")
    logger.info(f"Files without significant issues: {files_without_bugs} ({files_without_bugs/len(analyses)*100:.1f}%)")

    # Show sample analyses
    logger.info("\n" + "="*60)
    logger.info("SAMPLE ANALYSES")
    logger.info("="*60)

    for i, analysis in enumerate(analyses[:5]):
        logger.info(f"\nFile: {analysis.eval_id}")

        summary_list = analysis.parsed_data.get('summary', [])
        if summary_list:
            # Show first summary (or combine if multiple)
            summary_text = summary_list[0] if len(summary_list) == 1 else " | ".join(summary_list[:2])
            logger.info(f"Summary: {summary_text[:300] if len(summary_text) > 300 else summary_text}")

        bugs_list = analysis.parsed_data.get('bugs', [])
        if bugs_list and any(bug for bug in bugs_list if bug and bug != 'N/A'):
            logger.info(f"Bugs/Issues:")
            # Show bugs from all segments
            for seg_idx, bugs in enumerate(bugs_list[:3]):  # Limit to first 3 segments
                if bugs and bugs != 'N/A':
                    if analysis.was_segmented and len(bugs_list) > 1:
                        logger.info(f"  [Segment {seg_idx+1}]")
                    # Limit bug output to first 300 chars per segment
                    bug_preview = bugs[:300] + "..." if len(bugs) > 300 else bugs
                    for line in bug_preview.split('\n')[:3]:  # Show first 3 lines
                        if line.strip():
                            logger.info(f"    {line.strip()}")

        if analysis.was_segmented:
            logger.info(f"  (Analyzed in {analysis.num_segments} segments)")

    if len(analyses) > 5:
        logger.info(f"\n... and {len(analyses) - 5} more files")


def main():
    """CLI entry point for SLURM log analysis."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze SLURM .out files for failure modes"
    )

    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Directory containing SLURM .out files"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="slurm_failure_analysis.jsonl",
        help="Output JSONL file (default: slurm_failure_analysis.jsonl)"
    )

    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="openai/gpt-4o-mini",
        help="Model name (default: openai/gpt-4o-mini)"
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.5,
        help="Temperature for model generation (default: 0.5)"
    )

    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=10,
        help="Maximum concurrent API calls (default: 10)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of files to analyze (for testing)"
    )

    parser.add_argument(
        "--max-tokens-per-segment",
        type=int,
        default=400000,
        help="Maximum tokens per transcript segment (default: 400000)"
    )

    args = parser.parse_args()

    asyncio.run(
        analyze_slurm_directory(
            log_dir=args.input_dir,
            output_file=args.output,
            model_name=args.model,
            temperature=args.temperature,
            max_concurrent=args.max_concurrent,
            max_tokens_per_segment=args.max_tokens_per_segment,
            limit=args.limit
        )
    )


if __name__ == "__main__":
    main()