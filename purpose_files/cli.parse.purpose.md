# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

# Module: cli.parse
# @ai-path: cli.parse
# @ai-source-file: parse.py
# @ai-role: CLI Entrypoint
# @ai-intent: "Convert raw files to parsed text with configurable paths."

> Offers a `parse` command that writes `.txt` files and stub metadata.

### 🎯 Intent & Responsibility
- Allow users to parse individual files or entire directories.
- Provide optional overrides for PathConfig directories.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | input_path | Path | File or folder to parse |
| 📥 In | parsed_name | str | Optional name override for single file |
| 📥 In | root/raw_dir/parsed_dir/metadata_dir | Path | Optional path overrides |
| 📤 Out | stub.json | File | Metadata stub linking raw and parsed files |

### 🔗 Dependencies
- `core.storage.upload_local.prepare_document_for_processing`
- `core.config.config_registry.get_path_config`

### 🗣 Dialogic Notes
- Path override logic mirrors upcoming GUI workflow needs.
