# Module: core.metadata
> Provides standardized metadata handling utilities: schema validation, file-based I/O, merging logic, and fallback metadata recovery.

### 🎯 Intent & Responsibility
- Ensures metadata consistency across the pipeline through JSON Schema validation.
- Provides robust read/write utilities for `.meta.json` files.
- Merges multiple metadata fragments into a unified structure.
- Supports recovery of parsed text or metadata from fallback file paths or S3.

### 📥 Inputs & 📤 Outputs
| Direction | Name              | Type          | Brief Description                                    |
|-----------|-------------------|---------------|------------------------------------------------------|
| 📥 In     | metadata           | dict          | Input metadata for validation or saving.             |
| 📥 In     | path               | Path/str      | File or directory paths (local or S3).               |
| 📥 In     | metadata fragments | list[dict]    | Chunk-level metadata to merge.                       |
| 📤 Out    | valid              | bool          | Result of schema validation.                         |
| 📤 Out    | merged_metadata    | dict          | Combined output metadata after merging.              |
| 📤 Out    | parsed_text        | str or None   | Fallback-loaded parsed text content.                 |

### 🔗 Dependencies
- `jsonschema` for validation.
- `pathlib`, `json`, `os`, `boto3` for I/O.
- `core.config` for environment-specific paths or credentials.

### ⚙️ AI-Memory Tags
- `@ai-assumes:` Schema format remains stable; `.meta.json` naming conventions are consistent.
- `@ai-breakage:` Changes to metadata schema files or `config.LOCAL_META_PATH` structure will break validation and I/O routines.
- `@ai-risks:` Silent failure modes if metadata merging logic encounters malformed or partial chunks; fallback logic can mask underlying bugs.

### 🗣 Dialogic Notes
- Originally modularized to support ingestion pipelines and multi-stage processing workflows.
- May benefit from centralizing schema definitions and metadata versioning in the future.
- `get_parsed_text()` is particularly defensive—designed to always "get something" even under failure.
