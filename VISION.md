# 📘 Project Vision: Cognitive Scaffold as Cognitive Prosthetic

> “What is this archive? Why did I save this? What connects these ideas?”

**Cognitive Scaffold** exists to answer questions like these—not just through search, but through memory-aware synthesis, emergent patterning, and semantic organization.

---

## 🔍 Purpose

This project began as a way to reclaim fragmented insights buried across personal notes, conversations, and forgotten exports. It has evolved into a toolkit for:

- Building **memory scaffolds** that grow over time
- Structuring messy corpora (notes, PDFs, exports, essays, code)
- Synthesizing ideas with memory-aware summarization
- Enabling **agentic exploration** of knowledge bases

It is inspired by systems thinking, LLM workflows, and personal research needs—designed as a cognitive prosthetic for thinkers navigating complexity.

---

## 🎯 Design Philosophy

- **Metadata is Memory** – enriching documents with semantic tags, summaries, themes, and traceable provenance
- **LLMs as Synthesizers** – not oracles, but pattern recognizers that make reflection scalable
- **Context is King** – `FrameStore` allows persistent memory across prompts and pipelines
- **Modular by Default** – each tool can run standalone or as part of a CLI + agent ecosystem
- **Scaffold, Don’t Solve** – prioritize augmentation, not automation

---

## 🧠 Core Components

| Component      | Role                                                      |
|----------------|-----------------------------------------------------------|
| `parser/`      | Extracts clean text and segments semantic chunks          |
| `embedder/`    | Embeds chunks into OpenAI vectors                         |
| `retriever/`   | Queries the vector index (FAISS)                          |
| `summarizer/`  | Synthesizes summaries from retrieved chunks               |
| `frame_store/` | Stores persistent memory frames for prompt injection      |
| `agent_hub/`   | Runs multiple agents with shared retrieval & memory       |

Each component follows a `.purpose.md` contract describing IO schema, coordination logic, and extension hooks.

---

## 🔮 Future Roadmap

- [ ] Semantic clustering and thematic labeling
- [ ] Embeddable web UI and Obsidian plug-in
- [ ] Visual exploration (UMAP/2D map, trail search)
- [ ] "Ask my archive" RAG interface
- [ ] Versioned memory with time-aware summarization
- [ ] Multi-user team knowledge graphs

---

## 🧰 Built With

- Python 3.9+
- Typer CLI
- OpenAI Embeddings
- FAISS for fast vector search
- Optional LLMs (GPT/Claude) for synthesis
- Custom QAT schema for modular design contracts
- OpenAI Codex
- Codex++ custom augmentation

---

## 🤖 Author's Intent

This project was built to support:

- Long-form writing
- Research and paper scaffolding
- Personal knowledge exploration
- AI-augmented creative thinking

Ultimately, it's a step toward **self-reflective toolchains**—where LLMs act not as task-doers, but as memory extenders and conceptual mirrors.

> Created by Zach Rhodes • [Contact](mailto:zachary.d.rhodes@gmail.com)