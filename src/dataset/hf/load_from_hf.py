import json
from datasets import load_dataset

dataset = load_dataset("your-org/researchbench")

papers = dataset["papers"]
tasks = dataset["tasks"]

print(f"Loaded {len(papers)} papers")
print(f"Loaded {len(tasks)} tasks")
print(f"\nFirst paper: {papers[0]['paper_id']}")
print(f"First task: {tasks[0]['task_id']} (paper: {tasks[0]['paper_id']})")

example_task = tasks[0]
expected_output = json.loads(example_task['expected_output'])
tolerance = json.loads(example_task['tolerance'])
print(f"\nExpected output (deserialized): {expected_output}")
print(f"Tolerance (deserialized): {tolerance}")
