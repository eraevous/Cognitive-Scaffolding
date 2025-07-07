# Module: core.workflows.main_commands
> Orchestrates full document classification pipeline—parsing, summarization, metadata validation, and S3 integration—via Claude-based LLM workflows.

### 🎯 Intent & Responsibility
- Coordinate document ingestion, classification, and metadata generation.
- Dynamically route input through chunked or standard summarization based on content size and format.
- Validate and merge output into `.meta.json`, locally or on S3.

### 📥 Inputs & 📤 Outputs
| Direction | Name             | Type              | Brief Description                                                                    |
|-----------|------------------|-------------------|---------------------------------------------------------------------------------------|
| 📥 In     | file_name         | str               | Raw input file path (PDF, DOCX, etc.)                                                |
| 📥 In     | parsed_name       | Optional[str]     | Custom filename for parsed `.txt` version                                            |
| 📥 In     | name              | str               | Name of parsed file (e.g., `foo.txt`)                                                |
| 📥 In     | segmentation      | str               | "semantic" or "paragraph" segmentation strategy |
| 📤 Out    | metadata          | dict              | Structured JSON metadata saved locally or uploaded to S3                             |

### 🔗 Dependencies
- `core.llm.summarize_text` – for Claude-based document classification
- `core.parsing.chunk_text` – for breaking up long documents
- `core.metadata.schema` – for metadata validation
- `core.metadata.merge` – for combining chunk-level summaries
- `core.storage.s3_utils` – for metadata upload to S3
- `core.config.{path_config, remote_config}` – for paths and cloud config

### ⚙️ AI-Memory Tags
- `@ai-assumes:` LLM summarization output conforms to expected metadata schema.
- `@ai-breakage:` Chunking strategy or Lambda output structure changes can cause downstream merging to fail.
- `@ai-risks:` Stub merging may overwrite key fields unless preemptively managed.

### 🗣 Dialogic Notes
- `classify()` chooses summarization strategy based on size and chatlog heuristics.
- Supports optional `segmentation` choice to use semantic or paragraph boundaries.
- `pipeline_from_upload()` provides a single-call ingestion-to-metadata interface.
- Works with either local-only or hybrid S3-local workflows.
- Meant to decouple CLI and backend logic, enabling reuse in batch processing or UIs.
