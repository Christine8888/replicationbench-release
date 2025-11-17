import argparse
import json
import os
import logging
from pathlib import Path
from typing import Optional, List
from inspect_ai import eval
from dataset.dataloader import Dataloader
from evaluation.inspect_task import paper as paper_task

logger = logging.getLogger(__name__)


def run_single_evaluation(
    paper_id: str,
    model: str,
    log_dir: str,
    workspace: Optional[str] = None,
    papers_dir: Optional[str] = None,
    tasks_dir: Optional[str] = None,
    manuscripts_dir: Optional[str] = None,
    task_types: Optional[List[str]] = None,
    masked: bool = True,
    message_limit: int = 500,
    token_limit: int = 200000,
    execution_timeout: int = 6000,
    time_limit: int = 12000,
    attempts: int = 1,
    cache: bool = True,
    mode: str = "base",
    include_workspace: bool = True,
    display: str = "full",
    sandbox: str = "local",
    python_name: str = "python",
    bash_name: str = "bash"
) -> None:
    """Run evaluation for a single paper.

    Args:
        paper_id: Paper ID to evaluate
        model: Model name for Inspect AI
        log_dir: Directory for evaluation logs
        workspace: Paper-specific workspace directory (e.g., /workspace/paper_id)
        papers_dir: Papers directory (optional, uses default if None)
        tasks_dir: Tasks directory (optional, uses default if None)
        manuscripts_dir: Manuscripts directory (optional, uses default if None)
        task_types: Task types to evaluate
        masked: Whether to use masked text
        message_limit: Max messages in conversation
        token_limit: Max tokens in conversation
        execution_timeout: Tool execution timeout
        time_limit: Total task timeout
        attempts: Number of attempts
        cache: Use prompt caching
        mode: Agent mode ('base' or 'react')
        include_workspace: Alert agent about pre-downloaded data
        display: Display mode for Inspect
        sandbox: Sandbox environment ("local" or "docker")
    """
    logger.info(f"Running evaluation for paper: {paper_id}")
    os.makedirs(log_dir, exist_ok=True)

    loader = Dataloader(
        papers_dir=papers_dir,
        tasks_dir=tasks_dir,
        manuscripts_dir=manuscripts_dir,
        paper_ids=[paper_id],
        task_types=task_types,
        load_text=True,
        masked=masked
    )

    if paper_id not in loader.papers:
        logger.error(f"Paper {paper_id} not found")
        raise ValueError(f"Paper {paper_id} not found")

    paper_obj = loader.papers[paper_id]

    task = paper_task(
        paper_obj=paper_obj,
        workspace=workspace,
        attempts=attempts,
        message_limit=message_limit,
        token_limit=token_limit,
        execution_timeout=execution_timeout,
        time_limit=time_limit,
        cache=cache,
        mode=mode,
        include_workspace=include_workspace,
        sandbox=sandbox,
        python_name=python_name,
        bash_name=bash_name
    )

    model_args = {}
    if model.startswith("openai/") or model.startswith("azure/"):
        model_args = {"responses_api": False}

    logger.info(f"Starting evaluation with model: {model}")
    eval(
        task,
        model=model,
        model_args=model_args,
        log_dir=log_dir,
        display=display,
        retry_on_error=3
    )
    logger.info("Evaluation complete")


def main():
    """CLI args are only for *overriding* config file values, not for setting defaults"""
    parser = argparse.ArgumentParser(description="Run single paper evaluation")

    parser.add_argument("--paper_id", "-p", required=True, help="Paper ID to evaluate")
    parser.add_argument("--model", "-m", help="Model name (required if not in config)")
    parser.add_argument("--log_dir", "-l", required=True, help="Log directory")

    parser.add_argument("--workspace", help="Paper-specific workspace directory")
    parser.add_argument("--papers_dir", help="Papers directory")
    parser.add_argument("--tasks_dir", help="Tasks directory")
    parser.add_argument("--manuscripts_dir", help="Manuscripts directory")

    parser.add_argument("--task_types", nargs="+", help="Task types to evaluate")
    parser.add_argument("--no_masking", action="store_true", help="Disable text masking")

    parser.add_argument("--message_limit", type=int, default=None)
    parser.add_argument("--token_limit", type=int, default=None)
    parser.add_argument("--execution_timeout", type=int, default=None)
    parser.add_argument("--time_limit", type=int, default=None)
    parser.add_argument("--attempts", type=int, default=None)

    parser.add_argument("--no_cache", action="store_true", help="Disable prompt caching")
    parser.add_argument("--mode", choices=["base", "react"], default=None)
    parser.add_argument("--no_workspace", action="store_true", help="Don't alert agent about workspace")
    parser.add_argument("--display", default=None)
    parser.add_argument("--sandbox", choices=["local", "docker"], default="local",
                        help="Sandbox environment (local or docker)")

    parser.add_argument("--python_name", default="python", help="Name for python tool (default: python)")
    parser.add_argument("--bash_name", default="bash", help="Name for bash tool (default: bash)")

    parser.add_argument("--config", help="JSON config file (overrides other args)")

    args = parser.parse_args()

    if args.config:
        logger.info(f"Loading config from {args.config}")
        with open(args.config) as f:
            config = json.load(f)

        for key, value in config.items():
            key_lower = key.lower()
            if not hasattr(args, key_lower) or getattr(args, key_lower) is None:
                setattr(args, key_lower, value)

    if args.message_limit is None:
        args.message_limit = 500
    if args.token_limit is None:
        args.token_limit = 200000
    if args.execution_timeout is None:
        args.execution_timeout = 6000
    if args.time_limit is None:
        args.time_limit = 12000
    if args.attempts is None:
        args.attempts = 1
    if args.mode is None:
        args.mode = "base"
    if args.display is None:
        args.display = "conversation" # for better readability

    if hasattr(args, 'cache') and not args.no_cache:
        args.no_cache = not args.cache
    if hasattr(args, 'masking') and not args.no_masking:
        args.no_masking = not args.masking
    if hasattr(args, 'include_workspace') and not args.no_workspace:
        args.no_workspace = not args.include_workspace

    if not args.model:
        parser.error("--model is required (either via CLI or config file)")

    run_single_evaluation(
        paper_id=args.paper_id,
        model=args.model,
        log_dir=args.log_dir,
        workspace=args.workspace,
        papers_dir=args.papers_dir,
        tasks_dir=args.tasks_dir,
        manuscripts_dir=args.manuscripts_dir,
        task_types=args.task_types,
        masked=not args.no_masking,
        message_limit=args.message_limit,
        token_limit=args.token_limit,
        execution_timeout=args.execution_timeout,
        time_limit=args.time_limit,
        attempts=args.attempts,
        cache=not args.no_cache,
        mode=args.mode,
        include_workspace=not args.no_workspace,
        display=args.display,
        sandbox=args.sandbox,
        python_name=args.python_name,
        bash_name=args.bash_name
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
