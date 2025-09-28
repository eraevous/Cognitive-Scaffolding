# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

# Module: core.storage.upload_local
# @ai-path: core.storage.upload_local
# @ai-source-file: upload_local.py
# @ai-role: Local Ingestion Utility
# @ai-intent: "Convert documents to text and save stubs on the local filesystem."

> Provides helper functions to parse raw files into `.txt` and generate stub metadata.

### 🎯 Intent & Responsibility
- Prepare local documents for classification workflows.
- Accept optional `PathConfig` overrides for flexible directory layout.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | file_path | Path | Path to the source file |
| 📥 In | parsed_name | str | Optional name for `.txt` output |
| 📥 In | paths | PathConfig | Optional directory configuration |
| 📤 Out | stub | dict | Mapping of raw and parsed file paths |

### 🔗 Dependencies
- `core.parsing.extract_text`
- `core.config.config_registry.get_path_config`

### 🗣 Dialogic Notes
- Called by CLI utilities and pipeline steps during ingestion.
