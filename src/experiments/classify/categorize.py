
import re
from collections import defaultdict
from inspect_ai.model import get_model, GenerateConfig, ChatMessageUser
from dataset.dataloader import Dataloader
import asyncio


CATEGORIES = """1. Data Loading and Processing - Tasks that involve retrieving, parsing, filtering, and organizing data
2. Summary Statistics and Measurements - Computing summary statistics, fractions, counts, or direct measurements from data
3. Model Fitting and Parameter Estimation - Fitting models to data to estimate parameters
4. Bayesian Inference - Hierarchical models, MCMC sampling, posterior analysis, credible intervals
5. Physical Simulations and Theoretical Calculations - Running physics-based simulations or implementing theoretical calculations
6. Machine Learning Applications - Building, training, and evaluating ML models"""


def create_categorization_prompt(abstract: str, task_description: str, task_instructions: str) -> str:
    prompt = f"""You are categorizing research tasks. Given a paper abstract and task details, classify the task into exactly ONE of these categories:

{CATEGORIES}

Paper Abstract:
{abstract}

Task Description:
{task_description}

Task Instructions:
{task_instructions}

Respond with ONLY the category number (1-6) and nothing else."""
    return prompt


def extract_category(response: str) -> int:
    match = re.search(r'\b([1-6])\b', response)
    if match:
        return int(match.group(1))
    return 0


async def categorize_task(model, paper_abstract: str, task) -> int:
    instructions = "\n".join(task.instructions)
    prompt = create_categorization_prompt(paper_abstract, task.description, instructions)

    messages = [ChatMessageUser(content=prompt)]
    response = await model.generate(messages, config=GenerateConfig(temperature=0.0, max_tokens=10))

    category = extract_category(response.completion)
    return category


async def categorize_all_tasks():
    loader = Dataloader(filters={"source": "expert"}, load_text=False)
    model = get_model("anthropic/claude-haiku-4-5")

    categorization = {}
    counts = defaultdict(int)

    tasks_list = []
    for paper_id, paper in sorted(loader.papers.items()):
        for task_id, task in sorted(paper.tasks.items()):
            tasks_list.append((paper_id, paper, task_id, task))

    print(f"Categorizing {len(tasks_list)} tasks...")
    
    for i, (paper_id, paper, task_id, task) in enumerate(tasks_list, 1):
        category = await categorize_task(model, paper.abstract, task)
        categorization[task_id] = category
        counts[category] += 1

        if i % 10 == 0:
            print(f"  Progress: {i}/{len(tasks_list)}")

    category_names = {
        1: "Data Loading and Processing",
        2: "Summary Statistics and Measurements",
        3: "Model Fitting and Parameter Estimation",
        4: "Bayesian Inference",
        5: "Physical Simulations and Theoretical Calculations",
        6: "Machine Learning Applications"
    }

    print("\n" + "="*80)
    print("CATEGORIZATION RESULTS")
    print("="*80)
    print(f"{'#':<5} {'Category':<60} {'Count':<10}")
    print("-"*80)

    total = 0
    for cat_num in range(1, 7):
        count = counts[cat_num]
        total += count
        print(f"{cat_num:<5} {category_names[cat_num]:<60} {count:<10}")

    print("-"*80)
    print(f"{'':5} {'Total':<60} {total:<10}")
    print("="*80)

    if counts[0] > 0:
        print(f"\nWarning: {counts[0]} tasks could not be categorized")

    return categorization, counts

if __name__ == "__main__":
    asyncio.run(categorize_all_tasks())