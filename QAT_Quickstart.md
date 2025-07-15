# 🚀 Quickstart: Cognitive Scaffold & Quasi-Agent Tools (QAT)

Cognitive Scaffold is built around **Quasi-Agent Tools (QATs)**—modular, memory-aware components that parse, embed, summarize, and retrieve knowledge. This guide walks through a minimal setup, the core CLI, and how agents can interact with persistent context.

---

## 🧠 What is a QAT?

A **Quasi-Agent Tool** is a lightweight, callable module with:

- A clearly defined **input/output schema**
- Optional **purpose file** documenting intent and coordination
- Ability to function **standalone** or as part of an **agent pipeline**

Think: modular skills with composable logic.

Each major component (parser, embedder, retriever, summarizer, memory store) follows this format.

---

## 🛠️ Setup

Clone the repo and install dependencies:

```bash
git clone https://github.com/yourname/cognitive-scaffold.git
cd cognitive-scaffold
pip install -e .
````

Make sure your `OPENAI_API_KEY` is set in your environment if using embedding/summarization features.

---

## 📁 Input Format

Start with any `.txt`, `.pdf`, `.docx`, or `chatgpt_export.zip`. The pipeline expects raw input files that it will:

1. Parse
2. Segment into semantic chunks
3. Embed
4. Retrieve and synthesize as needed

---

## 🖥 CLI Example Workflow

```bash
# Step 0 (Optional): Parse ChatGPT Data Export
kairos export parse ./chatGPT_docs

# Step 1: Parse documents to plain text
kairos parse ./raw_docs

# Step 2: Summarize and classify
kairos classify ./parsed_docs

# Step 3: Embed for vector search
kairos embed all

# Step 4: Run a retrieval-based summary
kairos search "How did I write about emergence?"

# Step 5: Launch a multi-agent summarization pipeline - Currently WIP
kairos agent --roles synthesizer thinker # WIP
```

Use `kairos --help` for full CLI options.

---

## 🧠 Code Example: Memory + Retrieval

```python
from core.memory.frame_store import FrameStore
from core.retrieval.retriever import Retriever
from core.synthesis.summarizer import summarize_documents

store = FrameStore()
store.save_frame("intro", "This text is injected into prompts")

retriever = Retriever()
docs = retriever.query("Recursive agency in symbolic systems", top_k=3)

summary = summarize_documents(docs, retriever)
combined = store.inject_memory(summary, ["intro"])

print(combined)
```

---

## 🧩 Sample `.purpose.md` (Tool Contract)

Each QAT tool has a corresponding file like:

```
core/embeddings/embedder.purpose.md
```

Example fields:

```yaml
# Tool: Embedder

- Input: List of semantic text chunks
- Output: FAISS-indexed vector embeddings
- Coordination: Called after parsing, before retrieval
- Tags: [embedding, vector-search, QAT]
```

These documents allow introspection and future agent orchestration.

---

## 🧪 Testing

```bash
pytest src/tests/
```

Tests cover:

- File parsing
- Chunking & summarization
- Memory injection
- CLI execution
- ChatGPT export parsing
- Deduplication

---

## 🧠 What's Next?

- Add your own `.purpose.md` for new tools
- Integrate the toolkit into research pipelines or RAG systems
- Build memory-driven agents using `agent_hub` and `frame_store`

> Cognitive Scaffold is designed as a **cognitive prosthetic**—it doesn’t just store knowledge, it helps you remember _why it mattered_.

---

## 📬 Support

For ideas, bugs, or collaboration:

- Open an issue
- Fork the project
- Reach out: [zachary.d.rhodes@gmail.com](mailto:zachary.d.rhodes@gmail.com)
