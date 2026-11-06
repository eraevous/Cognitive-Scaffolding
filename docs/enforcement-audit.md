# Enforcement audit: governing instructions as executable dependencies

**Status: draft for owner review.** Docs only. Nothing here changes a rule, a check, a hook or CI;
every fix is proposed, not applied. Asked for by the external review CH-035 §6 and DEC-120
(enforcement audit), taken under the DEC-136 idle policy.

Audited on 2026-11-06 against `origin/master` at `f511dc2`. Sources read: `AGENTS.md`,
`CHARTER.md`, `CONTRIBUTING.md`, `.github/workflows/ci.yaml`, `.github/workflows/telosmith.yml`,
`.github/pull_request_template.md`, `.claude/settings.json`, `.pre-commit-config.yaml`,
`pyproject.toml` (`[tool.ruff]`, `[tool.black]`), `pytest.ini`, `tests/test_doc_drift.py`,
`ast_deps.csv`, `.aec/records.jsonl`, `Codex_++/`.

## Labels

| Label | Meaning |
| --- | --- |
| `enforced` | a hook, CI job, test or script fails when the rule is broken; the path is named |
| `procedural` | relies on a person (or an agent) doing it; nothing fails if they don't |
| `advisory` | guidance or an epistemic stance; not the kind of thing a check can fail on |
| `planned` | names a mechanism that does not exist yet |
| `obsolete` | contradicted by the current records or code |

## What was run (read-only)

- `ruff check .` (ruff 0.17.x local; CI pins 0.13.1): all checks passed. Rule set is `E4, E7, E9, F` only.
- `black --check .` (black 26.5.1, the CI pin): 101 files unchanged.
- `python3 -m pytest -q tests/test_doc_drift.py`: 1 passed. The full `pytest -q` stops at import (`No module named 'fitz'`): the suite needs the third-party `requirements.txt` stack, which this read-only pass did not install. CI installs it.
- `python3 -m aec edges . -o <scratch>` then `python3 -m aec check .aec/records.jsonl --edges <scratch>`: 0 errors, 0 warnings; records are `AU-owner@1`, `P0@1`, `CS-D-ledger@1`, `CS-R-parse@1`, `CS-R-retrieve@1`, `CS-R-synthesize@1`.
- In the Telosmith checkout: the pinned commit `f961902b2dbe` exists and its CLI has `code-impact --exit-code`; Telosmith has no `v0.5.0` tag.
- `git branch -r`: `origin/master` is the only remote branch and the default.
- grep over `src/` (excluding `src/tests`): 0 `print(` calls; `os.getenv`/`os.environ` in `core/utils/budget_tracker.py` and `core/logger.py`; `import faiss` only in `core/vectorstore/faiss_store.py`; `boto3` in six modules (`cli/upload_utils.py`, `core/metadata/io_helpers.py`, `core/workflows/main_commands.py`, `core/storage/aws_clients.py`, `core/storage/s3_utils.py`, `core/utils/lambda_summary.py`); `openai` in ten modules; `@ai-intent` in 31 of 86 modules; 42 purpose files in `Codex_++/purpose_files/`.
- grep over `src/` for `DriftDiff`, `PurposeWeaver`, `IntentTracer`, `MetaChecker`: no definitions.

## Rules and their enforcement

### AGENTS.md

