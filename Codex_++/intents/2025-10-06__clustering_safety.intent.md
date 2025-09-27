@ai-intent: Safeguard clustering pipeline against missing deps and degenerate embedding payloads

- Normalized embedding loader to coerce dict payloads and always emit 2D arrays, preventing 1D/empty crashes in downstream reducers.
- Added guardrails to clustering algorithms for zero/one sample cases and dependency-less environments; tightened UMAP neighbor bounds.
- Wrapped optional imports (tiktoken, umap, hdbscan, faiss) with runtime errors so tests can skip gracefully instead of failing on import.
- Introduced fixture-driven clustering test harness that bypasses remote configs/OpenAI while still exercising export outputs.
