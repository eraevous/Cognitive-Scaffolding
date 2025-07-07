# Module: core.utils.logger

# @ai-path: core.utils.logger
# @ai-source-file: logger.py
# @ai-role: utility
# @ai-intent: "Provide a thin wrapper for consistent, environment-aware logging across modules."

> Provide a simple helper to configure and retrieve Python loggers with a common format.

### 🎯 Intent & Responsibility
- Ensure consistent log formatting across modules.
- Respect `LOG_LEVEL` environment variable for verbosity control.

### 📥 Inputs & 📤 Outputs
| Direction | Name        | Type            | Brief Description |
|-----------|-------------|-----------------|-------------------|
| 📥 In     | name        | str             | Target logger name |
| 📥 In     | LOG_LEVEL   | env str         | Overrides default log level |
| 📤 Out    | logger      | logging.Logger  | Configured logger object |

### 🔗 Dependencies
- `logging`, `os`

### 🗣 Dialogic Notes
- Called by `core.embeddings.embedder` for detailed error reporting.
- Additional modules may import this to standardize logging.
