# QAT Quickstart Guide

This project uses the **Quasi-Agent Tool (QAT)** layout for modular AI workflows. The root contains several key files:

- `qat_manifest.json` – defines active agents and pipeline modules.
- `qat_instructions.json` – runtime directives and repository rules.
- `core_seed.yml` – shared terminology and defaults.
- `src/` – python source code for the pipeline.
- `intents/` – transient design notes (`*.intent.md`).
- `purpose_files/` – stable module contracts (`*.purpose.md`).
- `docs/` – documentation, including this quickstart.


## Minimal Pipeline Example

The snippet below stores a memory frame and generates a summary from document IDs:

```python
from core.memory.frame_store import FrameStore
from core.retrieval.retriever import Retriever
from core.synthesis.summarizer import summarize_documents

store = FrameStore()
store.save_frame("intro", "These notes will appear before the summary")

retriever = Retriever()
text_summary = summarize_documents(["doc1", "doc2"], retriever)

combined = store.inject_memory(text_summary, ["intro"])
print(combined)
```

This assumes a FAISS index and chunk directory have been built in `src/core/vectorstore`.
