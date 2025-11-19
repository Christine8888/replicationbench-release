"""Purge all logs and evals for a specific paper.

Deletes:
1. All slurm log directories matching {paper_id}_*
2. All .eval files containing the paper_id in the filename
"""

import argparse
import logging
import re
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def normalize_paper_id(paper_id: str) -> set[str]:
    """Get all possible variants of paper_id (with _ and -)."""
    return {
        paper_id,
        paper_id.replace('_', '-'),
        paper_id.replace('-', '_')
    }


def find_slurm_logs_for_paper(
    slurm_dirs: list[str],
    paper_id: str
) -> list[Path]:
    """Find all slurm log directories for a paper.

    Args:
        slurm_dirs: List of slurm log directory paths
        paper_id: Paper ID to search for

    Returns:
        List of directory paths to delete
    """
    to_delete = []
    paper_variants = normalize_paper_id(paper_id)

    for slurm_dir in slurm_dirs:
        dir_path = Path(slurm_dir)
        if not dir_path.exists():
            logger.warning(f"Directory does not exist: {slurm_dir}")
            continue

        # Pattern: {paper_name}_{timestamp}
        for subdir in dir_path.iterdir():
            if not subdir.is_dir():
                continue

            # Check if directory name starts with any paper variant
            dir_name = subdir.name
            for variant in paper_variants:
                # Match {paper_id}_{digits}_{digits}
                if re.match(rf'^{re.escape(variant)}_\d{{8}}_\d{{6}}$', dir_name):
                    to_delete.append(subdir)
                    break

    return to_delete


def find_evals_for_paper(
    eval_dirs: list[str],
    paper_id: str
) -> list[Path]:
    """Find all .eval files for a paper.

    Args:
        eval_dirs: List of directories containing .eval files
        paper_id: Paper ID to search for

    Returns:
        List of .eval file paths to delete
    """
    to_delete = []
    paper_variants = normalize_paper_id(paper_id)

    for eval_dir in eval_dirs:
        dir_path = Path(eval_dir)
        if not dir_path.exists():
            logger.warning(f"Directory does not exist: {eval_dir}")
            continue

        # Search recursively for .eval files
        for eval_file in dir_path.rglob('*.eval'):
            # Check if filename contains any paper variant
            # Format: {timestamp}_{paper_name}_{hash}.eval
            file_name = eval_file.name

            for variant in paper_variants:
                # Match timestamp_{paper_id}_{hash}.eval
                if re.search(rf'_(?:{re.escape(variant)})_[a-zA-Z0-9]+\.eval$', file_name):
                    to_delete.append(eval_file)
                    break

    return to_delete


def purge_all_paper(
    paper_id: str,
    slurm_dirs: list[str] | None = None,
    eval_dirs: list[str] | None = None,
    dry_run: bool = True
) -> tuple[int, int]:
    """Purge all logs and evals for a specific paper.

    Args:
        paper_id: Paper ID to purge
        slurm_dirs: List of slurm log directories
        eval_dirs: List of directories containing .eval files
        dry_run: If True, only report what would be deleted

    Returns:
        Tuple of (slurm_deleted_count, eval_deleted_count)
    """
    slurm_to_delete = []
    evals_to_delete = []

    # Find slurm logs
    if slurm_dirs:
        logger.info(f"Searching for slurm logs for paper: {paper_id}")
        slurm_to_delete = find_slurm_logs_for_paper(slurm_dirs, paper_id)
        if slurm_to_delete:
            logger.info(f"\nFound {len(slurm_to_delete)} slurm log directories:")
            for d in slurm_to_delete:
                logger.info(f"  {d}")
        else:
            logger.info("  No slurm logs found")

    # Find eval files
    if eval_dirs:
        logger.info(f"\nSearching for .eval files for paper: {paper_id}")
        evals_to_delete = find_evals_for_paper(eval_dirs, paper_id)
        if evals_to_delete:
            logger.info(f"\nFound {len(evals_to_delete)} .eval files:")
            for f in evals_to_delete:
                logger.info(f"  {f}")
        else:
            logger.info("  No .eval files found")

    # Summary
    total = len(slurm_to_delete) + len(evals_to_delete)
    logger.info(f"\nTotal items to delete: {total}")
    logger.info(f"  - {len(slurm_to_delete)} slurm log directories")
    logger.info(f"  - {len(evals_to_delete)} .eval files")

    # Delete if not dry run
    if not dry_run and total > 0:
        logger.info("\nDeleting items...")

        # Delete slurm logs
        for d in slurm_to_delete:
            shutil.rmtree(d)
            logger.info(f"  Deleted directory: {d}")

        # Delete eval files
        for f in evals_to_delete:
            f.unlink()
            logger.info(f"  Deleted file: {f}")

        logger.info("\nDeletion complete!")
    elif dry_run and total > 0:
        logger.info("\n(Dry run - no items deleted. Use --execute to actually delete)")

    return len(slurm_to_delete), len(evals_to_delete)


def main():
    parser = argparse.ArgumentParser(
        description="Purge all logs and evals for a specific paper"
    )
    parser.add_argument(
        "paper_id",
        help="Paper ID to purge (e.g., 'astm3', 'tng_hod')"
    )
    parser.add_argument(
        "--slurm-logs",
        nargs="+",
        help="Directory or directories containing slurm logs"
    )
    parser.add_argument(
        "--eval-logs",
        nargs="+",
        help="Directory or directories containing .eval files"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete items (default is dry-run)"
    )

    args = parser.parse_args()

    if not args.slurm_logs and not args.eval_logs:
        parser.error("Must specify at least one of --slurm-logs or --eval-logs")

    slurm_count, eval_count = purge_all_paper(
        paper_id=args.paper_id,
        slurm_dirs=args.slurm_logs,
        eval_dirs=args.eval_logs,
        dry_run=not args.execute
    )

    logger.info(f"\nFinal summary:")
    logger.info(f"  Slurm logs: {slurm_count} directories")
    logger.info(f"  Eval files: {eval_count} files")
    if args.execute:
        logger.info("Items have been deleted.")


if __name__ == "__main__":
    main()
