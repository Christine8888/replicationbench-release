"""Launch evaluations on cluster using Slurm."""
import sys
sys.path.append("/home/users/cye/researchbench/src")
import argparse
import json
import os
import subprocess
import logging
from pathlib import Path
from cluster_config import DEFAULT_CONFIG, ClusterConfig
from dataset.dataloader import Dataloader
from evaluation.cluster.slurm import get_slurm_executor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Memory configuration for papers requiring more memory
MEMORY_CONFIG = {
    "fable_mps": 256,
    "tng_hod": 256,
}


def has_existing_eval(paper_id: str, log_dir: str) -> Path | None:
    """Check if paper already has an eval file in the log directory.

    Args:
        paper_id: Paper ID to check
        log_dir: Directory to search for eval files

    Returns:
        Path to existing eval file if found, None otherwise
    """
    log_path = Path(log_dir)
    if not log_path.exists():
        return None

    # Normalize paper_id: check both with hyphens and underscores
    # Paper IDs may use either "_" or "-" as separators
    paper_id_normalized = paper_id.replace("_", "-")
    paper_id_alt = paper_id.replace("-", "_")

    for eval_file in log_path.glob('*.eval'):
        # Check for paper_id with both normalizations
        if (f"_{paper_id}_" in eval_file.name or
            f"_{paper_id_normalized}_" in eval_file.name or
            f"_{paper_id_alt}_" in eval_file.name):
            return eval_file

    return None


def run_paper_job(
    paper_id: str,
    config_path: str,
    cluster_config: ClusterConfig,
    run_name: str,
    needs_gpu: bool = False
) -> dict:
    """Execute evaluation for a single paper in Singularity container.

    Args:
        paper_id: Paper ID to evaluate
        config_path: Path to experiment config JSON
        cluster_config: Cluster configuration
        run_name: Run name for logging
        needs_gpu: Whether GPU is needed

    Returns:
        Job result dict
    """
    paper_workspace = os.path.join(cluster_config.workspace_base, paper_id)
    overlay_path = os.path.join(paper_workspace, "overlay")
    job_tmp_dir = os.path.join(cluster_config.tmp_base, f"job_{paper_id}_{os.getpid()}")
    os.makedirs(job_tmp_dir, exist_ok=True)

    logger.info(f"Running {paper_id} (GPU: {needs_gpu})")

    singularity_cmd = [
        "/usr/bin/singularity", "exec",
        "--overlay", overlay_path,
        "--bind", f"{paper_workspace}:{paper_workspace}:ro",
        "--bind", f"{overlay_path}:{overlay_path}:rw",
        "--bind", f"{cluster_config.home_dir}:{cluster_config.home_dir}:ro",
        "--bind", f"{cluster_config.home_dir}/.config:{cluster_config.home_dir}/.config:rw",
        "--bind", f"{cluster_config.home_dir}/.cache:{cluster_config.home_dir}/.cache:rw",
        "--bind", f"{cluster_config.home_dir}/.pyenv:{cluster_config.home_dir}/.pyenv:rw",
        "--bind", f"{cluster_config.home_dir}/.local/share/inspect_ai:{cluster_config.home_dir}/.local/share/inspect_ai:rw",
        "--bind", f"{cluster_config.inspect_log_dir}:{cluster_config.inspect_log_dir}:rw",
        "--bind", f"{job_tmp_dir}:/tmp:rw"
    ]

    if needs_gpu:
        singularity_cmd.append("--nv")

    # Get src directory (go up from run/ to experiments/ to src/)
    src_dir = Path(__file__).parent.parent.parent.absolute()

    bash_cmd = (
        f"export PYTHONUSERBASE=/usr/local && "
        f"export PYTHONPATH=/tmp/.local/lib/python3.11/site-packages:{src_dir}:{cluster_config.home_dir}/.local/lib/python3.11/site-packages:$PYTHONPATH && "
        f"export PATH=/usr/local/bin:/tmp/.local/bin:$PATH && "
        f"export HOME=/tmp && "
        f"export GALPYRC=/tmp/.galpyrc && "
        f"export XDG_CONFIG_HOME=/tmp/.config && "
        f"export XDG_CACHE_HOME=/tmp/.cache && "
        f"export MPLCONFIGDIR=/tmp/.matplotlib && "
        f"source {cluster_config.api_key_path} && "
        f"cd {os.getcwd()} && "
        f"mkdir -p /tmp/inspect_ai && "
        f"python3 -m evaluation.run_single "
        f"--paper_id {paper_id} "
        f"--config {config_path} "
        f"--log_dir {cluster_config.inspect_log_dir}/{run_name}/logs "
        f"--workspace {paper_workspace}"
    )

    singularity_cmd.extend([
        cluster_config.singularity_image,
        "/bin/bash", "-c",
        bash_cmd
    ])

    process = subprocess.run(singularity_cmd)

    return {
        "paper_id": paper_id,
        "exit_code": process.returncode
    }


