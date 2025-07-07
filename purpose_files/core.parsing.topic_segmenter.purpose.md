- @ai-path: core.parsing.topic_segmenter
- @ai-source-file: topic_segmenter.py
- @ai-role: analysis.utility
- @ai-intent: "Detect topic shifts in text using UMAP + HDBSCAN over window embeddings."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: low
- @ai-risk-performance: "Embedding and clustering can be slow on long documents."

# Module: core.parsing.topic_segmenter
> Identify topical boundaries in documents with density-based clustering.

### 🎯 Intent & Responsibility
- Slide a fixed-size window over tokenized text and embed each slice.
- Reduce embedding dimensions with UMAP.
- Cluster windows via HDBSCAN; boundaries form when cluster IDs change.
- Provide optional parameter hooks for UMAP/HDBSCAN configuration.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | text | str | Raw text to segment |
| 📥 In | window_tokens | int | Token count for each embedding window |
| 📥 In | step_tokens | int | Step size between window starts |
| 📥 In | cluster_method | str | Clustering algorithm; currently only `"hdbscan"` |
| 📥 In | model | str | Embedding model name |
| 📤 Out | segments | List[Dict[str, Any]] | Segment dicts with `text`, `start`, `end`, `cluster_id` |

### 🔗 Dependencies
- `tiktoken`, `umap-learn`, `hdbscan`
- `core.embeddings.embedder.embed_text`
- `core.utils.logger.get_logger`

### 🗣 Dialogic Notes
- Noise points (`cluster_id = -1`) simply propagate as separate segments.
- Future versions may support additional clustering methods or heuristics.
