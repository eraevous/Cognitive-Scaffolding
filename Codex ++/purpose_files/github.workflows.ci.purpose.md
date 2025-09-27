# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

# Module: github.workflows.ci

# @ai-path: github.workflows.ci
# @ai-source-file: .github/workflows/ci.yaml
# @ai-role: devops-pipeline
# @ai-intent: "Enforce linting, testing, and formatting gates through GitHub Actions."

### 🎯 Intent & Responsibility
- Execute repository quality gates (`ruff`, `pytest`, `black --check`) on pushes and pull requests across mainline and feature branches.
- Provide automated feedback to maintainers before merge, reinforcing local dev parity with CI.

### 📥 Inputs & 📤 Outputs
| Direction | Name                    | Type                                        | Brief Description |
|-----------|-------------------------|---------------------------------------------|-------------------|
| 📥 In     | repository snapshot     | git checkout (HEAD commit)                  | Source files fetched via `actions/checkout@v4`. |
| 📥 In     | python-version          | str (semver)                                | Runtime selected by `actions/setup-python@v5` (3.11). |
| 📥 In     | workflow triggers       | GitHub event payload (`push`/`pull_request`) | Covers `main`, `develop`, and `feature/**`, `bugfix/**`, `release/**` branches to gate work-in-progress refs. |
| 📤 Out    | quality status          | Literal["success", "failure"]              | Aggregated job result surfaced as GitHub Check. |
| 📤 Out    | step annotations        | List[GitHubActionAnnotation]                | Inline diagnostics from `ruff`, `pytest`, or `black`. |

### 🔄 Coordination Mechanics
- Single `quality` job runs sequential steps; failure in any gate short-circuits subsequent checks.
- Uses GitHub Actions log/annotation channel for feedback, aligning with @ai-cadence: run for rapid regression signals.
- Shared pip cache is implicit via default Actions runner; no custom caching introduced.

### 🔗 Dependencies
- `actions/checkout@v4` for code retrieval.
- `actions/setup-python@v5` to provision Python 3.11 runtime.
- PyPI packages installed via `pip install -r requirements.txt`, editable install `pip install -e .`, and targeted tools (`black`, `ruff`). The requirements set now includes `pytest-mock` to supply the `mocker` fixture expected by the pytest suite.

### ⚠️ Integration Risks
- Installing heavy optional deps (e.g., `faiss-cpu`, `PyMuPDF`) may increase runtime; monitor for timeouts.
- Workflow assumes tests do not require external secrets; any future secret usage must leverage GitHub encrypted secrets.

### 🧩 Ecosystem Anchoring
- Governs quality gates for modules documented under `purpose_files/`, ensuring synchronization with memory architecture.
- Supports maintainers (`architect`, `executor`, `memory_architect`) by providing automatic regress detection before merge.
- Downstream: PR reviewers rely on the `quality` job status to approve merges; failure should trigger `.intent.md` updates for remediation.
