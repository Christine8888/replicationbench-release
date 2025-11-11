"""Re-categorize tasks based on full descriptions and instructions."""
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
print("\n" + "="*100)
print("FULL TASK DETAILS FOR CATEGORIZATION")
print("="*100)

# Display all tasks with full information
for idx, item in enumerate(all_tasks, 1):
    task = item['task']
    print(f"\n{'='*100}")
    print(f"[{idx}/{len(all_tasks)}] {task.task_id}")
    print(f"{'='*100}")
    print(f"Paper: {item['paper_title']}")
    print(f"Kind: {task.kind}")
    print(f"Difficulty: {task.difficulty}")
    print(f"\nDescription:")
    print(f"  {task.description}")
    print(f"\nInstructions:")
    for i, instruction in enumerate(task.instructions, 1):
        # Print full instruction, wrapping at 100 chars for readability
        lines = [instruction[j:j+100] for j in range(0, len(instruction), 100)]
        for line_num, line in enumerate(lines):
            if line_num == 0:
                print(f"  {i}. {line}")
            else:
                print(f"     {line}")
    print()
