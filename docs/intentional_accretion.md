# Intentional Accretion Cores for Kairos

This note proposes alternative "strong spine" candidates and supporting layers to make Kairos accretive by design. Each core keeps the invariants small and opinionated while allowing edges to sediment and evolve.

## 1) Artifact Spine + Provenance Ledger (Minimal Default)
- **Spine:** A single content-addressed artifact schema (documents, chunks, embeddings, summaries) plus a provenance ledger that records transformations and constraints.
- **Why it fits:** The charter already demands deterministic IDs and schema validation; formalizing the ledger turns history into a first-class citizen and leaves space for new processors to sediment.
- **Edges:**
  - New ingestion/analysis tools write append-only events into the ledger, tagging inputs, outputs, and constraint checks.
  - Deprecation flags live in the ledger, enabling graceful decay without deletion.
  - Backfills can replay the ledger to rebuild downstream stores (FAISS, caches, exports).
- **Governance hooks:** Ledger can enforce meta-rules ("reject if schema mismatch" or "route to arbitration if collision").

## 2) Reconciliation Loop (“Civic Layer”) Kernel
- **Spine:** A small reconciliation service that evaluates assertions about the knowledgebase (e.g., schema compatibility, embedding freshness, memory consistency) and produces resolutions or warnings.
- **Why it fits:** Mirrors Kubernetes’ reconciliation loop and provides the contradiction interpreter described in the paradigm.
- **Edges:**
  - Modules publish assertions ("chunk version v3 missing embedding") to a queue; the reconciler schedules remediation steps using plug-in handlers.
  - Arbitration policies (precedence, tie-breaks, grace periods) are declarative, versioned, and logged as fossils.
  - Supports partial failure: unresolved assertions are quarantined with fallback paths (e.g., serve stale embeddings with a notice).
- **Governance hooks:** Acts as the judicial layer, producing justification artifacts that downstream agents (summarizers, retrievers) can cite.

## 3) Memory & Precedent Store Core
- **Spine:** A structured store for decisions, rationales, and playbooks ("fossils") keyed by context (module, schema version, risk profile).
- **Why it fits:** Embeds interpretability into sediment so future accretion can be intentional, not accidental.
- **Edges:**
  - Agents append decision entries with `what/why/constraints/alternatives/risks` as first-class fields.
  - Retrieval API allows workflows to fetch relevant precedents before acting, encouraging meta-rule reuse.
  - Supports "formalize-after-stability": entries that recur can be elevated into charter rules or validation checks.
- **Governance hooks:** Enables BudgetTracker or risk gates to demand precedent lookups before expensive actions.

## 4) Interface Bus + Orthogonal Domains (Optional Spine Swap)
- **Spine:** A narrow interface contract (IO tables + event types) for the four pipeline domains: ingestion, summarization/classification, embedding/retrieval, synthesis/export.
- **Why it fits:** Keeps domains orthogonal, allows independent evolution, and tolerates optional dependencies.
- **Edges:**
  - Domain adapters translate between the interface bus and specific implementations (PDF parser, FAISS, tiktoken fallback).
  - Versioned IO tables make refactors refactor-friendly: new versions can coexist until arbitration retires older ones.
  - Encourages ecological deployment (multiple retrievers or summarizers can run in parallel, reconciled via the civic layer).

## Recommended Next Steps (layered, low-risk)
1. **Adopt the Artifact Spine + Provenance Ledger** as the default core: formalize the event schema, append-only log location, and replay utilities.
2. **Prototype the Reconciliation Loop** as a Typer command or background job that reads ledger assertions and emits resolutions; start with embedding freshness and schema drift checks.
3. **Introduce the Memory & Precedent Store** by capturing rationales in `.intent.md` (short-term) and migrating to a structured store once patterns stabilize.
4. **Gradually enforce the Interface Bus** by documenting current IO tables for each domain and versioning them before major refactors.

This combination preserves a tiny, stable spine while encouraging intentional sedimentation, meta-rules, and graceful decay across Kairos.
