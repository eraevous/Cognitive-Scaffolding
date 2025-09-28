# Module: core.config
> Centralizes environment-backed configuration, filesystem defaults, and compatibility exports for the legacy configuration helpers.

### 🎯 Intent & Responsibility
- Load `.env` variables via `python-dotenv` and expose normalized project settings (paths, S3 prefixes, AWS identifiers).
- Provide resolved `Path` objects for local directories (raw, parsed, metadata, output, organized) and configuration files.
- Re-export legacy configuration helpers (`PathConfig`, `RemoteConfig`, registry) while injecting environment-driven file locations.

### 📥 Inputs & 📤 Outputs
| Direction | Name                  | Type             | Brief Description |
|-----------|-----------------------|------------------|-------------------|
| 📥 In     | `.env` variables       | `Dict[str, str]` | Optional overrides for bucket names, prefixes, config file paths, and local dirs. |
| 📥 In     | `remote_config.json`   | JSON file        | Static fallback for AWS + S3 settings when env overrides are absent. |
| 📥 In     | `path_config.json`     | JSON file        | Static fallback for filesystem layout defaults. |
| 📤 Out    | `AWS_BUCKET_NAME`      | `Optional[str]`  | Bucket identifier consumed by storage + Lambda helpers. |
| 📤 Out    | `S3_PREFIXES`          | `Dict[str, str]` | Canonical prefixes for `raw`, `parsed`, `stub`, `metadata`. |
| 📤 Out    | `LOCAL_*_DIR`          | `Path`           | Resolved project directories (raw, parsed, metadata, output, organized). |
| 📤 Out    | `PATH_CONFIG_PATH`     | `Path`           | File path used by `PathConfig.from_file`. |
| 📤 Out    | `REMOTE_CONFIG_PATH`   | `Path`           | File path used by `RemoteConfig.from_file`. |
| 📤 Out    | `get_path_config()`    | `Callable[[], PathConfig]` | Cached accessor honoring environment overrides. |
| 📤 Out    | `get_remote_config()`  | `Callable[[], RemoteConfig]` | Cached accessor honoring environment overrides. |

### 🔗 Dependencies & Coordination
- `dotenv.load_dotenv` ensures `.env` is parsed before any registry loads.
- `core.configuration.config_registry.configure` receives resolved file paths and schema overrides to keep caches aligned.
- Downstream agents: storage (`core.storage.s3_utils`, `upload_s3`), metadata (`core.metadata.io`), clustering (`core.clustering.pipeline`), CLI upload/organize utilities, and Lambda invokers import these constants.
- Coordinates with `BudgetTracker` indirectly via shared environment context but maintains no counters.

### ⚙️ AI-Memory Tags & Risks
- `@ai-intent: central_environment_config`
- `@ai-role: orchestrator`
- `@ai-risks: env_drift` — Missing `.env` values fall back to repo defaults; misconfigured overrides propagate broadly.
- `@ai-assumes:` JSON configs remain alongside the module unless environment variables redirect them.

### 🗣 Dialogic Notes
- The module injects compatibility shims (`sys.modules['core.config.<legacy>']`) so legacy imports continue to work post-migration.
- Environment-relative paths resolve against the repo root to keep CLI ergonomics unchanged.
- S3 download prefix defaults to the `raw` prefix but can diverge via `S3_DOWNLOAD_PREFIX`.
- Future drift: consider validating prefix trailing slashes and surfacing warnings when `.env` supplies conflicting settings.
