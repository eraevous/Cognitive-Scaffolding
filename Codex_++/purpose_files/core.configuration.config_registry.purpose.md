# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: core.configuration.config_registry
- @ai-source-file: config_registry.py
- @ai-role: config_registry
- @ai-intent: "Cache and expose path + remote configuration objects with safe overrides."
- @ai-version: 0.4.0
- @ai-generated: true
- @human-reviewed: false
- @schema-version: 0.3
- @ai-risk-pii: none
- @ai-risk-performance: "Negligible — lazily loads JSON once per process."
- @ai-dependencies: core.configuration.path_config, core.configuration.remote_config, os, pathlib
- @ai-used-by: core.config, cli.*, scripts.pipeline, core.embeddings.embedder, core.retrieval.retriever
- @ai-downstream: core.metadata.schema, gui.chat_gui, core.workflows.main_commands

## Module Summary
The registry centralizes configuration loading and caching. It tracks the current JSON file locations, allows overrides via `configure`, and exposes singleton instances for `PathConfig` and `RemoteConfig`. Trace A consolidation introduced default-path reset semantics and ensures `.resolve(strict=False)` is applied to all overrides.

### IO Contracts
| Channel | Name | Type | Description |
| --- | --- | --- | --- |
| 📥 In | path_config_path | Path \| str \| None | Optional override for path config file; `None` resets to default JSON. |
| 📥 In | remote_config_path | Path \| str \| None | Optional override for remote config file; `None` resets to default JSON. |
| 📤 Out | PathConfig | PathConfig | Cached filesystem configuration (schema, directories, feature flags). |
| 📤 Out | RemoteConfig | RemoteConfig | Cached remote settings (API keys, S3 prefixes). |

### Schema Resolution
- Delegates to `PathConfig.from_file` which leverages `validate_schema_path` for default schema fallback.
- Maintains `_DEFAULT_*` path constants resolved with `.expanduser().resolve(strict=False)` to avoid brittle relative paths.
- Resetting overrides with `configure(path_config_path=None)` clears the cached object and rehydrates from defaults, ensuring deterministic schema usage across repeated calls.

### Coordination Mechanics
- Acts as the configuration nexus for CLI commands, pipelines, and long-lived services via module-level singletons.
- Works with `core.config` shim to maintain backwards compatibility while pointing to Trace A modules.
- Relies on `pathlib.Path` for normalization and is safe to invoke from multi-threaded contexts thanks to simple module-level caching.

### Integration Notes
- Accessed by embedding, retrieval, metadata validation, storage, and GUI modules for consistent configuration state.
- Tests patch `get_path_config` to inject temporary directories; the new reset semantics keep caches deterministic between tests.
- CLI guardrails now depend on this registry rather than embedding schema literals.

### Risks & Mitigations
- **Stale caches:** `force_reload=True` path ensures updates propagate; `configure(None)` clears overrides explicitly.
- **Invalid overrides:** `.resolve(strict=False)` combined with try/except fallback yields default configs when files are missing.
