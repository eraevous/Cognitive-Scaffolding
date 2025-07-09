#__________________________________________________________________
# File: __init__.py
# No docstring found


#__________________________________________________________________
# File: io.py
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

from core.metadata.schema import validate_metadata
from core.storage.local import load_json, save_json


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
    return metadata#__________________________________________________________________
# File: io_helpers.py
"""
📦 Module: core_lib.metadata.io_helpers
- @ai-path: core_lib.metadata.io_helpers
- @ai-source-file: combined_metadata.py
- @ai-role: Parsed Text Resolver
- @ai-intent: "Return parsed document content by resolving from local file, stub + raw reparsing, or S3 fallback."

🔍 Module Summary:
This module provides a fault-tolerant system for retrieving parsed document text. It first checks for local 
parsed files, then tries regenerating from raw sources if metadata stubs exist, and finally attempts S3 
downloads if necessary. This ensures robust handling of missing or incomplete parsed data during preprocessing.

🗂️ Contents:

| Name              | Type    | Purpose                                 |
|:------------------|:--------|:----------------------------------------|
| get_parsed_text    | Function | Recover parsed text via local or remote fallback methods. |

🧠 For AI Agents:
- @ai-dependencies: pathlib, json, boto3, fitz (for PDF parsing if used downstream)
- @ai-uses: Path, remote.prefixes, parsed_path, stub_path, raw_path
- @ai-tags: fallback, resilience, file-recovery, S3-aware

⚙️ Meta:
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Added fallback logic to retrieve missing parsed text
- @change-summary: Implements stub and S3 fallback for document parsing
- @notes: ""

👤 Human Overview:
    - Context: Used when parsed documents may be partially missing during preprocessing or ingestion.
    - Change Caution: Remote config assumptions (S3 paths) are hardcoded; breaking changes may occur if path structures change.
    - Future Hints: Support automatic stub regeneration and compression handling for large parsed files.
"""

"""
📦 Module: core_lib.metadata.io_helpers
- @ai-path: core_lib.metadata.io_helpers
- @ai-source-file: combined_metadata.py
- @ai-role: Parsed Text Resolver
- @ai-intent: "Return parsed document content by resolving from local file, stub + raw reparsing, or S3 fallback."

🔍 Module Summary:
This module provides a fault-tolerant system for retrieving parsed document text. It first checks for local 
parsed files, then tries regenerating from raw sources if metadata stubs exist, and finally attempts S3 
downloads if necessary. This ensures robust handling of missing or incomplete parsed data during preprocessing.

🗂️ Contents:

| Name              | Type    | Purpose                                 |
|:------------------|:--------|:----------------------------------------|
| get_parsed_text    | Function | Recover parsed text via local or remote fallback methods. |

🧠 For AI Agents:
- @ai-dependencies: pathlib, json, boto3, fitz (for PDF parsing if used downstream)
- @ai-uses: Path, remote.prefixes, parsed_path, stub_path, raw_path
- @ai-tags: fallback, resilience, file-recovery, S3-aware

⚙️ Meta:
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Added fallback logic to retrieve missing parsed text
- @change-summary: Implements stub and S3 fallback for document parsing
- @notes: ""

👤 Human Overview:
    - Context: Used when parsed documents may be partially missing during preprocessing or ingestion.
    - Change Caution: Remote config assumptions (S3 paths) are hardcoded; breaking changes may occur if path structures change.
    - Future Hints: Support automatic stub regeneration and compression handling for large parsed files.
"""

import json
from pathlib import Path

from core_lib.config.remote_config import RemoteConfig
from core_lib.parsing.extract_text import extract_text
from core_lib.storage.s3_utils import get_s3_client

remote = RemoteConfig.from_file(Path(__file__).parent.parent / "config" / "remote_config.json")

def get_parsed_text(name: str) -> str:
    parsed_path = Path(remote.prefixes["parsed"]) / name
    stub_path = Path(remote.prefixes["metadata"]) / f"{name}.stub.json"

    if parsed_path.exists():
        return parsed_path.read_text(encoding="utf-8")

    if stub_path.exists():
        with stub_path.open("r", encoding="utf-8") as f:
            stub = json.load(f)

        raw_file = Path(stub["source_file"]).name
        raw_path = Path(remote.prefixes["raw"]) / raw_file

        if raw_path.exists():
            print(f"♻️ Re-parsing from raw file: {raw_file}")
            text = extract_text(str(raw_path))
            parsed_path.write_text(text, encoding="utf-8")
            return text

    print(f"⬇️ Downloading parsed file from S3: {name}")
    s3 = get_s3_client()
    s3.download_file(Bucket=remote.bucket_name, Key=f"{remote.prefixes['parsed']}{name}", Filename=str(parsed_path))
    return parsed_path.read_text(encoding="utf-8")#__________________________________________________________________
