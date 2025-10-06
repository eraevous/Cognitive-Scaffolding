# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: core.retrieval.retriever
- @ai-source-file: retriever.py
- @ai-role: retriever
- @ai-intent: "Rank vector-store hits for one or more natural-language queries."
- @ai-version: 0.3.0
- @ai-generated: true
- @human-reviewed: false
- @schema-version: 0.3
- @ai-risk-pii: low
- @ai-risk-performance: "Embedding + FAISS search bounded by query batch size."
- @ai-dependencies: core.configuration.config_registry, core.embeddings.embedder, core.logger.get_logger, core.vectorstore.faiss_store, json, numpy, pathlib
- @ai-used-by: core.workflows.main_commands, cli.pipeline, scripts.pipeline
- @ai-downstream: core.synthesis.summarizer, gui.chat_gui

## Module Summary
Retriever centralizes semantic search against the FAISS index. It resolves storage locations via the shared `PathConfig` cache, infers embedding dimensions, and exposes helpers for single query, multi-query, and file-based retrieval. Result aggregation can collapse chunk-level hits back to document-level summaries for downstream synthesis loops.

### IO Contracts
| Channel | Name | Type | Description |
| --- | --- | --- | --- |
| 📥 In | store | FaissStore \| None | Optional pre-built index; defaults to vector path from `PathConfig`. |
| 📥 In | model | str \| None | Embedding model override; auto-inferred from FAISS index dimension when omitted. |
| 📥 In | chunk_dir | Path \| None | Directory containing cached chunk text; defaults to `<vector>/chunks` when present. |
| 📥 In | texts | Iterable[str] | Query strings handled by `query_multi`. |
| 📤 Out | ranked | List[Tuple[str, float]] | Ranked `(doc_id, score)` pairs for top-k hits. |
| 📤 Out | enriched | List[Tuple[str, float, str]] | Ranked triples including chunk text when `return_text=True`. |

### Schema Resolution
- Delegates filesystem discovery to `core.configuration.config_registry.get_path_config`.
- `PathConfig` internally calls `validate_schema_path`, ensuring cached schema paths stay reproducible even when overrides are missing.
- Vector index (`mosaic.index`), `id_map.json`, and optional chunk cache resolve under `paths.vector`.

### Coordination Mechanics
- Embedding provider: `core.embeddings.embedder` (uses same registry + schema contract).
- Vector store: `core.vectorstore.faiss_store.FaissStore` handles search, exposes `index.d` for dimension inference.
- Logging: `core.logger.get_logger` surfaces cadence + model auto-detection to observability feeds.
- Aggregation: merges multi-query hits, supports chunk aggregation for the Synthesizer agent.

### Integration Notes
- Upstream call sites: CLI (`cli.pipeline.run_all`), scripted ingestion (`scripts.pipeline.run_pipeline`), and workflow orchestrators (`core.workflows.main_commands`).
- Downstream: Summarization (`core.synthesis.summarizer`) and GUI retrieval experiences consume ranked outputs.
- Maintains compatibility with Trace A schema consolidation by never embedding schema literals; all configuration flows through cached registries.

### Risks & Mitigations
- **Index drift:** Embedding model mismatch mitigated by dimension auto-detection and logging.
- **Missing chunk text:** Gracefully returns empty strings when chunk files absent; aggregation still returns ranking.
- **Config drift:** Reliance on `PathConfig` ensures shared schema + vector roots even across CLI/worker contexts.
