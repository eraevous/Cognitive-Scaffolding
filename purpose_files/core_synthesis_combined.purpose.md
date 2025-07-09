# Module: core.synthesis
> Tools for document-level synthesis and insight linking.

### 🎯 Intent & Responsibility
- Summarize retrieved text using OpenAI models.
- Consolidate related documents into single distilled outputs.
- Provide simple interfaces for higher-level workflows to request aggregated insights.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | query | str | Search or question text |
| 📥 In | retriever | Retriever | Retrieval component |
| 📤 Out | summary_data | Dict[str, List[str]] | Combined summary and source IDs |

### 🔗 Dependencies
- `core.llm.invoke.summarize_text`
- `core.retrieval.retriever.Retriever`
- `core.utils.logger`

### ⚙️ AI-Memory Tags
- `@ai-assumes:` LLM APIs accessible and retriever configured.
- `@ai-breakage:` Missing chunks or API failures yield empty summaries.
- `@ai-risks:` Summaries may surface sensitive content; use memory guardrails when needed.

### 🗣 Dialogic Notes
- Designed as a thin synthesis layer feeding more complex agents or UIs.
- Will integrate with Memory Bank for persistent insight injection.
