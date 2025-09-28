"""
📦 Module: core_lib.metadata.io
- @ai-path: core_lib.metadata.io
- @ai-source-file: combined_metadata.py
- @ai-role: Metadata I/O Handler
- @ai-intent: "Provide save/load operations for document metadata with JSON validation and schema enforcement."

🔍 Module Summary:
This module defines two core I/O functions: `save_metadata`, which saves a dictionary of document metadata 
to a `.meta.json` file (after validating it against a schema), and `load_metadata`, which reads metadata back 
from disk and ensures it's still valid. It uses `Path`-based file management and schema-driven validation to 
ensure reliable storage and retrieval of metadata objects.

🗂️ Contents:

| Name              | Type    | Purpose                                           |
|:------------------|:--------|:--------------------------------------------------|
| save_metadata     | Function | Save validated metadata to a .meta.json file.      |
| load_metadata     | Function | Load and validate metadata from a .meta.json file. |

🧠 For AI Agents:
- @ai-dependencies: pathlib, json
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
- @notes: ""

👤 Human Overview:
    - Context: Used to persist and restore metadata in document processing workflows.
    - Change Caution: Schema assumptions are embedded; changes must synchronize with validation logic.
    - Future Hints: Extend for versioning support or alternate formats like YAML if needed.
"""

from pathlib import Path

from core.config import LOCAL_METADATA_DIR
from core.metadata.schema import validate_metadata
from core.storage.local import load_json, save_json


def save_metadata(
    filename: str, metadata: dict, meta_dir: Path = LOCAL_METADATA_DIR
) -> str:
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


def load_metadata(filename: str, meta_dir: Path = LOCAL_METADATA_DIR) -> dict:
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
