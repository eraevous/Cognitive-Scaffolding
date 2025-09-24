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
- Batch short texts with `embed_text_batch` so overlapping windows do not spam the API.
- Insert vectors into `FaissStore` for later retrieval or clustering.
- Store a JSON map linking hashed IDs to document filenames.
- When segmenting, persist chunk metadata with embeddings for downstream search.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | source_dir | Path | Directory containing text or `.meta.json` files |
| 📥 In | method | Literal[str] | How to select text (`"parsed"`, `"raw"`, `"summary"`, `"meta"`) |
| 📥 In | model | str | OpenAI model name |
| 📥 In | segment_mode | bool | Overrides config to use topic segmentation when True; defaults to `PathConfig.semantic_chunking` |
| 📥 In | chunk_dir | Path (optional) | Where to write chunk text when `segment_mode` is enabled |
| 📤 Out | rich_doc_embeddings.json | JSON file of `{doc_id: vector}` |
| 📤 Out | mosaic.index | FAISS index persisted to disk |
| 📤 Out | id_map.json | Map of int IDs to original filenames |
| 📤 Out | chunks/*.json | Per-chunk files with text, embedding, and metadata |

### 🔗 Dependencies
- `openai`, cached `OpenAI` client instance, and `tiktoken`
- `numpy` for array math and averaging long-text embeddings
- `core.vectorstore.faiss_store` for index management
- `core.config.config_registry` for path lookups and remote API keys
- `core.utils.logger` for logging
- `core.utils.budget_tracker.get_budget_tracker` for request budgeting

### 🗣 Dialogic Notes
- Document IDs are hashed via Blake2b and **masked to 63 bits** (`0x7FFF_FFFF_FFFF_FFFF`) so FAISS can store them as signed `int64` without overflow.
- Embeddings for long documents are averaged from token chunks, while short inputs are batched per request to cut run time.
- A module-level OpenAI client and encoding cache prevent repeated session setup when thousands of chunks are processed.
- FAISS index is recreated on each run if dimensions mismatch.
- Topic segmentation import is lazy to avoid circular dependencies with
  `semantic_chunk`.
- If `segment_mode` is omitted, `PathConfig.semantic_chunking` determines whether
  to segment via topics or simple paragraphs.
- Estimated OpenAI cost is checked via `BudgetTracker`; batched calls debit budgets by total token count before dispatch.

### 9 Pipeline Integration
- @ai-pipeline-order: inverse
- **Coordination Mechanics:** Embedding generation triggers semantic chunking when enabled and writes vectors to `FaissStore`. Index files are then consumed by `core.retrieval.retriever`.
- **Integration Points:** Downstream usage includes Retriever search, Synthesizer summarization loops, and TokenMap Analyzer for chunk metrics.
- **Risks:** Excessive chunk count inflates API spend and FAISS index size; GPU memory may limit batch processing.
