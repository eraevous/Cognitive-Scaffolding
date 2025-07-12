# Module: core.parsing.openai_export
- @ai-path: core.parsing.openai_export
- @ai-source-file: openai_export.py
- @ai-role: parser
- @ai-intent: "Parse ChatGPT Data Export zip to extract conversation transcripts and user prompts with optional Markdown formatting."
- @ai-version: 0.1.2
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
| 📥 In     | markdown    | bool           | Save transcripts as `.md` when True |
| 📤 Out    | conversation | Path            | File path for each conversation transcript |
| 📤 Out    | prompts      | Path            | File path for user prompts only |
| 📤 Out    | outputs      | List[Dict[str, Path]] | [{'conversation': Path, 'prompts': Path}] per chat |
| ❗ Error   | ValueError   | N/A             | Raised when messages cannot be extracted |
=======

### 🔗 Dependencies
- `zipfile`, `json`, `pathlib`
- `core.parsing.normalize.normalize_filename`

### 🗣 Dialogic Notes
- Only linear path from `current_node` is reconstructed; branches are ignored.
- File names are normalized and truncated to avoid OS issues.
- Prompts are separated to help detect duplicate questions across chats.
- Conversations may be written in Markdown when the `markdown` flag is enabled.
- Zip archives with a top-level directory are supported by scanning for
  `conversations.json` within the archive.
- Malformed mapping nodes are skipped; missing messages yield an "unknown" role
  when content exists.

### 9 Pipeline Integration
- **Coordination Mechanics:** Used by Typer command `chatgpt parse` to generate files on demand. Outputs may feed indexing or deduplication workflows.
- **Integration Points:** Downstream modules could ingest these transcripts for embedding or topic analysis.
- **Risks:** Export contains personal data; handle securely and avoid accidental commits.
