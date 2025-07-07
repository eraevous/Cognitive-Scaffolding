- @ai-path: core.parsing.semantic_chunk
- @ai-source-file: semantic_chunk.py
- @ai-role: analysis.utility
- @ai-intent: "Segment text using embedding-based window clustering to infer topic boundaries."
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
- Sample small windows from text (e.g., 200 tokens sliding by 100).
- Embed each window with OpenAI and cluster vectors via KMeans.
- Detect boundaries where cluster assignment changes to yield semantic segments.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | text | str | Raw document text to segment |
| 📥 In | window_tokens | int | Size of sliding windows for sampling |
| 📥 In | step_tokens | int | Step between window starts |
| 📥 In | n_clusters | int | Number of clusters for KMeans |
| 📤 Out | chunks | List[str] | Topic-coherent text segments |

### 🔗 Dependencies
- `tiktoken` for tokenization
- `sklearn.cluster.KMeans`
- `core.embeddings.embedder.embed_text`

### 🗣 Dialogic Notes
- Works best when text length >> window size, giving enough context for clustering.
- Future improvements might use HDBSCAN or heuristics to auto-select cluster count.