| # | Rule (short quote) | Where stated | Enforcing mechanism | Label | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | "Precedence: Charter > Agents. If a generated change would violate the Charter, stop, switch to Drift" | Governing Docs | None | `procedural` | — |
| 2 | "Records ... are the design truth; agents may append provisional records and proposed decisions, never accepted ones" | Records and ledgers | `aec check` in CI `telosmith.yml` and the hook fails an accepted decision whose `decided_by` does not govern; it cannot see who wrote `epistemic: committed` | `enforced` for accepted decisions without authority; `procedural` for the epistemic field | read Telosmith `records.py`; ran `aec check` |
| 3 | "Append only. Never edit or delete an earlier line in `.aec/records.jsonl`" | Records and ledgers | `aec check` catches conflicting duplicates; nothing diffs the file against the base | `procedural` for a silent rewrite | read `telosmith.yml` |
| 4 | "The Codex++ files ... are kept, and G-13 still applies ... they have not been imported" | Records and ledgers | None; statement of fact (confirmed: no `import-purpose` records in `.aec/records.jsonl`) | `advisory` | records list |
| 5 | "After editing code, the Claude Code hook runs `aec check` and `aec code-impact` ... without it, the hook reports that and does not block" | Records and ledgers; `.claude/settings.json` | Hook present, same shape as relay-kit's; exits 1 with a message when `aec` is missing `--exit-code`, 2 on findings. Claude Code only; Codex and humans do not run it | `enforced` locally (Claude Code); CI backstop `telosmith.yml` | read hook |
| 6 | "The `telosmith` CI job runs the same check on every pull request" | Records and ledgers | `telosmith.yml` `on: [push, pull_request]` (this workflow does cover `master`); records check fails on errors; code-impact report-only | `enforced` (records check); `advisory` (code-impact) | read workflow |
| 7 | Dual-Channel Protocol: `analysis` / `commentary` / `intent` channels; "`intent` ... written to `.intent.md`" | §1 | None. These are model output channels (the `analysis`/`commentary` names come from a 2025 OpenAI model convention); no tool in this repo reads or writes an `intent` channel. CH-035 §6 calls this "nonstandard" | `obsolete` (describes a model interface, not this repo; see mismatch 4) | grep `src/` for `intent` channel handling: none |
| 8 | Run/Drift cadence, heuristics table, "If uncertain, default to Drift", cadence tags `@ai-cadence` | §2 | None; the table names `BudgetTracker` as a drift trigger (exists, `core/utils/budget_tracker.py`, but emits no cadence signal) and `DriftDiff` (does not exist) | `procedural` (practice); the `DriftDiff`/BudgetTracker-trigger references are `planned` | grep `src/` |
| 9 | "Use `DriftDiff` to compare AST IO vs `.purpose.md` expectations" | §3, §7 | No `DriftDiff` in `src/`, `tests/` or `pyproject.toml` scripts. The nearest thing is `tests/test_doc_drift.py`, which compares `@ai-dependencies` tags of five purpose files with the checked-in `ast_deps.csv` | `planned` (the name); `enforced` only for 5 of 42 purpose files, against a static CSV (row 24) | grep; read the test |
| 10 | "`.purpose.md`, `.intent.md` ... are found in the `codex_++` directory one level up from project root" | §3 | None; and the statement is wrong for this repo: they are in `Codex_++/` (capital C, underscore) *inside* the repo root, and `tests/test_doc_drift.py` reads them from there | `obsolete` | `ls Codex_++`; read test paths |
| 11 | "Prompt user if `.purpose.md` is missing — stub and label with `@ai-generated: true`" | §3 | None (42 purpose files for 86 `src/` modules) | `procedural` | counts above |
| 12 | "Write as `.intent.md` using ISO timestamp and module path, e.g. `codex_++/intents/2025-07-02__....intent.md`" | §4 | None; path again says `codex_++` while files live in `Codex_++/intents/` | `procedural` (path text `obsolete`) | `ls Codex_++/intents` |
| 13 | G-00 "Changes must comply with CHARTER.md. CI enforces Charter checks" | §5 | `ci.yaml` runs ruff (`E4,E7,E9,F`), pytest and `black --check`. None of these checks a Charter rule except Charter 8 via `test_doc_drift.py` (partially). See the Charter table | `obsolete` as stated ("CI enforces Charter checks" is not true for 9 of 10 Charter rules) | read `ci.yaml`, `pyproject.toml` |
| 14 | G-01 "No commits to `main` without valid `.purpose.md` present or stubbed" | §5 | None; the default branch is `master`, not `main`, and 44 modules have no purpose file today | `obsolete` (branch name) + `procedural` | `git branch -r`; counts |
| 15 | G-02 "If AST IO != `.purpose.md`, raise and draft reconciliation" | §5 | `tests/test_doc_drift.py` for dependencies only (not IO), 5 modules, static CSV | `procedural` (mostly); narrow `enforced` slice | read test |
| 16 | G-03 "If `@ai-risk-*` is high or unknown, require human checkoff" | §5 | None | `procedural` | grep tests for `ai-risk`: none |
| 17 | G-04 "Log change in module role, coupling, or edge behavior in `.intent.md`" | §5 | None | `procedural` | — |
| 18 | G-05 "Auto-generate `.purpose.md` scaffolds with required schema fields" | §5 | No generator in `src/` or `tools/` (grep `PurposeWeaver`, `scaffold`, `purpose` writers: none) | `planned` | grep |
| 19 | G-06 "Obey Run/Drift cadence" | §5 | None | `procedural` | — |
| 20 | G-07 "Never store secrets or plaintext credentials" | §5 | No secret scan in CI; `.gitignore` is the only guard. (relay-kit has `prepublish_scan.py` for its repo; nothing equivalent here) | `procedural` | read `ci.yaml` |
| 21 | G-08 "All OpenAI calls must respect `BudgetTracker` if configured" | §5; Charter 4 | `BudgetTracker` exists; `tests/test_llm_invoke.py` covers `core/llm/invoke.py`. No test asserts that the ten `openai`-importing modules route through it (Charter 4 "budget test that fails if calls bypass the tracker") | `procedural`; the Charter's named test is `planned` | grep `openai` in `src/`; read test list |
| 22 | G-09 "Changes lacking `@ai-intent` block CI until resolved" | §5 | No CI step or test reads `@ai-intent`; 55 of 86 `src/` modules lack it and CI is green | `obsolete` (claims a CI gate that does not exist) | grep; read `ci.yaml` |
| 23 | G-10 "`.purpose.md` must include output schema, coordination notes, and integration anchors" | §5 | No schema validation of purpose files (`test_doc_drift.py` reads one tag) | `procedural` | read test |
| 24 | G-11 "Use `@ai-pipeline-order: inverse` ..." | §5 | None; no occurrences in `src/` | `advisory` | grep |
| 25 | G-12 "All modules must declare io.exports if they expose public functions/classes" | §5 | None | `procedural` | grep tests: none |
| 26 | G-13 "PR must include either: updated .purpose.md or new .intent.md referencing the change" | §5; reaffirmed in Records section | No CI diff check; PR template has no such item | `procedural` | read `pull_request_template.md`, `ci.yaml` |
| 27 | §6 Agent roles (`architect`, `executor`, `memory_architect`, `fork_agent`, `meta_guard`, future `risk_auditor`) | §6 | No code or config defines these roles | `planned` / `advisory` | grep `src/` for role names: none |
| 28 | §7 Toolchain hooks: `DriftDiff`, `Run/Drift Tracker`, `Thread Fork Agent`, `PurposeWeaver`, `IntentTracer`, `MetaChecker`; "may be ... triggered by commit hooks" | §7 | None of the six exists in `src/`, `tools/`, `.pre-commit-config.yaml` or `.claude/settings.json` | `planned` (all six); the "triggered by commit hooks" sentence is `obsolete` for the hooks that exist (black/ruff/isort only) | grep; read pre-commit config |
| 29 | §9 "Codex cannot persist `.intent.md`, but may simulate it via structured `commentary`" | §9 | None; and the premise is outdated for coding agents that write files (CH-035 §6) | `obsolete` | — |
| 30 | Enrichment protocol for `.purpose.md` generation (expand outputs, coordination mechanics, integration points, ecosystem anchors; `@codex-role` preamble) | Enrichment Protocol | None | `procedural` | — |

