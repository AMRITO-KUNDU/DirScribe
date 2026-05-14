"""Modern Fluent-style DirScribe GUI."""

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


@dataclass(frozen=True)
class _WorkerResult:
    ok: bool
    message: str
    output_file: Path | None = None
    summary: str | None = None


def main() -> None:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError as exc:
        raise SystemExit(
            "Tkinter is required to run the GUI."
        ) from exc

    from core.writer import build_project_summary

    # =========================================================
    # Fluent Colors
    # =========================================================

    BG = "#ffffff"
    SURFACE = "#f8f9fb"

    BORDER = "#d8dbe2"

    BLUE = "#0078d4"
    BLUE_HOVER = "#106ebe"

    TEXT = "#1b1b1b"
    SUBTEXT = "#5f5f5f"

    # =========================================================
    # Ribbon Buttons
    # =========================================================

    class PrimaryRibbonButton(tk.Frame):
        """Large WinRAR/Office-style command."""

        def __init__(
            self,
            master,
            icon: str,
            text: str,
            command,
        ):
            super().__init__(
                master,
                bg=SURFACE,
            )

            self.button = tk.Button(
                self,
                text=f"{icon}\n{text}",
                command=command,
                font=("Segoe UI", 10),
                bg=BG,
                fg=TEXT,
                activebackground="#edf5ff",
                activeforeground=TEXT,
                relief="flat",
                borderwidth=0,
                justify="center",
                cursor="hand2",
                width=10,
                height=6,
                padx=12,
                pady=10,
            )

            self.button.pack(
                fill="both",
                expand=True,
            )

            self.button.bind(
                "<Enter>",
                self._hover_on,
            )

            self.button.bind(
                "<Leave>",
                self._hover_off,
            )

        def _hover_on(self, _event):
            self.button.configure(
                bg="#edf5ff",
                highlightbackground=BLUE,
                highlightcolor=BLUE,
                highlightthickness=1,
            )

        def _hover_off(self, _event):
            self.button.configure(
                bg=BG,
                highlightthickness=0,
            )

    class ToolButton(tk.Button):
        """Small utility toolbar button."""

        def __init__(
            self,
            master,
            text: str,
            command,
        ):
            super().__init__(
                master,
                text=text,
                command=command,
                font=("Segoe UI", 9),
                bg=BG,
                fg=TEXT,
                activebackground="#edf5ff",
                relief="flat",
                borderwidth=0,
                padx=12,
                pady=6,
                cursor="hand2",
            )

            self.bind(
                "<Enter>",
                lambda e: self.configure(
                    bg="#edf5ff"
                ),
            )

            self.bind(
                "<Leave>",
                lambda e: self.configure(
                    bg=BG
                ),
            )

    # =========================================================
    # App
    # =========================================================

    class App(tk.Tk):
        def __init__(self):
            super().__init__()

            self.title("DirScribe")

            self.geometry("1200x760")
            self.minsize(900, 600)

            self.configure(bg=BG)

            self._queue: queue.Queue[_WorkerResult] = (
                queue.Queue()
            )

            self._running = False

            self.project_var = tk.StringVar(value="")

            self.output_var = tk.StringVar(
                value=str(
                    Path.cwd()
                    / "project_overview.txt"
                )
            )

            self._last_summary: str = ""

            self._last_output_file: Path | None = None

            self._setup_style()
            self._build_ui()

            self.bind(
                "<Return>",
                lambda _e: self._start_generate(),
            )

            self.after(
                100,
                self._poll_queue,
            )

        # =====================================================
        # Styling
        # =====================================================

        def _setup_style(self):
            style = ttk.Style(self)

            for theme in (
                "vista",
                "clam",
            ):
                try:
                    style.theme_use(theme)
                    break
                except tk.TclError:
                    continue

            style.configure(
                "Modern.TFrame",
                background=BG,
            )

            style.configure(
                "Modern.TLabel",
                background=BG,
                foreground=TEXT,
                font=("Segoe UI", 9),
            )

        # =====================================================
        # Layout
        # =====================================================

        def _build_ui(self):
            self.columnconfigure(0, weight=1)
            self.rowconfigure(3, weight=1)

            # =================================================
            # Top Ribbon Surface
            # =================================================

            ribbon = tk.Frame(
                self,
                bg=SURFACE,
                height=170,
                highlightbackground=BORDER,
                highlightthickness=1,
            )

            ribbon.grid(
                row=0,
                column=0,
                sticky="ew",
            )

            ribbon.grid_propagate(False)

            ribbon.columnconfigure(0, weight=1)

            # =============================================
            # Main Command Area
            # =============================================

            command_area = tk.Frame(
                ribbon,
                bg=SURFACE,
            )

            command_area.pack(
                side="top",
                fill="x",
                padx=18,
                pady=(14, 6),
            )

            # Primary Actions
            primary_group = tk.Frame(
                command_area,
                bg=SURFACE,
            )

            primary_group.pack(
                side="left",
            )

            PrimaryRibbonButton(
                primary_group,
                "📁",
                "Open Project",
                self._browse_project,
            ).pack(
                side="left",
                padx=(0, 10),
            )

            PrimaryRibbonButton(
                primary_group,
                "▶",
                "Generate",
                self._start_generate,
            ).pack(
                side="left",
            )

            # Divider
            divider = tk.Frame(
                command_area,
                bg=BORDER,
                width=1,
                height=110,
            )

            divider.pack(
                side="left",
                padx=22,
                pady=6,
            )

            # Secondary Actions
            utility_group = tk.Frame(
                command_area,
                bg=SURFACE,
            )

            utility_group.pack(
                side="left",
                pady=(10, 0),
            )

            utility_title = tk.Label(
                utility_group,
                text="OUTPUT",
                bg=SURFACE,
                fg=SUBTEXT,
                font=("Segoe UI", 8, "bold"),
            )

            utility_title.pack(
                anchor="w",
                pady=(0, 10),
            )

            utility_row = tk.Frame(
                utility_group,
                bg=SURFACE,
            )

            utility_row.pack(anchor="w")

            ToolButton(
                utility_row,
                "💾 Save As",
                self._browse_output,
            ).pack(
                side="left",
                padx=(0, 6),
            )

            ToolButton(
                utility_row,
                "📄 Open Output",
                self._open_last_output,
            ).pack(
                side="left",
                padx=(0, 6),
            )

            ToolButton(
                utility_row,
                "📋 Copy Text",
                self._copy_all,
            ).pack(side="left")

            # =================================================
            # Folder Path Area
            # =================================================

            path_container = tk.Frame(
                self,
                bg=BG,
            )

            path_container.grid(
                row=1,
                column=0,
                sticky="ew",
                padx=18,
                pady=(14, 10),
            )

            path_container.columnconfigure(
                1,
                weight=1,
            )

            path_label = tk.Label(
                path_container,
                text="Project Folder",
                bg=BG,
                fg=TEXT,
                font=("Segoe UI", 9),
            )

            path_label.grid(
                row=0,
                column=0,
                sticky="w",
                padx=(0, 12),
            )

            # Blue outline entry
            entry_border = tk.Frame(
                path_container,
                bg=BLUE,
                padx=1,
                pady=1,
            )

            entry_border.grid(
                row=0,
                column=1,
                sticky="ew",
            )

            entry_border.columnconfigure(
                0,
                weight=1,
            )

            self.project_entry = tk.Entry(
                entry_border,
                textvariable=self.project_var,
                relief="flat",
                borderwidth=0,
                font=("Segoe UI", 10),
                bg=BG,
                fg=TEXT,
                insertbackground=TEXT,
            )

            self.project_entry.grid(
                row=0,
                column=0,
                sticky="ew",
                ipady=8,
                padx=1,
                pady=1,
            )

            # =================================================
            # Preview Surface
            # =================================================

            preview_outer = tk.Frame(
                self,
                bg=BG,
            )

            preview_outer.grid(
                row=3,
                column=0,
                sticky="nsew",
                padx=18,
                pady=(0, 18),
            )

            preview_outer.columnconfigure(
                0,
                weight=1,
            )

            preview_outer.rowconfigure(
                1,
                weight=1,
            )

            # Preview Header
            preview_header = tk.Frame(
                preview_outer,
                bg=BG,
            )

            preview_header.grid(
                row=0,
                column=0,
                sticky="ew",
                pady=(0, 8),
            )

            preview_title = tk.Label(
                preview_header,
                text="Generated Preview",
                bg=BG,
                fg=TEXT,
                font=("Segoe UI", 11, "bold"),
            )

            preview_title.pack(
                side="left",
            )

            # Blue outline editor
            editor_border = tk.Frame(
                preview_outer,
                bg=BLUE,
                padx=1,
                pady=1,
            )

            editor_border.grid(
                row=1,
                column=0,
                sticky="nsew",
            )

            editor_border.columnconfigure(
                0,
                weight=1,
            )

            editor_border.rowconfigure(
                0,
                weight=1,
            )

            editor_surface = tk.Frame(
                editor_border,
                bg=BG,
            )

            editor_surface.grid(
                row=0,
                column=0,
                sticky="nsew",
            )

            editor_surface.columnconfigure(
                0,
                weight=1,
            )

            editor_surface.rowconfigure(
                0,
                weight=1,
            )

            self.preview = tk.Text(
                editor_surface,
                wrap="word",
                bg=BG,
                fg=TEXT,
                relief="flat",
                borderwidth=0,
                font=("Consolas", 10),
                padx=16,
                pady=16,
                insertbackground=TEXT,
            )

            self.preview.grid(
                row=0,
                column=0,
                sticky="nsew",
            )

            scrollbar = ttk.Scrollbar(
                editor_surface,
                orient="vertical",
                command=self.preview.yview,
            )

            scrollbar.grid(
                row=0,
                column=1,
                sticky="ns",
            )

            self.preview.configure(
                yscrollcommand=scrollbar.set,
                state="disabled",
            )

        # =====================================================
        # Actions
        # =====================================================

        def _browse_project(self):
            folder = filedialog.askdirectory(
                title="Select Project Folder"
            )

            if not folder:
                return

            self.project_var.set(folder)

            self._refresh_output_path()

        def _browse_output(self):
            initial = Path(
                self.output_var.get()
                or "project_overview.txt"
            )

            path = filedialog.asksaveasfilename(
                title="Save Output As",
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ],
                initialdir=str(initial.parent)
                if initial.parent.exists()
                else None,
                initialfile=initial.name,
            )

            if path:
                self.output_var.set(path)

        def _refresh_output_path(self):
            project_text = (
                self.project_var.get().strip()
            )

            if not project_text:
                return

            project_path = Path(
                project_text
            ).expanduser()

            self.output_var.set(
                str(
                    project_path
                    / "project_overview.txt"
                )
            )

        def _set_running(
            self,
            running: bool,
        ):
            self._running = running

        def _start_generate(self):
            if self._running:
                return

            project_text = (
                self.project_var.get().strip()
            )

            output_text = (
                self.output_var.get().strip()
            )

            if not project_text:
                messagebox.showerror(
                    "DirScribe",
                    "Select a project folder first.",
                )
                return

            project_path = Path(
                project_text
            ).expanduser()

            if (
                not project_path.exists()
                or not project_path.is_dir()
            ):
                messagebox.showerror(
                    "DirScribe",
                    "Project folder path is invalid.",
                )
                return

            output_file = Path(
                output_text
            ).expanduser()

            self._set_preview_text(
                "Generating...\n"
            )

            self._set_running(True)

            def worker():
                try:
                    summary = (
                        build_project_summary(
                            project_path.resolve()
                        )
                    )

                    output_file.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    output_file.write_text(
                        summary,
                        encoding="utf-8",
                    )

                except Exception as exc:
                    self._queue.put(
                        _WorkerResult(
                            False,
                            f"Failed: {exc}",
                        )
                    )
                    return

                self._queue.put(
                    _WorkerResult(
                        True,
                        "Done.",
                        output_file=output_file,
                        summary=summary,
                    )
                )

            threading.Thread(
                target=worker,
                daemon=True,
            ).start()

        def _poll_queue(self):
            try:
                result = self._queue.get_nowait()

            except queue.Empty:
                self.after(
                    100,
                    self._poll_queue,
                )
                return

            self._set_running(False)

            if (
                result.ok
                and result.output_file
                and result.summary
            ):
                self._last_output_file = (
                    result.output_file
                )

                self._last_summary = (
                    result.summary
                )

                self._set_preview_text(
                    result.summary
                )

            else:
                messagebox.showerror(
                    "DirScribe",
                    result.message,
                )

            self.after(
                100,
                self._poll_queue,
            )

        def _set_preview_text(
            self,
            text: str,
        ):
            self.preview.configure(
                state="normal"
            )

            self.preview.delete(
                "1.0",
                "end",
            )

            self.preview.insert(
                "end",
                text,
            )

            self.preview.configure(
                state="disabled"
            )

        def _copy_all(self):
            if not self._last_summary:
                return

            self.clipboard_clear()

            self.clipboard_append(
                self._last_summary
            )

            self.update_idletasks()

        def _open_last_output(self):
            if self._last_output_file is None:
                return

            self._open_path(
                self._last_output_file
            )

        def _open_path(
            self,
            path: Path,
        ):
            try:
                os.startfile(path)  # type: ignore[attr-defined]
                return

            except Exception:
                pass

            try:
                webbrowser.open(
                    path.resolve().as_uri()
                )

            except Exception:
                return

    App().mainloop()


if __name__ == "__main__":
    main()