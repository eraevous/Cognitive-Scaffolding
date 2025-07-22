# 🧠 Cognitive Scaffold (Kairos)

Cognitive Scaffold is a modular pipeline and agent toolkit for transforming raw documents into a searchable, semantic knowledge base. It combines document parsing, vector embeddings, memory-injected summarization, and multi-agent orchestration—backed by a flexible CLI and extensible architecture.

> “What is this document? Why might it be useful? How can I find more of the same?”

---

## 🚀 Highlights

- **Parse** `.pdf`, `.docx`, `.txt`, and ChatGPT export archives
- **Embed & Search** using OpenAI models + FAISS retrieval
- **Summarize & Synthesize** across semantically related documents
- **Inject Memory** via `FrameStore` to persist context across runs
- **Run Agents** through `agent_hub` with shared memory and budget control
- **Deduplicate Prompts** for data cleaning and fine-tuning prep
- **Visualize AST Call Graphs** from source code

See [docs/QAT_Quickstart.md](docs/QAT_Quickstart.md) for usage examples and design layout.

---

## 🏗️ Pipeline Overview

```

[Upload] → [Parse Text] → [Semantic Chunking]  
↓ ↓  
[Summarize] [Embed → FAISS Index]  
↓ ↓  
[Retrieve + Memory Injection] → [Summarize → Export]

````

---

## 🧪 Minimal Example

```python
from core.memory.frame_store import FrameStore
from core.retrieval.retriever import Retriever
from core.synthesis.summarizer import summarize_documents

store = FrameStore()
store.save_frame("intro", "These notes will appear before the summary")

retriever = Retriever()
summary = summarize_documents(["doc1", "doc2"], retriever)
print(store.inject_memory(summary, ["intro"]))
````

---

## 🖥 CLI Quick Reference

|Command|Purpose|
|---|---|
|`kairos parse`|Parse a file or directory into `.txt`|
|`kairos classify`|Summarize & generate metadata|
|`kairos embed all`|Generate document embeddings|
|`kairos search`|Query the FAISS index|
|`kairos dedup prompts`|Remove duplicate lines from prompt files|
|`kairos export-chatgpt`|Parse a ChatGPT export zip|
|`kairos agent`|Launch multi-agent pipeline by role|

Install with `pip install -e .` and run `kairos --help` to explore all options.

---

## 📂 Repository Structure

```
├── src/
│   ├── cli/                # Typer commands
│   ├── core/               # Parsing, embedding, memory, agents
│   ├── tools/              # AST graph, deduplication, utilities
│   └── tests/              # Unit tests
├── purpose_files/          # `.purpose.md` design contracts
├── docs/                   # Guides and architecture notes
└── ast_deps.csv            # Example AST output
```

---

## 🔎 Learn More

- 📘 [Project Vision & Philosophy →](https://chatgpt.com/c/docs/VISION.md)
- 🧠 [Quickstart Guide →](https://chatgpt.com/c/docs/QAT_Quickstart.md)
- 🧪 [Test Coverage →](https://chatgpt.com/c/src/tests/)

---

## 🤝 Contributing

Pull requests and collaboration ideas welcome! This scaffold is designed for personal knowledgebases, research pipelines, and semantic search assistants.

---

## 🧠 License

TBD — Intended for open knowledge-sharing and ethical deployment.
