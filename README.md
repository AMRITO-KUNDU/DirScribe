# DirScribe

DirScribe is a Python tool that generates comprehensive text summaries of software projects, including a directory structure and supported file contents. It is useful for code reviews, documentation, and sharing codebase context with AI tools or collaborators.

## Features

- **Directory tree generation** — creates a visual tree structure of a project.
- **File content extraction** — extracts contents from text-based files.
- **Smart filtering** — ignores common directories such as `node_modules`, `.git`, virtual environments, build outputs, and patterns from `.gitignore`.
- **Developer integration API** — exposes importable helpers under `cli/` so developers can integrate DirScribe into their own Python projects.
- **Command text interface** — provides a CUI under `cui/` for people who want to run DirScribe from a command window.
- **Optional GUI picker** — keeps GUI folder selection separate so users can choose CUI or GUI-assisted workflows.
- **Modular layout** — separates core logic, developer integration helpers, CUI code, and future GUI work.

## Project Structure

```text
DirScribe/
├── core/              # Main logic
│   ├── tree_builder.py
│   ├── file_reader.py
│   └── writer.py
├── cli/               # Developer integration API
│   └── main.py
├── cui/               # Command text user interface
│   └── main.py
├── gui/               # Future GUI entry points / optional picker
│   └── app.py
├── builds/            # Build artifacts/output folder
├── LICENSE            # Apache 2.0 license
├── README.md
└── requirements.txt
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Tkinter is optional and only required for GUI folder selection

### Setup

```bash
git clone https://github.com/yourusername/dirscribe.git
cd dirscribe
pip install -r requirements.txt
```

## Usage

### CUI: command text window

Run the command text interface with an explicit project path:

```bash
python cui/main.py --path /path/to/project --output project_overview.txt
```

Run the CUI text menu:

```bash
python cui/main.py
```

Use the GUI folder picker from the CUI:

```bash
python cui/main.py --gui --output project_overview.txt
```

### CLI: developer integration API

Use `cli` from another Python project when you want DirScribe as an importable helper instead of an end-user command window:

```python
from cli import summarize_project, write_project_summary

summary = summarize_project("/path/to/project")
output_path = write_project_summary("/path/to/project", "project_overview.txt")
```

## License

DirScribe is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
