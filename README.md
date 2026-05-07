# DirScribe

DirScribe is a Python tool that generates comprehensive text summaries of software projects, including a directory structure and supported file contents. It is useful for code reviews, documentation, and sharing codebase context with AI tools or collaborators.

## Features

- **Directory tree generation** — creates a visual tree structure of a project.
- **File content extraction** — extracts contents from text-based files.
- **Smart filtering** — ignores common directories such as `node_modules`, `.git`, virtual environments, build outputs, and patterns from `.gitignore`.
- **Multiple input methods** — supports CLI flags, an optional GUI folder picker, or interactive prompts.
- **Modular layout** — separates core logic, CLI code, and future GUI work.

## Project Structure

```text
DirScribe/
├── core/              # Main logic
│   ├── tree_builder.py
│   ├── file_reader.py
│   └── writer.py
├── cli/               # Command-line interface
│   └── main.py
├── gui/               # Future GUI entry points
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

Run the CLI with an explicit project path:

```bash
python -m cli.main --path /path/to/project --output project_overview.txt
```

Use the GUI folder picker:

```bash
python -m cli.main --gui --output project_overview.txt
```

Run interactively:

```bash
python -m cli.main
```

## License

DirScribe is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
