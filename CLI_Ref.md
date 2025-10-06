# Kairos CLI Reference

## kairos classify classify-one

1. **CLI entrypoint** – `kairos` launches Typer’s root app and dispatches to the `classify` sub-app, resolving the `classify-one` command defined in `cli/classify.py`.    
2. **Argument parsing** – Typer converts `name`, `chunked`, and `segmentation` options into Python types.    
3. **Classification call** – The command invokes `core.workflows.main_commands.classify`, which loads the parsed text, optionally segments or chunks it, and summarizes it into metadata.    
4. **Metadata persistence** – The resulting dictionary is validated and written to `<paths.metadata>/<name>.meta.json`.    
5. **Console output** – A success message and the metadata JSON are printed to `stdout`.    

---

## kairos batch classify-all

1. **CLI entrypoint** – Typer routes `kairos batch classify-all` to `classify_all` in `cli/batch_ops.py`.    
2. **Path resolution** – `get_path_config()` supplies directories for parsed text and metadata.    
3. **Iteration & decision** – For each `*.txt` file, the command skips existing metadata unless `--overwrite` is given.    
4. **Classification** – Remaining files are classified via `main_commands.classify`, echoing success or error per document.    
5. **Output** – Each processed file gains a `.meta.json`; progress is printed.    

---

## kairos batch upload-all

1. **Dispatch** – `kairos batch upload-all <dir>` triggers `upload_all`.    
2. **Loop & upload** – Every file in the directory is passed to `upload_and_prepare`, which uploads and parses it.    
3. **Result** – Success or failure is printed for each file.    

---

## kairos batch ingest-all

1. **Dispatch** – Invoked as `kairos batch ingest-all <dir>`.    
2. **Full pipeline** – For each file, `pipeline_from_upload` performs upload, parse, and classify, honoring segmentation and chunking options.    
3. **Output** – A truncated metadata summary is printed for each document; errors are reported per file.    

---

## kairos embed all

1. **CLI entrypoint** – Typer resolves `kairos embed all` to `cli/embed.py`’s `all` command.    
2. **Argument parsing** – `method` selects the text source (`parsed` / `summary` / `raw` / `meta`); `out_path` may override the default file.    
3. **Path config** – `get_path_config` provides directories and segmenting mode.    
4. **Embedding generation** – `generate_embeddings` reads the chosen text source and writes embeddings to JSON.    
5. **Completion** – The embeddings file is saved; no further output beyond Typer’s exit.    

---

## kairos cluster run-all

1. **CLI entrypoint** – `kairos cluster run-all` dispatches to the `cluster` Typer app and selects `run_all`.    
2. **Path defaults** – If not supplied, paths to embeddings, metadata, and output derive from `get_path_config()`.    
3. **Pipeline orchestration** – `run_all_steps` loads embeddings, reduces dimensions, clusters points, labels clusters with GPT, and exports artifacts.    
4. **Artifacts** – JSON/CSV maps, a UMAP plot, and labeled assignments are written to the output directory.    
5. **Console** – Confirmation messages report pipeline completion.    

---

## kairos pipeline run-all

1. **CLI entrypoint** – `kairos pipeline run-all` maps to the `run_all` command in `cli/pipeline.py`.    
2. **Path resolution** – `_resolve_paths` merges user overrides with defaults from `get_path_config`.    
3. **Ingestion phase** – `run_full_pipeline` uploads, parses, classifies, and embeds all documents in the input directory.    
4. **Clustering phase** – The resulting embeddings are passed to `run_all_steps` for clustering and labeling.    
5. **Outputs** – Embeddings, metadata, cluster summaries, and plots populate the configured output directory.    

---

## kairos parse run

1. **CLI entrypoint** – `kairos parse run <input>` dispatches to `run` in `cli/parse.py`.    
2. **Path merging** – `_resolve_paths` integrates optional directory overrides with defaults.    
3. **File handling** – If `input_path` is a directory, each file is processed; otherwise a single file is parsed.    
4. **Processing** – `prepare_document_for_processing` stores the raw file, parsed text, and stub metadata.    
5. **Result** – Parsed `.txt` files and stubs appear in the specified directories.    

---

## kairos tokens summary

1. **CLI entrypoint** – Typer routes `kairos tokens summary` to `summary` in `tokens.py`.    
2. **Config load** – The command reads `path_config.json` (or override) to locate the parsed directory.    
3. **Token counting** – `TokenStats.from_dir` computes counts for all `*.txt` files and prints a textual summary.    
4. **Optional histogram** – With `--show-hist`, NumPy bins the counts and prints a textual bar chart.    

---

## kairos tokens spite

1. **Dispatch** – `kairos tokens spite` invokes `recite`.    
2. **Output** – The command prints each “spite verse” bullet to `stdout`.    

---

## kairos search semantic

1. **CLI entrypoint** – `kairos search semantic "query"` selects the `semantic` command.    
2. **Retriever creation** – A `Retriever` instance initializes embeddings and search index.    
3. **Query execution** – `retriever.query` returns top-k document ID/score pairs.    
4. **Output** – Results are printed line by line as `doc_id score`.    

---

## kairos search file

1. **Dispatch** – `kairos search file <path>` triggers `semantic_file`.    
2. **File query** – The file text is read and sent to `retriever.query_file` for similarity search.    
3. **Output** – Top matches are printed as with `semantic`.    

---

## kairos agent run

1. **CLI entrypoint** – `kairos agent run "prompt" --roles "synthesizer,critic"` targets `run` in `cli/agent.py`.    
2. **Role parsing** – The comma-separated roles string is split into a list.    
3. **Agent orchestration** – `run_agents` spins up the specified agents and executes a multi-agent conversation loop.    
4. **Console** – Conversation output streams to `stdout` until agents finish.    

---

## kairos chatgpt parse

1. **CLI entrypoint** – `kairos chatgpt parse <export_path>` maps to `parse_export`.    
2. **Argument parsing** – `export_path` must exist; `out_dir` and `markdown` options refine output behavior.    
3. **Export parsing** – `parse_chatgpt_export` extracts conversations, optionally writing Markdown transcripts.    
4. **Output** – The command prints how many conversations were parsed into the output directory. 

---

## kairos dedup dedup-prompts

1. **CLI entrypoint** – `kairos dedup dedup-prompts` routes to `dedup_prompts`.    
2. **Path defaults** – If `prompt_dir` or `out_file` is omitted, defaults derive from path config and local paths.    
3. **Deduplication** – `dedup_lines_in_folder` reads all prompt files, removes duplicate lines, and writes a unique list.    
4. **Output** – Typer echoes the path of the deduped output file.    

---

## kairos export parse

1. **CLI entrypoint** – `kairos export parse <zip>` selects the `parse` command in `cli/export.py`.    
2. **Path selection** – If `--out-dir` is absent, the command writes results to `<paths.parsed>/chatgpt_export` via `get_path_config`.    
3. **Parsing** – `parse_chatgpt_export` extracts conversations from the ZIP into text files.    
4. **Completion** – Parsed conversations populate the output directory; no additional console output beyond Typer’s exit.