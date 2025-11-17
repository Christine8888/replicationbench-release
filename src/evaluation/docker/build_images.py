"""Build Docker images for paper evaluations."""

import os
import subprocess
import logging
from pathlib import Path
from typing import List, Optional
from dataset.dataloader import Dataloader

logger = logging.getLogger(__name__)


def filter_dependencies(deps: List[str]) -> List[str]:
    """Filter out dependencies already in base image."""
    base_installed = [
        'numpy', 'scipy', 'matplotlib', 'pandas', 'astropy', 'scikit-learn',
        'anthropic', 'openai', 'scikit-image', 'seaborn', 'datasets',
        'plotly', 'sympy', 'networkx', 'numba', 'h5py', 'tqdm', 'pyyaml',
        'toml', 'requests', 'filelock', 'torch', 'tensorflow', 'inspect-ai',
        'jupyter', 'ipython', 'black', 'pytest'
    ]

    additional_deps = []
    for dep in deps:
        dep_name = dep.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].lower()
        if dep_name not in base_installed:
            additional_deps.append(dep)

    return additional_deps


def generate_paper_dockerfile(paper) -> str:
    """Generate Dockerfile for a specific paper."""
    deps = paper.execution_requirements.dependencies if paper.execution_requirements else []
    additional_deps = filter_dependencies(deps)

    dockerfile = f"""FROM replicationbench:base

"""

    if additional_deps:
        dockerfile += f"RUN python3 -m pip install --no-cache-dir {' '.join(additional_deps)}\n\n"

    dockerfile += "WORKDIR /tmp\n"

    return dockerfile


def generate_compose_file(paper_id: str, needs_gpu: bool = False) -> str:
    """Generate docker-compose.yaml for a paper."""
    compose = f"""services:
  default:
    image: replicationbench:{paper_id}
    volumes:
      - ../../workspace/{paper_id}:/workspace:ro
    working_dir: /tmp
    command: "tail -f /dev/null"
    init: true
    network_mode: host
    stop_grace_period: 1s
"""

    if needs_gpu:
        compose += """    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
"""

    return compose


def build_base_image(force_rebuild: bool = False) -> bool:
    """Build the base Docker image."""
    dockerfile_path = Path(__file__).parent / "Dockerfile.base"

    if not force_rebuild:
        result = subprocess.run(
            ["docker", "images", "-q", "replicationbench:base"],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            logger.info("Base image already exists, skipping build")
            return True

    logger.info("Building base image...")
    logger.info(f"Running: docker build -f {dockerfile_path.name} -t replicationbench:base .")

    result = subprocess.run(
        ["docker", "build", "-f", str(dockerfile_path), "-t", "replicationbench:base", "."],
        cwd=dockerfile_path.parent,
        check=False
    )

    if result.returncode != 0:
        logger.error(f"Failed to build base image (exit code: {result.returncode})")
        return False

    logger.info("Base image built successfully")
    return True


def build_paper_image(paper_id: str, force_rebuild: bool = False) -> Path:
    """Build Docker image for a specific paper."""
    loader = Dataloader(paper_ids=[paper_id], load_text=False)
    if paper_id not in loader.papers:
        raise ValueError(f"Paper {paper_id} not found")

    paper = loader.papers[paper_id]

    docker_dir = Path(f"docker/{paper_id}")
    docker_dir.mkdir(parents=True, exist_ok=True)

    if not force_rebuild:
        result = subprocess.run(
            ["docker", "images", "-q", f"replicationbench:{paper_id}"],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            logger.info(f"Image for {paper_id} already exists, skipping build")
            return docker_dir

    dockerfile_content = generate_paper_dockerfile(paper)
    (docker_dir / "Dockerfile").write_text(dockerfile_content)

    needs_gpu = paper.execution_requirements.needs_gpu if paper.execution_requirements else False
    compose_content = generate_compose_file(paper_id, needs_gpu)
    (docker_dir / "compose.yaml").write_text(compose_content)

    logger.info(f"Building image for {paper_id}...")
    logger.info(f"Running: docker build -f Dockerfile -t replicationbench:{paper_id} .")

    result = subprocess.run(
        ["docker", "build", "-f", "Dockerfile", "-t", f"replicationbench:{paper_id}", "."],
        cwd=docker_dir,
        check=False
    )

    if result.returncode != 0:
        logger.error(f"Failed to build image for {paper_id} (exit code: {result.returncode})")
        raise RuntimeError(f"Docker build failed for {paper_id}")

    logger.info(f"Image built successfully for {paper_id}")
    return docker_dir


def main():
    """CLI for building Docker images."""
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Build Docker images for ReplicationBench")
    parser.add_argument("--base", action="store_true", help="Build base image")
    parser.add_argument("--paper-id", "--paper_id", help="Paper ID to build image for")
    parser.add_argument("--all", action="store_true", help="Build images for all papers")
    parser.add_argument("--force", action="store_true", help="Force rebuild even if image exists")

    args = parser.parse_args()

    if args.base or args.all:
        if not build_base_image(args.force):
            exit(1)

    if args.paper_id:
        build_paper_image(args.paper_id, args.force)
    elif args.all:
        loader = Dataloader(load_text=False)
        for paper_id in loader.papers.keys():
            try:
                build_paper_image(paper_id, args.force)
            except Exception as e:
                logger.error(f"Failed to build image for {paper_id}: {e}")


if __name__ == "__main__":
    main()