- @ai-path: core.retrieval.retriever
- @ai-source-file: retriever.py
- @ai-role: logic
- @ai-intent: "Embed text queries and return top-k document filenames from the vector store."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: low
- @ai-risk-performance: "Embedding model calls incur latency and cost."

# Module: core.retrieval.retriever
> Unified interface for semantic search against the FAISS vector store.

### 🎯 Intent & Responsibility
- Convert query text to embeddings using the configured model.
 - Delegate search to `FaissStore` and return ranked document filenames using `id_map.json`.
- Provide an easy-to-mock layer for CLI and future agent use.
- Detect index dimension at init and switch embedding model accordingly.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | text | str | Search query text |
| 📥 In | k | int | Number of results to return |
| 📥 In | chunk_dir | Path (optional) | Directory holding text chunks for retrieval |
| 📥 In | return_text | bool (optional) | Include chunk text when `chunk_dir` is configured |
| 📤 Out | results | List[Tuple[str, float]] or List[Tuple[str, float, str]] | Matching IDs and scores, with text when requested |

### 🔗 Dependencies
- `core.embeddings.embedder.embed_text`
- `core.vectorstore.faiss_store.FaissStore`
- `numpy`
- `core.utils.logger`

### 🗣 Dialogic Notes
- Embedding model is configurable; defaults to OpenAI `text-embedding-3-small`.
- Agents will call this layer instead of accessing FAISS directly.
- When no model is specified, the retriever infers one by reading the FAISS index dimension.
- Uses `id_map.json` to translate FAISS integer IDs back to document filenames.
- When embeddings include chunk IDs (`doc_chunk01`), results may refer to those composite identifiers and `return_text` can load the chunk file if available.

### 9 Pipeline Integration
- @ai-pipeline-order: inverse
- **Coordination Mechanics:** Receives query embeddings from `embed_text` and consults `FaissStore`; optionally loads chunk text for Synthesizer steps.
- **Integration Points:** Results feed directly into the Synthesizer RAG loop and TokenMap Analyzer for token-level context alignment.
- **Risks:** Retrieval across many chunks may load large text blobs and increase latency; misaligned embeddings reduce search quality.
