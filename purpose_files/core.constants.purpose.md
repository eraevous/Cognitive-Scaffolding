# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

- @ai-path: core.constants
- @ai-role: shared_config
- @ai-intent: "Provide canonical constants (prefixes, schema defaults, error messages) for reuse across core modules."
- @schema-version: 0.2
- @ai-generated: true
- @human-reviewed: false
- @ai-risk-performance: low
- @ai-risk-pii: low

## 🎯 Purpose & Responsibilities
Centralize immutable strings and templates that multiple core modules reference. This avoids configuration drift for
S3 prefixes, schema filenames, and high-level error messages used throughout the ingestion and LLM workflows.

## 📤 Outputs (Structured)
| Name                                | Type                  | Description |
|-------------------------------------|-----------------------|-------------|
| `DEFAULT_S3_PREFIXES`               | `Dict[str, str]`      | Canonical bucket subfolder prefixes for `raw`, `parsed`, `stub`, `metadata`. |
| `DEFAULT_S3_DOWNLOAD_PREFIX`        | `str`                 | Default prefix applied when downloading S3 artifacts. |
| `DEFAULT_METADATA_SCHEMA_PATH`      | `str`                 | Relative path to the JSON schema for metadata validation. |
| `ERROR_*` constants (11 variants)   | `str` templates       | Preformatted error messages for schema, config, tokenizer, prompt, and S3 failures. |

## 🔄 Coordination Mechanics
- No runtime logic; modules import constants at load time to format error strings consistently.
- Message templates expect `.format(...)` substitution (e.g., `{path}`, `{spec}`, `{available}`) and should be filled before raising exceptions.
- Aligns with Run cadence modules (`executor` role) by preventing divergence in user-facing errors without extra synchronization.

## 🔗 Integration Points
- Upstream consumers: `core.config`, `core.configuration.{path_config,remote_config}`, `core.metadata.schema`, `core.storage.s3_utils`, `core.parsing.openai_export`, `core.llm.invoke`, `core.analysis.token_stats`.
- Downstream effects: surfaces identical messaging to CLI and logging layers, improving observability consistency for agents like `BudgetTracker` and GUI surfaces.

## 🌐 Ecosystem Anchoring
- @ai-used-by: executor agents that perform config loading, parsing, retrieval, and LLM invocation.
- @ai-downstream: logging infrastructure, CLI feedback loops, orchestration workflows in `core.workflows` and GUI prompts relying on coherent error messages.
- Complements `core.config` orchestrator role by supplying immutable defaults while leaving environmental overrides to `config_registry`.

## ⚠️ Risks & Mitigations
- @ai-risk-drift: Medium — adding new error messages in modules without updating this hub may reintroduce duplication. Mitigate via code review checklist referencing this module.
- @ai-risk-integration: Low — pure constant exports with no side effects.

## ✅ Validation Notes
- No runtime hooks; unit validation relies on importing constants where needed.
- Ensure placeholders in templates stay synchronized with calling code parameters during future edits.
