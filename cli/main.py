"""Command-line entry point for DirScribe."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.writer import run
from gui.app import pick_folder_gui


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Project to text exporter")
    parser.add_argument("--path", help="Project folder path")
    parser.add_argument("--output", help="Output file", default="project_overview.txt")
    parser.add_argument("--gui", action="store_true", help="Use GUI folder picker")
    return parser.parse_args()


def resolve_project_path(args: argparse.Namespace) -> Path | None:
    """Resolve the project path from CLI flags, GUI mode, or interactive input."""
    if args.gui:
        return pick_folder_gui()

    if args.path:
        return Path(args.path)

    user_input = input("Enter project folder path (or press Enter for GUI): ").strip()
    if user_input:
        return Path(user_input)

    return pick_folder_gui()


def main() -> None:
    """Run the DirScribe CLI."""
    args = parse_args()
    project_path = resolve_project_path(args)

    if project_path is None:
        print("No folder selected.")
        return

    if not project_path.exists():
        print("Invalid path.")
        return

    run(project_path.resolve(), Path(args.output))


if __name__ == "__main__":
    main()
