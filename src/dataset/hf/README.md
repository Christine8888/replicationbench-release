---
dataset_info:
  features:
  - name: paper_id
    dtype: string
  - name: title
    dtype: string
  - name: abstract
    dtype: string
  - name: publication_date
    dtype: string
  - name: paper_link
    dtype: string
  - name: code_available
    dtype: bool
  - name: code_link
    dtype: string
  - name: source
    dtype: string
  - name: dataset
    list:
    - name: kind
      dtype: string
    - name: dataset_name
      dtype: string
    - name: data_instructions
      dtype: string
  - name: execution_requirements
    struct:
    - name: code_language
      dtype: string
    - name: dependencies
      sequence: string
    - name: needs_gpu
      dtype: bool
  - name: other_instructions
    dtype: string
  - name: full_text
    dtype: string
  splits:
  - name: papers
    num_bytes: TBD
    num_examples: TBD
  - name: tasks
    num_bytes: TBD
    num_examples: TBD
  download_size: TBD
  dataset_size: TBD
configs:
- config_name: default
  data_files:
  - split: papers
    path: papers.jsonl
  - split: tasks
    path: tasks.jsonl
---

# ReplicationBench
**arXiv**: [ReplicationBench: Can AI Agents Replicate Astrophysics Research Papers?](https://arxiv.org/abs/2510.24591)

**GitHub**: [https://github.com/Christine8888/replicationbench-release](https://github.com/Christine8888/replicationbench-release)

## Dataset Description

The ReplicationBench dataset contains 111 astrophysics research replication tasks spanning 20 research papers. The dataset includes:
- Original and masked manuscript text
- Metadata (title, abstract, publication info, etc.)
- Pointers to datasets and dataset access instructions
- Additional specifications from the authors
- Execution requirements
- Detailed descriptions and grading guidelines for each task

## Usage

```python
from datasets import load_dataset

# Load papers
papers_ds = load_dataset("ChristineYe8/replicationbench", split="papers")

# Load tasks
tasks_ds = load_dataset("ChristineYe8/replicationbench", split="tasks")
```

You can load the dataset from HuggingFace into native ReplicationBench format using [this script](https://github.com/Christine8888/replicationbench-release/blob/main/src/dataset/hf/load_from_hf.py). However, if using RB's native formats, we recommend using the native data loading instead, described [here](https://github.com/Christine8888/replicationbench-release).

## Citation

If you use ReplicationBench in your research, please cite:

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

MIT License
