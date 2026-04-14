# Project Summarizer

A Python tool that generates comprehensive text summaries of software projects, including directory structure and file contents. Perfect for code reviews, documentation, or sharing project overviews.

## Features

- **Directory Tree Generation**: Creates a visual tree structure of your project
- **File Content Extraction**: Extracts contents from text-based files
- **Smart Filtering**: Automatically ignores common directories (node_modules, .git, etc.)
- **Multiple Input Methods**: Command-line interface, GUI folder picker, or interactive prompts
- **Configurable Extensions**: Supports 50+ text file extensions
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites
- Python 3.6 or higher
- Tkinter (usually included with Python, optional for GUI mode)

### Install
```bash
# Clone the repository
git clone https://github.com/yourusername/project-summarizer.git
cd project-summarizer

# No additional dependencies required for basic functionality
# For GUI mode, tkinter is usually pre-installed with Python
```

## Usage

### Command Line Interface

```bash
# Basic usage - analyze current directory
python project_summarizer.py

# Specify project path
python project_summarizer.py --path /path/to/your/project

# Use GUI folder picker
python project_summarizer.py --gui

# Custom output file
python project_summarizer.py --path /path/to/project --output my_summary.txt
```

### Interactive Mode

When run without arguments, the script enters interactive mode:
```bash
python project_summarizer.py
# Enter project folder path (or press Enter for GUI): /path/to/project
```

### GUI Mode

Use the `--gui` flag or press Enter in interactive mode to open a folder selection dialog.

## Configuration

### Supported File Extensions

The script extracts content from these text-based file extensions:
- **Programming**: `.py`, `.js`, `.ts`, `.java`, `.c`, `.cpp`, `.go`, `.rb`, `.rs`, `.php`, etc.
- **Web**: `.html`, `.css`, `.json`, `.xml`, `.md`, `.yaml`, `.scss`, `.vue`, etc.
- **Config**: `.ini`, `.toml`, `.env`, `.dockerignore`, `.gitignore`, etc.
- **Data**: `.csv`, `.tsv`, `.sql`, `.log`
- **Scripts**: `.sh`, `.bat`, `.ps1`, `.awk`

### Ignored Directories

The following directories are automatically excluded:
- Version control: `.git`, `.svn`, `.hg`
- Dependencies: `node_modules`, `vendor`, `packages`
- Python: `venv`, `__pycache__`, `.eggs`
- Build outputs: `dist`, `build`, `target`, `out`, `bin`, `obj`
- IDEs: `.idea`, `.vscode`, `.vs`
- System files: `.DS_Store`, `Thumbs.db`
- Logs/Temp: `*.log`, `logs`, `tmp`, `temp`

### Customization

To modify file extensions or ignore patterns, edit the `TEXT_FILE_EXTENSIONS` and `DEFAULT_IGNORE` sets in `project_summarizer.py`.

## Output Format

The generated summary file contains:

```
Directory Structure:

project-name/
├── src/
│   ├── main.py
│   └── utils.py
└── README.md

File Contents:

--- src/main.py ---
[content of main.py]

--- src/utils.py ---
[content of utils.py]

--- README.md ---
[content of README.md]
```

## Examples

### Analyze a Node.js Project
```bash
python project_summarizer.py --path ./my-node-app --output node_app_summary.txt
```

### Analyze with GUI
```bash
python project_summarizer.py --gui
# Select folder in the dialog
```

### Quick Analysis of Current Directory
```bash
python project_summarizer.py
# Press Enter for GUI or enter a path
```

## Command Line Options

```
usage: project_summarizer.py [-h] [--path PATH] [--output OUTPUT] [--gui]

Project to text exporter

optional arguments:
  -h, --help       Show help message
  --path PATH      Project folder path
  --output OUTPUT  Output file (default: project_overview.txt)
  --gui            Use GUI folder picker
```

## Troubleshooting

### Script Closes Immediately
If double-clicking the script causes the window to close immediately, run it from command prompt:
```cmd
python project_summarizer.py
```

### GUI Not Working
If tkinter is not available, use command-line mode:
```bash
python project_summarizer.py --path /path/to/project
```

### Permission Errors
Ensure you have read permissions for the project directory and write permissions for the output location.

### Large Files
Files larger than 500 lines are truncated. Modify `MAX_FILE_LINES` in the script if needed.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- Directory tree generation
- File content extraction
- CLI and GUI interfaces
- Comprehensive file extension support
- Smart ignore patterns

## Support

If you find this tool useful, please star the repository! For issues or feature requests, please open an issue on GitHub.