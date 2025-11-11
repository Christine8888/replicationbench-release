"""Export full task details without any wrapping."""
from src.dataset.dataloader import Dataloader
import json

# Load only expert tasks
loader = Dataloader(filters={"source": "expert"}, load_text=False)

# Collect all tasks with paper context
all_tasks = []
for paper_id, paper in sorted(loader.papers.items()):
    for task_id, task in sorted(paper.tasks.items()):
        all_tasks.append({
            'task_id': task_id,
            'paper_id': paper_id,
            'paper_title': paper.title,
            'kind': task.kind,
            'difficulty': task.difficulty,
            'description': task.description,
            'instructions': task.instructions,
            'expected_output': task.expected_output
        })

# Export as JSON
with open('/Users/christineye/rb-release/all_expert_tasks_full.json', 'w') as f:
    json.dump(all_tasks, f, indent=2)

print(f"Exported {len(all_tasks)} tasks to all_expert_tasks_full.json")
