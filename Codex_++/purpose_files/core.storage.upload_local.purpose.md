# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

# Module: core.storage.upload_local
> Convert raw documents into parsed text and emit structured stubs for downstream pipelines.

### 🎯 Intent & Responsibility
- Copy raw documents into the configured `PathConfig.raw` directory and extract plain-text representations under `parsed`.
- Generate rich stub metadata capturing `file_info` (paths, extension, counts) and a placeholder `chunk_map` used by classification.
- Ensure ingestion directories exist, supporting both default and custom `PathConfig` layouts.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | file_path | Path | Source document to ingest |
| 📥 In | parsed_name | Optional[str] | Override for parsed `.txt` filename |
| 📥 In | paths | PathConfig | Directory configuration (defaults to registry) |
| 📤 Out | stub | Dict[str, Any] | `{ "file_info": {...}, "chunk_map": None }` persisted to `<parsed_name>.stub.json` |
| 📤 Out | parsed_file | Path | Parsed `.txt` written to `paths.parsed` |

### 🔗 Dependencies
- `core.parsing.extract_text` — performs format-specific text extraction.
- `core.configuration.config_registry.get_path_config` — supplies default directory structure.

### 🗣 Dialogic Notes
- `file_info` now records `source_file`, `parsed_file`, `source_ext`, `word_count`, and `char_count`, enabling later analytics without re-reading the raw document.
- `chunk_map` placeholder allows classification to detect whether chunk planning has been performed; subsequent stages overwrite `None` with detailed plans.
- Called by CLI/pipeline ingestion steps; errors surface early before expensive LLM calls.

### 9 Pipeline Integration
- @ai-pipeline-order: inverse
- **Coordination Mechanics:** Provides the initial artefacts consumed by `core.workflows.main_commands.prepare_chunk_plan` and the broader `scripts.pipeline` run.
- **Integration Points:** Stub structure is read/updated by classification, embeddings, and clustering stages to keep metadata aligned.
- **Risks:** Extraction failures halt ingestion; stub schema must evolve in lockstep with metadata validation.
