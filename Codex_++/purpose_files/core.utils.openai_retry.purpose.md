# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

- @ai-path: core.utils.openai_retry
- @ai-source-file: core/utils/openai_retry.py
- @ai-role: resilience
- @ai-intent: "Provide shared exponential backoff logic for OpenAI requests across the stack."
- @schema-version: 0.2
- @ai-version: 0.1.0
- @ai-generated: true
- @human-reviewed: false
- @ai-risk-performance: low
- @ai-risk-operations: "Centralized retry policy ensures consistent handling of rate limits."

# Module: core.utils.openai_retry
> Consolidated retry helper that pauses and retries OpenAI calls when rate limits or temporary 429 errors occur.

### 🎯 Intent & Responsibility
- Offer `retry_with_exponential_backoff` that wraps any callable interacting with OpenAI.
- Normalize logging of rate-limit errors so operators see pause durations and attempt counts.
- Provide configurable retry/backoff parameters while defaulting to conservative pauses.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | operation | Callable[[], T] | Zero-argument callable invoking an OpenAI API request. |
| 📥 In | retries | int | Maximum number of attempts before surfacing the exception (default 5). |
| 📥 In | base_delay | float | Initial delay before the first retry in seconds (default 2.0). |
| 📥 In | backoff_factor | float | Multiplier applied to the delay after each retry (default 2.0). |
| 📥 In | retriable_status_codes | Iterable[int] | HTTP status codes treated as retryable beyond `RateLimitError` (default `(429,)`). |
| 📥 In | logger | logging.Logger \| None | Optional logger used for resilience telemetry. |
| 📤 Out | result | T | The successful return value from ``operation``. Raises the last exception if retries exhausted. |

### 🔗 Dependencies
- `openai.RateLimitError`, `openai.APIStatusError` to detect throttling and HTTP 429 responses.
- `core.logger.get_logger` for structured logs when caller omits a logger.
- Standard library `time.sleep` for pause management.

### 🤝 Integration Points
- Invoked by `core.llm.invoke`, `core.embeddings.embedder`, GUI chat, and clustering labelers to guard OpenAI calls.
- Downstream agents (retriever, summarizer, chat UI) receive consistent retry semantics via this helper.
- Coordinates with `BudgetTracker` indirectly by allowing cost checks to pass once before shared retries occur.

### 🗣 Dialogic Notes
- @ai-used-by: core.llm.invoke, core.embeddings.embedder, gui.chat_gui, core.clustering.labeling, core.clustering.cluster_helpers
- @ai-coordination: Sits inside LLM/embedding call loops; respects Run cadence by pausing instead of skipping items when throttled.
- @ai-risks: Excessive retries on permanent failures are avoided by surfacing the last error after bounded attempts.
