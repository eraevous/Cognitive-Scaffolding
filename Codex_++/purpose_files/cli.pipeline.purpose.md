# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

# Module: cli.pipeline
# @ai-path: cli.pipeline
# @ai-source-file: pipeline.py
# @ai-role: CLI Entrypoint
# @ai-intent: "Run full or partial document processing pipelines via Typer."

> Exposes a single `run_all` command that uploads, classifies, embeds and clusters documents with optional path overrides.

### 🎯 Intent & Responsibility
- Provide an end-to-end ingestion pipeline from CLI.
- Allow path config overrides for GUI or alternative deployments.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | input_dir | Path | Folder of raw documents |
| 📥 In | chunked | bool | Classification chunk mode |
| 📥 In | segmentation | str | "semantic" or "paragraph" |
| 📥 In | method | str | Embedding source text |
| 📥 In | cluster_method | str | Clustering algorithm |
| 📥 In | model | str | Model for labeling |
| 📥 In | root/raw_dir/parsed_dir/metadata_dir/output_dir | Path | Optional path overrides |
| 📤 Out | cluster_output | Folder | CSV/PNG cluster exports |

### 🔗 Dependencies
- `scripts.pipeline.run_pipeline`
- `core.clustering.clustering_steps.run_all_steps`
- `core.config.config_registry.get_path_config`

### 🗣 Dialogic Notes
- Designed for automation and future GUI-driven pipelines.
