# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

- @ai-path: core.configuration.path_config
- @ai-role: filesystem_router
- @ai-intent: "Resolve root-relative storage folders and metadata schema locations for orchestrated agents."
- @schema-version: 0.2
- @ai-generated: true
- @human-reviewed: false
- @ai-risk-integration: medium
- @ai-risk-drift: medium

## 🎯 Purpose & Responsibilities
Translate on-disk hints (JSON config, environment variables, direct kwargs) into resolved `Path` objects that downstream pipelines rely on for ingest, parsing, metadata, and schema validation. Guarantees the metadata schema path always resolves to an absolute location, defaulting to the packaged artifact when overrides are absent or invalid.

## 📤 Outputs (Structured)
| Export | Type | Description |
| --- | --- | --- |
| `PathConfig.root` | `Path` | Absolute project root anchoring relative paths. |
| `PathConfig.raw` | `Path` | Directory for raw source documents. |
| `PathConfig.parsed` | `Path` | Directory containing normalized `.txt` extracts. |
| `PathConfig.metadata` | `Path` | Directory for generated `.meta.json` metadata. |
| `PathConfig.output` | `Path` | Directory for user-facing exports (plots, summaries). |
| `PathConfig.vector` | `Path` | Directory for embedding/vector artifacts. |
| `PathConfig.schema` | `Path` | Absolute metadata schema path resolved from override → env (`METADATA_SCHEMA_PATH`) → packaged default. |
| `PathConfig.semantic_chunking` | `bool` | Toggle used by chunking agents for semantic segmentation. |
| `PathConfig.from_file(config_path, *, schema_path)` | `Callable[[Union[str, Path]], PathConfig]` | Loader merging JSON hints with optional schema override supplied by the registry. |

## 🔄 Coordination Mechanics
- Participates in the configuration cache managed by `core.configuration.config_registry`; `get_path_config()` instantiates `PathConfig` once per override set, ensuring idempotent reuse across orchestration loops.
- `_resolve_path_relative_to_root` normalizes relative folders under the chosen root while leaving absolute overrides untouched, keeping CLI-driven runs portable.
- Schema selection honors explicit overrides, then checks `METADATA_SCHEMA_PATH`, and finally lands on `DEFAULT_METADATA_SCHEMA_PATH`, mirroring Trace B simplicity while guarding against missing files via registry validation.

## 🔗 Integration Points
- Upstream: `core.config` seeds defaults and environment-derived paths before delegating to `config_registry`.
- Downstream: ingest/export pipelines, metadata validators (`core.metadata.schema`), vector tooling, and retriever agents consume the resolved directories and schema path.
- Shares error messaging contract with `core.constants.ERROR_PATH_RESOLVE_FAILURE` for consistent exception text across agents.

## 🌐 Ecosystem Anchoring
- @ai-used-by: executor agents orchestrating ingestion, parsing, retrieval, export, and evaluation flows.
- @ai-downstream: schema validators, chunking controllers, and RAG retrievers that expect consistent directory and schema locations.
- Aligns with PurposeWeaver memory by exposing deterministic fields that other agents can diff to detect drift during Drift cadence.

## ⚠️ Risks & Mitigations
- @ai-risk-schema: medium — invalid overrides could misroute schema validation; mitigated through registry-level `validate_schema_path` warnings and packaged fallback.
- @ai-risk-io: low — raising `ValueError` with context prevents silent path resolution failures.

## ✅ Validation Notes
- Covered by `tests/test_config_registry_schema_override.py` (default, environment override, missing-file fallback, JSON guard against `schema` key).
- Additional regression coverage stems from existing pipeline tests ensuring directories resolve correctly across CLI invocations.
