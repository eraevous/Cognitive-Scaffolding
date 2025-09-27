# Module: cli.combined
> Consolidated Typer CLI entrypoints for ingestion, classification, upload, clustering, embedding, and recovery operations.

### 🎯 Intent & Responsibility
- Serves as the unified command-line interface for orchestrating core document pipeline operations.
- Exposes functionality for file ingestion, classification, embedding, cluster analysis, metadata organization, and S3 interactions.

### 📥 Inputs & 📤 Outputs
| Direction | Name         | Type    | Brief Description                                      |
|-----------|--------------|---------|--------------------------------------------------------|
| 📥 In     | file_path     | Path    | Raw document to upload or classify                     |
| 📥 In     | directory     | Path    | Folder of documents to batch upload or ingest          |
| 📥 In     | method        | str     | Embedding source (summary, parsed, raw, etc.)          |
| 📥 In     | segmentation  | str     | "semantic" or "paragraph" segmentation for classification |
| 📥 In     | model         | str     | Model to use for clustering (e.g., GPT-4)              |
| 📥 In     | cluster_method| str     | Algorithm for clustering (e.g., hdbscan)               |
| 📤 Out    | metadata      | JSON    | Saved `.meta.json` with classification/summary         |
| 📤 Out    | organized_dir | Folder  | Output directory of categorized files and metadata     |
| 📤 Out    | embeddings    | JSON    | Document embedding vectors                             |
| 📤 Out    | s3_uploads    | S3      | Raw and parsed documents uploaded                      |
| 📤 Out    | chatgpt_texts | Folder  | Conversation transcripts from ChatGPT exports |

### 🔗 Dependencies
- `core.workflows.main_commands` – Orchestrates classification, upload, ingestion
- `core.clustering.clustering_steps` – Runs clustering + labeling
- `core.embeddings.embedder` – Generates embeddings from text
- `scripts.pipeline` – Runs the full ingestion pipeline
- `typer`, `pathlib`, `shutil`, `json` – CLI and I/O operations
- `core.config.config_registry` – Loads path configurations

### ⚙️ AI-Memory Tags (Structured Cognitive Anchors)
- `@ai-assumes:` Valid parsed file and metadata formats, consistent file naming conventions.
- `@ai-breakage:` Changes to path configs, stub formats, or pipeline step interfaces will break CLI commands.
- `@ai-risks:` Multiple Typer apps mean command routing must remain carefully structured; state errors (e.g., missing metadata) can silently corrupt workflows.

### 🗣 Dialogic Notes
- This CLI structure consolidates multiple pipeline modules into a single entrypoint (`main.py`).
- Ideal for rapid experimentation, internal QA, or data teams to process corpora at scale.
- Long-term direction may involve breaking commands into namespace groupings or supporting `--dry-run` and audit modes.
- New sub-commands `search` and `agent` will expose FAISS retrieval and multi-agent RAG workflows.
- `search` accepts a natural language query and returns document IDs ranked by semantic similarity.
- `search file` looks up documents similar to the contents of a local text file.
- `agent` orchestrates cooperative roles such as Synthesizer and Insight Aggregator while respecting a budget cap.
- `chatgpt` parses personal ChatGPT exports into conversation and prompt files; `--markdown` saves transcripts as `.md`.
- A `dedup` command consolidates prompt text files into a single deduplicated list.

- Classification commands now accept `--segmentation` to switch between semantic or paragraph chunking.

- Export command `export parse` converts ChatGPT exports to text files.
### 9 Pipeline Integration
- @ai-pipeline-order: inverse
- **Coordination Mechanics:** CLI commands orchestrate uploads, segmentation, embedding, and retrieval through underlying workflow modules.
- **Integration Points:** Invokes `core.workflows.main_commands`, `core.embeddings.embedder`, and leverages Retriever and Synthesizer agents plus TokenMap Analyzer outputs.
- **Risks:** Mismatched CLI flags may bypass segmentation; large batch operations can exceed API budget.
