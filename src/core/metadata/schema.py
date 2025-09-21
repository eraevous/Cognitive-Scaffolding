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
from pathlib import Path

from jsonschema import validate

from core.config.config_registry import get_path_config
from core.constants import ERROR_SCHEMA_FILE_NOT_FOUND
from core.logger import get_logger

logger = get_logger(__name__)


def validate_metadata(metadata: dict) -> None:
    """
    Validate a metadata dictionary against the configured JSON schema.

    Args:
        metadata (dict): The metadata block to check.
        config_path (str | Path, optional): Optional override for config file.

    Raises:
        ValidationError: If metadata does not conform to schema.
        FileNotFoundError: If schema path is missing or invalid.
    """
    paths = get_path_config()
    schema_path = Path(paths.schema)
    logger.info("Using schema path: %s", schema_path)

    if not schema_path.exists():
        raise FileNotFoundError(ERROR_SCHEMA_FILE_NOT_FOUND.format(path=schema_path))

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    validate(instance=metadata, schema=schema)
