# Module: core.config
> Centralized configuration management for filesystem paths, remote service credentials, and runtime pipeline constants.

### 🎯 Intent & Responsibility
- Abstract and unify configuration loading across the codebase.
- Support environment-portable access to local filesystem paths and remote service credentials.
- Serve as the canonical source of truth for all directory structures and cloud service access patterns.

### 📥 Inputs & 📤 Outputs
| Direction | Name             | Type      | Brief Description                                            |
|-----------|------------------|-----------|--------------------------------------------------------------|
| 📥 In     | path_config.json  | JSON file | Project-specific directory structure for raw, parsed, etc.   |
| 📥 In     | remote_config.json| JSON file | Cloud configuration including S3, Lambda, OpenAI keys, etc.  |
| 📤 Out    | PathConfig        | object    | Path object with resolved root, raw, parsed, metadata, etc.  |
| 📤 Out    | RemoteConfig      | object    | Remote object with S3 bucket, region, prefixes, API keys     |

### 🔗 Dependencies
- `pathlib`, `json` – File I/O and path handling
- `core.config.path_config.PathConfig`
- `core.config.remote_config.RemoteConfig`

### ⚙️ AI-Memory Tags
- `@ai-assumes:` Configuration files exist and are valid JSON.
- `@ai-breakage:` Changing config schema (e.g., removing `prefixes` or `root`) breaks loading.
- `@ai-risks:` Silent fallback to default paths can lead to environment misalignment; missing config keys will throw at runtime.

### 🗣 Dialogic Notes
- `get_path_config()` and `get_remote_config()` provide cached access, reloadable via `force_reload=True`.
- Both `PathConfig` and `RemoteConfig` enforce structure but can be extended to support `.env`, CLI args, or dynamic reloading.
- This system separates runtime configuration concerns from hardcoded constants, enabling safe parallel use across local and cloud environments.
