"""
Module: core_lib.metadata.io 

- @ai-path: core_lib.metadata.io 
- @ai-source-file: combined_metadata.py 
- @ai-module: io 
- @ai-role: metadata_io 
- @ai-entrypoint: save_metadata(), load_metadata() 
- @ai-intent: "Provide save/load operations for document metadata with JSON validation and schema enforcement."

🔍 Summary: This module defines two core I/O functions: `save_metadata`, which saves a dictionary of document metadata to a `.meta.json` file (after validating it against a schema), and `load_metadata`, which reads metadata back from disk and ensures it's still valid. The module assumes `Path` directory structure and schema-driven safety.

📦 Inputs:
- filename (str): The document identifier (without extension).
- metadata (dict): Metadata dictionary to save (for `save_metadata`).
- meta_dir (Path): Path to metadata directory (default: `metadata/`).

📤 Outputs:
- save_metadata → str: Full path to the saved metadata file
- load_metadata → dict: Parsed and validated metadata dictionary

🔗 Related Modules:
- validate_metadata → schema enforcement
- save_json / load_json → raw I/O helpers
- merge_metadata_blocks → often called after classification

🧠 For AI Agents:
- @ai-dependencies: pathlib, json
- @ai-calls: validate_metadata, save_json, load_json, mkdir
- @ai-uses: Path, str, dict
- @ai-tags: metadata, validation, io, schema, persistence

⚙️ Meta: 
- @ai-version: 0.2.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Initial save/load with validation logic 
- @change-summary: Add schema validation to metadata I/O 
- @notes: 
"""


from core_lib.metadata.schema import validate_metadata
from core_lib.storage.local_utils import save_json, load_json
from pathlib import Path


def save_metadata(filename: str, metadata: dict, meta_dir: Path = Path("metadata")) -> str:
    """
    Validates and saves metadata to disk as a .meta.json file.

    @ai-role: saver
    @ai-intent: "Write validated metadata to disk for long-term storage"

    Args:
        filename (str): Base filename (no extension needed)
        metadata (dict): Metadata dictionary
        meta_dir (Path): Directory to save metadata to

    Returns:
        str: Path to the saved metadata file
    """
    validate_metadata(metadata)
    meta_dir.mkdir(parents=True, exist_ok=True)
    path = meta_dir / f"{filename}.meta.json"
    save_json(path, metadata)
    return str(path)


def load_metadata(filename: str, meta_dir: Path = Path("metadata")) -> dict:
    """
    Loads and validates metadata from a .meta.json file.

    @ai-role: loader
    @ai-intent: "Read a metadata file from disk and verify its structure"

    Args:
        filename (str): Base filename (no extension)
        meta_dir (Path): Directory to load from

    Returns:
        dict: Parsed and validated metadata
    """
    path = meta_dir / f"{filename}.meta.json"
    metadata = load_json(path)
    validate_metadata(metadata)
    return metadata