### CHARTER.md (each principle names its own "Enforce" line; this column says whether that mechanism exists)

| # | Rule (short quote) | Charter's stated enforcement | What exists | Label | Evidence |
| --- | --- | --- | --- | --- | --- |
| 31 | 1 "All paths, credentials, schema locations and flags come from PathConfig/RemoteConfig ... no ad-hoc `os.getenv` or `Path(__file__).parent` in feature code" | "grep check + unit test that scans modules for banned imports/patterns; pre-commit hook" | No such test or hook. `os.getenv`/`os.environ` found in `core/utils/budget_tracker.py` and `core/logger.py` (arguably infrastructure, not feature code) | `planned` (the named test); the rule itself is `procedural` | grep |
| 32 | 2 "Typer commands only parse args ... No logic in CLI" | "test that CLI modules contain no non-trivial branches" | No such test | `planned` | grep tests |
| 33 | 3 "Upload → Parse → ... → Export is the only pipeline; every stage reads/writes the shared JSON schema" | "schema validator in tests; fixture that round-trips a sample through all stages" | `tests/test_pipeline.py` and `tests/test_merge_stubs.py` exist; whether they round-trip every stage was not verified in this pass (suite not runnable without deps) | `procedural` pending verification | test list |
| 34 | 4 "Content-hash IDs; all LLM/embedding calls go through a single budgeted client" | "unit test that rejects non-hash IDs; budget test that fails if calls bypass the tracker" | `tests/test_embedder_id_mask.py` touches IDs; no bypass test for the ten `openai` importers | `planned` (bypass test); partial for IDs | grep |
| 35 | 5 "Optional deps degrade gracefully (UMAP/HDBSCAN/FAISS/tiktoken)" | "test matrix with deps absent" | No matrix in `ci.yaml` (one Python, full `requirements.txt`) | `planned` | read `ci.yaml` |
| 36 | 6 "All search uses the Retriever interface; no module reaches into FAISS directly" | "static import check that forbids faiss outside store modules" | No check; the rule happens to hold today (`import faiss` only in `core/vectorstore/faiss_store.py`) | `planned` (check); rule currently satisfied | grep |
| 37 | 7 "Use `core.logger.get_logger(__name__)` everywhere; no ad-hoc print/logging config" | "linter rule (deny print in src); unit test to scan modules" | ruff selects `E4,E7,E9,F` only, no `T20` (print); no scanning test. The rule holds today (0 `print(` in `src/` outside tests) | `planned` (lint rule); rule currently satisfied | read `pyproject.toml`; grep |
| 38 | 8 "Every module has a minimal `@ai-*` docblock + `.purpose.md` entry ... AST tests must match declared imports; CI fails on mismatches" | "AST vs purpose-file test; CI fails on mismatches" | `tests/test_doc_drift.py` in CI: 5 modules, `@ai-dependencies` only, compared against `ast_deps.csv` last regenerated 2026-10-28 (nothing in CI regenerates it, so a new import is caught only if someone updates the CSV) | `enforced` for 5/42 purpose files against a static snapshot; `procedural` for the rest and for the docblock | read test; `git log -- ast_deps.csv` |
| 39 | 9 "Stub cloud/LLM/FAISS/tiktoken in tests" | "fixtures that auto-patch heavy deps; coverage requirement" | Fixtures exist (`tests/fixtures/`); no coverage gate in `ci.yaml` or `pytest.ini` | `procedural`; coverage gate `planned` | read `pytest.ini` |
| 40 | 10 "All local/S3 I/O goes through storage helpers ... forbid direct boto3/filesystem calls outside storage modules" | "static import check" | No check; `boto3` is imported in four modules outside `core/storage/` (`cli/upload_utils.py`, `core/metadata/io_helpers.py`, `core/workflows/main_commands.py`, `core/utils/lambda_summary.py`) | `planned` (check); the rule is currently **violated** | grep |
| 41 | Anti-patterns and Definition of Done (config getters, thin CLI, schema-validated artifacts, budgeted client, logger, purpose/intent updated, stubs) | Charter closing | Review checklist; nothing in the PR template or CI | `procedural` | read PR template |

