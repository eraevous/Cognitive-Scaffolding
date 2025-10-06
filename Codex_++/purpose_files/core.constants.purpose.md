# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: core.constants
- @ai-source-file: constants.py
- @ai-role: constants
- @ai-intent: "Expose shared constants for storage prefixes, schema defaults, and error messaging."
- @ai-version: 0.3.0
- @ai-generated: true
- @human-reviewed: false
- @schema-version: 0.3
- @ai-risk-pii: none
- @ai-risk-performance: "Static definitions only."
- @ai-dependencies: pathlib
- @ai-used-by: core.configuration.path_config, core.storage.*, core.metadata.schema, core.utils.budget_tracker
- @ai-downstream: repo-wide modules referencing default prefixes & schema paths

## Module Summary
`core.constants` centralizes immutable values that multiple subsystems share—S3 directory prefixes, metadata schema location, and reusable error templates. Trace A consolidation converts the metadata schema constant into a fully-resolved `Path`, ensuring every consumer inherits the same absolute path without embedding literals.

### Output Schema
| Name | Type | Description |
| --- | --- | --- |
| DEFAULT_S3_PREFIXES | Dict[str, str] | Canonical prefix map for S3-backed storage (raw, parsed, stub, metadata). |
| DEFAULT_METADATA_SCHEMA_PATH | Path | Absolute metadata schema resolved via `Path.resolve(strict=False)`. |
| ERROR_* constants | str | Standardized error message templates for configuration + storage failures. |

### Coordination Mechanics
- Acts as the single source for schema path resolution; `PathConfig` and `validate_schema_path` read `DEFAULT_METADATA_SCHEMA_PATH` instead of redefining literals.
- Error templates feed into validation modules (`core.metadata.schema`) and storage code paths (`core.storage.upload_local`).
- S3 prefix defaults seed both CLI workflows and background workers via `core.config` and remote configuration.

### Integration Notes
- All Trace A configuration consumers indirectly rely on this module when computing resolved schema paths.
- `core.configuration.config_registry` ensures environment overrides still converge on the same default path when no custom schema provided.
- Changes here should trigger Drift review because they affect ingestion, retrieval, and storage simultaneously.

### Risks & Mitigations
- **Path drift:** Resolving the schema path with `strict=False` avoids raising when files are absent; downstream validation still checks existence.
- **Inconsistent prefixes:** Keeping S3 defaults centralized prevents CLI vs. server mismatches.
