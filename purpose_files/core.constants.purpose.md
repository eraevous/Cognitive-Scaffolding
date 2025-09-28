# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

- @ai-path: core.constants
- @ai-role: shared_config
- @ai-intent: "Publish canonical constants for storage prefixes, packaged schema assets, and reusable error templates."
- @schema-version: 0.3
- @ai-generated: true
- @human-reviewed: false
- @ai-risk-performance: low
- @ai-risk-pii: low

## 🎯 Purpose & Responsibilities
Consolidate static configuration used across core modules: bucket prefixes, local schema defaults, and shared error messages. Ensures every agent references the same packaged metadata schema path (`DEFAULT_METADATA_SCHEMA_PATH`) resolved relative to the module directory for portability across execution contexts.

## 📤 Outputs (Structured)
| Name | Type | Description |
| --- | --- | --- |
| `DEFAULT_S3_PREFIXES` | `Dict[str, str]` | Canonical bucket subfolder prefixes for `raw`, `parsed`, `stub`, `metadata`. |
| `DEFAULT_S3_DOWNLOAD_PREFIX` | `str` | Default prefix applied when downloading S3 artifacts. |
| `DEFAULT_METADATA_SCHEMA_PATH` | `Path` | Absolute path to the packaged JSON schema (computed via `Path(__file__).resolve().parent / "configuration" / "metadata_schema.json"`). |
| `ERROR_*` constants (11 variants) | `str` templates | Preformatted error messages for schema, config, tokenizer, prompt, and S3 failures. |

## 🔄 Coordination Mechanics
- Modules import constants at load time; no runtime mutation occurs, supporting deterministic behavior during Run cadence.
- Schema constant is consumed by `config_registry.validate_schema_path` and `PathConfig` to anchor fallback resolution.
- Error templates expect `.format(...)` substitution to inject context (e.g., `{path}`, `{spec}`).

## 🔗 Integration Points
- Upstream: `core.configuration.{config_registry,path_config}`, `core.config`, metadata validation utilities, and storage helpers rely on these constants for defaults and messaging.
- Downstream: CLI output, logging subsystems, and orchestrated agents (e.g., BudgetTracker, PurposeWeaver) surface error templates to users.

## 🌐 Ecosystem Anchoring
- @ai-used-by: executor agents orchestrating ingestion, parsing, metadata validation, and storage sync.
- @ai-downstream: Observability/risk agents leverage consistent error text to detect schema/config mismatches.
- Complements environment-driven overrides by supplying baseline values when `.env` or configure hooks are absent.

## ⚠️ Risks & Mitigations
- @ai-risk-drift: medium — adding new error messages in modules without updating this hub may reintroduce duplication; mitigate with review checklist referencing this module.
- @ai-risk-integration: low — exports are immutable constants.

## ✅ Validation Notes
- Exercised indirectly via unit tests that depend on `DEFAULT_METADATA_SCHEMA_PATH` (e.g., `tests/test_config_registry_schema_override.py`) and pipeline tests verifying error messaging.
