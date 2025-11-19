"""Purge old duplicate slurm log directories, keeping only the most recent for each paper.

For directories in format: {paper_name}_{timestamp}/
Example: astm3_20251117_161251/

Groups by paper_name and keeps only the most recent based on timestamp.
"""

import argparse
import logging
import re
import shutil
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


def parse_log_dirname(dirname: str) -> tuple[datetime, str] | None:
    """Parse slurm log directory name into (timestamp, paper_name).

    Format: {paper_name}_{timestamp}
    Example: astm3_20251117_161251

    Args:
        dirname: Name of directory

    Returns:
        Tuple of (timestamp, paper_name) or None if parse fails
    """
    # Pattern: everything up to last underscore is paper name, then timestamp
    # Timestamp format: YYYYMMDD_HHMMSS
    pattern = r'^(.+)_(\d{8})_(\d{6})$'
    match = re.match(pattern, dirname)

    if not match:
        return None

    paper_name, date_str, time_str = match.groups()

    # Parse timestamp
    try:
        timestamp_str = f"{date_str}{time_str}"
        timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
    except ValueError as e:
        logger.warning(f"Could not parse timestamp in {dirname}: {e}")
        return None

    return timestamp, paper_name


def find_duplicate_logs(
    directories: list[str],
    dataloader: Dataloader | None = None
) -> dict[str, list[tuple[Path, datetime]]]:
    """Find duplicate slurm log directories grouped by paper.

    Args:
        directories: List of directory paths to search
        dataloader: Optional Dataloader to get expected paper names

    Returns:
        Dict mapping paper_name -> list of (path, timestamp) tuples
    """
    # Group log dirs by paper name
    paper_logs = defaultdict(list)

    # Get expected paper names if dataloader provided
    expected_papers = set()
    if dataloader:
        # Note: paper names in slurm logs keep underscores
        expected_papers = set(dataloader.papers.keys())

    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.warning(f"Directory does not exist: {directory}")
            continue

        # Look for subdirectories that match the pattern
        for log_dir in dir_path.iterdir():
            if not log_dir.is_dir():
                continue

            parsed = parse_log_dirname(log_dir.name)
            if not parsed:
                logger.debug(f"Could not parse dirname: {log_dir.name}")
                continue

            timestamp, paper_name = parsed

            # If we have expected papers, check if this is one of them
            # Try both with underscores and hyphens
            paper_name_normalized = paper_name.replace('-', '_')
            if expected_papers and paper_name_normalized not in expected_papers:
                logger.debug(f"Skipping {log_dir.name} - paper not in expected set")
                continue

            paper_logs[paper_name].append((log_dir, timestamp))

    return paper_logs


def purge_old_logs(
    directories: list[str],
    dry_run: bool = True,
    use_dataloader: bool = True
) -> tuple[int, int]:
    """Purge old duplicate slurm log directories, keeping only most recent per paper.

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

    # Find all log dirs grouped by paper
    paper_logs = find_duplicate_logs(directories, dataloader)

    # Find duplicates and mark old ones for deletion
    to_delete = []
    total_dirs = 0

    for paper_name, logs in paper_logs.items():
        total_dirs += len(logs)

        if len(logs) <= 1:
            continue

        # Sort by timestamp (most recent first)
        logs.sort(key=lambda x: x[1], reverse=True)

        # Keep first (most recent), delete rest
        most_recent = logs[0]
        old_logs = logs[1:]

        logger.info(f"\n{paper_name}: Found {len(logs)} versions")
        logger.info(f"  Keeping: {most_recent[0].name} ({most_recent[1]})")
        logger.info(f"  Removing {len(old_logs)} old version(s):")

        for log_path, timestamp in old_logs:
            logger.info(f"    - {log_path.name} ({timestamp})")
            to_delete.append(log_path)

    logger.info(f"\nSummary: {len(to_delete)} old duplicates out of {total_dirs} total log directories")

    if not dry_run and to_delete:
        logger.info("\nDeleting old directories...")
        for d in to_delete:
            shutil.rmtree(d)
            logger.info(f"  Deleted: {d}")
    elif dry_run and to_delete:
        logger.info("\n(Dry run - no directories deleted. Use --execute to actually delete)")

    return len(to_delete), total_dirs


def main():
    parser = argparse.ArgumentParser(
        description="Purge old duplicate slurm log directories, keeping only the most recent for each paper"
    )
    parser.add_argument(
        "directories",
        nargs="+",
        help="Directory or directories to search for log subdirectories"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete directories (default is dry-run)"
    )
    parser.add_argument(
        "--no-dataloader",
        action="store_true",
        help="Don't use dataloader to filter expected papers"
    )

    args = parser.parse_args()

    deleted_count, total_count = purge_old_logs(
        args.directories,
        dry_run=not args.execute,
        use_dataloader=not args.no_dataloader
    )

    logger.info(f"\nFinal summary: Would delete {deleted_count} / {total_count} log directories")
    if args.execute:
        logger.info("Directories have been deleted.")


if __name__ == "__main__":
    main()
