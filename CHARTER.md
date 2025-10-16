# 🛠️ Refactor Charter: Principles to Build (and Review) By

Below: each principle has (Rule → Why → Enforce). Keep this list short, stable, and testable.

1) Single Source of Truth for Configuration

- Rule: All paths, credentials, schema locations, and flags come from PathConfig/RemoteConfig (via a cached getter). No ad-hoc os.getenv or Path(__file__).parent in feature code.
- Why: Prevents “local hacks” that fork behavior.
Enforce: grep check + unit test that scans modules for banned imports/patterns; pre-commit hook.

2) Thin CLIs, Fat Workflows

- Rule: Typer commands only parse args, resolve config, and call a pure function in core.workflows.*. No logic in CLI.
- Why: Prevents drift between automation and manual runs; keeps surfaces consistent.
Enforce: test that CLI modules contain no non-trivial branches (>N LOC / cyclomatic threshold).

3) One Ingestion Path, Layered Stages

- Rule: Upload → Parse → (Summarize/Classify) → Embed → Cluster → Export is the only pipeline. Every stage reads/writes the shared JSON schema (+ .stub.json provenance).
- Why: Eliminates bespoke “side doors.”
Enforce: schema validator in tests; fixture that round-trips a sample through all stages.

4) Deterministic IDs + Budgeted LLM Calls

- Rule: All chunks, embeddings, and artifacts use content-hash IDs. All LLM/embedding calls go through a single budgeted client (w/ token counting + hard caps).
- Why: Reproducibility and cost control.
Enforce: unit test that rejects non-hash IDs; budget test that fails if calls bypass the tracker.

5) Optional Deps Must Degrade Gracefully

- Rule: UMAP/HDBSCAN/FAISS/tiktoken are optional; guarded imports with explicit fallbacks (semantic→paragraph chunking, etc.).
- Why: Keeps the pipeline usable across environments.
Enforce: test matrix with deps absent; assert informative errors/fallback logs.

6) Retrieval Is an Interface, Not an Implementation

- Rule: All search uses the Retriever interface. FAISS is a plugin behind it; no module reaches into FAISS directly.
- Why: Swap/extend vector stores without churn.
Enforce: static import check that forbids faiss outside store modules.

7) Observability via a Single Logger

- Rule: Use core.logger.get_logger(__name__) everywhere; no ad-hoc print/logging config.
- Why: Consistent diagnostics and filterability.
Enforce: linter rule (deny print in src); unit test to scan modules for logging.getLogger.

8) Docs-as-Contracts (QAT)

- Rule: Every module has a minimal @ai-* docblock + .purpose.md entry listing inputs/outputs/deps/risks. AST tests must match declared imports.
- Why: Prevents architectural drift; boosts readability for AI tooling.
Enforce: AST vs purpose-file test; CI fails on mismatches.

9) Tests Prefer Isolation Over Integration

- Rule: Stub cloud/LLM/FAISS/tiktoken in tests; assert flow and schema conformance, not vendor behavior.
- Why: Fast, deterministic feedback; avoids flaky CI.
Enforce: fixtures that auto-patch heavy deps; coverage requirement on orchestration paths.

10) Storage Semantics Are Centralized

- Rule: All local/S3 I/O goes through storage helpers that validate schema before write; S3 prefixes come from config only.
- Why: Stops silent divergence and “just this once” paths.
Enforce: forbid direct boto3/filesystem calls outside storage modules (static import check).

❌ Anti-Patterns to Ban (AI-Coding Drift Hotspots)

Inline openai.ChatCompletion.create(...) / direct vendor calls (must use shared clients).

“Convenience” environment reads and ad-hoc Path(...) in feature code.

New JSON shapes written from a module without a schema contract update.

Direct FAISS access outside the store; print() for debugging; one-off CSV writers.

✅ Definition of Done (per PR)

- Uses config getters; no direct env/paths.
- If CLI: zero business logic (parse → delegate).
- Reads/writes only schema-validated artifacts.
- LLM/embedding calls go through budgeted client.
- Logger via core.logger; no print.
- Purpose/intent updated; AST-import test passes.
- Tests stub heavy deps; cover control flow.