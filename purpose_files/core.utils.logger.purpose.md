# Module: core.utils.logger

# @ai-path: core.utils.logger
# @ai-source-file: logger.py
# @ai-role: utility
# @ai-intent: "Provide a thin wrapper for consistent, environment-aware logging across modules."

> Provide a compatibility shim that re-exports the central logging helpers.

### 🎯 Intent & Responsibility
- Maintain backwards compatibility for modules still importing `core.utils.logger`.
- Proxy calls to `core.logger` so configuration logic stays centralized.

### 📥 Inputs & 📤 Outputs
| Direction | Name        | Type            | Brief Description |
|-----------|-------------|-----------------|-------------------|
| 📥 In     | name        | str             | Target logger name |
| 📥 In     | LOG_LEVEL   | env str         | Overrides default log level |
| 📤 Out    | logger      | logging.Logger  | Configured logger object |

### 🔗 Dependencies
- `core.logger` for actual setup and retrieval

### 🗣 Dialogic Notes
- Called by `core.embeddings.embedder` for detailed error reporting.
- Additional modules may import this to standardize logging.
- Used by `core.parsing.semantic_chunk` to emit boundary details when
  LOG_LEVEL is set to DEBUG.
