- @ai-path: core.parsing.topic_segmenter
- @ai-source-file: topic_segmenter.py
- @ai-role: analysis.utility
- @ai-intent: "Detect topic shifts in text using UMAP + HDBSCAN over window embeddings with paragraph fallback.."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: low
- @ai-risk-performance: "Uses embedding calls; cost scales with document size. Embedding and clustering can be slow on long documents."

# Module: core.parsing.topic_segmenter
> Simple wrapper combining `semantic_chunk_text` and paragraph chunking.
> Identify topical boundaries in documents to segment text into topic-coherent chunks and use density-based clustering.

### 🎯 Intent & Responsibility
- Run `semantic_chunk_text` to infer segment boundaries via embeddings.
- Fall back to `chunk_text` when only one segment is produced.
- Slide a fixed-size window over tokenized text and embed each slice.
- Reduce embedding dimensions with UMAP.
- Cluster windows via HDBSCAN; boundaries form when cluster IDs change.
- Provide optional parameter hooks for UMAP/HDBSCAN configuration.

=======
| 📥 In | text | str | Raw text to segment |
| 📥 In | window_tokens | int | Token count for each embedding window |
| 📥 In | step_tokens | int | Step size between window starts |
| 📥 In | cluster_method | str | Clustering algorithm; currently only `"hdbscan"` |
| 📥 In | model | str | Embedding model name |
| 📤 Out | segments | List[Dict[str, Any]] | Segment dicts with `text`, `start`, `end`, `cluster_id` |
| 📤 Out | chunks | List[str] | List of topic-aligned text segments |

### 🔗 Dependencies
- `tiktoken`, `umap-learn`, `hdbscan`
- `core.embeddings.embedder.embed_text`
- `core.utils.logger.get_logger`
- `core.parsing.semantic_chunk_text`
- `core.parsing.chunk_text`

### 🗣 Dialogic Notes
- Noise points (`cluster_id = -1`) simply propagate as separate segments.
- Future versions may support additional clustering methods or heuristics
- Designed for embedding generation when `segment_mode` is enabled.
- Keeps segments small and coherent for improved retrieval granularity.
