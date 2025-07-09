# Module: core.memory
> Lightweight memory utilities for saving and recalling conversation frames.

### 🎯 Intent & Responsibility
- Provide persistent storage for short text snippets.
- Offer helper functions to recall recent frames for context injection.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | content | str | Frame text to store |
| 📥 In | limit | int | Number of frames to load |
| 📤 Out | path | Path | Saved frame path |
| 📤 Out | frames | List[str] | Loaded frame texts |

### 🔗 Dependencies
- `json`, `datetime`, `pathlib`
- `core.utils.logger`

### 🗣 Dialogic Notes
- Frames can be attached to synthesized outputs for persistent memory.
