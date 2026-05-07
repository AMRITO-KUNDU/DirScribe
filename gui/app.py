"""Tkinter GUI for DirScribe."""

from __future__ import annotations

import os
import queue
import sys
import threading
import webbrowser
from dataclasses import dataclass
from pathlib import Path


if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def pick_folder_gui() -> Path | None:
    """Open a folder picker when Tkinter is available."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return None

    try:
        root = tk.Tk()
    except tk.TclError:
        return None

    root.withdraw()
    folder = filedialog.askdirectory(title="Select Project Folder")
    root.destroy()
    return Path(folder) if folder else None


@dataclass(frozen=True)
class _WorkerResult:
    ok: bool
    message: str
    output_file: Path | None = None
    summary: str | None = None


def main() -> None:
    """Run the DirScribe GUI app."""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError as exc:
        raise SystemExit("Tkinter is required to run the GUI.") from exc

    from core.writer import build_project_summary

    class App(tk.Tk):
        def __init__(self) -> None:
            super().__init__()
            self.title("DirScribe")
            self.minsize(760, 520)

            self._queue: queue.Queue[_WorkerResult] = queue.Queue()
            self._running = False

            self.project_var = tk.StringVar(value="")
            self.output_var = tk.StringVar(value=str(Path.cwd() / "project_overview.txt"))
            self.status_var = tk.StringVar(value="Ready.")

            self._last_summary: str = ""
            self._last_output_file: Path | None = None

            self._setup_style()
            self._build_ui()

            self.bind("<Return>", lambda _event: self._start_generate())
            self.after(100, self._poll_queue)

        def _setup_style(self) -> None:
            style = ttk.Style(self)
            # Keep it minimal: use native theme when available.
            for theme in ("vista", "xpnative", "clam"):
                try:
                    style.theme_use(theme)
                    break
                except tk.TclError:
                    continue

            style.configure("Path.TEntry", padding=(6, 4))
            style.configure("Tiny.TButton", padding=(6, 2))

        def _build_ui(self) -> None:
            outer = ttk.Frame(self, padding=8)
            outer.grid(row=0, column=0, sticky="nsew")
            self.columnconfigure(0, weight=1)
            self.rowconfigure(0, weight=1)
            outer.columnconfigure(0, weight=1)
            outer.rowconfigure(2, weight=1)

            # Row 0: project folder
            row0 = ttk.Frame(outer)
            row0.grid(row=0, column=0, sticky="ew")
            row0.columnconfigure(1, weight=1)

            ttk.Label(row0, text="Folder:").grid(row=0, column=0, sticky="w", padx=(0, 6))
            self.project_entry = ttk.Entry(row0, textvariable=self.project_var, style="Path.TEntry")
            self.project_entry.grid(row=0, column=1, sticky="ew")
            self.project_browse = ttk.Button(row0, text="Browse...", command=self._browse_project)
            self.project_browse.grid(row=0, column=2, sticky="ew", padx=(6, 0))

            # Row 1: output + actions
            row1 = ttk.Frame(outer)
            row1.grid(row=1, column=0, sticky="ew", pady=(8, 0))
            row1.columnconfigure(1, weight=1)

            ttk.Label(row1, text="Output:").grid(row=0, column=0, sticky="w", padx=(0, 6))
            self.output_label = ttk.Label(row1, textvariable=self.output_var)
            self.output_label.grid(row=0, column=1, sticky="w")
            self.output_change = ttk.Button(row1, text="Save As...", style="Tiny.TButton", command=self._browse_output)
            self.output_change.grid(row=0, column=2, sticky="e", padx=(6, 0))

            actions = ttk.Frame(outer)
            actions.grid(row=2, column=0, sticky="ew", pady=(8, 0))
            actions.columnconfigure(0, weight=1)

            self.generate_btn = ttk.Button(actions, text="Generate", command=self._start_generate)
            self.generate_btn.grid(row=0, column=0, sticky="w")
            self.copy_btn = ttk.Button(actions, text="Copy All", command=self._copy_all)
            self.copy_btn.grid(row=0, column=1, sticky="w", padx=(6, 0))
            self.open_btn = ttk.Button(actions, text="Open File", command=self._open_last_output)
            self.open_btn.grid(row=0, column=2, sticky="w", padx=(6, 0))
            self.open_folder_btn = ttk.Button(actions, text="Open Folder", command=self._open_last_folder)
            self.open_folder_btn.grid(row=0, column=3, sticky="w", padx=(6, 0))

            # Row 3: preview
            preview_frame = ttk.Frame(outer)
            preview_frame.grid(row=3, column=0, sticky="nsew", pady=(10, 0))
            preview_frame.columnconfigure(0, weight=1)
            preview_frame.rowconfigure(0, weight=1)
            outer.rowconfigure(3, weight=1)

            self.preview = tk.Text(
                preview_frame,
                wrap="word",
                borderwidth=1,
                relief="solid",
                font=("Consolas", 10),
            )
            self.preview.grid(row=0, column=0, sticky="nsew")
            self.preview.configure(state="disabled")

            yscroll = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview.yview)
            yscroll.grid(row=0, column=1, sticky="ns")
            self.preview.configure(yscrollcommand=yscroll.set)

            bottom = ttk.Frame(outer)
            bottom.grid(row=4, column=0, sticky="ew", pady=(8, 0))
            bottom.columnconfigure(0, weight=1)

            ttk.Label(bottom, textvariable=self.status_var).grid(row=0, column=0, sticky="w")
            self.progress = ttk.Progressbar(bottom, mode="indeterminate")
            self.progress.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        def _browse_project(self) -> None:
            folder = filedialog.askdirectory(title="Select Project Folder")
            if not folder:
                return
            self.project_var.set(folder)
            self._refresh_output_path()
            self.project_entry.icursor("end")
            self.status_var.set("Ready.")

        def _browse_output(self) -> None:
            initial = Path(self.output_var.get() or "project_overview.txt")
            path = filedialog.asksaveasfilename(
                title="Save Output As",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialdir=str(initial.parent) if initial.parent.exists() else None,
                initialfile=initial.name,
            )
            if path:
                self.output_var.set(path)

        def _refresh_output_path(self) -> None:
            project_text = self.project_var.get().strip()
            if project_text:
                project_path = Path(project_text).expanduser()
                self.output_var.set(str(project_path / "project_overview.txt"))
            else:
                self.output_var.set(str(Path.cwd() / "project_overview.txt"))

        def _set_running(self, running: bool) -> None:
            self._running = running
            state = "disabled" if running else "normal"
            for widget in (
                self.project_entry,
                self.project_browse,
                self.output_change,
                self.generate_btn,
                self.copy_btn,
                self.open_btn,
                self.open_folder_btn,
            ):
                widget.configure(state=state)
            if running:
                self.progress.start(8)
            else:
                self.progress.stop()

        def _start_generate(self) -> None:
            if self._running:
                return

            project_text = self.project_var.get().strip()
            output_text = self.output_var.get().strip()

            if not project_text:
                messagebox.showerror("DirScribe", "Select a project folder first.")
                return

            project_path = Path(project_text).expanduser()
            if not project_path.exists() or not project_path.is_dir():
                messagebox.showerror("DirScribe", "Project folder path is invalid.")
                return

            if not output_text:
                messagebox.showerror("DirScribe", "Please choose an output file path.")
                return

            output_file = Path(output_text).expanduser()
            self.status_var.set("Scanning project...")
            self._set_preview_text("Generating preview...\n")
            self._set_running(True)

            def worker() -> None:
                try:
                    summary = build_project_summary(project_path.resolve())
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    output_file.write_text(summary, encoding="utf-8")
                except Exception as exc:  # noqa: BLE001
                    self._queue.put(_WorkerResult(False, f"Failed: {exc}"))
                    return

                self._queue.put(_WorkerResult(True, "Done.", output_file=output_file, summary=summary))

            threading.Thread(target=worker, daemon=True).start()

        def _poll_queue(self) -> None:
            try:
                result = self._queue.get_nowait()
            except queue.Empty:
                self.after(100, self._poll_queue)
                return

            self._set_running(False)
            if result.ok and result.output_file is not None and result.summary is not None:
                self._last_output_file = result.output_file
                self._last_summary = result.summary
                self._set_preview_text(result.summary)
                self.status_var.set(f"Saved: {result.output_file}")
            else:
                self.status_var.set(result.message)
                messagebox.showerror("DirScribe", result.message)

            self.after(100, self._poll_queue)

        def _set_preview_text(self, text: str) -> None:
            self.preview.configure(state="normal")
            self.preview.delete("1.0", "end")
            self.preview.insert("end", text)
            self.preview.configure(state="disabled")

        def _copy_all(self) -> None:
            if not self._last_summary:
                messagebox.showinfo("DirScribe", "Nothing to copy yet. Generate a summary first.")
                return
            try:
                self.clipboard_clear()
                self.clipboard_append(self._last_summary)
                self.update_idletasks()
            except tk.TclError:
                messagebox.showerror("DirScribe", "Copy failed.")
                return
            self.status_var.set("Copied preview to clipboard.")

        def _open_last_output(self) -> None:
            if self._last_output_file is None:
                messagebox.showinfo("DirScribe", "No output file yet. Generate a summary first.")
                return
            self._open_path(self._last_output_file)

        def _open_last_folder(self) -> None:
            if self._last_output_file is None:
                messagebox.showinfo("DirScribe", "No output folder yet. Generate a summary first.")
                return
            self._open_path(self._last_output_file.parent)

        def _open_path(self, path: Path) -> None:
            try:
                os.startfile(path)  # type: ignore[attr-defined]
                return
            except Exception:
                pass

            try:
                webbrowser.open(path.resolve().as_uri())
            except Exception:
                return

    App().mainloop()


if __name__ == "__main__":
    main()