# File: merge.py
"""
📦 Module: core_lib.metadata.merge
- @ai-path: core_lib.metadata.merge
- @ai-source-file: combined_metadata.py
- @ai-role: Metadata Aggregator
- @ai-intent: "Combine segmented metadata chunks into one unified dict and resolve filename identity from stubs."

🔍 Module Summary:
This module supports post-classification workflows by merging multiple metadata dictionaries into a single 
consolidated result and resolving parsed filenames via inspection of metadata stubs. It uses aggregation, 
majority voting, and flattening strategies to unify partial outputs.

🗂️ Contents:

| Name                    | Type    | Purpose                                 |
|:------------------------|:--------|:----------------------------------------|
| merge_metadata_blocks    | Function | Merge multiple metadata block dictionaries. |
| resolve_parsed_filename  | Function | Resolve parsed `.txt` filenames using stub files. |

🧠 For AI Agents:
- @ai-dependencies: json, pathlib, collections
- @ai-uses: ValueError, FileNotFoundError, Counter, Path
- @ai-tags: metadata-merging, filename-resolution, pipeline-support

⚙️ Meta:
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add chunk metadata merge + filename resolution logic
- @change-summary: Created post-classification tools to consolidate metadata and map filenames
- @notes: ""

👤 Human Overview:
    - Context: Used to cleanly combine classified chunk outputs and standardize downstream metadata.
    - Change Caution: Assumes consistent key presence across partial outputs; schema changes may impact logic.
    - Future Hints: Add support for weight-based merging or user-overridable merge strategies.
"""

"""
📦 Module: core_lib.metadata.merge
- @ai-path: core_lib.metadata.merge
- @ai-source-file: combined_metadata.py
- @ai-role: Metadata Aggregator
- @ai-intent: "Combine segmented metadata chunks into one unified dict and resolve filename identity from stubs."

🔍 Module Summary:
This module supports post-classification workflows by merging multiple metadata dictionaries into a single 
consolidated result and resolving parsed filenames via inspection of metadata stubs. It uses aggregation, 
majority voting, and flattening strategies to unify partial outputs.

🗂️ Contents:

| Name                    | Type    | Purpose                                 |
|:------------------------|:--------|:----------------------------------------|
| merge_metadata_blocks    | Function | Merge multiple metadata block dictionaries. |
| resolve_parsed_filename  | Function | Resolve parsed `.txt` filenames using stub files. |

🧠 For AI Agents:
- @ai-dependencies: json, pathlib, collections
- @ai-uses: ValueError, FileNotFoundError, Counter, Path
- @ai-tags: metadata-merging, filename-resolution, pipeline-support

⚙️ Meta:
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add chunk metadata merge + filename resolution logic
- @change-summary: Created post-classification tools to consolidate metadata and map filenames
- @notes: ""

👤 Human Overview:
    - Context: Used to cleanly combine classified chunk outputs and standardize downstream metadata.
    - Change Caution: Assumes consistent key presence across partial outputs; schema changes may impact logic.
    - Future Hints: Add support for weight-based merging or user-overridable merge strategies.
"""


import json
from collections import Counter
from pathlib import Path
from typing import Dict, List


def merge_metadata_blocks(blocks: List[Dict]) -> Dict:
    """
    Merge multiple metadata blocks (from chunked summarization) into a single unified metadata dict.

    @ai-role: merger
    @ai-intent: "Combine multiple partial metadata objects into one"

    Args:
        blocks (List[Dict]): List of metadata dictionaries.

    Returns:
        Dict: Merged metadata dictionary.

    Raises:
        ValueError: If no valid blocks are provided.
    """
    if not blocks:
        raise ValueError("No valid metadata blocks to merge.")

    def flatten(key: str) -> List:
        return list({x for block in blocks for x in block.get(key, [])})

    summary = " ".join(block.get("summary", "") for block in blocks)
    topics = flatten("topics")
    tags = flatten("tags")
    themes = flatten("themes")
    priority = round(sum(block.get("priority", 3) for block in blocks) / len(blocks))

    def most_common(key: str) -> str:
        return Counter(block.get(key, "") for block in blocks).most_common(1)[0][0]

    return {
        "summary": summary.strip(),
        "topics": topics,
        "tags": tags,
        "themes": themes,
        "priority": priority,
        "tone": most_common("tone"),
        "stage": most_common("stage"),
        "depth": most_common("depth"),
        "category": most_common("category")
    }

def resolve_parsed_filename(raw_or_parsed: str, stub_dir: str = "metadata") -> str:
    """
    Resolves a filename (raw or parsed) into its parsed .txt equivalent by inspecting stub files.

    @ai-role: filename resolver
    @ai-intent: "Translate raw input filename into its parsed .txt target using stub metadata"

    Args:
        raw_or_parsed (str): Filename of the raw or parsed file.
        stub_dir (str): Directory where stub files are stored.

    Returns:
        str: Filename of the parsed .txt file.

    Raises:
        FileNotFoundError: If no matching stub is found.
    """
    name = Path(raw_or_parsed).name

    if name.endswith(".txt"):
        return name

    stub_path = Path(stub_dir)
    for stub_file in stub_path.glob("*.stub.json"):
        with open(stub_file, "r", encoding="utf-8") as f:
            stub = json.load(f)
        if Path(stub.get("source_file", "")).name.lower() == name.lower():
            return Path(stub["parsed_file"]).name

    raise FileNotFoundError(f"No stub found for raw file '{name}'")#__________________________________________________________________
# File: schema.py
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
from typing import Union

from jsonschema import ValidationError, validate

from core.config.config_registry import get_path_config
from core.config.path_config import PathConfig

paths = get_path_config()

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
    schema_path = Path(paths.schema)
    print(f"[schema.py] Using schema path: {schema_path}")

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    validate(instance=metadata, schema=schema)
#__________________________________________________________________
# File: stub.py
# No docstring found

