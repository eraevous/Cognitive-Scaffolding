- @ai-path: core.synthesis.summarizer
- @ai-source-file: summarizer.py
- @ai-role: synthesizer
- @ai-intent: "Retrieve related documents and return a consolidated summary with source links."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: medium
- @ai-risk-performance: "Multiple LLM calls per query increase latency and cost."

# Module: core.synthesis.summarizer
> Utility for linking similar insights and generating a single distillation.

### 🎯 Intent & Responsibility
- Use `Retriever` to fetch top-k related chunks for a query.
- Summarize each chunk via `summarize_text` and combine into one summary.
- Return summary text and list of source identifiers.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | query | str | Search text or question |
| 📥 In | retriever | Retriever | Retrieval interface |
| 📥 In | chunk_dir | Path | Directory holding text chunks |
| 📥 In | k | int | Number of matches to summarize |
| 📤 Out | result | Dict[str, List[str]] | `{summary: str, sources: [ids...]}` |

### 🔗 Dependencies
- `core.retrieval.retriever.Retriever`
- `core.llm.invoke.summarize_text`
- `core.utils.logger`

### 🗣 Dialogic Notes
- Designed for small sets of documents; large batches may exceed token limits.
- Agents may chain this after initial retrieval for deeper synthesis.

### 9 Pipeline Integration
- @ai-pipeline-order: normal
- **Coordination Mechanics:** Called by higher-level workflows after retrieval. May append outputs to Memory Bank.
- **Integration Points:** Downstream tools expect `{summary, sources}` dict. Upstream calls supply query text.
- **Risks:** Summarization quality depends on retrieved text; failures return empty summary.
