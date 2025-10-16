@ai-intent: Document pipeline metadata fixes and summarizer chunk retrieval adjustments

- Pipeline loop now classifies every newly parsed document and relies on normalized names from `upload_and_prepare` to avoid stale metadata.
- Retriever exposes `get_chunk_text` so summarizers pull stored chunk bodies directly instead of issuing text-similarity lookups by identifier.
- `summarize_documents` consumes `get_chunk_text`, ensuring summaries reflect the requested documents even when identifiers were sanitized during ingestion.
