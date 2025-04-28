"""
📦 Module: core_lib.storage.local_utils
- @ai-path: core_lib.storage.local_utils
- @ai-source-file: combined_storage.py
- @ai-role: File I/O Utilities
- @ai-intent: "Read and write local JSON files to support metadata storage and configuration."

🔍 Module Summary:
This module provides simple helper functions for saving and loading dictionaries to and from JSON files on disk, 
using UTF-8 encoding. Intended for use cases like metadata caching, configuration persistence, and 
intermediate storage in local environments.

🗂️ Contents:

| Name        | Type     | Purpose                              |
|:------------|:---------|:-------------------------------------|
| save_json   | Function | Save a dictionary as a JSON file.    |
| load_json   | Function | Load a dictionary from a JSON file.  |

🧠 For AI Agents:
- @ai-dependencies: json, pathlib
- @ai-uses: Path, open, dump, load
- @ai-tags: json, file-io, metadata, utility

⚙️ Meta:
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add JSON load/save utilities for local disk persistence
- @change-summary: Standardize file-based JSON I/O
- @notes: ""

👤 Human Overview:
    - Context: Useful for persisting lightweight data structures locally between processing stages.
    - Change Caution: Paths should be validated externally to avoid writing over critical files.
    - Future Hints: Add atomic save operations or backup file support for better resilience.
"""



import json
from pathlib import Path
from typing import Union


def save_json(path: Union[str, Path], data: dict) -> None:
    """
    Save a dictionary as pretty-printed JSON to a file.

    @ai-role: saver
    @ai-intent: "Write JSON content from a dict to a file"

    Args:
        path (Union[str, Path]): Destination file path
        data (dict): Data to save
    """
    path = Path(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(path: Union[str, Path]) -> dict:
    """
    Load JSON data from a file and return as a dict.

    @ai-role: loader
    @ai-intent: "Read file contents and parse into dict"

    Args:
        path (Union[str, Path]): Path to JSON file

    Returns:
        dict: Loaded JSON data
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)