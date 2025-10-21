# Module: scripts.pipeline
> Drives the ingestion pipeline end-to-end: upload, chunk planning, classification, embeddings, clustering, and logging.

### 🎯 Intent & Responsibility
- Provide a resumable orchestration layer over upload, chunking, classification, embedding, and clustering stages.
- Persist detailed run logs under `PathConfig.root/logs`, emitting concise console updates while retaining diagnostics in file.
- Bridge chunk metadata from `core.workflows.main_commands` into embeddings and clustering so downstream artefacts stay aligned.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | input_dir | Path | Root directory containing raw documents to ingest |
| 📥 In | chunked | bool | Force chunking even when under the context window |
| 📥 In | overwrite | bool | Reclassify documents that already have `.meta.json` |
| 📥 In | method | str | Embedding source text (`parsed`, `summary`, `raw`, `meta`) |
| 📥 In | segmentation | str | Chunk segmentation strategy (`semantic`/`paragraph`) |
| 📥 In | start_from | str | Stage to resume from (`upload`, `chunk`, `classify`, `embed`, `cluster`) |
| 📥 In | cluster_method | str | Clustering algorithm (`hdbscan`, `spectral`, …) |
| 📥 In | label_model | str | OpenAI model for cluster labeling |
| 📤 Out | logs | File & stdout | Timestamped log file under `<root>/logs/` plus concise console progress |
| 📤 Out | artefacts | Files | Updated stubs, chunk metadata, `.meta.json`, embeddings JSON, cluster exports |

### 🔗 Dependencies
- `core.configuration.config_registry.get_path_config` for environment-scoped directories.
- `core.workflows.main_commands` (upload, chunk planning, classification) to produce metadata and chunk records.
- `core.embeddings.embedder.generate_embeddings` for vector generation.
- `core.embeddings.loader`, `core.clustering.algorithms`, `core.clustering.labeling`, `core.clustering.export` for clustering/visuals.
- `core.metadata.schema.validate_metadata` to ensure cluster annotations keep metadata valid.

### ⚙️ AI-Memory Tags
- `@ai-assumes:` Chunk metadata includes `text`; embeddings file is JSON mapping doc/chunk ids to vectors.
- `@ai-breakage:` Missing optional dependencies (`umap`, `hdbscan`) gracefully skip clustering but leave previous outputs untouched.
- `@ai-risks:` Starting from later stages without up-to-date chunk metadata may regenerate segments—warn in logs.

### 🗣 Dialogic Notes
- Stage helpers (`_run_upload_stage`, `_run_chunk_stage`, `_run_classification_stage`, `_run_embedding_stage`, `_run_cluster_stage`) encapsulate retry-friendly logic.
- `_setup_pipeline_logger()` records full diagnostics to disk; console output stays succinct per stage.
- `_load_chunk_cache()` allows resumes from `classify`/`embed`/`cluster` without re-running earlier steps, relying on saved chunk artefacts.
- Clustering attaches labels back into metadata via the new `cluster` field and exports summary CSV/plot assets.

### 9 Pipeline Integration
- @ai-pipeline-order: inverse
- **Coordination Mechanics:** Upload → chunk plan → classify → embed → cluster; each stage reads/writes artefacts consumed by the next and can be resumed midstream via `start_from`.
- **Integration Points:** Feeds chunk records to the embedder, embeddings to clustering, and writes cluster info back to `.meta.json`.
- **Risks:** Skipped stages rely on artefacts produced earlier; manual edits or deletions can desynchronise embeddings/clusters from metadata.
