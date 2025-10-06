# Commands Quick Reference

## classify — `kairos classify classify-one`

1. CLI entry dispatch: `kairos classify classify-one` triggers Typer’s `classify_one` command
2. Argument parsing: Typer converts `name`, `chunked`, and `segmentation` to Python types
3. Classification call: `core.workflows.main_commands.classify` processes the document and returns metadata
4. Output: success notice and returned metadata are printed to stdout

## batch — `kairos batch …`

### classify-all

1. Typer resolves `classify-all` and collects flags (`chunked`, `overwrite`, `segmentation`)
2. File iteration: scans `parsed` directory from path config for `*.txt` files
3. Skip logic: existing metadata skips unless `overwrite` is true
4. Classification: each file runs through `classify` with progress messages

### upload-all

1. Iterates over files in the provided directory
2. Calls `upload_and_prepare` for each, reporting success or failure

### ingest-all

1. For every file in the directory, prints start message
2. `pipeline_from_upload` runs upload → parse → classify; summaries are logged

## embed — `kairos embed all`

1. Options resolve embedding source (`method`) and output path
2. Path config loads default directories; semantic chunking flag is retrieved
3. `generate_embeddings` produces and saves embeddings accordingly

## cluster — `kairos cluster run-all`

1. Typer parses embedding, metadata, and output paths plus method/model options
2. Defaults filled from path config when options are omitted
3. `run_all_steps` orchestrates dimensionality reduction, clustering, labeling, and export

## pipeline — `kairos pipeline run-all`

1. User-supplied directories and overrides are parsed
2. `_resolve_paths` merges overrides with defaults into a `PathConfig`
3. `run_full_pipeline` uploads, parses, classifies, and embeds documents
4. `run_all_steps` performs clustering and labeling on resulting embeddings

## parse — `kairos parse run`

1. Path overrides resolve into a `PathConfig`
2. If the input path is a directory, each file is prepared for processing; otherwise a single file is handled

## tokens — `kairos tokens …`

### summary

1. Config file is read to locate the parsed directory
2. `TokenStats.from_dir` computes token counts; summary is printed
3. Optional histogram visualization renders if requested

### spite

1. Loads `spite_verses` and prints each line with bullet formatting

## search — `kairos search …`

### semantic

1. Builds a `Retriever` instance and logs the query
2. Top‑k document IDs and scores are printed to stdout

### file

1. Reads text from the provided file path and queries via `Retriever.query_file`
2. Outputs top‑k similar IDs with scores

## agent — `kairos agent run`

1. Typer splits the comma‑separated role string into a list
2. `run_agents` executes a multi‑agent loop using the prompt and roles

## chatgpt — `kairos chatgpt parse`

1. Validates export path, target output directory, and markdown option
2. `parse_chatgpt_export` extracts conversations; count is echoed to the user

## dedup — `kairos dedup dedup-prompts`

1. Defaults resolve prompt directory and output file from path config if missing
2. dedup_lines_in_folder writes unique prompt lines; completion message emitted

## export — `kairos export parse`

1. Optionally sets destination folder for parsed conversations using path config
2. Invokes `parse_chatgpt_export` to generate conversation files from the ZIP