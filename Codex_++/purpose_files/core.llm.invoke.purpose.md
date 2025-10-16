# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

- @ai-path: core.llm.invoke
- @ai-source-file: core/llm/invoke.py
- @ai-role: summarizer
- @ai-intent: "Issue templated prompts to OpenAI chat completions and parse JSON summaries for standard and chatlog documents."
- @schema-version: 0.2
- @ai-generated: true
- @human-reviewed: false
- @ai-risk-pii: medium
- @ai-risk-performance: "OpenAI latency; budget tracker enforcement may raise if limits hit."

# Module: core.llm.invoke
> Format prompt templates and relay them to OpenAI before parsing structured summary payloads.

### 🎯 Intent & Responsibility
- Provide `load_prompt` for retrieving summarization prompt templates from disk.
- Offer `run_openai_completion` that enforces BudgetTracker checks and executes chat completions.
- Expose `summarize_text` to build prompts (including overrides) and return parsed JSON summaries.
- Respect `RemoteConfig` for API keys and propagate doc_type-specific behavior (`standard` vs `chatlog`).

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | prompt_name | str | Filename stem for prompt template (`load_prompt`). |
| 📥 In | prompt | str | Fully rendered prompt sent to OpenAI (`run_openai_completion`). |
| 📥 In | text | str | Document or chatlog content to summarize (`summarize_text`). |
| 📥 In | doc_type | Literal["standard", "chatlog"] | Selects base prompt variant. |
| 📥 In | model | str | OpenAI model id (`gpt-4`, `gpt-4o`). |
| 📥 In | prompt_override | Optional[str] | Custom template with `{text}` placeholder. |
| 📥 In | config | RemoteConfig | Supplies `openai_api_key`; lazily loaded if omitted. |
| 📤 Out | summary | Dict[str, Any] | JSON-decoded dict containing keys like `summary`, `topics`, optional `category`. |

### 🔗 Dependencies
- `tiktoken` for token estimation to feed `BudgetTracker`.
- `openai.OpenAI` chat completions client.
- `core.configuration.remote_config.RemoteConfig` for credentials.
- `core.utils.budget_tracker.get_budget_tracker` for spend enforcement.
- Prompt templates stored under `core/llm/prompts`.

### 🤝 Integration Points
- Consumed by `core.synthesis.summarizer.summarize_text` orchestration.
- Upstream CLI flows (`cli.pipeline`, `cli.embed`) indirectly call through summarization pipeline.
- Shares spend metrics with global BudgetTracker used by embeddings and retrieval agents.

### 🗣 Dialogic Notes
- @ai-role: executor
- @ai-used-by: core.synthesis.summarizer
- @ai-downstream: core.workflows.insurance_verification, cli.pipeline
- Coordination: participates in agent loops where retriever output feeds summarizer before response synthesis; `summarize_text` must emit JSON conforming to downstream schema expectations for section/topic summaries.
