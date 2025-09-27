@ai-intent: Restore recursive ingestion in scripts.pipeline

- Updated `run_pipeline` to walk the input directory tree with `Path.rglob` so nested source files are uploaded again.
- Added regression coverage ensuring nested raw documents trigger upload calls in order.
