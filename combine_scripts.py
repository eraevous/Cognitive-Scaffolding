import os
from pathlib import Path
import csv
import typer
from typing import List

app = typer.Typer()

SEPARATOR = "#" + "_" * 66 + "\n"


def should_ignore_dir(dir_name: str, ignore_dirs: List[str]) -> bool:
    """Check if a directory should be ignored based on its name."""
    return dir_name in ignore_dirs


def collect_py_files(root_dir: Path, ignore_dirs: List[str]):
    py_files = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not should_ignore_dir(d, ignore_dirs)]
        files = [f for f in filenames if f.endswith(".py")]
        if files:
            rel_path = Path(dirpath).relative_to(root_dir)
            py_files[rel_path] = [Path(dirpath) / f for f in files]
    return py_files


def extract_module_docstring(file_path: Path) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        lines = content.splitlines()
        if lines and (lines[0].startswith('"""') or lines[0].startswith("'''")):
            doc = []
            delim = lines[0][:3]
            for line in lines:
                doc.append(line)
                if line.endswith(delim) and len(doc) > 1:
                    break
            return "\n".join(doc)
    except Exception:
        pass
    return "# No docstring found"


def combine_files(file_paths: List[Path]) -> (str, int):
    combined = []
    total_lines = 0
    for file_path in sorted(file_paths):
        combined.append(SEPARATOR)
        combined.append(f"# File: {file_path.name}\n")
        docstring = extract_module_docstring(file_path)
        combined.append(docstring + "\n\n")
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            total_lines += len(lines)
            combined.extend(lines)
    return "".join(combined), total_lines


@app.command()
def combine_scripts(
    root: Path = typer.Argument(..., help="Root directory to search"),
    ignore_dirs: str = typer.Option("env", help="Comma-separated list of directory names to ignore"),
    output_dir: str = typer.Option("Combined_Scripts", help="Output directory for combined files"),
    log_csv: str = typer.Option("combined_log.csv", help="CSV file to store summary log")
):
    """
    Combine all Python files in subdirectories of ROOT into one script per subdirectory.
    Adds separator and docstring for each file. Logs stats in CSV.
    """
    ignore_list = [d.strip() for d in ignore_dirs.split(",") if d.strip()]
    typer.echo(f"🔍 Ignoring Python files in {ignore_list}...")

    root_path = root.resolve()
    output_path = root_path / output_dir
    output_path.mkdir(exist_ok=True)

    file_map = collect_py_files(root_path, ignore_list)
    log_rows = [("Combined_File", "Num_Source_Files", "Total_Lines")]

    for rel_dir, files in file_map.items():
        if not files:
            continue
        filename = f"{'.'.join(rel_dir.parts)}.combined.py"
        combined_code, line_count = combine_files(files)
        output_file = output_path / filename
        output_file.write_text(combined_code, encoding="utf-8")
        log_rows.append((filename, len(files), line_count))

    with open(output_path / log_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(log_rows)

    typer.echo(f"✅ Combined {len(file_map)} script groups. Output in: {output_path}")


if __name__ == "__main__":
    app()