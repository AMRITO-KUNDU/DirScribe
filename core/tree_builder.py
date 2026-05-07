"""Build directory trees and apply ignore rules."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Iterable

DEFAULT_IGNORE = {
    # Version Control
    ".git",
    ".svn",
    ".hg",
    # Dependencies & Packages
    "node_modules",
    "vendor",
    "packages",
    # Python
    "venv",
    "__pycache__",
    ".eggs",
    "*.egg-info",
    # Build & Dist
    "dist",
    "build",
    "target",
    "out",
    "bin",
    "obj",
    # IDEs
    ".idea",
    ".vscode",
    ".vs",
    # OS & System
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    # Logs & Temp
    "*.log",
    "logs",
    "tmp",
    "temp",
    ".tmp",
    ".cache",
    # Testing & Coverage
    ".coverage",
    "coverage",
    ".nyc_output",
    # Other Common
    ".env",
    ".env.*",
    "secrets",
}


def load_gitignore(root: Path) -> set[str]:
    """Load non-comment ignore patterns from a project's .gitignore file."""
    ignore_patterns: set[str] = set()
    gitignore = root / ".gitignore"

    if not gitignore.exists():
        return ignore_patterns

    try:
        with gitignore.open("r", encoding="utf-8") as file:
            for line in file:
                pattern = line.strip()
                if pattern and not pattern.startswith("#"):
                    ignore_patterns.add(pattern)
    except OSError:
        return ignore_patterns

    return ignore_patterns


def should_ignore(path: Path, ignore_patterns: Iterable[str]) -> bool:
    """Return True when a path matches any configured ignore pattern."""
    path_text = str(path)
    return any(
        fnmatch.fnmatch(path_text, pattern) or pattern in path.parts
        for pattern in ignore_patterns
    )


def generate_tree(root: Path, ignore_patterns: Iterable[str]) -> str:
    """Generate a visual tree for root while skipping ignored paths."""
    root_name = root.name or root.resolve().name
    lines = [f"{root_name}/"]

    def walk(directory: Path, prefix: str = "") -> None:
        items = sorted(directory.iterdir(), key=lambda item: (item.is_file(), item.name.lower()))
        visible_items = [item for item in items if not should_ignore(item, ignore_patterns)]

        for index, item in enumerate(visible_items):
            connector = "└── " if index == len(visible_items) - 1 else "├── "
            lines.append(prefix + connector + item.name)

            if item.is_dir():
                extension = "    " if index == len(visible_items) - 1 else "│   "
                walk(item, prefix + extension)

    walk(root)
    return "\n".join(lines)
