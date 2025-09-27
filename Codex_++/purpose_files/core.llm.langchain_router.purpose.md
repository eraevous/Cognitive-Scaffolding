# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

- @ai-path: core.llm.langchain_router
- @ai-source-file: core/llm/langchain_router.py
- @ai-role: adapter
- @ai-intent: "Route LLM calls to local Mistral 7B or Amazon Bedrock models through LangChain and MCP interfaces."
- @schema-version: 0.2
- @ai-generated: true
- @human-reviewed: false
- @ai-risk-pii: high
- @ai-risk-performance: "Local models may respond slowly; Bedrock incurs network latency."

# Module: core.llm.langchain_router
> Unified gateway translating generic generation requests into LangChain runs against local or Bedrock-hosted models.

### 🎯 Intent & Responsibility
- Provide a single `generate` function accepting chat-style messages and model metadata.
- Normalize responses into `{text, tokens_used, provider}`.
- Expose MCP-compatible streaming hooks and cost logging via `BudgetTracker`.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | messages | List[Dict[str, str]] | Conversation history `{role, content}` |
| 📥 In | model | str | Model identifier (`mistral-7b`, `bedrock:anthropic.claude`) |
| 📥 In | config | RemoteConfig | Credentials, runtime flags |
| 📤 Out | result | Dict[str, Any] | `{text: str, tokens_used: int, provider: str}` |

### 🔗 Dependencies
- `langchain`
- `boto3` for Amazon Bedrock
- local model runtime (`ctransformers`, `ollama`, etc.)
- `core.utils.budget_tracker`

### 🤝 Integration Points
- Used by `core.parsing.insurance_verification` for field extraction.
- Accessible to `core.agent_hub` sessions for conversational reasoning.
- Shares cost metrics with global `BudgetTracker`.

### 🗣 Dialogic Notes
- @ai-used-by: core.parsing.insurance_verification
- @ai-downstream: core.workflows.insurance_verification
- @ai-role: architect
