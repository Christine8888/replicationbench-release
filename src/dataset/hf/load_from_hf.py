"""Example script to load ResearchBench from HuggingFace and convert to Dataloader format."""

import json
import sys
from pathlib import Path
from datasets import load_dataset
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dataset.dataloader import Dataloader


def load_from_huggingface(dataset_name="ChristineYe8/replicationbench"):
    """Load ResearchBench from HuggingFace and convert to Dataloader format.

    Args:
        dataset_name: HuggingFace dataset name

    Returns:
        Dataloader instance
    """
    dataset = load_dataset(dataset_name)

    papers = dataset["papers"]
    tasks = dataset["tasks"]

    print(f"Loaded {len(papers)} papers")
    print(f"Loaded {len(tasks)} tasks")

    tasks_by_paper = {}
    for task in tasks:
        paper_id = task['paper_id']
        if paper_id not in tasks_by_paper:
            tasks_by_paper[paper_id] = []

        # Deserialize JSON strings
        task_dict = {
            'task_id': task['task_id'],
            'paper_id': task['paper_id'],
            'kind': task['kind'],
            'difficulty': task['difficulty'],
            'description': task['description'],
            'instructions': task['instructions'],
            'expected_output': json.loads(task['expected_output']),
            'tolerance': json.loads(task['tolerance']),
            'parents': task['parents']
        }
        tasks_by_paper[paper_id].append(task_dict)

    # Build paper dictionaries with tasks
    paper_dicts = []
    for paper in papers:
        paper_dict = dict(paper)
        paper_id = paper_dict['paper_id']

        paper_dict['tasks'] = {
            task['task_id']: task
            for task in tasks_by_paper[paper_id]
        }

        paper_dicts.append(paper_dict)

    loader = Dataloader.from_dicts(paper_dicts)

    print(f"Successfully loaded {len(loader.papers)} papers into Dataloader")
    return loader


if __name__ == '__main__':
    loader = load_from_huggingface()

    print("\nExample paper:")
    paper_id = list(loader.papers.keys())[0]
    paper = loader.papers[paper_id]
    print(f"  ID: {paper.paper_id}")
    print(f"  Title: {paper.title}")
    print(f"  Tasks: {len(paper.tasks)}")

    if paper.tasks:
        task_id = list(paper.tasks.keys())[0]
        task = paper.tasks[task_id]
        print(f"\nExample task:")
        print(f"  ID: {task.task_id}")
        print(f"  Kind: {task.kind}")
        print(f"  Expected output: {task.expected_output}")
        print(f"  Tolerance: {task.tolerance}")