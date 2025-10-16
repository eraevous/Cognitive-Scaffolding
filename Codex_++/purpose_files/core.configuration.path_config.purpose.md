# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: core.configuration.path_config
- @ai-source-file: path_config.py
- @ai-role: config_paths
- @ai-intent: "Resolve ingestion directories and metadata schema locations for all pipelines."
- @ai-version: 0.4.0
- @ai-generated: true
- @human-reviewed: false
- @schema-version: 0.3
- @ai-risk-pii: none
- @ai-risk-performance: "Negligible — pure path arithmetic."
- @ai-dependencies: core.constants.ERROR_PATH_RESOLVE_FAILURE, json, logging, os, pathlib
- @ai-used-by: core.configuration.config_registry, cli.pipeline, scripts.pipeline, core.embeddings.embedder, core.retrieval.retriever
- @ai-downstream: core.metadata.schema, core.storage.upload_local

## Module Summary
`PathConfig` encapsulates all filesystem roots required by the Trace A ingestion stack. It normalizes user overrides relative to a project root, validates the metadata schema path, and exposes convenience constructors for JSON configuration. The companion helper `validate_schema_path` guards against missing schema files while preserving reproducible defaults.

### IO Contracts
| Channel | Name | Type | Description |
| --- | --- | --- | --- |
| 📥 In | root | Path \| str \| None | Base directory used for relative path expansion. |
| 📥 In | raw/parsed/metadata/output/vector | Path \| str \| None | Optional overrides for specific storage folders. |
| 📥 In | schema | Path \| str \| None | Optional schema override validated via `validate_schema_path`. |
| 📥 In | semantic_chunking | bool | Feature flag toggling semantic chunk segmentation. |
| 📤 Out | PathConfig.root | Path | Absolute root directory. |
| 📤 Out | PathConfig.schema | Path | Resolved metadata schema path (always absolute + validated). |
| 📤 Out | PathConfig.vector | Path | Vector index + chunk artifact directory. |

### Schema Resolution
- Defaults to `core.constants.DEFAULT_METADATA_SCHEMA_PATH`, resolved with `Path.resolve(strict=False)`.
- `validate_schema_path` checks overrides, logs a warning when files are missing, and falls back to the default schema while keeping the cache warm.
- JSON deserialization via `PathConfig.from_file` now omits inline schema literals, aligning with Trace A consolidation.

### Coordination Mechanics
- Central feed into `core.configuration.config_registry`, ensuring CLI, workflows, and services consume the same cached instance.
- Logging via `core.logger` (transitively) documents fallback behavior for observability.
- Propagates semantic chunking flag to embedding + classification pipelines.

### Integration Notes
- Consumed during CLI path resolution (`cli.pipeline._resolve_paths`) and ingestion pipelines (`scripts.pipeline.run_pipeline`).
- Referenced by metadata validation (`core.metadata.schema.validate_metadata`) and storage helpers (`core.storage.upload_local`).
- Maintains compatibility with environment overrides defined in `core.config` while removing hard-coded schema paths.

### Risks & Mitigations
- **User typos:** `_resolve_path_relative_to_root` raises descriptive errors using `ERROR_PATH_RESOLVE_FAILURE`.
- **Missing schema files:** `validate_schema_path` logs a warning and reverts to the known-good default, preventing runtime crashes.
