# Module: core.parsing.openai_export
- @ai-path: core.parsing.openai_export
- @ai-source-file: openai_export.py
- @ai-role: parser
- @ai-intent: "Parse ChatGPT Data Export zip to extract conversation transcripts and user prompts."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: high
- @ai-risk-performance: low

> Processes the `conversations.json` file included in OpenAI's user data export and writes each conversation to its own text file along with a prompt-only file.

### 🎯 Intent & Responsibility
- Load the export archive or folder.
- Extract conversations in order of `current_node` parent pointers.
- Save full transcripts and user-only prompts to disk for later analysis.

### 📥 Inputs & 📤 Outputs
| Direction | Name         | Type            | Brief Description |
|-----------|--------------|-----------------|-------------------|
| 📥 In     | export_path  | Path            | Path to `.zip` export or extracted folder |
| 📥 In     | out_dir      | Path            | Directory to write conversation and prompt files |
| 📤 Out    | conversation | Path            | File path for each conversation transcript |
| 📤 Out    | prompts      | Path            | File path for user prompts only |

### 🔗 Dependencies
- `zipfile`, `json`, `pathlib`
- `core.parsing.normalize.normalize_filename`

### 🗣 Dialogic Notes
- Only linear path from `current_node` is reconstructed; branches are ignored.
- File names are normalized and truncated to avoid OS issues.
- Prompts are separated to help detect duplicate questions across chats.

### 9 Pipeline Integration
- **Coordination Mechanics:** Intended for manual invocation or future CLI command. Outputs may feed indexing or deduplication workflows.
- **Integration Points:** Downstream modules could ingest these transcripts for embedding or topic analysis.
- **Risks:** Export contains personal data; handle securely and avoid accidental commits.
