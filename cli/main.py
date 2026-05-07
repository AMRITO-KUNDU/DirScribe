"""Developer-facing integration helpers for DirScribe.

Import this module from another Python project when you want to call
DirScribe programmatically instead of using the command text interface.
"""

from __future__ import annotations

from pathlib import Path

from core.file_reader import extract_contents
from core.tree_builder import DEFAULT_IGNORE, generate_tree, load_gitignore
from core.writer import build_project_summary, run


def collect_ignore_patterns(project_path: str | Path) -> set[str]:
    """Return DirScribe's default ignore rules plus the project's .gitignore rules."""
    root = Path(project_path).expanduser().resolve()
    return DEFAULT_IGNORE | load_gitignore(root)


def get_project_tree(project_path: str | Path) -> str:
    """Return only the rendered directory tree for a project."""
    root = Path(project_path).expanduser().resolve()
    return generate_tree(root, collect_ignore_patterns(root))


def get_project_contents(project_path: str | Path) -> str:
    """Return only supported file contents for a project."""
    root = Path(project_path).expanduser().resolve()
    return extract_contents(root, collect_ignore_patterns(root))


def summarize_project(project_path: str | Path) -> str:
    """Return the complete DirScribe summary for a project."""
    return build_project_summary(Path(project_path).expanduser().resolve())


def write_project_summary(
    project_path: str | Path,
    output_file: str | Path = "project_overview.txt",
) -> Path:
    """Write a DirScribe summary and return the output path."""
    root = Path(project_path).expanduser().resolve()
    destination = Path(output_file).expanduser()
    run(root, destination)
    return destination


__all__ = [
    "collect_ignore_patterns",
    "get_project_contents",
    "get_project_tree",
    "summarize_project",
    "write_project_summary",
]
