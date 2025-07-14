# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

# Module: cli.embed
# @ai-path: cli.embed
# @ai-source-file: embed.py
# @ai-role: CLI Entrypoint
# @ai-intent: "Invoke document embedding generation via Typer command."

> Thin command wrapper that calls `core.embeddings.embedder.generate_embeddings`.

### 🎯 Intent & Responsibility
- Provide `embed all` for embedding parsed or summarized text files.
- Relay the `segment_mode` configuration from `PathConfig`.

### 📥 Inputs & 📤 Outputs
| Direction | Name   | Type | Brief Description |
|-----------|-------|------|-------------------|
| 📥 In     | method | str  | Source text: parsed, summary, raw, meta |
| 📥 In     | out_path | Path | Optional path for embeddings JSON |
| 📤 Out    | rich_doc_embeddings.json | File | Vectors persisted by embedder |

### 🔗 Dependencies
- `typer`
- `core.embeddings.embedder.generate_embeddings`
- `core.config.config_registry.get_path_config`

### 🗣 Dialogic Notes
- Registered under `embed` sub-command in `cli.main`.
- Default method set to `parsed` to embed text files directly.
