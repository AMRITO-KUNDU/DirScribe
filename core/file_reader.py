"""Read supported text files for project summaries."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .tree_builder import DEFAULT_IGNORE, should_ignore

TEXT_FILE_EXTENSIONS = {
    # Programming Languages
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp",
    ".go", ".rb", ".rs", ".php", ".scala", ".kt", ".swift", ".dart", ".lua", ".pl", ".pm",
    ".r", ".m", ".hs", ".ml", ".fs", ".fsx", ".vb", ".cs", ".clj", ".cljs", ".elm", ".ex",
    ".exs", ".nim", ".zig", ".cr", ".d", ".nimble", ".v", ".pony", ".tcl", ".tk",
    # Web Technologies
    ".html", ".htm", ".css", ".scss", ".sass", ".less", ".vue", ".svelte", ".pug", ".ejs",
    ".hbs", ".handlebars", ".mustache", ".twig", ".jsp", ".asp", ".aspx", ".erb", ".haml",
    # Configuration & Data
    ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".properties",
    ".env", ".dotenv", ".lock", ".sum", ".mod", ".gradle", ".pom", ".Dockerfile", ".dockerignore",
    ".gitignore", ".gitattributes", ".editorconfig", ".prettierrc", ".eslintrc", ".babelrc",
    ".tsconfig", ".jsconfig", ".package", ".requirements", ".Pipfile", ".pyproject", ".setup",
    # Documentation
    ".md", ".rst", ".adoc", ".tex", ".bib", ".txt", ".rtf", ".docx", ".pdf", ".epub",
    # Scripts & Shell
    ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd", ".awk", ".sed", ".tcl",
    # Data Formats
    ".csv", ".tsv", ".sql", ".db", ".sqlite", ".sqlite3", ".parquet", ".avro", ".orc",
    # Logs & Other
    ".log", ".out", ".err", ".pid", ".sock", ".tmp", ".temp", ".cache", ".bak", ".old",
    ".new", ".orig", ".swp", ".swo", ".DS_Store", "Thumbs.db", "desktop.ini",
}

MAX_FILE_LINES = 500


def is_text_file(path: Path) -> bool:
    """Return True when a path has a supported text-like extension."""
    return path.suffix.lower() in TEXT_FILE_EXTENSIONS


def extract_contents(root: Path, ignore_patterns: Iterable[str]) -> str:
    """Extract contents from supported files below root."""
    output: list[str] = []

    for path in root.rglob("*"):
        if path.is_dir() or should_ignore(path, ignore_patterns) or not is_text_file(path):
            continue

        rel = path.relative_to(root)
        output.append(f"\n--- {rel} ---\n")

        try:
            with path.open("r", encoding="utf-8", errors="ignore") as file:
                lines = file.readlines()
        except OSError as exc:
            output.append(f"[Error reading file: {exc}]\n")
            continue

        if len(lines) > MAX_FILE_LINES:
            lines = lines[:MAX_FILE_LINES]
            lines.append("\n... [truncated]\n")

        output.extend(lines)

    return "".join(output)
