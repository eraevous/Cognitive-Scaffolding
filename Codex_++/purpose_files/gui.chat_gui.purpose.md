# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

- @ai-path: gui.chat_gui
- @ai-source-file: gui/chat_gui.py
- @ai-role: conversation_ui
- @ai-intent: "Provide a Streamlit-based interface for chatting with the configured OpenAI model."
- @schema-version: 0.2
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false

# Module: gui.chat_gui
> Minimal chat interface to converse with the OpenAI model defined in `RemoteConfig`.

### 🎯 Intent & Responsibility
- Render a Streamlit UI for user and assistant messages.
- Maintain conversation state in `st.session_state`.
- Send conversation to OpenAI via `run_openai_chat`, enforcing `BudgetTracker` limits.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | messages | List[Dict[str, str]] | Conversation history with `role` and `content` fields. |
| 📥 In | model | str | Model ID to use (default `gpt-4o`). |
| 📥 In | config | RemoteConfig | Provides API key for OpenAI access. |
| 📤 Out | updated_messages | List[Dict[str, str]] | Chat history appended with assistant reply. |

### 🔗 Dependencies
- `streamlit`
- `openai`, `tiktoken`, `core.utils.openai_retry`
- `core.config.config_registry.get_remote_config`
- `core.utils.budget_tracker.get_budget_tracker`

### 🗣 Dialogic Notes
- Launch with `streamlit run chat_gui.py`.
- Requires `src/core/config/remote_config.json` containing `openai_api_key`, loaded via `config_registry`.
- Designed for quick experiments; no retrieval or memory injection yet.

### 9 Pipeline Integration
- **Coordination Mechanics:** Standalone interface; loops via Streamlit callbacks.
- **Integration Points:** Could later integrate with `Retriever` or `FrameStore` for RAG workflows.
- **Risks:** Missing config still raises runtime errors; rate limits trigger exponential backoff instead of skipping chats.