### CONTRIBUTING.md

| # | Rule | Enforcing mechanism | Label | Evidence |
| --- | --- | --- | --- | --- |
| 42 | "Make your change, with tests where the project has them" | `ci.yaml` runs pytest on PRs and on pushes to the listed branches | `enforced` (on PRs; see mismatch 1 for pushes) | read `ci.yaml` |
| 43 | "Open a pull request and check the CLA box" | Template checkbox; no CLA bot | `procedural` | read template |

Counts by primary label (43 rules): `enforced` 6 (rows 2, 5, 6, 15 (narrow), 38 (narrow), 42), `procedural` 19 (rows 1, 3, 8, 11, 12, 16, 17, 19, 20, 21, 23, 25, 26, 30, 31, 33, 39, 41, 43), `advisory` 3 (rows 4, 24, 27), `planned` 9 (rows 9, 18, 28, 32, 34, 35, 36, 37, 40), `obsolete` 6 (rows 7, 10, 13, 14, 22, 29).

## Mismatches found

1. **`ci.yaml` push filter omits the default branch.** `on.push.branches` lists `main`, `develop`, `feature/**`, `bugfix/**`, `release/**`; the repo's only branch and default is `master`. Pull requests are still checked; a direct push to `master` runs `telosmith.yml` but not ruff/pytest/black. (CH-035 §6.)
   *Proposed fix:* add `"master"` to the list (or replace `"main"` with it).
