# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

- @ai-path: core.workflows.insurance_verification
- @ai-source-file: core/workflows/insurance_verification.py
- @ai-role: pipeline
- @ai-intent: "Orchestrate end-to-end extraction of standardized insurance data from heterogeneous forms."
- @schema-version: 0.2
- @ai-generated: true
- @human-reviewed: false
- @ai-risk-pii: high
- @ai-risk-performance: "Throughput dependent on LLM speed and document size."

# Module: core.workflows.insurance_verification
> High-level workflow that loads verification files, invokes the parser, and persists normalized policy records.

### 🎯 Intent & Responsibility
- Iterate over one or more input files and associated mapping configs.
- Delegate extraction to `core.parsing.insurance_verification` with appropriate LLM settings.
- Store or return aggregated records for downstream analysis or search.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | files | List[str] | Paths to verification forms |
| 📥 In | mapping | Dict[str, str] | Mapping configuration shared across files |
| 📥 In | model | str | Target model identifier for `langchain_router` |
| 📤 Out | records | List[Dict[str, Any]] | List of standardized policy dictionaries |

### 🔗 Dependencies
- `core.parsing.insurance_verification`
- `core.llm.langchain_router`
- `core.storage.upload_local` or similar persistence layer

### 🤝 Integration Points
- Upstream CLI command may call this pipeline.
- Downstream vector store or metadata modules consume resulting records.
- Potential agent-hub role to validate extracted fields.

### 🗣 Dialogic Notes
- @ai-role: orchestrator
- @ai-downstream: core.vectorstore.faiss_store
