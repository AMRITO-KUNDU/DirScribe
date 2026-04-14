import os
import argparse
import fnmatch
from pathlib import Path
from collections import deque

# Optional GUI (fallback if not available)
try:
    import tkinter as tk
    from tkinter import filedialog
    GUI_AVAILABLE = True
except Exception:
    GUI_AVAILABLE = False


# ---------------- CONFIG ---------------- #
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
    ".new", ".orig", ".swp", ".swo", ".DS_Store", "Thumbs.db", "desktop.ini"
}

DEFAULT_IGNORE = {
    # Version Control
    ".git", ".svn", ".hg", ".bzr", ".cvs",
    
    # Dependencies & Packages
    "node_modules", "vendor", "packages", "lib", "libs", "third_party", "external",
    "bower_components", ".npm", ".yarn", ".bundle", ".sass-cache", ".jspm",
    
    # Python
    "venv", "__pycache__", ".eggs", "*.egg-info", ".tox", ".coverage", ".pytest_cache",
    ".mypy_cache", ".dmypy.json", ".python-version", ".venv", "env", "ENV",
    
    # JavaScript/Node
    ".nyc_output", ".grunt", ".bower", ".yo-rc.json", ".karma", ".protractor",
    
    # Java
    "target", ".gradle", ".mvn", ".m2", ".settings", ".project", ".classpath",
    
    # C/C++
    "build", "cmake-build-*", "CMakeFiles", "*.o", "*.obj", "*.exe", "*.dll", "*.so",
    "*.dylib", "*.a", "*.lib", "*.pdb", "*.ilk", "*.exp", "*.manifest",
    
    # Rust
    "target", ".cargo", "Cargo.lock",
    
    # Go
    "vendor", ".go-build",
    
    # .NET
    "bin", "obj", ".vs", "*.user", "*.suo", "*.cache", "*.log",
    
    # IDEs
    ".idea", ".vscode", ".eclipse", ".settings", ".project", ".classpath", ".metadata",
    ".recommenders", ".springBeans", ".sts4-cache", ".atom", ".sublime-project",
    ".sublime-workspace",
    
    # OS
    ".DS_Store", "Thumbs.db", "desktop.ini", ".directory", ".Trash-*",
    
    # Build & Dist
    "dist", "build", "out", "output", "release", "debug", "x64", "x86", "win32", "linux",
    "macos", "ios", "android", "*.app", "*.dmg", "*.pkg", "*.deb", "*.rpm", "*.msi",
    
    # Logs & Temp
    "logs", "*.log", "tmp", "temp", ".tmp", ".temp", ".cache", ".tmpdir",
    
    # Testing
    ".coverage", "coverage", "htmlcov", ".nyc_output", ".junit", "test-results",
    
    # Documentation
    "docs/_build", "docs/build", "site", ".doctrees",
    
    # Other
    ".env", ".env.*", "secrets", "keys", "credentials", ".aws", ".ssh"
}

MAX_FILE_LINES = 500


# ---------------- UTIL ---------------- #
def is_text_file(path: Path):
    return path.suffix.lower() in TEXT_FILE_EXTENSIONS


def load_gitignore(root: Path):
    ignore_patterns = set()
    gitignore = root / ".gitignore"

    if gitignore.exists():
        try:
            with open(gitignore, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        ignore_patterns.add(line)
        except:
            pass

    return ignore_patterns


def should_ignore(path: Path, ignore_patterns):
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(str(path), pattern) or pattern in path.parts:
            return True
    return False


# ---------------- TREE ---------------- #
def generate_tree(root: Path, ignore_patterns):
    lines = []
    prefix_stack = []

    def walk(directory: Path, prefix=""):
        items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        items = [i for i in items if not should_ignore(i, ignore_patterns)]

        for index, item in enumerate(items):
            connector = "└── " if index == len(items) - 1 else "├── "
            lines.append(prefix + connector + item.name)

            if item.is_dir():
                extension = "    " if index == len(items) - 1 else "│   "
                walk(item, prefix + extension)

    lines.append(f"{root.name}/")
    walk(root)
    return "\n".join(lines)


# ---------------- CONTENT ---------------- #
def extract_contents(root: Path, ignore_patterns):
    output = []

    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if should_ignore(path, ignore_patterns):
            continue
        if not is_text_file(path):
            continue

        rel = path.relative_to(root)
        output.append(f"\n--- {rel} ---\n")

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

                if len(lines) > MAX_FILE_LINES:
                    lines = lines[:MAX_FILE_LINES]
                    lines.append("\n... [truncated]\n")

                output.extend(lines)

        except Exception as e:
            output.append(f"[Error reading file: {e}]\n")

    return "".join(output)


# ---------------- GUI PICKER ---------------- #
def pick_folder_gui():
    if not GUI_AVAILABLE:
        return None

    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Project Folder")
    return Path(folder) if folder else None


# ---------------- MAIN LOGIC ---------------- #
def run(project_path: Path, output_file: Path):
    print("\nScanning project...\n")

    ignore_patterns = DEFAULT_IGNORE | load_gitignore(project_path)

    tree = generate_tree(project_path, ignore_patterns)
    contents = extract_contents(project_path, ignore_patterns)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Directory Structure:\n\n")
        f.write(tree)
        f.write("\n\nFile Contents:\n")
        f.write(contents)

    print(f"\nDone. Output saved to: {output_file}\n")


# ---------------- CLI ---------------- #
def main():
    parser = argparse.ArgumentParser(description="Project to text exporter")
    parser.add_argument("--path", help="Project folder path")
    parser.add_argument("--output", help="Output file", default="project_overview.txt")
    parser.add_argument("--gui", action="store_true", help="Use GUI folder picker")

    args = parser.parse_args()

    # Decide input method
    if args.gui:
        project_path = pick_folder_gui()
        if not project_path:
            print("No folder selected.")
            return
    elif args.path:
        project_path = Path(args.path)
    else:
        # fallback interactive
        user_input = input("Enter project folder path (or press Enter for GUI): ").strip()
        if not user_input:
            project_path = pick_folder_gui()
            if not project_path:
                print("No folder selected.")
                return
        else:
            project_path = Path(user_input)

    if not project_path.exists():
        print("Invalid path.")
        return

    output_file = Path(args.output)

    run(project_path, output_file)


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")