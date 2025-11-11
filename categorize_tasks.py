"""Display all expert tasks for categorization."""
from src.dataset.dataloader import Dataloader

# Load only expert tasks
loader = Dataloader(filters={"source": "expert"}, load_text=False)

# Collect all tasks with paper context
all_tasks = []
for paper_id, paper in sorted(loader.papers.items()):
    for task_id, task in sorted(paper.tasks.items()):
        all_tasks.append({
            'paper_id': paper_id,
            'task_id': task_id,
            'task': task,
            'paper_title': paper.title
        })

print(f"Total expert tasks: {len(all_tasks)}")
print("\n" + "="*80)
print("ALL EXPERT TASKS")
print("="*80 + "\n")

# Display all tasks
for idx, item in enumerate(all_tasks, 1):
    task = item['task']
    print(f"\n[{idx}] {task.task_id}")
    print(f"    Paper: {item['paper_title']}")
    print(f"    Kind: {task.kind}")
    print(f"    Difficulty: {task.difficulty}")
    print(f"    Description: {task.description}")
    if task.instructions:
        print(f"    Instructions: {task.instructions[0][:100]}..." if len(task.instructions[0]) > 100 else f"    Instructions: {task.instructions[0]}")
