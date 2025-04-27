"""
Module: core_lib.metadata.schema 

- @ai-path: core_lib.metadata.schema 
- @ai-source-file: combined_metadata.py 
- @ai-module: schema 
- @ai-role: validator 
- @ai-entrypoint: validate_metadata() 
- @ai-intent: "Ensure metadata files follow a shared JSON schema structure."

🔍 Summary:
This module handles loading and applying the project's unified metadata schema. `load_schema` reads the schema JSON from disk, and `validate_metadata` confirms that metadata files conform to the schema's structure and constraints using the `jsonschema` package.

📦 Inputs:
- metadata (dict): A metadata dictionary to validate
- path (Path): Location of the schema file (defaults to SCHEMA_PATH)

📤 Outputs:
- load_schema → dict: Parsed schema dictionary
- validate_metadata → bool: Returns True if valid, raises on error

🔗 Related Modules:
- io.py → validates metadata before saving
- merge.py → produces merged metadata that is validated before upload
- metadata_schema.json → defines required fields like summary, topics, tags, etc.

🧠 For AI Agents:
- @ai-dependencies: json, jsonschema, pathlib
- @ai-calls: open, load, validate
- @ai-uses: SCHEMA_PATH, Path, dict
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
- @notes: 
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