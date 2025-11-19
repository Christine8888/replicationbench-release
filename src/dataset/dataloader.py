"""Load papers and tasks from directory."""

from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from .wrappers.paper import Paper
from .wrappers.task import Task
from .text_loader import load_paper_text


_PACKAGE_DIR = Path(__file__).parent
_DEFAULT_PAPERS_DIR = _PACKAGE_DIR / "papers"
_DEFAULT_TASKS_DIR = _PACKAGE_DIR / "tasks"
_DEFAULT_MANUSCRIPTS_DIR = _PACKAGE_DIR / "manuscripts"


class Dataloader:
    """Loads papers with tasks and text.

    Paper is the atomic unit - each Paper object contains its tasks and text.
    """

    def __init__(
        self,
        papers_dir: Optional[str] = None,
        tasks_dir: Optional[str] = None,
        manuscripts_dir: Optional[str] = None,
        paper_ids: Optional[List[str]] = None,
        task_types: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        load_text: bool = True,
        masked: bool = True
    ):
        """Initialize dataloader.

        Args:
            papers_dir: Papers directory (default: bundled data)
            tasks_dir: Tasks directory (default: bundled data)
            manuscripts_dir: Manuscripts directory (default: bundled data)
            paper_ids: Specific papers to load (None = all)
            task_types: Task types to load (None = all)
            filters: Attribute filters to include (e.g., {"source": "showyourwork"})
            load_text: Whether to load text content
            masked: Load masked text vs unmasked text
        """
        self.papers_dir = Path(papers_dir) if papers_dir else _DEFAULT_PAPERS_DIR
        self.tasks_dir = Path(tasks_dir) if tasks_dir else _DEFAULT_TASKS_DIR
        self.manuscripts_dir = Path(manuscripts_dir) if manuscripts_dir else _DEFAULT_MANUSCRIPTS_DIR
        self.paper_ids = paper_ids
        self.task_types = task_types
        self.filters = filters
        self.load_text = load_text
        self.masked = masked

        self.papers: Dict[str, Paper] = {}
        self._load()

    def _load(self) -> None:
        """Load papers with tasks and text."""
        paper_files = self._discover_papers()

        for paper_file in paper_files:
            paper_id = paper_file.stem

            if self.paper_ids and paper_id not in self.paper_ids:
                continue

            paper = Paper.from_json(str(paper_file))

            if self.filters:
                if not all(getattr(paper, key, None) == value for key, value in self.filters.items()):
                    continue

            paper.tasks = self._load_tasks(paper_id)

            if self.load_text:
                paper.full_text = load_paper_text(
                    str(self.manuscripts_dir),
                    paper_id,
                    masked=self.masked
                )

            self.papers[paper_id] = paper

    def _discover_papers(self) -> List[Path]:
        """Find all paper JSON files."""
        return sorted(self.papers_dir.glob("*.json"))

    def _load_tasks(self, paper_id: str) -> Dict[str, Task]:
        """Load all tasks for a paper, sorted by difficulty (easiest first)."""
        task_dir = self.tasks_dir / paper_id

        if not task_dir.exists():
            return {}

        tasks = {}
        for task_file in task_dir.glob("*.json"):
            task = Task.from_json(str(task_file))

            if self.task_types and task.kind not in self.task_types:
                continue

            if not task.validate_tolerance():
                print(f"Warning: Invalid tolerance for {task.task_id}")

            tasks[task.task_id] = task

        # Sort tasks by difficulty (easiest first)
        sorted_tasks = dict(sorted(tasks.items(), key=lambda x: x[1].difficulty))

        return sorted_tasks

    def filter_papers(self, **criteria) -> List[str]:
        """Filter papers by metadata.

        Examples:
            loader.filter_papers(source="expert")
            loader.filter_papers(code_available=True)
        """
        matching = []
        for paper_id, paper in self.papers.items():
            if all(getattr(paper, key, None) == value for key, value in criteria.items()):
                matching.append(paper_id)
        return matching

    @classmethod
    def from_dicts(cls, paper_dicts: List[Dict[str, Any]]) -> 'Dataloader':
        """Load papers from list of dictionaries.

        Args:
            paper_dicts: List of paper dictionaries with metadata and tasks

        Returns:
            Dataloader instance with papers loaded from dicts
        """
        from datetime import datetime
        from .wrappers.paper import _parse_datasets, _parse_executor

        loader = cls.__new__(cls)
        loader.papers = {}
        loader.papers_dir = None
        loader.tasks_dir = None
        loader.manuscripts_dir = None
        loader.paper_ids = None
        loader.task_types = None
        loader.load_text = True
        loader.masked = True

        for data in paper_dicts:
            pub_date = datetime.strptime(data['publication_date'], "%Y-%m-%d")

            paper = Paper(
                paper_id=data['paper_id'],
                title=data['title'],
                abstract=data['abstract'],
                publication_date=pub_date,
                paper_link=data.get('paper_link', ''),
                code_available=data.get('code_available', False),
                code_link=data.get('code_link'),
                source=data.get('source', 'expert'),
                datasets=_parse_datasets(data.get('dataset', []), data['paper_id']),
                execution_requirements=_parse_executor(data.get('execution_requirements')),
                other_instructions=data.get('other_instructions'),
                full_text=data.get('full_text', ''),
                tasks={}
            )

            if 'tasks' in data:
                for task_id, task_data in data['tasks'].items():
                    instructions = task_data['instructions']
                    if isinstance(instructions, str):
                        instructions = [instructions]

                    task = Task(
                        task_id=task_data['task_id'],
                        paper_id=task_data['paper_id'],
                        kind=task_data['kind'],
                        difficulty=task_data['difficulty'],
                        description=task_data['description'],
                        instructions=instructions,
                        expected_output=task_data['expected_output'],
                        tolerance=task_data['tolerance'],
                        parents=task_data.get('parents')
                    )
                    paper.tasks[task_id] = task

            loader.papers[paper.paper_id] = paper

        return loader

    @classmethod
    def from_jsonl(cls, jsonl_path: str) -> 'Dataloader':
        """Load papers from JSONL file.

        Args:
            jsonl_path: Path to JSONL file

        Returns:
            Dataloader instance with papers loaded from JSONL
        """
        with open(jsonl_path, 'r') as f:
            paper_dicts = [json.loads(line) for line in f]
        return cls.from_dicts(paper_dicts)

    def export_to_jsonl(
        self,
        output_path: str,
        include_text: bool = True,
        include_tasks: bool = True
    ) -> None:
        """Export all papers to JSONL format.

        Each line is a complete Paper with all associated data.

        Args:
            output_path: Path to output JSONL file
            include_text: Include full_text field
            include_tasks: Include tasks field
        """
        with open(output_path, 'w') as f:
            for paper in self.papers.values():
                paper_dict = paper.to_dict(
                    include_text=include_text,
                    include_tasks=include_tasks
                )
                f.write(json.dumps(paper_dict) + '\n')
