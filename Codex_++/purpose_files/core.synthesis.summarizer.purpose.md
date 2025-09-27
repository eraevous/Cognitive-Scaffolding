- @ai-path: core.synthesis.summarizer
- @ai-source-file: summarizer.py
- @ai-role: synthesizer
- @ai-intent: "Combine retrieved document text and return a short summary using the base LLM summarizer."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.2
- @ai-risk-pii: low
- @ai-risk-performance: "Dependent on retrieval and LLM; large texts may exceed model limits."

# Module: core.synthesis.summarizer
> Lightweight aggregator summarizing multiple retrieved chunks into a single paragraph.

### 🎯 Intent & Responsibility
- Query `Retriever` for each document ID and collect associated text.
- Send combined text to `summarize_text` from `core.llm.invoke`.
- Return only the `summary` field from the parsed response.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | doc_ids | Iterable[str] | Document identifiers stored in FAISS index |
| 📥 In | retriever | Retriever | Retrieval interface for chunk text |
| 📤 Out | summary | str | Combined summary text |

### 🔗 Dependencies
- `core.retrieval.retriever.Retriever`
- `core.llm.invoke.summarize_text`
- `typing` utilities

### 🗣 Dialogic Notes
- `summarize_documents` gracefully handles missing text; empty retrieval yields empty summary.
- Designed for chaining with `Retriever` and future `Memory` modules as part of insight synthesis pipelines.
- Available via `from core.synthesis import summarize_documents` for package-level access.

### 9 Pipeline Integration
- **Coordination Mechanics:** Accepts document IDs from search steps; output feeds into higher-level synthesizers or reporting agents.
- **Integration Points:** Upstream `Retriever.query`; downstream `FrameStore` for memory injection or CLI summarization commands.
- **Risks:** Large combined text may hit token limits; consider chunking in future versions.
