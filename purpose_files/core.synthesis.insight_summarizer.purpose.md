# Module: core.synthesis.insight_summarizer
- @ai-path: core.synthesis.insight_summarizer
- @ai-source-file: insight_summarizer.py
- @ai-role: synthesizer
- @ai-intent: "Aggregate summaries from multiple documents and highlight shared insights."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: low
- @ai-risk-performance: "Multiple LLM calls may increase latency and cost."

> Utility functions that generate cross-document summaries to surface common themes.

### 🎯 Intent & Responsibility
- Summarize each document using `core.llm.invoke.summarize_text`.
- Combine individual summaries into a single overview linking related ideas.
- Provide a simple API for downstream pipelines to request insight linking.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | docs | List[str] | Raw text documents or segments |
| 📥 In | model | str | OpenAI model name for summarization |
| 📤 Out | summary | str | Consolidated overview of shared insights |

### 🔗 Dependencies
- `core.llm.invoke.summarize_text`

### 🗣 Dialogic Notes
- Intended as a lightweight synthesizer step after retrieval.
- Summaries are concatenated and re-summarized to produce a concise insight report.

### 9 Pipeline Integration
- @ai-pipeline-order: inverse
- **Coordination Mechanics:** Receives raw docs from Retriever or other modules. Outputs feed into Memory frames or downstream write-ups.
- **Integration Points:** Can be called by Livewire or CLI to synthesize search results. Works with `core.memory.frame_store` for persistence.
- **Risks:** Large document lists may exceed model context limits; ensure docs are pre-summarized when needed.
