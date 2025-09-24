@ai-intent: Accelerate embedding pipeline without breaking semantic chunk fidelity

- Added cached OpenAI client + encoding reuse in `core.embeddings.embedder` so repeated chunk calls stop reinitializing HTTP sessions.
- Introduced `embed_text_batch` and refactored `semantic_chunk` to batch both window + segment embeddings, eliminating the tight loop of single-request OpenAI calls.
- Budget tracker now charges batched requests once per payload, keeping spend checks aligned with new aggregation behavior.
