# 🧠 Cognitive Scaffold
An extensible assistant for structuring, retrieving, and exploring unstructured documents, notes, and thoughts.
> “What is this document? Why might it be useful? How can I find more of the same?”
Cognitive Scaffold answers these questions using intelligent summarization, rich metadata extraction, semantic clustering, and AI-augmented reasoning.

---

## 🌟 Core Features

- 📄 **Parse and process documents** from `.txt`, `.pdf`, `.docx`, and `.md`
- 🤖 **Generate structured metadata** with LLMs (Claude or GPT)
- 🧠 **Classify, cluster, and label** documents using UMAP + HDBSCAN or Spectral
- 🔍 **Organize and explore** based on category, themes, tags, tone, and stage
- 🧭 **Suggest exploration trails** and semantic connections
- 🧰 **Export to folders**, metadata files, and future-ready search/RAG systems

---

## 🧱 Architecture Overview

```
[Raw documents]
      ↓
[Parse → .txt]
      ↓
[Summarize → metadata.json]
      ↓
[Classify and Cluster]
      ↓
[Organize into folders or dashboards]
      ↓
[Explore via CLI, Obsidian, or RAG]
```

---
```
┌────────────────────┐
│   Raw Documents    │
└────────┬───────────┘
         │
         ▼
┌─────────────────────────────┐
│ Parse + Chunk Text          │
│  (extract_text, chunk_text) │
└────────┬────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Classify w/ Claude (AWS Lambda)│
│ Summarize -> Metadata JSON     │
└────────┬───────────────────────┘
         │
         ▼
┌───────────────────────────────┐
│   Store Metadata (.meta.json) │
└────────┬──────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Load Embeddings (from JSON) │
└────────┬─────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ UMAP Dimensionality Reduction (2D) │
└────────┬───────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Dual Clustering:                     │
│ - HDBSCAN (density)                  │
│ - Spectral Clustering (partitioning) │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Label clusters with GPT-4 (smart)  │
└────────┬───────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Visualize (UMAP Plots) + Export CSV  │
│ - Cluster Maps                       │
│ - Metadata Summary CSV               │
└──────────────────────────────────────┘
```
---

## 🧩 Metadata Schema

Documents are enriched with rich, layered metadata:

```json
{
  "summary": "Explores emergence and symbolic reasoning in AI.",
  "topics": ["emergent behavior", "AI cognition"],
  "tags": ["Fourth Seed", "2024", "writing"],
  "category": "AI Philosophy",
  "themes": ["recursive agency", "symbolic anchors"],
  "priority": 4,
  "tone": "reflective",
  "depth": "philosophical",
  "stage": "draft",
  "file_info": { "word_count": 2893, "reading_level": "Grade 10" },
  "lexical_analysis": { "top_terms": [...], "cluster_position": [0.42, 0.87] },
  "custom": { "author": "Zach", "project": "Mosaic Solidarity" },
  "reasoning": { "what_is_this": "...", "exploration_trails": [...] }
}
```

Schema versioning and validation supported.

---

## 💻 CLI Usage

Use `typer`-based CLI commands to manage documents:

```bash
# Upload and parse a local file
python main.py upload my_draft.docx

# Generate metadata via Claude/GPT
python main.py classify my_draft.txt

# View saved metadata
python main.py show-meta my_draft.txt

# Organize a document based on metadata or cluster map
python main.py organize my_draft.txt

# List documents by category, tag, or priority
python main.py list --category "AI Philosophy" --tag "emergence"

# Classify all parsed docs
python main.py classify-all

# Organize everything
python main.py organize-all --cluster-file output/cluster_assignments.json
```

---

## 🧪 Testing

```bash
pytest tests/
```

Covers:
- Metadata schema and validation
- Document parsing logic
- Chunking and summarization
- Chat scraping (ChatGPT logs)
- Clustering and labeling

---

## 🧠 Design Philosophy

- **Metadata is Memory** – capture rich cognitive scaffolds
- **Everything is Modular** – personal and org modes share core logic
- **Clustering ≠ Tagging** – UMAP + GPT creates emergent thematic structures
- **Built to Grow** – export, search, and visualize insights over time

---

## 🔮 Roadmap

- [ ] 🖼️ Web & Obsidian UIs for browsing and exploration
- [ ] 🧠 RAG interface: “Ask my archive”
- [ ] 📁 Versioned metadata + history
- [ ] 🤝 Multi-user/org mode with access controls
- [ ] 🌐 Slack/Teams bots, Notion/CRM integrations
- [ ] 🔎 Visual semantic search interface

---

## 🤖 Authors & Vision

Created by Zach as a cognitive prosthetic — reclaiming forgotten insights, structuring fragmented thoughts, and surfacing emergent themes.

The long-term goal: build a **memory scaffold** for personal growth, creative work, and collective intelligence.

---

## 🛠️ Requirements

- Python 3.9+
- AWS credentials (if using Lambda/S3 mode)
- `requirements.txt` coming soon

---

## 📂 Repo Layout (Post Refactor)

```
core_lib/
  ├── parsing/
  ├── metadata/
  ├── clustering/
  ├── chatlogs/
  ├── utils/
cli/
  └── main.py
scripts/
  └── cluster_docs.py
tests/
  └── test_metadata.py
storage/
  └── io.py
```

---

## 📬 Contributions & Collaboration

Want to collaborate, adapt this for your org, or build similar tools for other contexts?

Open an issue, fork the project, or reach out to explore where it can go.

---

## 🧠 License

TBD — intended for open knowledge-sharing, attribution-based use, and ethical deployment.