2. **G-09 claims a CI gate on `@ai-intent` that does not exist.** 55 of 86 `src/` modules lack the tag and CI is green.
   *Proposed fix:* either relabel G-09 "procedural (planned CI check)" or add a small pytest that lists modules without `@ai-intent` and asserts the list is a known allowlist, shrinking over time.
3. **G-00 "CI enforces Charter checks" overstates.** Of the ten Charter "Enforce" mechanisms, one exists in a narrow form (Charter 8 via `test_doc_drift.py`); nine are not implemented. Two of them are satisfied by luck today (no `print`, FAISS only in the store), one is currently violated (Charter 10: `boto3` in four non-storage modules).
   *Proposed fix:* change G-00 to "CI enforces ruff (`E4,E7,E9,F`), black and pytest; Charter checks are planned unless a row below names a test", and add an "Exists today: yes/no" column to the Charter's Enforce lines. Owner's call whether Charter 10 is still a rule; if yes, open an issue for the four modules.
4. **AGENTS.md names six toolchain hooks and six agent roles that do not exist, with no implemented/planned distinction.** `DriftDiff`, `PurposeWeaver`, `IntentTracer`, `MetaChecker`, `Run/Drift Tracker`, `Thread Fork Agent`; `architect`, `executor`, `memory_architect`, `fork_agent`, `meta_guard`. Also the "intent channel" and "Codex cannot persist `.intent.md`" describe a 2025 model interface. (CH-035 §6.)
   *Proposed fix:* add "(planned)" after each name in §6 and §7, or move §1, §6, §7 and §9 to `Codex_++/docs/` as design history and leave a one-line pointer; rewrite §1 to say that `.intent.md` files are written directly by any agent that can write files.
5. **Purpose-file location is stated wrongly.** AGENTS.md §3 and §4 say `codex_++` "one level up from project root"; the files are in `Codex_++/` at the repo root, and `tests/test_doc_drift.py` depends on that.
   *Proposed fix:* replace both mentions with `Codex_++/` (repo root).
6. **The one existing Charter check runs against a static snapshot.** `test_doc_drift.py` compares purpose tags with `ast_deps.csv` (last changed 2026-10-28); nothing regenerates the CSV in CI, so an added import in those five modules passes until someone updates the CSV by hand. Telosmith's `aec edges` already produces a live AST snapshot in the `telosmith` job.
   *Proposed fix:* derive the dependency set from `.aec/edges.jsonl` (regenerated every run) instead of `ast_deps.csv`, or add a CI step that regenerates the CSV and fails on diff.
7. **G-01 names `main`; the branch is `master`.** Same root cause as mismatch 1.
   *Proposed fix:* say "the default branch".
8. **Tooling pins disagree between pre-commit and CI.** `.pre-commit-config.yaml` pins black 23.12.1, ruff v0.3.7 and runs isort; `ci.yaml` pins black 26.5.1 and ruff 0.13.1 and does not run isort. A file formatted by the 2023 black can fail the 2026 `black --check` (style changes between those years), and isort findings never reach CI.
   *Proposed fix:* pin the same versions in both, drop isort or add it to CI, and note in CONTRIBUTING that pre-commit is optional (it is not mentioned there today).
9. **Telosmith pin comment points at a release that does not exist.** `telosmith.yml`: "change the ref only to a release >= v0.5.0"; Telosmith has no `v0.5.0` tag.
   *Proposed fix:* as in the relay-kit audit: tag upstream, or say "a reviewed commit at or after `f961902b2dbe`".
10. **`pyproject.toml` names the package `kairos`, version `0.0.1`; the repo, README and AGENTS.md say Cognitive-Scaffolding.** Not a rule violation, but a docs-truth item for a cold reader.
    *Proposed fix:* owner decides the name; one line in README explaining it until then.

## What this audit did not do

- It did not run the full pytest suite (third-party dependencies not installed in this read-only pass); CI does.
- It did not audit the 42 purpose files or the `Codex_++/intents/` notes individually.
- It did not judge whether the Charter's rules are still the owner's intent for this repo, it only asked what would fail if each rule were broken.
