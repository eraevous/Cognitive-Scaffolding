# Module: core.utils.dedup
# @ai-path: core.utils.dedup
# @ai-source-file: dedup.py
# @ai-role: utility
# @ai-intent: "Gather unique lines from prompt text files and persist them."

> Helper to merge multiple text files and remove duplicate lines.

### 🎯 Intent & Responsibility
- Iterate through all `.txt` files in a folder.
- Collect unique, non-empty lines.
- Write a sorted list of these lines to an output path.

### 📥 Inputs & 📤 Outputs
| Direction | Name        | Type | Brief Description |
|-----------|------------|------|------------------|
| 📥 In     | folder      | Path | Directory containing prompt files |
| 📥 In     | output_file | Path | Destination for deduplicated lines |
| 📤 Out    | dedup_file  | File | File with unique prompt lines |

### 🔗 Dependencies
- `pathlib.Path`

### 🗣 Dialogic Notes
- Used by `cli.dedup` to consolidate prompt files before training or evaluation.

