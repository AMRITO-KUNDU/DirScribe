"""Write DirScribe project summaries."""

from __future__ import annotations

from pathlib import Path

from .file_reader import extract_contents
from .tree_builder import DEFAULT_IGNORE, generate_tree, load_gitignore


def build_project_summary(project_path: Path) -> str:
    """Build the full project summary text for a project path."""
    ignore_patterns = DEFAULT_IGNORE | load_gitignore(project_path)
    tree = generate_tree(project_path, ignore_patterns)
    contents = extract_contents(project_path, ignore_patterns)

    return f"Directory Structure:\n\n{tree}\n\nFile Contents:\n{contents}"


def run(project_path: Path, output_file: Path) -> None:
    """Generate and write a project summary file."""
    print("\nScanning project...\n")

    summary = build_project_summary(project_path)
    output_file.write_text(summary, encoding="utf-8")

    print(f"\nDone. Output saved to: {output_file}\n")
