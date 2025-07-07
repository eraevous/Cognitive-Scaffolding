- @ai-path: core.vectorstore.faiss_store
- @ai-source-file: faiss_store.py
- @ai-role: storage
- @ai-intent: "Persist and search embedding vectors using a FAISS index with ID mapping."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: low
- @ai-risk-performance: "Large indexes consume memory; retrieval speed depends on vector count."

# Module: core.vectorstore.faiss_store
> Lightweight wrapper around FAISS providing add/search and on-disk persistence.
> Embedding generation stores a JSON map of `{int_id: doc_id}` alongside the index for lookup.

### 🎯 Intent & Responsibility
- Manage an inner-product FAISS index keyed by document IDs.
- Provide `add(ids, vecs)`, `search(vec, k)`, and `persist()` methods.
- Load existing indexes from disk on initialization.
- Accepts a `dim` parameter and warns if a stored index exists with a different
  dimension.
- Numeric IDs are resolved back to filenames via `id_map.json` written by the embedding step.

### 📥 Inputs & 📤 Outputs
| Direction | Name  | Type | Brief Description |
|-----------|-------|------|-------------------|
| 📥 In | ids | List[int] | Unique identifiers for each vector |
| 📥 In | vecs | np.ndarray | 2D array of float32 vectors |
| 📥 In | vec | np.ndarray | Query vector for search |
| 📤 Out | results | List[Tuple[int, float]] | `(id, score)` pairs from search |
| 📤 Out | index_file | Path | Saved FAISS index on disk |

### 🔗 Dependencies
- `faiss` – vector index implementation
- `numpy` – numeric arrays
- `pathlib.Path` – file handling
- `core.utils.logger` – warns on dimension mismatches

### 🗣 Dialogic Notes
- Designed as a swap-in component for alternative stores like Qdrant or Milvus.
- Future enhancement: write-ahead log for crash-safe incremental indexing.
