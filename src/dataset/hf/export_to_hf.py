import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dataset.dataloader import Dataloader


def export_papers(loader, output_path, include_text=True):
    with open(output_path, 'w') as f:
        for paper in loader.papers.values():
            data = {
                'paper_id': paper.paper_id,
                'title': paper.title,
                'abstract': paper.abstract,
                'publication_date': paper.publication_date.strftime('%Y-%m-%d'),
                'paper_link': paper.paper_link,
                'code_available': paper.code_available,
                'code_link': paper.code_link,
                'source': paper.source,
                'dataset': [ds.to_dict() for ds in paper.datasets],
                'execution_requirements': paper.execution_requirements.to_dict() if paper.execution_requirements else None,
                'other_instructions': paper.other_instructions,
                'blacklist_packages': paper.blacklist_packages
            }

            if include_text:
                data['full_text'] = paper.full_text

            f.write(json.dumps(data) + '\n')


def export_tasks(loader, output_path):
    with open(output_path, 'w') as f:
        for paper in loader.papers.values():
            for task in paper.tasks.values():
                instructions = task.instructions
                if isinstance(instructions, str):
                    instructions = [instructions]

                data = {
                    'task_id': task.task_id,
                    'paper_id': task.paper_id,
                    'kind': task.kind,
                    'difficulty': task.difficulty,
                    'description': task.description,
                    'instructions': instructions,
                    'expected_output': json.dumps(task.expected_output),
                    'tolerance': json.dumps(task.tolerance),
                    'parents': task.parents
                }

                f.write(json.dumps(data) + '\n')


if __name__ == '__main__':
    loader = Dataloader(
        filters={'source': 'expert'},
        load_text=True,
        masked=True
    )

    output_dir = Path(__file__).parent

    export_papers(loader, output_dir / 'papers.jsonl', include_text=True)
    print(f"Exported {len(loader.papers)} papers to papers.jsonl")

    export_tasks(loader, output_dir / 'tasks.jsonl')
    total_tasks = sum(len(paper.tasks) for paper in loader.papers.values())
    print(f"Exported {total_tasks} tasks to tasks.jsonl")
