# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

# Module: core.parsing.normalize
- @ai-path: core.parsing.normalize
- @ai-source-file: normalize.py
- @ai-role: utility
- @ai-intent: "Standardize strings for safe filenames."
- @schema-version: 0.2
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false

> Provides a lightweight helper for converting arbitrary labels into filesystem-safe slugs.

### 🎯 Intent & Responsibility
- Replace spaces and invalid characters with underscores.
- Lowercase results and collapse repeated underscores.
- Used across parsing modules to ensure consistent file names.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | name | str | Raw title or identifier |
| 📤 Out | slug | str | Normalized path-safe name |

### 🔗 Dependencies
- `re`
- Consumed by `core.parsing.openai_export` and potential upload utilities.

### 9 Pipeline Integration
- **Coordination Mechanics:** Called inline by parsers when generating output file paths.
- **Integration Points:** Downstream modules expect sanitized names for metadata files and transcripts.
- **Risks:** Overzealous filtering could produce duplicate slugs; uniqueness is not guaranteed.
