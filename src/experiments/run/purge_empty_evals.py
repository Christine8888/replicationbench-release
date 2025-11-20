"""Purge empty .eval files from log directories.

An .eval file is considered empty if it only contains _journal/start.json
and no actual evaluation results (samples, summaries, etc.).
"""

import argparse
import fnmatch
import logging
import zipfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def is_empty_eval(eval_path: Path) -> bool:
    """Check if .eval file is empty (only contains start.json).

    Args:
        eval_path: Path to .eval file

    Returns:
        True if file is empty/incomplete, False if it has results
    """
    if not eval_path.exists():
        return False

    if eval_path.stat().st_size == 0:
        return True

    try:
        with zipfile.ZipFile(eval_path, 'r') as zf:
            namelist = zf.namelist()

            # Empty if only has start.json
            if len(namelist) == 1 and namelist[0] == '_journal/start.json':
                return True

            # Also check for presence of actual results
            has_samples = any('samples/' in name for name in namelist)
            has_summaries = 'summaries.json' in namelist

            # If it has more files but no results, consider it empty
            if not has_samples and not has_summaries:
                return True

            return False

    except (zipfile.BadZipFile, OSError) as e:
        logger.warning(f"Could not read {eval_path}: {e}")
        return True


def should_exclude(file_path: Path, exclude_patterns: list[str]) -> bool:
    """Check if a file should be excluded based on patterns.

    Args:
        file_path: Path to check
        exclude_patterns: List of patterns to match against

    Returns:
        True if file should be excluded, False otherwise
    """
    if not exclude_patterns:
        return False

    # Check both the full path and just the filename
    full_path_str = str(file_path)
    filename = file_path.name

    for pattern in exclude_patterns:
        # Check if pattern matches the filename or full path
        if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(full_path_str, pattern):
            return True
        # Also check if pattern is an exact match for filename
        if filename == pattern:
            return True

    return False


def purge_empty_evals(directories: list[str], dry_run: bool = True, exclude: list[str] = None) -> tuple[int, int]:
    """Purge empty .eval files from directories.

    Args:
        directories: List of directory paths to search
        dry_run: If True, only report what would be deleted
        exclude: List of patterns to exclude from deletion

    Returns:
        Tuple of (empty_count, total_count)
    """
    empty_files = []
    excluded_files = []
    total_files = 0

    exclude = exclude or []

    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.warning(f"Directory does not exist: {directory}")
            continue

        for eval_file in dir_path.rglob('*.eval'):
            total_files += 1

            # Check if file should be excluded
            if should_exclude(eval_file, exclude):
                if is_empty_eval(eval_file):
                    excluded_files.append(eval_file)
                continue

            if is_empty_eval(eval_file):
                empty_files.append(eval_file)

    logger.info(f"Found {len(empty_files)} empty .eval files out of {total_files} total")

    if excluded_files:
        logger.info(f"Excluded {len(excluded_files)} empty files from deletion due to --exclude patterns")
        logger.info("\nExcluded empty files:")
        for f in excluded_files:
            logger.info(f"  {f} (excluded)")

    if empty_files:
        logger.info("\nEmpty files to be deleted:")
        for f in empty_files:
            logger.info(f"  {f}")

    if not dry_run and empty_files:
        logger.info("\nDeleting empty files...")
        for f in empty_files:
            f.unlink()
            logger.info(f"  Deleted: {f}")
    elif dry_run and empty_files:
        logger.info("\n(Dry run - no files deleted. Use --execute to actually delete)")

    return len(empty_files), total_files


def main():
    parser = argparse.ArgumentParser(
        description="Purge empty .eval files from log directories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be deleted
  python purge_empty_evals.py ../../../logs

  # Exclude specific files
  python purge_empty_evals.py ../../../logs --exclude important.eval backup_*.eval

  # Exclude files matching a pattern
  python purge_empty_evals.py ../../../logs --exclude "*backup*" --execute

  # Exclude multiple patterns
  python purge_empty_evals.py ../../../logs --exclude test_*.eval experiment_42.eval
        """
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
        "--exclude",
        nargs="*",
        default=[],
        help="Patterns or filenames to exclude from deletion (supports wildcards like *.eval)"
    )

    args = parser.parse_args()

    empty_count, total_count = purge_empty_evals(
        args.directories,
        dry_run=not args.execute,
        exclude=args.exclude
    )

    logger.info(f"\nSummary: {empty_count} empty / {total_count} total .eval files")


if __name__ == "__main__":
    main()
