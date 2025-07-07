- @ai-path: core.parsing.topic_segmenter
- @ai-source-file: topic_segmenter.py
- @ai-role: analysis.utility
- @ai-intent: "Provide a simple wrapper over semantic_chunk_text for topic segmentation."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: low
- @ai-risk-performance: low

# Module: core.parsing.topic_segmenter
> Minimal interface to segment text into topic-coherent chunks.

### 🎯 Intent & Responsibility
- Offer a lightweight function `segment_text` that calls `semantic_chunk_text`.
- Serve as stable entrypoint if future segmentation backends change.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | text | str | Document text to segment |
| 📤 Out | chunks | List[str] | Segmented text blocks |

### 🔗 Dependencies
- `core.parsing.semantic_chunk_text`

### 🗣 Dialogic Notes
- Acts as abstraction layer; more advanced segmentation can swap in later.
