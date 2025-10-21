# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: core.parsing.semantic_chunk
- @ai-source-file: semantic_chunk.py
- @ai-role: retrieval.segmentation
- @ai-intent: "Default to lightweight, retrieval-first change-point splitting that preserves micro-digressions while keeping adaptive clustering optional and non-destructive."
- @ai-version: 0.3.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.3
- @ai-risk-pii: low
- @ai-risk-performance: "Batch embedding respects BudgetTracker; adaptive clustering guarded by small-N clamps and optional dependencies."
- @ai-dependencies: core.embeddings.embedder, core.logger, numpy, sklearn.cluster.SpectralClustering, umap-learn?, hdbscan?, hashlib

# Module: core.parsing.semantic_chunk

> Segment documents into retrieval-ready spans without flattening narrative flow. The module defaults to **coarse change-point detection** and only invokes **adaptive clustering** (UMAP → Spectral/HDBSCAN) when explicitly requested.

---

### 🎯 Intent & Responsibility

- Tokenize with `tiktoken` when available, falling back to a character tokenizer so short docs never error.
- Slide configurable windows (`window_tokens`, `step_tokens`) across the document and batch-embed them with `embed_text_batch`, ensuring BudgetTracker accounting through the shared embedder client.
- Compute cosine deltas between adjacent windows to mark topic change-points (`change_point_cosine_tau`); enforce a `max_chunk_tokens` guard so majority topics cannot wash out digressions.
- Merge leftover micro spans only when boundaries were length-induced, preserving change-point cuts even when they are small (`min_chunk_tokens`).
- Re-embed finalized chunk texts in batches, emit provenance (`window_ids`, optional `source_doc_id`), and hash each chunk (`sha256`) for downstream audits.
- Adaptive mode (opt-in) assigns cluster IDs via UMAP + Spectral or HDBSCAN with small-N clamps and noise normalization; clustering never rewrites chunk text.

---

### 📥 Inputs & 📤 Outputs

|Direction|Name|Type|Brief Description|
|---|---|---|---|
|📥 In|text|str|Raw document text to segment|
|📥 In|model|str|Embedding model passed to `embed_text_batch` (default `text-embedding-3-small`) |
|📥 In|window_tokens|int|Token count per sliding window (default 256)|
|📥 In|step_tokens|int|Stride between windows (default 128)|
|📥 In|mode|Literal["coarse","adaptive"]|Default `"coarse"`; adaptive enables clustering metadata|
|📥 In|cluster_method|Literal["spectral","hdbscan"]|Adaptive-mode clustering backend (noise mapped to cluster `0`)|
|📥 In|change_point_cosine_tau|float|Cosine-distance threshold for change-point splits (default 0.28)|
|📥 In|min_chunk_tokens|int|Minimum token span before post-merge (default 120)|
|📥 In|max_chunk_tokens|int|Upper bound per chunk to avoid flattening (default 1200)|
|📥 In|batch_size|int \| None|Optional cap for batch embedding payloads|
|📥 In|source_doc_id|str \| None|Propagated provenance identifier for downstream stores|
|📤 Out|chunks|List[Dict[str, Any]]|Each chunk includes: `text: str`, `embedding: List[float]`, `start: int`, `end: int`, `topic_change_score: float`, `cluster_id: Optional[int]`, `window_ids: List[int]`, `source_doc_id: Optional[str]`, `sha256: str`. `cluster_id` remains `None` in coarse mode.|

---

### 🔗 Dependencies & Coordination

- Embedding: `core.embeddings.embedder.embed_text_batch` (BudgetTracker-aware) with optional `embed_text` fallback for long payloads.
- Tokenization: `tiktoken` encodings when available; character tokenizer fallback ensures graceful degradation.
- Adaptive clustering: optional `umap-learn`, `sklearn.cluster.SpectralClustering`, and `hdbscan`; missing packages trigger coarse-mode fallback without raising.
- Logging: `core.logger.get_logger` surfaces boundary decisions for Drift reviews.
- Ecosystem anchors: outputs feed `core.parsing.topic_segmenter`, `core.embeddings.embedder.generate_embeddings`, retriever ingestion, and knowledge/audit tooling via `window_ids` + `sha256` hashes.

Coordination notes:
- Respects the **single ingestion pipeline** (`segment_mode=True`) by emitting chunk dictionaries that downstream vectorstore loaders accept verbatim.
- Shared embedder client + batch helpers prevent per-window API thrash and respect shared budget state.
- Change-point segmentation executes before any adaptive clustering, so downstream agents can rely on stable chunk IDs even when clustering metadata is absent.

---

### 🗣 Dialogic Notes & Risks

- **Scaffold, don’t solve:** chunking preserves evolving meaning; retrieval/clustering agents consume metadata for heavier semantic organization.
- Small-N guard: fewer than 3 windows return a single coherent chunk with zero topic-change score.
- Optional dependencies (UMAP/HDBSCAN) degrade gracefully; adaptive mode emits `cluster_id=None` when tooling is unavailable.
- Risks: excessive length guards can still over-fragment smooth prose; operators should tune `max_chunk_tokens` based on retrieval context. Budget overrun mitigated by batched embeddings and centralized BudgetTracker checks.
- Future enrichers (`emit_keywords`, `emit_entities`) can hook onto the returned metadata schema without disrupting current contracts.

---

### 9 Pipeline Integration

- @ai-pipeline-order: inverse
- **Coordination:** invoked by embedding workflows (`segment_mode=True`) and by higher-level parsers that surface digressions for retrieval-first knowledge graphs.
- **Integration Points:** feeds `core.retrieval.retriever`, metadata analyzers, summarizers, and future audit trails via the emitted hashes and window provenance.
- **Risks & Mitigations:** digressions are preserved because post-merge logic refuses to cross change-point boundaries; cluster metadata augments without rewriting text, preventing knowledge loss.
