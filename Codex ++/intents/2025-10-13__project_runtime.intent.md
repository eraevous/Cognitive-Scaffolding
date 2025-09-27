@ai-intent: Align project runtime constraints with deployment environment

- Lowered `requires-python` to `>=3.11` in `pyproject.toml` so local and CI environments pinned to 3.11 continue to install deps.
- No runtime code changes required; existing workflows remain compatible with 3.11 API surface.