def main():
    parser = argparse.ArgumentParser(description="Launch batch evaluations on cluster")
    parser.add_argument("--config", "-c", required=True, help="Experiment config JSON")
    parser.add_argument("--run_name", "-r", help="Override run name")
    parser.add_argument("--paper_id", "-p", help="Run single paper only")
    args = parser.parse_args()

    with open(args.config) as f:
        exp_config = json.load(f)

    if args.run_name:
        exp_config["RUN_NAME"] = args.run_name

    cluster_config = DEFAULT_CONFIG

    # Ensure base log directories exist
    Path(cluster_config.slurm_log_dir).mkdir(parents=True, exist_ok=True)
    Path(cluster_config.inspect_log_dir).mkdir(parents=True, exist_ok=True)
    Path(cluster_config.tmp_base).mkdir(parents=True, exist_ok=True)

    # Create run-specific directories
    slurm_log_dir = os.path.join(cluster_config.slurm_log_dir, exp_config["RUN_NAME"])
    inspect_log_dir = os.path.join(cluster_config.inspect_log_dir, exp_config["RUN_NAME"], "logs")
    Path(slurm_log_dir).mkdir(parents=True, exist_ok=True)
    Path(inspect_log_dir).mkdir(parents=True, exist_ok=True)

    logger.info(f"Slurm logs: {slurm_log_dir}")
    logger.info(f"Inspect logs: {inspect_log_dir}")

    paper_list = [args.paper_id] if args.paper_id else []

    loader = Dataloader(
        task_types=exp_config.get("TASK_TYPES"),
        masked=exp_config.get("MASKING", True),
        paper_ids=paper_list,
        filters=exp_config.get("FILTERS")
    )

    paper_ids = list(loader.papers.keys())
    # NOTE: running without chandra_representation 
    paper_ids = [p for p in paper_ids if p != "chandra_representation"]
    
    total_tasks = sum(len(loader.papers[pid].tasks) for pid in paper_ids)
    logger.info(f"Found {len(paper_ids)} papers to process")
    logger.info(f"Total tasks to evaluate: {total_tasks}")

    # Check for existing eval files and filter out papers that already have results
    papers_to_run = []
    for paper_id in paper_ids:
        existing_eval = has_existing_eval(paper_id, inspect_log_dir)
        if existing_eval:
            logger.warning(f"Skipping {paper_id}: eval file already exists at {existing_eval}")
        else:
            papers_to_run.append(paper_id)

    if len(papers_to_run) < len(paper_ids):
        logger.info(f"Filtered: {len(papers_to_run)}/{len(paper_ids)} papers will be run")
        paper_ids = papers_to_run

    if not paper_ids:
        logger.info("No papers to run - all have existing eval files")
        return

    # Group papers by (needs_gpu, mem_gb) to create appropriate executors
    from collections import defaultdict
    paper_groups = defaultdict(list)

    for paper_id in paper_ids:
        paper = loader.papers[paper_id]
        needs_gpu = (
            paper.execution_requirements and
            paper.execution_requirements.needs_gpu
        )
        # Get paper-specific memory, defaulting to cluster config
        mem_gb = MEMORY_CONFIG.get(paper_id, cluster_config.mem_gb)
        paper_groups[(needs_gpu, mem_gb)].append(paper_id)

    logger.info(f"Paper groupings by resource requirements:")
    for (needs_gpu, mem_gb), papers in paper_groups.items():
        logger.info(f"  GPU={needs_gpu}, Memory={mem_gb}GB: {len(papers)} papers")

    # Create executors and submit jobs for each group
    for (needs_gpu, mem_gb), group_papers in paper_groups.items():
        # Use highmem partition for high memory jobs (> 128GB), otherwise GPU or CPU partition
        if mem_gb > 128:
            partition = cluster_config.highmem_partition
        elif needs_gpu:
            partition = cluster_config.gpu_partition
        else:
            partition = cluster_config.cpu_partition

        executor = get_slurm_executor(
            log_dir=slurm_log_dir,
            partition=partition,
            time_hours=cluster_config.time_hours,
            cpus_per_task=cluster_config.cpus_per_task,
            mem_gb=mem_gb,
            job_name=exp_config['RUN_NAME'],
            array_parallelism=cluster_config.n_parallel,
            enable_gpu=needs_gpu
        )

        for paper_id in group_papers:
            with executor.batch():
                job = executor.submit(
                    run_paper_job,
                    paper_id,
                    args.config,
                    cluster_config,
                    exp_config["RUN_NAME"],
                    needs_gpu
                )
                logger.info(f"Submitted job for {paper_id} (Partition={partition}, GPU={needs_gpu}, Memory={mem_gb}GB)")

    logger.info(f"All {len(paper_ids)} jobs submitted to Slurm")
    logger.info(f"Maximum {cluster_config.n_parallel} jobs will run concurrently per executor group")


if __name__ == "__main__":
    main()
