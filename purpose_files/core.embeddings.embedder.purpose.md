# Module: core.embeddings.embedder
# @ai-path: core.embeddings.embedder
# @ai-source-file: embedder.py
# @ai-role: logic
# @ai-intent: "Generate document embeddings and persist them in a FAISS index."
# @ai-version: 0.1.0
# @ai-generated: true
# @ai-verified: false
# @human-reviewed: false
# @schema-version: 0.2
# @ai-risk-pii: medium

> Converts textual documents to embeddings and writes them to a FAISS index with a mapping of hashed document IDs.

### 🎯 Intent & Responsibility
- Create embeddings for parsed, raw, summary, or metadata text.
- Insert vectors into `FaissStore` for later retrieval or clustering.
- Store a JSON map linking hashed IDs to document filenames.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | source_dir | Path | Directory containing text or `.meta.json` files |
| 📥 In | method | Literal[str] | How to select text (`"parsed"`, `"raw"`, `"summary"`, `"meta"`) |
| 📥 In | model | str | OpenAI model name |
| 📥 In | segment_mode | bool | If true, split docs via `topic_segmenter` and embed each chunk |
| 📥 In | chunk_dir | Path (optional) | Where to write chunk text when `segment_mode` is enabled |
| 📤 Out | rich_doc_embeddings.json | JSON file of `{doc_id: vector}` |
| 📤 Out | mosaic.index | FAISS index persisted to disk |
| 📤 Out | id_map.json | Map of int IDs to original filenames |

### 🔗 Dependencies
- `openai`, `tiktoken`, `numpy`
- `core.vectorstore.faiss_store` for index management
- `core.config.config_registry` for path lookups
- `core.utils.logger` for logging

### 🗣 Dialogic Notes
- Document IDs are hashed via Blake2b and **masked to 63 bits** (`0x7FFF_FFFF_FFFF_FFFF`) so FAISS can store them as signed `int64` without overflow.
- Embeddings for long documents are averaged from token chunks.
- FAISS index is recreated on each run if dimensions mismatch.
- Topic segmentation import is lazy to avoid circular dependencies with
  `semantic_chunk_text`.
