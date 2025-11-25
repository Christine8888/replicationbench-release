# ReplicationBench: Can AI Agents Replicate Astrophysics Research Papers?

ReplicationBench evaluates whether AI agents can replicate real astrophysics research papers from scratch. The dataset consists of 111 astrophysics research replication tasks spanning 20 research papers, which can be run and evaluated in computational sandboxes and scored objectively against the original results. Read the paper on [arXiv](https://arxiv.org/abs/2510.24591) for more details.

![ReplicationBench Overview](./figure_1.png)

## Installation

```bash
# Clone just the release branch
git clone --branch main --single-branch https://github.com/Christine8888/replicationbench-release.git
cd replicationbench-release

# Basic installation -- for dataset loading and prompt generation only
uv pip install -e .

# Install with dependencies for downloading datasets
uv pip install -e ".[download]"

# Install with all dependencies (evaluations + datasets)
uv pip install -e ".[all]"
```

## Running Evaluations

### Using Inspect AI

We support running evaluations using [Inspect AI](https://inspect.aisi.org.uk). This release code only supports running evaluations on the core ReplicationBench dataset (not ReplicationBench-Plus). You can get a list of the paper IDs with the following code:

```python
from dataset.dataloader import Dataloader

loader = Dataloader()
for paper_id in loader.papers:
    print(paper_id)
```

ReplicationBench can run in two modes:

#### 1. Local Sandbox (Simplest)
Note that you should generally *not* run agents without some form of sandboxing. However, the ReplicationBench paper's experiments were run on a shared computing resource that did not have Docker support. We used an alternative containerization system (Singularity) and launched containers for every evaluation, but used Inspect's local sandboxing within the containers.

```python
from evaluation.run_single import run_single_evaluation

run_single_evaluation(
    paper_id="gw_cosmo",
    model="anthropic/claude-sonnet-4-5",
    log_dir="./logs/my_run",
    workspace="./workspace/gw_cosmo",
    sandbox="local"
)
```

#### 2. Docker Sandbox (Recommended)
If you have Docker installed, Inspect natively supports using Docker for sandboxed code execution. Use the following steps to build corresponding Docker images (using `subprocess` to call Docker directly) and run evaluations for each paper.

```bash
# 1. Install Docker (https://docs.docker.com/get-docker/)

# 2. Build base image (contains common scientific packages)
python -m src.evaluation.docker.build_images --base

# 3. Build paper-specific image (will be built as replicationbench:{paper_id})
python -m src.evaluation.docker.build_images --paper-id gw_cosmo

# 4. Download datasets for paper to ./workspace/{paper_id}
python -m src.evaluation.setup \
    --paper-id gw_cosmo \
    --workspace-base ./workspace \
    --data-only

# 5. Run evaluation from the paper's docker directory
cd docker/gw_cosmo
python -m evaluation.run_single \
    --paper_id gw_cosmo \
    --model anthropic/claude-sonnet-4-5 \
    --log_dir ../../logs/my_run \
    --workspace ../../workspace/gw_cosmo \
    --sandbox docker \
    --message_limit 1000 \
    --token_limit 5000000 \
    --time_limit 21600 \ # timeout for entire evaluation
    --execution_timeout 7200 # timeout for individual tool calls
```

The base image includes common scientific packages, and paper-specific dependencies are automatically added from each paper's metadata. Papers requiring GPU acceleration automatically have GPU device access configured in their `compose.yaml` file (requires nvidia-container-toolkit on the host). Docker images can be built on any machine and will work on GPU machines as CUDA-enabled PyTorch is included in the base image. 

### API Keys
Set environment variables for your LLM provider before running evaluations:
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
```

See [Inspect AI documentation](https://inspect.aisi.org.uk/models.html) for more details on setting up model providers.

### Viewing Logs
You can use Inspect's built-in log viewer to view evaluation outputs:
```bash
inspect view --log-dir /path/to/log/directory
```

## Python Interface to the Dataset

### Loading Papers and Tasks
You can use the Dataloader to load papers with their associated tasks.
```python
from dataset.dataloader import Dataloader

# load all expert-written tasks
loader = Dataloader()
print(f"Loaded {len(loader.papers)} papers")
for paper_id in loader.papers:
    print(f"  - {paper_id}")

# see example task
task_id = list(loader.papers["gw_cosmo"].tasks.keys())[0]
task = loader.papers["gw_cosmo"].tasks[task_id]
print(task.description)
print(task.instructions)
print(task.expected_output)
print(task.tolerance)
```

### Standard Evaluation Prompts
You can generate evaluation prompts matching the prompts used in the ReplicationBench paper as follows:

```python
from evaluation.core.prompts import get_paper_prompt

paper = loader.papers["gw_cosmo"]
prompt = get_paper_prompt(
    paper=paper,
    workspace="/path/to/workspace/gw_cosmo",  # Optional: workspace path
    include_workspace=True  # Tell agent about pre-downloaded data in the workspace
)
```

### Python Environment Setup
Set up the Python environment for a paper programmatically:

```python
from dataset.dataloader import Dataloader
from evaluation.setup import setup_paper_environment

loader = Dataloader(paper_ids=["gw_cosmo"])
paper = loader.papers["gw_cosmo"]

workspace_dir = "./workspace/gw_cosmo"
setup_paper_environment(
    paper,
    workspace_dir=workspace_dir,
    download_data=True,  # Download datasets
    install_deps=True    # Install Python dependencies
)
```

**Note:** `install_deps=True` installs Python dependencies directly using `pip`, so this should be run inside an isolated environment (virtualenv, conda, or Docker container).

## Known Issues
- Agents may occasionally guess answers due to random chance or general domain knowledge. We strongly suggest filtering and penalizing traces with "guessing" behavior
- Neither this codebase nor TerminalBench provide safeguards preventing agents from accessing the answers via web browsing tools, such as by finding source code or reading the original paper manuscript. This behavior does not appear in our experiments but could affect the fidelity of evaluations.

## Contributing

We welcome contributions of new papers and tasks! If you are a researcher and have a candidate paper you would like to add to the dataset, please contact us with **[this form](https://docs.google.com/forms/d/e/1FAIpQLSe9JcvIFzBD_z1KhOsqNRDhcUBY6seGZRJyRfE_yE4TLPRu5A/viewform?usp=sharing&ouid=101310934872802722547)**. We will reach out with further instructions on how to adapt the paper for the dataset.

We also accept direct PRs for tasks; see [the PR instructions](PR_INSTRUCTIONS.md) for detailed instructions.

## Citation and License

If you use ReplicationBench in your work, please cite:

```bibtex
@misc{ye2025replicationbenchaiagentsreplicate,
      title={ReplicationBench: Can AI Agents Replicate Astrophysics Research Papers?},
      author={Christine Ye and Sihan Yuan and Suchetha Cooray and Steven Dillmann and Ian L. V. Roque and Dalya Baron and Philipp Frank and Sergio Martin-Alvarez and Nolan Koblischke and Frank J Qu and Diyi Yang and Risa Wechsler and Ioana Ciuca},
      year={2025},
      eprint={2510.24591},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2510.24591},
}
```

## License

ReplicationBench is released under the [MIT License](LICENSE).