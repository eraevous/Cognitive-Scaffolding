- @ai-path: core.utils.budget_tracker
- @ai-source-file: budget_tracker.py
- @ai-role: utility
- @ai-intent: "Track and limit API spending across embedding and agent operations."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false
- @schema-version: 0.2
- @ai-risk-pii: none
- @ai-risk-performance: "Adding checks introduces slight overhead per call."

# Module: core.utils.budget_tracker
> Simple cost accounting helper that aborts operations when monthly spend exceeds a configured limit.

### 🎯 Intent & Responsibility
- Wrap OpenAI API calls to accumulate token usage and convert to dollar cost.
- Provide `check(cost)` and `reset(month)` helpers for CLI and agents.

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description |
|-----------|------|------|-------------------|
| 📥 In | max_usd | float | Monthly budget ceiling |
| 📥 In | cost | float | Cost increment to add |
| 📤 Out | ok | bool | Whether the call is allowed |

### 🔗 Dependencies
- `time` for month tracking
- `pathlib.Path` for optional log persistence

### 🗣 Dialogic Notes
- Aligns with AGENTS rule `G-08` to respect spending limits.
- CLI commands and agents import this utility to fail fast when the budget is hit.
