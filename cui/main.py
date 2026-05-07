"""Command text user interface for DirScribe."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.writer import run
from gui.app import pick_folder_gui


def parse_args() -> argparse.Namespace:
    """Parse command text interface arguments."""
    parser = argparse.ArgumentParser(description="DirScribe command text interface")
    parser.add_argument("--path", help="Project folder path")
    parser.add_argument("--output", help="Output file", default="project_overview.txt")
    parser.add_argument("--gui", action="store_true", help="Use GUI folder picker")
    return parser.parse_args()


def choose_project_path(args: argparse.Namespace) -> Path | None:
    """Choose a project path from flags, GUI mode, or the text menu."""
    if args.gui:
        return pick_folder_gui()

    if args.path:
        return Path(args.path).expanduser()

    return prompt_for_project_path()


def prompt_for_project_path() -> Path | None:
    """Prompt users in a command text window for how they want to select a project."""
    while True:
        print("\nDirScribe CUI")
        print("1) Enter project folder path")
        print("2) Open GUI folder picker")
        print("3) Quit")

        choice = input("Choose an option [1-3]: ").strip()

        if choice == "1":
            user_input = input("Project folder path: ").strip()
            return Path(user_input).expanduser() if user_input else None

        if choice == "2":
            return pick_folder_gui()

        if choice == "3":
            return None

        print("Invalid option. Please enter 1, 2, or 3.")


def main() -> None:
    """Run the DirScribe command text user interface."""
    args = parse_args()
    project_path = choose_project_path(args)

    if project_path is None:
        print("No folder selected.")
        return

    if not project_path.exists() or not project_path.is_dir():
        print("Invalid project folder path.")
        return

    run(project_path.resolve(), Path(args.output).expanduser())


if __name__ == "__main__":
    main()
