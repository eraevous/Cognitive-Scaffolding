# Module: cli.dedup
# @ai-path: cli.dedup
# @ai-source-file: dedup.py
# @ai-role: CLI Entrypoint
# @ai-intent: "Expose prompt deduplication via Typer command."

> Thin wrapper around `core.utils.dedup.dedup_lines_in_folder`.

### 🎯 Intent & Responsibility
- Provide a `dedup_prompts` command for unique prompt lines.
- Default paths rely on `get_path_config`.

### 📥 Inputs & 📤 Outputs
| Direction | Name       | Type | Brief Description |
|-----------|-----------|------|------------------|
| 📥 In     | prompt_dir | Path | Folder of `.txt` prompt files |
| 📥 In     | out_file   | Path | File path for deduplicated lines |
| 📤 Out    | dedup_file | File | Written dedup file |

### 🔗 Dependencies
- `typer`
- `core.config.config_registry.get_path_config`
- `core.utils.dedup.dedup_lines_in_folder`

### 🗣 Dialogic Notes
- Registered in `cli.main` under the `dedup` sub-command.

