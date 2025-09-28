- @ai-path: core.analysis.token_stats
- @ai-source-file: token_stats.py
- @ai-role: analysis.utility
- @ai-intent: "Quickly compute token counts and distribution stats for any glob of text files; expose the same via Typer (`mosaic tokens`)."
- @ai-tags: tokens, statistics, cli, extensibility
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @last-commit: Initial implementation: token count utility + CLI command
- @change-summary: "Introduced pluggable tokenizer registry, histogram option, and CLI integration."

---

## 🔍 Summary
`core.analysis.token_stats` provides a lightweight, pluggable way to measure token usage across the project’s parsed documents (or any text blob).  
It supports multiple tokenizer back-ends (currently Tiktoken and HuggingFace) through a registry pattern and surfaces a one-liner Typer command (`mosaic tokens`) for quick inspection.  
Primary goals: **cost awareness**, **dataset health checks**, and **foundation for future workflow metrics**.

---

## 📥 Inputs

| Name        | Type   | Description                                                      |
|-------------|--------|------------------------------------------------------------------|
| `path_pattern` | str / Glob | Glob relative to CWD selecting text files (default `parsed/**/*.txt`) |
| `tokenizer` | str    | Registry key in the form `<family>:<model>` (e.g. `tiktoken:gpt-4o-mini`) |

---

## 📤 Outputs

| Output                | Description                                                    |
|-----------------------|----------------------------------------------------------------|
| `TokenStats` instance | Holds raw counts, file list, and helper methods.               |
| `describe()` str      | Human-readable summary (min, max, mean, median, quartiles).    |
| *(CLI)* stdout        | Same summary plus optional ASCII histogram.                    |
| `to_dict()`           | Machine-readable counts (future: JSON export / plotting).      |

---

## 📞 Calls

- `get_tokenizer(spec)` → resolves to `Callable[[str], int]`
- Standard library: `statistics`, `dataclasses`, `pathlib`, `typing`
- Optional: NumPy (only when `--show-hist` is requested)

---

## 🔗 Dependencies

- `tiktoken` (for OpenAI models)
- `transformers` (optional; only if user registers a HF tokenizer)
- `numpy` (optional; histogram rendering)

---

## 🧠 Design Rationale

* **Registry pattern** keeps the core logic tokenizer-agnostic—future BPEs or domain-specific encoders drop in via one mapping line.  
* **Pure-Python fallback**—NumPy import is gated behind `show_hist`, so headless servers without NumPy still get core stats.  
* **CLI & API parity**—the same `TokenStats` object powers both programmatic use and Typer output, aligning with existing CLI design.  
* **Extensibility hooks**—`to_dict()` intentionally mirrors other modules’ `*.json` dumps, allowing dashboards or CI to consume stats later.  

---

## ❌ Edge Cases

| Case                               | Handling strategy                                      |
|------------------------------------|--------------------------------------------------------|
| Binary or non-UTF8 file hit        | `try/except` skip with warning (file path printed).    |
| Unknown tokenizer spec             | Raises `ValueError` with available keys listed.        |
| Empty glob                         | Returns summary `"No files processed."`                |

---

## ✅ Test Guarantees

- Correctly counts tokens for an English text sample with both Tiktoken and HF tokenizer.  
- Histogram buckets sum to total file count.  
- Skips unreadable files without crashing the entire run.  

---

## 👥 Collaboration Meta

- @human-edited: false  
- @notes: “Intended as a stepping stone toward budgeting & usage dashboards; next logical upgrade is JSON export + CI gating.”  

---

## 📘 Related Modules

- `cli.main` (Typer root – registers the `tokens` sub-app)  
- `core.config.config_registry` (eventual place to store preferred default tokenizer)  

---

## 📗 System Context

**System Goal:** Provide quick corpus-level metrics so that ingest, embedding, and OpenAI cost parameters can be tuned proactively.

**Architectural Rules:**  
*Utility modules must remain import-side-effect free*—no implicit network calls or config loads at import time.

---

## 💡 Notes

1. Histogram is ASCII art for zero-dep portability; can later swap to Matplotlib via `python_user_visible` for rich charts.  
2. Tokenizer registry intentionally supports family prefixes (`tiktoken:`, `huggingface:`) to avoid name collisions.  
3. Future extension: plug a **custom base-12 tokenizer** or delta-encoding token meter to satisfy duodecimal experimentation.
