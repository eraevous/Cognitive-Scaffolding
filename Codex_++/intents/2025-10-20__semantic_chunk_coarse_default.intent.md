@ai-intent: Re-center semantic chunking on coarse, retrieval-first segmentation while preserving optional adaptive clustering.

- Replaced clustering-first logic with change-point driven coarse mode that guards digressions, enforces max-token spans, and batches both window + chunk embeddings through the shared embedder (BudgetTracker respected).
- Added provenance-rich chunk schema (`topic_change_score`, `window_ids`, `source_doc_id`, `sha256`) and graceful tokenization fallback so short or dependency-light environments still emit usable chunks.
- Bound adaptive mode behind explicit `mode="adaptive"`, clamped UMAP/Spectral/HDBSCAN hyperparameters, and ensured cluster metadata never rewrites text or erases change-point cuts.
- Authored focused tests for short docs, digressions, max-span guards, adaptive clustering, and batch-size telemetry to keep the new defaults stable.
