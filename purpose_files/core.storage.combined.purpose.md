# Module: core.storage
> Unified document and metadata I/O system for local and S3-based pipelines, with validation and format handling.

### 🎯 Intent & Responsibility
- Save, load, and manage documents and metadata locally or via AWS S3.
- Validate metadata schemas before persistence.
- Enable ingestion workflows across local dev and cloud deployments.
- Support stub creation, raw/parsed upload, and extraction-based transformation.

### 📥 Inputs & 📤 Outputs
| Direction | Name            | Type         | Brief Description                                                         |
|-----------|------------------|--------------|---------------------------------------------------------------------------|
| 📥 In     | file_path        | str          | Path to input file for upload or parsing                                  |
| 📥 In     | metadata         | dict         | Metadata dictionary to validate and persist                               |
| 📥 In     | config           | RemoteConfig | S3 credentials, bucket, and prefix metadata                               |
| 📤 Out    | json_file        | Path         | Saved local or S3-hosted JSON metadata                                    |
| 📤 Out    | parsed_text_path | Path         | Filepath of parsed `.txt` content                                         |
| 📤 Out    | upload_success   | bool         | Indicates successful upload/processing outcome                            |

### 🔗 Dependencies
- `boto3`, `json`, `pathlib`, `os`, `shutil`
- `core.config.remote_config`, `core.config.path_config`
- `core.parsing.extract_text`
- `core.metadata.schema` – for metadata validation

### ⚙️ AI-Memory Tags
- `@ai-assumes:` Metadata adheres to schema; AWS credentials configured correctly.
- `@ai-breakage:` Changes to metadata field names, prefix structures, or parsing output format.
- `@ai-risks:` Race conditions if concurrent uploads write to same S3 keys; missing metadata fields silently break downstream stages.

### 🗣 Dialogic Notes
- Local and S3 paths mirror each other for consistency in hybrid pipelines.
- Stub generation preserves doc state even without full LLM or summary.
- AWS integration is modular: switching regions, buckets, or client config is straightforward but must respect `RemoteConfig` expectations.
- Future improvements could include async support, retry logic, and CLI wrappers for ingestion orchestration.
