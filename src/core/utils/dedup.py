from pathlib import Path


def dedup_lines_in_folder(folder: Path, output_file: Path) -> None:
    """Collect unique lines from all *.txt files in ``folder`` and write them.

    Lines are stripped of trailing newlines. Empty lines are ignored.
    The resulting file is sorted alphabetically.
    """
    unique = set()
    for txt_file in folder.glob("*.txt"):
        with txt_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    unique.add(line)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as out:
        for line in sorted(unique):
            out.write(line + "\n")

