"""
📦 Module: core_lib.metadata.schema
- @ai-path: core_lib.metadata.schema
- @ai-source-file: combined_metadata.py
- @ai-role: Metadata Schema Validator
- @ai-intent: "Ensure metadata files follow a shared JSON schema structure."

🔍 Module Summary:
This module defines schema enforcement for document metadata structures. It loads the unified schema from 
disk and validates metadata dictionaries against it using `jsonschema`, raising clear errors when violations occur.

🗂️ Contents:

| Name                 | Type    | Purpose                                           |
|:---------------------|:--------|:--------------------------------------------------|
| load_schema          | Function | Load metadata schema from a JSON file.             |
| validate_metadata    | Function | Validate a metadata dictionary against the schema. |

🧠 For AI Agents:
- @ai-dependencies: json, jsonschema, pathlib
- @ai-uses: Path, dict, SCHEMA_PATH
- @ai-tags: schema, validation, metadata-safety

⚙️ Meta:
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add schema enforcement using jsonschema
- @change-summary: Load and apply schema to metadata dictionaries
- @notes: ""

👤 Human Overview:
    - Context: Used to validate metadata before saving, uploading, or processing in pipelines.
    - Change Caution: Changes to schema structure require updating validation logic accordingly.
    - Future Hints: Allow dynamic schema selection for supporting multiple metadata versions.
"""

import json
from jsonschema import validate, ValidationError
from pathlib import Path
from core_lib.config.path_config import PathConfig

SCHEMA_PATH = PathConfig.from_file().root / PathConfig.from_file().schema


def load_schema(path: Path = SCHEMA_PATH) -> dict:
    """
    Loads a JSON schema from file.

    @ai-role: loader
    @ai-intent: "Load the latest metadata schema JSON from disk"

    Args:
        path (Path): Path to the schema JSON file

    Returns:
        dict: Loaded schema
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_metadata(metadata: dict, schema_path: Path = SCHEMA_PATH) -> bool:
    """
    Validates a metadata dictionary against a JSON schema.

    @ai-role: validator
    @ai-intent: "Confirm metadata meets schema structure and constraints"

    Args:
        metadata (dict): Metadata to validate
        schema_path (Path): Path to the schema file

    Returns:
        bool: True if valid, raises ValidationError otherwise
    """
    schema = load_schema(schema_path)
    validate(instance=metadata, schema=schema)
    return True