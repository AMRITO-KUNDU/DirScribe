import os
import textwrap

# Supported file extensions
TEXT_FILE_EXTENSIONS = {
    # Programming Languages
    ".py", ".js", ".ts", ".java", ".c", ".cpp", ".go", ".rb", ".rs", ".php", ".swift",
    ".sh", ".bat", ".pl", ".dart", ".kt", ".m", ".scala", ".cs", ".lua", ".r", ".jl",
    # Frontend/Web
    ".html", ".css", ".scss", ".less", ".xml", ".xhtml", ".tsx", ".jsx", ".vue", ".json",
    # Config / Project Files
    ".yml", ".yaml", ".ini", ".env", ".toml", ".lock", ".json5",
    # Data / Logs
    ".csv", ".tsv", ".sql", ".log",
    # Documentation / Text
    ".txt", ".md", ".rst",
    # Templates / Scripts
    ".jsp", ".aspx", ".htaccess", ".ejs", ".hbs", ".twig"
}

MAX_FILE_LINES = 500  # Maximum lines to include for large files


def is_text_file(file_name):
    _, ext = os.path.splitext(file_name)
    return ext.lower() in TEXT_FILE_EXTENSIONS


def generate_ascii_tree(root_path):
    tree_lines = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        level = dirpath.replace(root_path, "").count(os.sep)
        indent = "    " * level
        folder_name = os.path.basename(dirpath)
        tree_lines.append(f"{indent}{folder_name}/")

        subindent = "    " * (level + 1)
        for f in filenames:
            tree_lines.append(f"{subindent}{f}")

    return "\n".join(tree_lines)


def extract_file_contents(root_path):
    content_lines = []
    for dirpath, _, filenames in os.walk(root_path):
        for file in filenames:
            if not is_text_file(file):
                continue

            file_path = os.path.join(dirpath, file)
            relative_path = os.path.relpath(file_path, root_path)

            content_lines.append(f"\n--- {relative_path} ---\n")

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                    if len(lines) > MAX_FILE_LINES:
                        lines = lines[:MAX_FILE_LINES]
                        lines.append("\n... [truncated]\n")

                    content_lines.extend(lines)

            except Exception as e:
                content_lines.append(f"[Error reading file: {e}]\n")

    return "".join(content_lines)


def main():
    project_path = input("Enter your project folder path: ").strip()
    if not os.path.isdir(project_path):
        print("Invalid folder path. Exiting.")
        return

    output_file = input("Enter output file name (default: project_overview.txt): ").strip()
    if not output_file:
        output_file = "project_overview.txt"

    output_path = os.path.abspath(output_file)

    print("\nGenerating project overview...\n")

    ascii_tree = generate_ascii_tree(project_path)
    file_contents = extract_file_contents(project_path)

    with open(output_path, "w", encoding="utf-8") as out_file:
        out_file.write("Project File Structure:\n")
        out_file.write(ascii_tree)
        out_file.write("\n\nFile Contents:\n")
        out_file.write(file_contents)

    print(f"\nProject overview saved to: {output_path}")
    input("Press Enter to close...")


if __name__ == "__main__":
    main()
