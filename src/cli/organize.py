""" 
Module: core_lib.metadata.organize
- @ai-path: core_lib.metadata.organize
- @ai-source-file: core_lib/metadata/organize.py
- @ai-module: organize
- @ai-role: Metadata-based File Organizer
- @ai-entrypoint: false
- @ai-intent: "Organizes files into structured output directories based on metadata-derived categories or optional clustering assignments."

🔍 Summary:
Organizes files into categorized folders based on metadata or provided clustering labels. It loads metadata for the given filename, determines the target category, moves parsed and source files accordingly, and copies associated metadata. Handles missing files with warnings and ensures category folders are created safely.

📦 Inputs:

- name (str): Base filename (without extension) to organize.
- cluster_map (Dict[str, str]): Optional mapping of filename keys to cluster categories.
- meta_dir (Path): Directory containing metadata files (default "metadata/").
- parsed_dir (Path): Directory containing parsed text files (default "parsed/").
- raw_dir (Path): Directory containing raw source files (default "raw/").
- out_dir (Path): Directory where organized files are placed (default "organized/").

📤 Outputs:

- None: The function operates via file system side effects (moving, copying, printing status).

🔗 Related Modules:

- core_lib.metadata.io (for `load_metadata` function)

🧠 For AI Agents:

- @ai-dependencies: pathlib.Path, shutil, json
- @ai-calls: load_metadata, Path.exists, Path.mkdir, Path.replace, shutil.copy
- @ai-uses: Path, shutil
- @ai-tags: organization, clustering, metadata, file management

⚙️ Meta:
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: 
- @change-summary: Initial structured documentation
- @notes: 
"""


import shutil
from pathlib import Path
from typing import Dict

from core.config import (
    LOCAL_METADATA_DIR,
    LOCAL_ORGANIZED_DIR,
    LOCAL_PARSED_DIR,
    LOCAL_RAW_DIR,
)
from core.logger import get_logger
from core.metadata.io import load_metadata


logger = get_logger(__name__)


def organize_file(
    name: str,
    cluster_map: Dict[str, str] = {},
    meta_dir: Path = LOCAL_METADATA_DIR,
    parsed_dir: Path = LOCAL_PARSED_DIR,
    raw_dir: Path = LOCAL_RAW_DIR,
    out_dir: Path = LOCAL_ORGANIZED_DIR,
) -> None:
    """
    Organize a file into a folder based on its metadata or clustering label.

    Args:
        name (str): Parsed filename (without extension).
        cluster_map (Dict[str, str]): Optional cluster labels for doc IDs.
        meta_dir (Path): Directory containing metadata.
        parsed_dir (Path): Directory of parsed .txt files.
        raw_dir (Path): Directory of raw source files.
        out_dir (Path): Output folder for organization.
    """
    meta_path = meta_dir / f"{name}.meta.json"
    if not meta_path.exists():
        logger.error("[red]No metadata found for %s[/red]", name)
        return

    meta = load_metadata(name, meta_dir)

    name_key = Path(name).stem.lower()
    cluster_label = cluster_map.get(name_key)
    category = cluster_label or meta.get("category", "uncategorized")
    safe_category = category.lower().replace(" ", "_")

    organized_path = out_dir / safe_category
    organized_path.mkdir(parents=True, exist_ok=True)

    parsed_file = Path(meta.get("parsed_file", f"{name_key}.txt")).name
    parsed_src = parsed_dir / parsed_file
    parsed_dst = organized_path / parsed_file
    if parsed_src.exists():
        parsed_src.replace(parsed_dst)
        logger.info("[green]Moved parsed file to %s[/green]", parsed_dst)
    else:
        logger.warning("[yellow]Parsed file missing: %s[/yellow]", parsed_src)

    source_file = meta.get("source_file")
    if source_file:
        source_name = Path(source_file).name
        source_src = raw_dir / source_name
        source_dst = organized_path / source_name
        if source_src.exists():
            source_src.replace(source_dst)
            logger.info("[cyan]Moved source file to %s[/cyan]", source_dst)
        else:
            logger.warning("[yellow]Source file missing: %s[/yellow]", source_src)

    shutil.copy(meta_path, organized_path / meta_path.name)
    logger.info("[blue]Copied metadata to %s[/blue]", organized_path / meta_path.name)
