@ai-intent: Capture tradeoff introduced by enabling Black checks in CI

- Added GitHub Actions job that now enforces `black --check .`, but repository currently has multiple files failing formatting.
- Local run shows 26 files would be reformatted; deferred mass reformat to keep diff scoped to CI plumbing.
- Follow-up needed: schedule formatting sprint or selectively update modules before merging CI enforcement into default branch.
