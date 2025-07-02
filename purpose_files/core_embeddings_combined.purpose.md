# Module: core.embeddings
> Generate and load vector embeddings from textual data (parsed, raw, summaries, metadata) for downstream clustering.

### 🎯 Intent & Responsibility
- Generate semantic document embeddings using OpenAI embedding models.
- Load embeddings from JSON into doc ID list and NumPy matrix for clustering workflows.

### 📥 Inputs & 📤 Outputs
| Direction | Name         | Type               | Brief Description                                                |
|-----------|--------------|--------------------|------------------------------------------------------------------|
| 📥 In     | method       | Literal[str]       | Source text selection: `"parsed"`, `"summary"`, `"raw"`, `"meta"` |
| 📥 In     | source_dir   | Path (optional)    | Directory to pull text or metadata from (auto-selected by method) |
| 📥 In     | model        | str                | OpenAI model used to generate embeddings (default: `text-embedding-3-small`) |
| 📥 In     | embedding_path | Path              | Path to existing JSON file with `{doc_id: vector}` format         |
| 📤 Out    | embeddings   | Dict[str, List[float]] | Document ID to vector mapping                                    |
| 📤 Out    | doc_ids      | List[str]          | Ordered list of document identifiers                             |
| 📤 Out    | X            | np.ndarray         | 2D array of embeddings for clustering                            |
| 📤 Out    | JSON file    | Path               | Serialized embedding output (`rich_doc_embeddings.json`)         |

### 🔗 Dependencies
- `openai` – Embedding model API
- `json`, `numpy`, `pathlib` – Data handling and persistence
- `core.config.config_registry` – To load user-defined paths and credentials

### ⚙️ AI-Memory Tags
- `@ai-assumes:` Metadata contains summaries; paths are set correctly in config.
- `@ai-breakage:` Method label mismatch, API key failures, or malformed `.meta.json` will break generation.
- `@ai-risks:` API costs may be high for large document sets; text truncation not enforced.

### 🗣 Dialogic Notes
- The embedding generation adapts based on the method—"summary" and "meta" pull from JSON metadata, while "parsed"/"raw" use file text directly.
- JSON output is a lightweight, interoperable format suitable for direct clustering use.
- A future enhancement could batch texts for API efficiency or allow token truncation thresholds to be configured.
