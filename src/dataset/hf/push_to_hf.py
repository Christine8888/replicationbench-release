"""Push ResearchBench dataset to HuggingFace."""

import sys
from pathlib import Path
from huggingface_hub import HfApi

# Ensure we're in the right directory
hf_dir = Path(__file__).parent
repo_id = "ChristineYe8/replicationbench"

def push_to_huggingface():
    """Push papers.jsonl, tasks.jsonl, and README.md to HuggingFace."""

    papers_file = hf_dir / "papers.jsonl"
    tasks_file = hf_dir / "tasks.jsonl"
    readme_file = hf_dir / "README.md"

    print(f"Pushing to HuggingFace dataset: {repo_id}")
    print(f"Files to upload:")
    print(f"  - papers.jsonl ({papers_file.stat().st_size / 1024 / 1024:.2f} MB)")
    print(f"  - tasks.jsonl ({tasks_file.stat().st_size / 1024 / 1024:.2f} MB)")
    print(f"  - README.md ({readme_file.stat().st_size / 1024:.2f} KB)")

    api = HfApi()

    api.upload_file(
        path_or_fileobj=str(papers_file),
        path_in_repo="papers.jsonl",
        repo_id=repo_id,
        repo_type="dataset"
    )
    print("✓ papers.jsonl uploaded")

    api.upload_file(
        path_or_fileobj=str(tasks_file),
        path_in_repo="tasks.jsonl",
        repo_id=repo_id,
        repo_type="dataset"
    )
    print("✓ tasks.jsonl uploaded")

    api.upload_file(
        path_or_fileobj=str(readme_file),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="dataset"
    )
    print("✓ README.md uploaded")

    print(f"View at: https://huggingface.co/datasets/{repo_id}")


if __name__ == '__main__':
    push_to_huggingface()
