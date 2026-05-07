"""Future GUI entry points and helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def pick_folder_gui() -> Path | None:
    """Open a folder picker when Tkinter is available."""
    if importlib.util.find_spec("tkinter") is None:
        return None

    import tkinter as tk
    from tkinter import filedialog

    try:
        root = tk.Tk()
    except tk.TclError:
        return None

    root.withdraw()
    folder = filedialog.askdirectory(title="Select Project Folder")
    root.destroy()
    return Path(folder) if folder else None


def main() -> None:
    """Placeholder for a future full GUI application."""
    folder = pick_folder_gui()
    if folder is None:
        print("No folder selected.")
    else:
        print(folder)


if __name__ == "__main__":
    main()
