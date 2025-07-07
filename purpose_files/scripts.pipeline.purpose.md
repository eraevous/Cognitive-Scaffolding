    # Module: scripts.pipeline
> Orchestrates the full local-to-cloud document processing pipeline—upload, classification, and embedding—via a single CLI-executable function.

### 🎯 Intent & Responsibility
- Serve as a one-stop execution layer for the full LLM-powered pipeline.
- Ingest files from a local folder, route them through upload + parsing → classification → embedding stages.
- Handle optional chunked summarization and overwrite behavior for idempotent operation.

### 📥 Inputs & 📤 Outputs
| Direction | Name         | Type     | Brief Description                                                               |
|-----------|--------------|----------|----------------------------------------------------------------------------------|
| 📥 In     | input_dir     | Path     | Directory containing raw documents                                               |
| 📥 In     | chunked       | bool     | Whether to use paragraph-based chunking during classification                    |
| 📥 In     | overwrite     | bool     | Whether to reprocess files that already have a `.meta.json`                     |
| 📥 In     | method        | str      | Embedding source: `parsed`, `summary`, `raw`, or `meta`                         |
| 📤 Out    | stdout log    | str/log  | Upload, classification, and embedding progress per document                     |
| 📤 Out    | output files  | Files    | `.parsed.txt`, `.meta.json`, and `.embedding.json` per document (local or S3)   |

### 🔗 Dependencies
- `core.config.config_registry.get_path_config`
- `core.workflows.main_commands.{upload_and_prepare, classify}`
- `core.embeddings.embedder.generate_embeddings`

### ⚙️ AI-Memory Tags
- `@ai-assumes:` Parsed and metadata folders exist and are writable.
- `@ai-breakage:` Output format changes or schema shifts in `.meta.json` or embedding source text.
- `@ai-risks:` Skipping classification due to existing `.meta.json` could propagate stale metadata unless `overwrite=True`.

### 🗣 Dialogic Notes
- This is the operational entry point for batch processing; ideal for CLI runners, cron jobs, or one-off runs.
- Handles exceptions gracefully at each step; doesn’t halt pipeline on single failure.
- Embedding method can be aligned with downstream semantic search or classification heuristics.
- Could be expanded to support logging, dry-run mode, or parallel processing.
- When embeddings are generated, vectors are simultaneously added to the FAISS index for immediate searchability.
