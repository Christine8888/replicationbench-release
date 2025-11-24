# Contributing Tasks to ReplicationBench

## Overview
Every paper in ReplicationBench consists of:
- `paper_id`: A unique and informative identifier for the paper
- `src/dataset/manuscripts/{paper_id}.txt`: The full text of the paper
- `src/dataset/papers/{paper_id}.json`: Metadata for the paper, including details about dataset access and execution requirements
- `src/dataset/tasks/{paper_id}/`: A directory for tasks associated with the paper
    - `src/dataset/tasks/{paper_id}/{task_id}.json`: Information for the task, including the task's `kind`, `description`, `instructions`, `expected_output`, and `tolerance`

## Submitting a Task PR

See [gw_cosmo.json](src/dataset/papers/gw_cosmo.json) for an example paper and [classifier_performance.json](src/dataset/tasks/hubble_trails/classifier_performance.json) for an example task. [paper_template.json](src/dataset/paper_template.json) and [task_template.json](src/dataset/task_template.json) may also be useful templates.

To submit a PR containing new tasks, complete the following steps:

### 1. Choose a `paper_id` for the paper

### 2. Add the paper manuscript
Add the full text of the paper, preferably LaTeX source, at `src/dataset/manuscripts/{paper_id}.txt`.

### 3. Create paper metadata file
Create a new file `src/dataset/papers/{paper_id}.json` with the following metadata:

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `paper_id` | string | unique ID of the paper |
| `title` | string | full title |
| `abstract` | string | full abstract |
| `publication_date` | string | format: `YYYY-MM-DD` |

#### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `paper_link` | string | link to the paper (preferably arXiv) (default: `""`) |
| `code_available` | boolean | whether the code for the paper is available (default: `false`) |
| `code_link` | string | link to the code (default: `null`) |
| `execution_requirements` | dict | execution requirements (see below) (default: `null`) |
| `dataset` | dict or list[dict] | dataset metadata (see below) (default: `[]`) |
| `other_instructions` | string | any other specifications required for complete reproducibility (random seeds, hyperparameters, etc.) (default: `null`) |
| `source` | string | source of paper (default: `"expert"`) |

#### Execution Requirements
`execution_requirements` is an optional dictionary with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code_language` | list[string] | **Yes** | programming language(s) of the code (e.g., `["python"]` or `["C++", "Python"]`) |
| `dependencies` | list[string] | **Yes** | list of Python package dependencies (e.g., `["numpy", "scipy", "astropy>=5.0"]`) |
| `needs_gpu` | boolean | No | whether the task requires a GPU (default: `false`) |

#### Dataset Specification
`dataset` is a dictionary or list of dictionaries for datasets used in the paper. Datasets should be hosted on **HuggingFace** for easy access.

**Base fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dataset_name` | string | **Yes** | Name of the dataset |
| `kind` | string | **Yes** | Must be `"huggingface"` |
| `data_instructions` | dict | No | Instructions for accessing/reading the dataset<br>Example: `{"access_instructions": "Load with datasets.load_dataset()"}` |

**HuggingFace-specific fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `hf_name` | list[string] | **Yes** | HuggingFace dataset/repo name(s) |
| `hf_type` | list[string] | **Yes** | either `"dataset"` (standard HF dataset) or `"snapshot"` (full repo download) |
| `hf_split` | list[string] | No | dataset split(s) (default: `["train"]`) |
| `hf_link` | list[string] | No | HuggingFace URL(s) for reference |

**Example:**
```json
"dataset": {
    "dataset_name": "Gaia DR3 catalog",
    "kind": "huggingface",
    "hf_name": ["gaia-collaboration/gaia-dr3"],
    "hf_type": ["dataset"],
    "hf_split": ["train"],
    "hf_link": ["https://huggingface.co/datasets/gaia-collaboration/gaia-dr3"],
    "data_instructions": {
        "access_instructions": "Load with datasets.load_dataset('gaia-collaboration/gaia-dr3')"
    }
}
```

**Note:** If your paper doesn't require any datasets, you can omit the `dataset` field entirely or set it to an empty list `[]`.

### 4. Create tasks directory
Create a new folder in `src/dataset/tasks` with the name `{paper_id}`.

### 5. Select and create tasks
Select a suite of results from the paper that satisfy the following properties:
- i) Objective end results as numerical quantities
- ii) Roughly cover the main results and contributions of the paper
- iii) Span a range of difficulty levels (intermediate results, i.e. dataset sizes after selection cuts, can be used for easier tasks)
- iv) Require fully implementing the methodology of the paper for replication

For each task, choose a `task_id` and create a new JSON file in the `src/dataset/tasks/{paper_id}` directory with the task name.

### 6. Fill in task metadata
For each task JSON file, include the following fields:

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | unique ID of the task |
| `paper_id` | string | ID of the paper |
| `kind` | string | must be `"numeric"` |
| `difficulty` | integer | 1-10 rating (log scale) estimating how long it would take an expert that is not an author of the paper to recreate the task, given the complete instructions<br>1: <15 minutes, 5: ~10-20 hours, 10: 1+ months |
| `description` | string | short (~1 sentence) summary of the task |
| `instructions` | string or list[string] | full instructions specifying task requirements and exact output format<br>Do not repeat information already listed in the paper, but fully specify the task, and provide any additional details necessary for replication that are not in the manuscript (random seeds, hyperparameters, algorithm details, etc.) |
| `expected_output` | any | expected output as a single float, tuple, list, dict, etc. |
| `tolerance` | must match `expected_output` | tolerance range for correctness (any answers in `expected_output` ± `tolerance` will be graded as correct); should generally be as small as possible, while accounting for statistical fluctuations or numerical precision |

#### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `parents` | list[string] | list of parent task IDs that this task is dependent on (default: `null`) |

### 7. Submit a PR!

Please double check and ensure your PR includes:
- Paper manuscript (`src/dataset/manuscripts/{paper_id}.txt`)
- Paper metadata (`src/dataset/papers/{paper_id}.json`)
- All task files (`src/dataset/tasks/{paper_id}/*.json`)
- Datasets hosted on HuggingFace (with access instructions in the metadata)

We'll review and provide feedback. We will also do the manuscript masking automatically. Thank you for contributing to ReplicationBench!