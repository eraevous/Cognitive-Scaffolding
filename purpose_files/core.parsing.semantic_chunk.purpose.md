- @ai-path: core.parsing.semantic_chunk
- @ai-source-file: semantic_chunk.py
- @ai-role: analysis.utility
- @ai-intent: "Cluster window embeddings via UMAP/Spectral to produce labeled semantic chunks."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: low
- @ai-risk-performance: "Relies on embedding model and clustering; heavy docs may incur cost."

# Module: core.parsing.semantic_chunk
> Produce topic-aware text chunks by embedding overlapping windows and clustering them.

### 🎯 Intent & Responsibility
- Slide 256-token windows over the text with stride 128.
- Embed each window using `text-embedding-3-large`.
- Reduce dimensions with UMAP and cluster via Spectral Clustering (HDBSCAN fallback).
- Merge adjacent windows with identical cluster IDs into final chunks.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | text | str | Raw document text to segment |
| 📥 In | window_tokens | int | Token count for each window (default 256) |
| 📥 In | step_tokens | int | Token stride between windows (default 128) |
| 📥 In | cluster_method | str | "spectral" or "hdbscan" |
| 📤 Out | chunks | List[Dict[str, Any]] | Chunk objects with `text`, `embedding`, `topic`, `start`, `end`, `cluster_id` |

### 🔗 Dependencies
- `tiktoken` for tokenization
- `umap-learn`, `sklearn.cluster.SpectralClustering`, `hdbscan`
- `core.embeddings.embedder.embed_text`

### 🗣 Dialogic Notes
- Works best when text length >> window size, giving enough context for clustering.
- Future improvements might use HDBSCAN or heuristics to auto-select cluster count.

### 9 Pipeline Integration
- @ai-pipeline-order: inverse
- **Coordination Mechanics:** Called by `core.embeddings.embedder` when `segment_mode=True`; outputs are written to disk and embedded for vector search.
- **Integration Points:** Results feed into `core.retrieval.retriever`, `core.synthesizer` workflows, and TokenMap Analyzer.
- **Risks:** Overclustering can fragment context, while excessive window count drives GPU and API cost.
