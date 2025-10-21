- @ai-path: core.parsing.semantic_chunk    
- @ai-source-file: semantic_chunk.py    
- @ai-role: retrieval.segmentation    
- @ai-intent: "Segment text into retrieval-ready spans that preserve brief digressions and evolving meaning, preventing majority-topic washout. Clustering and UMAP/Spectral remain optional strategies rather than the core identity of the module."    
- @ai-version: 0.2.0    
- @ai-generated: true    
- @ai-verified: false    
- @human-reviewed: false    
- @schema-version: 0.2    
- @ai-risk-pii: low    
- @ai-risk-performance: "Batching controls cost; adaptive clustering or DR only used when beneficial."    

# Module: core.parsing.semantic_chunk

> Produce retrieval-ready text chunks that preserve small, meaningful digressions and avoid flattening evolving topics over time. Default behavior favors **lightweight change-point splitting**; UMAP/Spectral/HDBSCAN clustering is available in adaptive mode for more complex documents.

---

### 🎯 Intent & Responsibility

- Slide 256-token windows over the text with stride 128 to create overlapping semantic slices.    
- Embed windows in **batches** using `embed_text_batch` to control API cost.    
- **Default (coarse) mode**: detect topic shifts via cosine distance between adjacent window embeddings and split on meaningful changes — ensuring **brief digressions are preserved**.    
- **Adaptive mode**: optionally apply UMAP + Spectral (with HDBSCAN fallback) to merge/shape segments, while **never allowing majority-topic clusters to erase small spans**.    
- Merge or split spans using simple and transparent heuristics (`min_chunk_tokens`, cosine deltas, and `max_chunk_tokens`) to avoid both over-fragmentation and context-flattening.    
- Re-embed final chunks in batches for downstream retrieval and vector indexing.    

---

### 📥 Inputs & 📤 Outputs

|Direction|Name|Type|Brief Description|
|---|---|---|---|
|📥 In|text|str|Raw document text to segment|
|📥 In|window_tokens|int|Token count for each window (default 256)|
|📥 In|step_tokens|int|Token stride between windows (default 128)|
|📥 In|mode|str|`"coarse"` (default), `"adaptive"`, or `"protect-digressions"`|
|📥 In|cluster_method|str|(adaptive mode only) `"spectral"` or `"hdbscan"`|
|📤 Out|chunks|List[Dict[str, Any]]|Chunks with `text`, `embedding`, `start`, `end`, `topic_change_score`, `cluster_id?`, and metadata|

---

### 🔗 Dependencies

- `tiktoken` for tokenization    
- `core.embeddings.embedder.embed_text` and `embed_text_batch`    
- (adaptive mode only) `umap-learn`, `sklearn.cluster.SpectralClustering`, `hdbscan`    

---

### 🗣 Dialogic Notes

- **Philosophy:** preserve high-value digressions and evolving meaning; avoid “majority-topic washout.”    
- Clustering is a _tool_, not the identity of the module — **downstream embedding + clustering remain the workhorses of semantic organization.**    
- Short documents must **never error** and should return a single coherent chunk.    
- Change-point splitting based on cosine deltas provides predictable, retrieval-first behavior.    
- Metadata (`topic_change_score`, provenance, window_ids) supports downstream organization, audits, and knowledge-graph building.    
- Optional adaptive clustering can merge over-fragmented spans, but must not erase brief semantic shifts.    

---

### 9 Pipeline Integration

- @ai-pipeline-order: inverse    
- **Coordination:** invoked when `segment_mode=True`; produces chunk spans and embeddings for vector search.    
- **Integration Points:** Feeds the core retrieval engine, metadata analyzers, clustering pipelines, and future semantic organization workflows.    
- **Risks:** Over-fragmentation hurts readability; over-aggregation flattens meaning. Defaults favor coarse, stable, retrieval-friendly chunks that downstream systems may further refine or cluster.
