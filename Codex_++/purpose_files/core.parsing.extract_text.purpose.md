# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

# Module: core.parsing.extract_text
- @ai-path: core.parsing.extract_text
- @ai-source-file: extract_text.py
- @ai-role: parser
- @ai-intent: "Normalise document ingestion by converting common file formats into UTF-8 plain text strings."
- @ai-version: 0.1.0
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: medium
- @ai-risk-performance: low

> Wraps format-specific readers (txt, Markdown, DOCX, PDF) with graceful fallbacks so ingestion does not fail when optional dependencies are missing.

### 🎯 Intent & Responsibility
- Detect supported file extensions and route to format-specific readers.
- Convert DOCX/PDF inputs to plain text using optional third-party libraries.
- Provide deterministic fallbacks and warnings when dependencies are missing (e.g., markdown parser).
- Raise actionable errors for unsupported formats so CLI tooling can surface feedback.

### 📥 Inputs & 📤 Outputs
| Direction | Name      | Type              | Description |
|-----------|-----------|-------------------|-------------|
| 📥 In     | file_path | `Path | str`      | Location of the source document |
| 📤 Out    | text      | `str`             | UTF-8 decoded plain text extracted from the document |
| ⚠️ Error  | ValueError | —                | Raised when format unsupported or conversion fails |

### 🔗 Dependencies
- `pathlib.Path`
- Optional: `markdown`, `python-docx`, `fitz` (PyMuPDF)
- `core.utils.logger.get_logger`

### 🤝 Coordination Mechanics
- Invoked synchronously; no background workers.
- Acts as a leaf utility — upstream callers (`core.storage.upload_local`, CLI parse command) control iteration and error handling.
- Emits warnings through `core.utils.logger` so pipeline loggers capture dependency gaps.

### 🔌 Integration Points
- @ai-upstream: `core.storage.upload_local.prepare_document_for_processing`
- @ai-downstream: `core.workflows.main_commands.upload_and_prepare`, CLI ingestion commands (`cli.parse`)
- Outputs feed into semantic chunking (`core.parsing.semantic_chunk`) and embedding generation.

### 🧠 Ecosystem Anchoring
- @ai-role-map: {parser → executor}
- Shares logging conventions with `core.logger` to keep ingestion telemetry consistent.
- No direct BudgetTracker usage but supports Run cadence by keeping ingestion deterministic.

### ⚠️ Risks & Notes
- Missing optional dependencies degrade extraction quality (warnings emitted).
- Binary files or exotic formats surface ValueError quickly, enabling CLI recovery.
- Ensure future formats extend `_READERS` map while maintaining logger behaviour.
