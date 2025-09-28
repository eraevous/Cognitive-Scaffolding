# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

- @ai-path: core.configuration.config_registry
- @ai-role: config_cache
- @ai-intent: "Cache configuration singletons while validating metadata schema overrides."
- @schema-version: 0.2
- @ai-generated: true
- @human-reviewed: false
- @ai-risk-integration: medium
- @ai-risk-drift: medium

## 🎯 Purpose & Responsibilities
Provide memoized access to `PathConfig` and `RemoteConfig` while coordinating override inputs for configuration files and the metadata schema. Incorporates schema validation so downstream agents always receive an absolute, existing path or a logged fallback to the packaged default.

## 📤 Outputs (Structured)
| Export | Type | Description |
| --- | --- | --- |
| `configure(*, path_config_path, remote_config_path, metadata_schema_path)` | `Callable[..., None]` | Registers file overrides and invalidates caches; metadata schema overrides live on the configure closure instead of module globals. |
| `get_path_config(force_reload=False)` | `Callable[[bool], PathConfig]` | Returns cached `PathConfig`; reloads when overrides change or schema validation produces a new absolute path. |
| `get_remote_config(force_reload=False)` | `Callable[[bool], RemoteConfig]` | Returns cached `RemoteConfig` pointing at optional override or default JSON. |
| `validate_schema_path(path)` | `Callable[[Path], Path]` | Normalizes and verifies schema paths, logging warnings and falling back to packaged defaults when missing. |
| `path_config` | `Optional[Path]` | Current pointer to the path configuration JSON file. |
| `remote_config` | `Optional[Path]` | Current pointer to the remote configuration JSON file. |

## 🔄 Coordination Mechanics
- Maintains `_path_instance` and `_remote_instance` caches, enabling idempotent retrieval across repeated agent invocations.
- Schema overrides are stored on the `configure` function, avoiding additional module-level globals while keeping override scope explicit.
- `_resolve_schema_candidate` prioritizes configure override → environment variable (`METADATA_SCHEMA_PATH`) → packaged default; `validate_schema_path` ensures the resulting path exists or logs a warning before falling back.
- `get_path_config` compares the cached schema path with the validated result to decide whether re-instantiation is required, enforcing stability unless overrides change.

## 🔗 Integration Points
- Upstream: `core.config` sets default config file locations and may call `configure` for environment-driven overrides; tests and CLI utilities also exercise override hooks.
- Downstream: ingestion, retrieval, and export agents request cached configs via `get_path_config`/`get_remote_config`; metadata validation flows depend on the verified schema path.
- Collaborates with `core.configuration.path_config` for object construction and `core.constants.DEFAULT_METADATA_SCHEMA_PATH` for fallback.

## 🌐 Ecosystem Anchoring
- @ai-used-by: orchestrator/executor agents coordinating ingestion, remote sync, and metadata validation.
- @ai-downstream: PurposeWeaver and DriftDiff use consistent cached values to detect configuration drift; logging integrates with observability agents to surface warnings when overrides fail validation.
- Strengthens Run cadence by reusing validated config objects while providing Drift cadence hooks (configure + warnings) for intentional overrides.

## ⚠️ Risks & Mitigations
- @ai-risk-cache: medium — stale caches mitigated by invalidation on configure calls and schema-path comparisons in `get_path_config`.
- @ai-risk-schema: low — warnings trigger when schema files are missing and packaged fallback preserves backward compatibility.

## ✅ Validation Notes
- `tests/test_config_registry_schema_override.py` covers default resolution, environment override, missing-file fallback, and guard ensuring `path_config.json` lacks a `schema` key.
- Broader configuration behavior remains under `pytest` suites that instantiate pipeline configs.
