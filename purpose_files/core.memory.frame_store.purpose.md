# Module: core.memory.frame_store
- @ai-path: core.memory.frame_store
- @ai-source-file: frame_store.py
- @ai-role: memory
- @ai-intent: "Persist and recall lightweight conversation frames for context injection."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: medium
- @ai-risk-performance: "Frequent disk writes may impact I/O performance on slow storage."

> Maintain a simple directory of JSON files storing text snippets and metadata for later reuse.

### 🎯 Intent & Responsibility
- Save short text segments and associated metadata as "frames".
- Load frames by ID for light memory injection into LLM prompts.
- Enumerate available frames for exploratory workflows.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | text | str | Raw text to store in the frame |
| 📥 In | metadata | Optional[dict] | Additional context fields |
| 📥 In | frame_id | Optional[str] | Custom identifier for the frame |
| 📤 Out | frame_id | str | Generated or provided frame identifier |
| 📤 Out | frame | dict | Stored frame with text and metadata |
| 📤 Out | frames | List[str] | Available frame identifiers |

### 🔗 Dependencies
- `core.config.config_registry.get_path_config`
- `json`, `pathlib.Path`

### 🗣 Dialogic Notes
- Designed for ephemeral conversation snippets or summarization outputs.
- Frames are stored under `PathConfig.output / "frames"`.
- IDs are auto-incremented if not provided to ensure uniqueness.

### 9 Pipeline Integration
- @ai-pipeline-order: inverse
- **Coordination Mechanics:** Light memory injection occurs by loading frames before prompt generation. Retrieval modules or Livewire may reference `list_frames()` to suggest context.
- **Integration Points:** Upstream summarizers or chat loops can call `save_frame()`; downstream orchestrators read frames for context blending.
- **Risks:** Large numbers of frames may clutter disk space; consider periodic cleanup.
