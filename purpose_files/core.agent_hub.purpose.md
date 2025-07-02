- @ai-path: core.agent_hub
- @ai-source-file: agent_hub.py
- @ai-role: logic
- @ai-intent: "Spawn and manage cooperative agent sessions sharing a common retriever."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: medium
- @ai-risk-performance: "Concurrent agent calls can be costly if not budgeted."

# Module: core.agent_hub
> Minimal orchestration layer for multi-agent RAG workflows.

### 🎯 Intent & Responsibility
- Instantiate agent sessions based on role definitions and tool sets.
- Provide shared access to a `Retriever` for context gathering.
- Step each agent in a loop until tasks are complete.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | role | str | Agent role name (e.g., Synthesizer) |
| 📥 In | retriever | Retriever | Retrieval interface for context |
| 📤 Out | response | str | Agent-generated text or tool calls |

### 🔗 Dependencies
- `core.retrieval.retriever.Retriever`
- `openai` (for now) via `core.llm`
- `anyio` (future for async orchestration)

### 🗣 Dialogic Notes
- Initial roles include **Synthesizer**, **Associative Thinker**, **Insight Aggregator**, and **Amplifier**.
- Budget tracking hooks will abort loops if monthly cost exceeds configured cap.
