- @ai-path: core.memory.frame_store
- @ai-source-file: frame_store.py
- @ai-role: memory
- @ai-intent: "Persist and inject small text frames for lightweight conversational memory."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.2
- @ai-risk-pii: medium
- @ai-risk-performance: "File I/O per frame; minimal impact for short texts."

# Module: core.memory.frame_store
> File-backed frame storage for ephemeral memory injection.

### 🎯 Intent & Responsibility
- Store frame text as JSON files under `paths.output/frames` by default.
- Load frames by ID to support contextual recall.
- Provide `inject_memory` to prepend saved frames to new prompts.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | frame_id | str | Identifier for memory frame |
| 📥 In | text | str | Text content to store |
| 📥 In | frame_ids | list[str] | Frames to inject into prompt |
| 📤 Out | combined | str | Original text with prepended memory |
| 📤 Out | file_path | Path | Saved frame path on disk |

### 🔗 Dependencies
- `core.config.config_registry.get_path_config`
- `json`, `pathlib.Path`

### 🗣 Dialogic Notes
- Intended for lightweight human-in-the-loop use; not a fully fledged vector DB.
- Frame IDs are arbitrary strings (e.g., topic names or timestamps).

### 9 Pipeline Integration
- **Coordination Mechanics:** Used prior to LLM invocation to inject persistent notes or recap summaries.
- **Integration Points:** Works with `summarize_documents` outputs or manual notes.
- **Risks:** Stale frames may mislead summarization; implement expiration or versioning as needed.
