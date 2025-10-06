@ai-intent: Capture Trace A schema-config consolidation decisions
@ai-role: memory_architect
@ai-cadence: drift
@ai-risk-architecture: medium (config drift touches every pipeline)

## Context
- Completed audit of modules consuming `get_path_config` / `configure`; migrated imports to `core.configuration.*` and removed inline schema literals.
- Introduced `validate_schema_path` to centralize fallback behavior and ensure warnings surface once per process.
- DEFAULT_METADATA_SCHEMA_PATH now resolves to an absolute `Path` via `.resolve(strict=False)` to avoid surprises in air-gapped runs.

## Trade-offs & Rationale
- Opted for sentinel-based override reset in `config_registry.configure` to support `configure(path_config_path=None)` semantics without breaking legacy callers.
- Added CLI regression harness using Typer runner to prove cached schema reuse without invoking the heavy pipeline; keeps tests fast while covering integration cadence.
- Document drift guard rails implemented via `tests/test_doc_drift.py`; scope limited to refreshed modules to avoid destabilizing legacy docs.

## Follow-ups
- Consider regenerating `ast_deps.csv` after major refactors so drift guard remains trustworthy at larger scale.
- Evaluate extracting a shared CLI bootstrap helper (per prior intent) once other pipelines adopt Trace A config contract.
