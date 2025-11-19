"""Purge old duplicate .eval files, keeping only the most recent for each paper.

For .eval files in format: {timestamp}_{paper_name}_{hash}.eval
Groups by paper_name and keeps only the most recent based on timestamp.
"""

import argparse
import logging
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from dataset.dataloader import Dataloader

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def parse_eval_filename(filename: str) -> tuple[datetime, str, str] | None:
    """Parse .eval filename into (timestamp, paper_name, hash).

    Format: {timestamp}_{paper_name}_{hash}.eval
    Example: 2025-11-18T22-46-34-08-00_astm3_ekWFkpfi6xpNKaYjiME7m3.eval

    Args:
        filename: Name of .eval file

    Returns:
        Tuple of (timestamp, paper_name, hash) or None if parse fails
    """
    # Remove .eval extension
    name = filename.replace('.eval', '')

    # Pattern: timestamp is ISO-like format, then paper name, then hash
    # Timestamp format: YYYY-MM-DDTHH-MM-SS-TZ-TZ
    pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}-\d{2}-\d{2})_(.+?)_([a-zA-Z0-9]+)$'
    match = re.match(pattern, name)

    if not match:
        return None

    timestamp_str, paper_name, hash_str = match.groups()

    # Parse timestamp (convert hyphens back to colons for time portion)
    try:
        # Format: 2025-11-18T22-46-34-08-00 -> 2025-11-18T22:46:34-08:00
        # Split on 'T' first
        date_part, time_part = timestamp_str.split('T')
        # Time part has format: HH-MM-SS-TZ-TZ, convert to HH:MM:SS-TZ:TZ
        time_components = time_part.split('-')
        if len(time_components) == 5:
            hh, mm, ss, tz1, tz2 = time_components
            time_formatted = f"{hh}:{mm}:{ss}-{tz1}:{tz2}"
        else:
            # Fallback if format is different
            time_formatted = time_part.replace('-', ':', 2)  # Replace first 2 hyphens

        timestamp_formatted = f"{date_part}T{time_formatted}"
        timestamp = datetime.fromisoformat(timestamp_formatted)
    except (ValueError, IndexError) as e:
        logger.warning(f"Could not parse timestamp in {filename}: {e}")
        return None

    return timestamp, paper_name, hash_str


def normalize_paper_name(paper_name: str) -> str:
    """Normalize paper name (underscores to hyphens)."""
    return paper_name.replace('_', '-')


def find_duplicate_evals(
    directories: list[str],
    dataloader: Dataloader | None = None
) -> dict[str, list[tuple[Path, datetime, str]]]:
    """Find duplicate .eval files grouped by paper.

    Args:
        directories: List of directory paths to search
        dataloader: Optional Dataloader to get expected paper names

    Returns:
        Dict mapping paper_name -> list of (path, timestamp, hash) tuples
    """
    # Group evals by paper name
    paper_evals = defaultdict(list)

    # Get expected paper names if dataloader provided
    expected_papers = set()
    if dataloader:
        expected_papers = {normalize_paper_name(p) for p in dataloader.papers.keys()}

    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.warning(f"Directory does not exist: {directory}")
            continue

        for eval_file in dir_path.rglob('*.eval'):
            parsed = parse_eval_filename(eval_file.name)
            if not parsed:
                logger.warning(f"Could not parse filename: {eval_file.name}")
                continue

            timestamp, paper_name, hash_str = parsed

            # Normalize paper name
            paper_name_normalized = normalize_paper_name(paper_name)

            # If we have expected papers, check if this is one of them
            if expected_papers and paper_name_normalized not in expected_papers:
                logger.debug(f"Skipping {eval_file.name} - paper not in expected set")
                continue

            paper_evals[paper_name_normalized].append((eval_file, timestamp, hash_str))

    return paper_evals


def purge_old_evals(
    directories: list[str],
    dry_run: bool = True,
    use_dataloader: bool = True
) -> tuple[int, int]:
    """Purge old duplicate .eval files, keeping only most recent per paper.

    Args:
        directories: List of directory paths to search
        dry_run: If True, only report what would be deleted
        use_dataloader: If True, use Dataloader to get expected papers

    Returns:
        Tuple of (deleted_count, total_count)
    """
    # Load dataloader if requested
    dataloader = None
    if use_dataloader:
        try:
            logger.info("Loading dataloader to get expected papers...")
            dataloader = Dataloader(
                task_types=["numeric"],
                load_text=False,
                filters={"source": "expert"}
            )
            logger.info(f"Found {len(dataloader.papers)} expected papers")
        except Exception as e:
            logger.warning(f"Could not load dataloader: {e}")

    # Find all evals grouped by paper
    paper_evals = find_duplicate_evals(directories, dataloader)

    # Find duplicates and mark old ones for deletion
    to_delete = []
    total_files = 0

    for paper_name, evals in paper_evals.items():
        total_files += len(evals)

        if len(evals) <= 1:
            continue

        # Sort by timestamp (most recent first)
        evals.sort(key=lambda x: x[1], reverse=True)

        # Keep first (most recent), delete rest
        most_recent = evals[0]
        old_evals = evals[1:]

        logger.info(f"\n{paper_name}: Found {len(evals)} versions")
        logger.info(f"  Keeping: {most_recent[0].name} ({most_recent[1]})")
        logger.info(f"  Removing {len(old_evals)} old version(s):")

        for eval_path, timestamp, _ in old_evals:
            logger.info(f"    - {eval_path.name} ({timestamp})")
            to_delete.append(eval_path)

    logger.info(f"\nSummary: {len(to_delete)} old duplicates out of {total_files} total .eval files")

    if not dry_run and to_delete:
        logger.info("\nDeleting old files...")
        for f in to_delete:
            f.unlink()
            logger.info(f"  Deleted: {f}")
    elif dry_run and to_delete:
        logger.info("\n(Dry run - no files deleted. Use --execute to actually delete)")

    return len(to_delete), total_files


def main():
    parser = argparse.ArgumentParser(
        description="Purge old duplicate .eval files, keeping only the most recent for each paper"
    )
    parser.add_argument(
        "directories",
        nargs="+",
        help="Directory or directories to search for .eval files"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete files (default is dry-run)"
    )
    parser.add_argument(
        "--no-dataloader",
        action="store_true",
        help="Don't use dataloader to filter expected papers"
    )

    args = parser.parse_args()

    deleted_count, total_count = purge_old_evals(
        args.directories,
        dry_run=not args.execute,
        use_dataloader=not args.no_dataloader
    )

    logger.info(f"\nFinal summary: Would delete {deleted_count} / {total_count} .eval files")
    if args.execute:
        logger.info("Files have been deleted.")


if __name__ == "__main__":
    main()
