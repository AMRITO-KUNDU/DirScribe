"""Core DirScribe functionality."""

from .file_reader import DEFAULT_IGNORE, MAX_FILE_LINES, TEXT_FILE_EXTENSIONS, extract_contents
from .tree_builder import generate_tree, load_gitignore, should_ignore
from .writer import build_project_summary, run

__all__ = [
    "DEFAULT_IGNORE",
    "MAX_FILE_LINES",
    "TEXT_FILE_EXTENSIONS",
    "build_project_summary",
    "extract_contents",
    "generate_tree",
    "load_gitignore",
    "run",
    "should_ignore",
]
