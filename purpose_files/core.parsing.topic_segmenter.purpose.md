- @ai-path: core.parsing.topic_segmenter
- @ai-source-file: topic_segmenter.py
- @ai-role: analysis.utility
- @ai-intent: "Generate topic-based segments using semantic clustering with paragraph fallback."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: low
- @ai-risk-performance: "Uses embedding calls; cost scales with document size."

# Module: core.parsing.topic_segmenter
> Simple wrapper combining `semantic_chunk_text` and paragraph chunking.

### 🎯 Intent & Responsibility
- Run `semantic_chunk_text` to infer segment boundaries via embeddings.
- Fall back to `chunk_text` when only one segment is produced.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | text | str | Raw document text to segment |
| 📥 In | model | str | Embedding model for semantic chunking |
| 📤 Out | chunks | List[str] | List of topic-aligned text segments |

### 🔗 Dependencies
- `core.parsing.semantic_chunk_text`
- `core.parsing.chunk_text`

### 🗣 Dialogic Notes
- Designed for embedding generation when `segment_mode` is enabled.
- Keeps segments small and coherent for improved retrieval granularity.
