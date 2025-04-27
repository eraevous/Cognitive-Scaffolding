"""
Module: core_lib.storage.local_utils 

- @ai-path: core_lib.storage.local_utils 
- @ai-source-file: combined_storage.py 
- @ai-module: local_utils 
- @ai-role: file_io 
- @ai-entrypoint: save_json(), load_json() 
- @ai-intent: "Read and write local JSON files to support metadata storage and configuration."

🔍 Summary:
This module contains helper functions for saving and loading dictionaries to/from `.json` files using UTF-8 encoding. It's intended for use in local or intermediate storage pipelines, such as writing metadata, config files, or caching results.

📦 Inputs:
- path (str | Path): File path to read from or write to
- data (dict): Dictionary to serialize and write (for `save_json`)

📤 Outputs:
- save_json → None: Saves to disk
- load_json → dict: Parsed JSON dictionary

🔗 Related Modules:
- io.py → relies on this for metadata persistence
- schema.py → reads metadata for validation
- upload_utils → optionally uses these when staging uploads

🧠 For AI Agents:
- @ai-dependencies: json, pathlib
- @ai-calls: open, dump, load
- @ai-uses: Path, Union, str, dict
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
- @notes: 
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