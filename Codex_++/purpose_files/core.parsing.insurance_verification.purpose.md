# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

- @ai-path: core.parsing.insurance_verification
- @ai-source-file: core/parsing/insurance_verification.py
- @ai-role: extractor
- @ai-intent: "Parse insurance verification documents and map raw text to a canonical policy schema."
- @schema-version: 0.2
- @ai-generated: true
- @human-reviewed: false
- @ai-risk-pii: high
- @ai-risk-performance: "Large documents may increase latency; rely on chunking when necessary."

# Module: core.parsing.insurance_verification
> Ingests PDFs, DOCX, or text forms, compares against a mapping document, and yields normalized insurance metadata.

### 🎯 Intent & Responsibility
- Load document bytes from varied filetypes and extract raw text.
- Apply mapping rules and LLM prompts to align fields (policy number, coverages, deductibles, limitations).
- Emit structured records ready for downstream storage or retrieval.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | file_path | str | Path to insurance verification file |
| 📥 In | mapping | Dict[str, str] | Field mapping or path to mapping doc |
| 📥 In | llm | Callable | Generation hook from `langchain_router` |
| 📤 Out | record | Dict[str, Any] | `{insurer: str, policy_holder: str, coverages: List[Dict[str, Any]], deductibles: Dict[str, str], limitations: List[str]}` |

### 🔗 Dependencies
- `pdfplumber` / `python-docx` for file parsing
- `core.llm.langchain_router`
- `core.utils.budget_tracker`

### 🤝 Integration Points
- Consumed by `core.workflows.insurance_verification` pipeline.
- Records may be stored via `core.storage` or indexed by `core.vectorstore`.

### 🗣 Dialogic Notes
- @ai-used-by: core.workflows.insurance_verification
- @ai-role: extractor
