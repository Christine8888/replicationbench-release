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
  - name: blacklist_packages
    sequence: string
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
