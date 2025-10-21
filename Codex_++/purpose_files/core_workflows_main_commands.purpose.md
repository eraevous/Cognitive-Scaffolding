# Module: core.workflows.main_commands
> Orchestrates document preparation, chunk planning, LLM summarisation, and metadata persistence for ingestion pipelines.

### 🎯 Intent & Responsibility
- Generate deterministic chunk plans for parsed documents, persisting them alongside stubs for reuse.
- Summarise chunk records via the configured prompt, merge outputs into document-level metadata, and validate the enriched payload.
- Maintain `chunk_map`, per-chunk summaries, and optional `cluster` annotations while respecting existing stub overrides.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | file_name | str | Raw path consumed by `upload_and_prepare` |
| 📥 In | parsed_name | Optional[str] | Override for parsed `.txt` output |
| 📥 In | name | str | Parsed filename passed to `classify`/`prepare_chunk_plan` |
| 📥 In | segmentation | Literal[`semantic`,`paragraph`] | Chunking strategy used for planning |
| 📥 In | chunk_records | Optional[List[Dict[str, Any]]] | Pre-computed chunk metadata (includes text + offsets) reused during classification |
| 📤 Out | metadata | Dict[str, Any] | `.meta.json` including schema-required fields plus `file_info`, `chunk_map`, `chunks`, and optional `cluster` |
| 📤 Out | chunk metadata | List[Dict[str, Any]] | `<name>.chunks.json` persisted for resume operations |
| 📤 Out | stub | Dict[str, Any] | `.stub.json` updated with structured `file_info` + `chunk_map` summary |

### 🔗 Dependencies
- `core.parsing.topic_segmenter` / `core.parsing.chunk_text` — build semantic or paragraph chunk sequences capped by the context window.
- `core.llm.invoke.summarize_text` — produce per-chunk JSON summaries.
- `core.metadata.merge.merge_metadata_blocks` — collapse chunk-level metadata into document-level aggregates.
- `core.metadata.schema.validate_metadata` — enforce enriched schema (chunk + cluster fields).
- `core.storage.upload_local` — seeds stubs consumed and rewritten during classification.

### ⚙️ AI-Memory Tags
- `@ai-assumes:` Chunk metadata includes `text` content; stub `chunk_map` mirrors the saved chunk plan.
- `@ai-breakage:` Segmentation mismatches between planning and embeddings will desynchronise chunk indices.
- `@ai-risks:` Stub merges can clobber LLM output; schema drift must be mirrored before validation.

### 🗣 Dialogic Notes
- `prepare_chunk_plan()` handles chunk caching, stub updates, and disk writes; `load_chunk_metadata()` reloads artefacts for resume workflows.
- `classify()` accepts optional chunk records, guarantees chunking for texts beyond `MAX_CHARS`, and attaches per-chunk metadata under `chunks`.
- Updated stubs expose structured `file_info` and `chunk_map`, enabling embedding/clustering stages to align on identical chunk layouts.
- Chunk records preserve order, char spans, and summary payloads, supporting retrieval and visualisation layers downstream.

### 9 Pipeline Integration
- @ai-pipeline-order: inverse
- **Coordination Mechanics:** `prepare_chunk_plan → summarize_records → merge_stubs → persist` ensures chunk artefacts exist before summarisation, keeping embeddings and clustering consistent.
- **Integration Points:** Results feed into `scripts.pipeline`, `core.embeddings.embedder` (chunk-aware embeddings), and clustering modules which append `cluster` info.
- **Risks:** Missing chunk metadata when resuming from later stages triggers regeneration and may diverge from stored embeddings; monitor schema alignment for `chunk_map`/`chunks`.
