@ai-intent: Consensus drift + architecture audit (purpose_files vs ast_deps.csv)
@ai-cadence: drift-review

## 1. Discrepancies (Purpose vs AST)
- **cli layer (dedup/embed/parse/pipeline/tokens)** — Purpose docs cite only high-level CLI intent, omitting `typer.Option`/`Argument`/`echo` + `pathlib.Path` + config registry hooks surfaced in AST. → Documentation drift only; runtime stable, but CLI contracts may mislead onboarding.【F:purpose_files/cli.pipeline.purpose.md†L9-L39】【F:src/cli/pipeline.py†L1-L74】
- **core.agent_hub** — Purpose advertises async/OpenAI/anyio loops; actual implementation is a synchronous retriever logger stub. → Drift + architectural debt; not a runtime bug but blocks feature expectations.【F:purpose_files/core.agent_hub.purpose.md†L1-L35】【F:src/core/agent_hub.py†L1-L27】
- **core.analysis.token_stats** — Purpose omits dependency on `core.constants.ERROR_TOKENIZER_NOT_FOUND` + direct `transformers.AutoTokenizer`. Drift is informational; runtime stable.【F:purpose_files/core.analysis.token_stats.purpose.md†L1-L55】【F:src/core/analysis/token_stats.py†L20-L66】
- **core.embeddings.embedder** — Purpose compresses dependencies; AST shows explicit reliance on `chunk_text`, `semantic_chunk`, `hashlib`, `json`, `numpy`, FAISS, and `get_remote_config`. Doc also still names `core.utils.logger` instead of `core.logger`. → Drift masks high coupling and repeated OpenAI client instantiation.【F:purpose_files/core.embeddings.embedder.purpose.md†L1-L55】【F:src/core/embeddings/embedder.py†L1-L164】
- **core.retrieval.retriever** — Purpose focuses on embeddings/FAISS; AST shows use of `config_registry.get_path_config`, `MODEL_DIMS`, JSON/Path IO. Still references legacy `core.utils.logger`. → Drift; integration implications.【F:purpose_files/core.retrieval.retriever.purpose.md†L1-L53】【F:src/core/retrieval/retriever.py†L1-L119】
- **core.storage.upload_local** — Purpose omits JSON persistence, logger, and `PathConfig` override usage. Drift only.【F:purpose_files/core.storage.upload_local.purpose.md†L9-L34】【F:src/core/storage/upload_local.py†L1-L64】
- **core.utils.budget_tracker** — Purpose mentions Path/time; AST shows `json` + `os` for persistence/env parsing. Drift; runtime intact.【F:purpose_files/core.utils.budget_tracker.purpose.md†L1-L36】【F:src/core/utils/budget_tracker.py†L1-L57】
- **core.vectorstore.faiss_store** — Purpose cites FAISS/numpy/logger; AST adds `hashlib`. Drift low-risk but worth documenting.【F:purpose_files/core.vectorstore.faiss_store.purpose.md†L1-L49】【F:src/core/vectorstore/faiss_store.py†L1-L54】
- **core.workflows.main_commands** — Purpose omits segmentation + parsing utilities (`segment_text`, `chunk_text`) and `upload_local`. Drift only, but hides orchestration complexity.【F:purpose_files/core_workflows_main_commands.purpose.md†L1-L42】【F:src/core/workflows/main_commands.py†L34-L158】
- **gui.chat_gui** — Purpose covers Streamlit/OpenAI but misses reliance on LLM cost tables from `core.llm.invoke`. Drift only.【F:purpose_files/gui.chat_gui.purpose.md†L9-L49】【F:src/gui/chat_gui.py†L1-L56】
- **tools.ast_dependency_extractor** — Purpose still advertises `networkx`, but AST shows JSON/pathlib/pandas/typer. Drift only.【F:purpose_files/tools.ast_dependency_extractor.purpose.md†L1-L33】【F:src/tools/ast_dependency_extractor.py†L1-L207】
- **Stale / orphaned docs** — `core.llm.langchain_router`, `core.workflows.insurance_verification`, and some `*_combined.purpose.md` exist with no AST entries or src modules. → Orphaned purpose artifacts; cleanup needed.

## 2. Architecture + Modularization
- **High fan-out modules** — `embedder` + `main_commands` touch ~13 modules each; ripple risk on change. Candidates for responsibility split. (Trace A)
- **CLI boilerplate** — Config resolution (`get_path_config`) reimplemented across CLI modules. Opportunity: shared bootstrap helper. (Traces A+B)
- **Embedder** — Reinstantiates OpenAI client + budget tracker every call. Move to dependency-injected service; reduces perf cost + test fragility. (Trace B)
- **Retriever ↔ Embedder** — Tight coupling via `MODEL_DIMS` + import cycles; should centralize model constants. (Trace B)
- **Agent hub** — Stub misaligned with future orchestration needs; either downgrade doc promises or flesh out async/LLM orchestration. (Traces B+D)
- **Lambda summary** — Purpose still names `core_lib`; code uses `core.configuration.remote_config` + AWS clients. Needs updated docs + abstraction seam. (Trace D)
- **Doc hygiene** — Orphaned purpose files (C+D) suggest missing cleanup after refactors; prune or regenerate.

## 3. Potential Bugs / Runtime Risks
- **Chunk format mismatch** — `embedder` writes `.json` chunks; `retriever` expects `.txt`. → High-likelihood correctness bug when returning text. (Trace D)
- **Budget tracker persistence** — `_persist` overwrites without merging; multi-process runs may desync spend tracking. (Trace B)
- **Upload_local stub overwrite** — `prepare_document_for_processing` clobbers stubs with same parsed name. Risk of silent metadata loss. (Trace B)
- **FAISS index regenerate** — Deletes existing index; concurrent writers could corrupt store. Not test-breaking yet. (Trace B)
- **Filename normalization** — `pipeline_from_upload` chains `.replace` twice; brittle and may leave unsafe chars. Medium-risk runtime bug. (Trace A)

## 4. Next Steps
- Refresh `.purpose.md` files to match AST: especially `embedder`, `retriever`, `main_commands`, CLI wrappers.  
- Prune orphaned/stale purpose files.  
- Split embedder orchestration vs persistence; extract CLI config bootstrap.  
- Add lint to auto-flag purpose/AST drift.  
- Harden runtime: align chunk formats, fix budget tracker persistence, guard FAISS concurrency, normalize filenames safely.
