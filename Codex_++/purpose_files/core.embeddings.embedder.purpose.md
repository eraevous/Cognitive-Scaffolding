# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: core.embeddings.embedder
- @ai-source-file: embedder.py
- @ai-role: embedder
- @ai-intent: "Create OpenAI embeddings for documents, chunks, and ad-hoc queries while tracking spend."
- @ai-version: 0.4.0
- @ai-generated: true
- @human-reviewed: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: "OpenAI batching mitigates API round-trips but remains network bound."
- @ai-dependencies: core.configuration.config_registry, core.parsing.chunk_text, core.parsing.semantic_chunk, core.utils.budget_tracker, core.utils.openai_retry, core.vectorstore.faiss_store, hashlib, json, numpy, openai, pathlib, tiktoken
- @ai-used-by: scripts.pipeline, cli.embed, core.retrieval.retriever
- @ai-downstream: core.vectorstore.faiss_store, core.retrieval.retriever, cli.pipeline

## Module Summary
The embedder module encapsulates all embedding generation paths. It caches the OpenAI client, manages tokenizer lookups, enforces Trace A schema resolution through `PathConfig`, and persists vectors + chunk metadata for FAISS ingestion. Chunking strategies span simple text windows and semantic segmentation, enabling downstream retrieval quality.

### IO Contracts
| Channel | Name | Type | Description |
| --- | --- | --- | --- |
| 📥 In | source_dir | Path \| None | Directory containing text or metadata payloads for embedding. |
| 📥 In | method | Literal["parsed","summary","raw","meta"] | Source text selector for embedding generation. |
| 📥 In | segment_mode | bool \| None | Toggle semantic chunking; defaults to `PathConfig.semantic_chunking`. |
| 📥 In | model | str | Embedding model to request from OpenAI; informs FAISS index dimension. |
| 📥 In | chunk_dir | Path \| None | Optional override for chunk artifact directory. |
| 📤 Out | vectors | List[List[float]] | Embedding vectors persisted via `FaissStore`. |
| 📤 Out | id_map | Dict[str, str] | Mapping between FAISS integer ids and document or chunk identifiers. |
| 📤 Out | chunk_files | List[Path] | JSON chunk payloads written when semantic segmentation enabled. |

### Schema Resolution
- Uses `core.configuration.config_registry.get_path_config` to acquire cached paths and schema metadata.
- `PathConfig` applies `validate_schema_path`, guaranteeing schema lookups survive missing overrides and remain reproducible across CLI invocations.
- All vector + chunk outputs live under `paths.vector`, aligning retrieval and clustering flows.

### Coordination Mechanics
- Budget control: `core.utils.budget_tracker` enforces estimated spend per request.
- Client bootstrap: `core.configuration.config_registry.get_remote_config` supplies API keys (via cached remote config).
- Chunk orchestration: `core.parsing.chunk_text` (windowing) and `core.parsing.semantic_chunk` (topic-aware segmentation) feed the embedding loop.
- Persistence: `core.vectorstore.faiss_store` writes FAISS indices, while `hashlib` ensures deterministic chunk identifiers.
- Tokenizer: `tiktoken` encodes inputs to respect `MAX_EMBED_TOKENS` constraints.

### Integration Notes
- Entry point for ingestion pipeline (`scripts.pipeline.generate_embeddings`) and CLI embed workflows.
- Supplies embeddings to `core.retrieval.retriever` and clustering routines.
- Shares Trace A configuration contract with CLI + workflow modules—no inline schema literals remain after consolidation.

### Risks & Mitigations
- **Rate limits / cost spikes:** budget tracker halts requests before spend overrun, and OpenAI calls are wrapped in exponential backoff so batches pause instead of failing when 429s occur.
- **Schema drift:** reliance on `PathConfig` ensures metadata directories align with validated schema path.
- **Large documents:** long inputs automatically chunked and averaged to avoid OpenAI token limits.
