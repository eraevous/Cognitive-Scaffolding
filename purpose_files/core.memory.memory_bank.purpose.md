- @ai-path: core.memory.memory_bank
- @ai-source-file: memory_bank.py
- @ai-role: memory
- @ai-intent: "Persist and recall short text frames for context injection."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: medium
- @ai-risk-performance: low

# Module: core.memory.memory_bank
> Minimal persistent storage for conversation or document snippets.

### 🎯 Intent & Responsibility
- Save text frames to disk with timestamped filenames.
- Load recent frames for reuse in prompts or analysis.
- Serve as lightweight memory layer for QAT workflows.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | content | str | Text snippet to store |
| 📥 In | memory_dir | Path | Folder for frames (optional) |
| 📥 In | limit | int | Number of frames to load |
| 📤 Out | path | Path | Saved frame file path |
| 📤 Out | frames | List[str] | Recent frame contents |

### 🔗 Dependencies
- `json`, `datetime`, `pathlib.Path`
- `core.utils.logger`

### 🗣 Dialogic Notes
- Frames are simple JSON files; external systems may ingest them.
- High-volume storage may require pruning strategies not yet implemented.

### 9 Pipeline Integration
- @ai-pipeline-order: normal
- **Coordination Mechanics:** Called after summarization or user actions to persist context. Retrieval functions can inject loaded frames before LLM calls.
- **Integration Points:** May be used by Livewire or synthesis modules for memory injection. Upstream modules pass text; downstream consumers read returned frames.
- **Risks:** Saving sensitive text may leak PII if not redacted. Consider encryption for sensitive deployments.
