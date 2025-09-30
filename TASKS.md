# 🛠 Codebase Cleanup & Consistency Roadmap

This repo was largely AI-generated. The following tasks are structured so that AI tools (e.g., Codex) can execute them with minimal human clarification.
Tasks are derived directly from the `Codex ++\intents\2025-09-23__purpose_ast_consistency.intent.md` **intent file**, prioritized by impact, feasibility, and system coherence.
Each task includes **goal**, **patch scope**, **Codex iteration prompts**, and **dependencies** to support recursive refinement loop.

---

## 🧩 1. High-Priority, High-Impact Fixes (Runtime & Architecture-Critical)

### **1.1 Chunk Format Mismatch**

**Goal:** Align `.json` output from `core.embeddings.embedder` with `.txt` expectations in `core.retrieval.retriever`.
**Impact:** Prevents silent failure in retrieval pipelines.
**Addressability:** High — isolated I/O contracts.

**Codex Patch Plan**

```text
Task: Align chunk format between embedder and retriever modules.
- Update embedder to write `.txt` chunks (or retriever to handle `.json`).
- Add interface constant CHUNK_FORMAT in core.config.
- Ensure all pipeline tests cover both modes.
```

**Dependencies:** retriever ↔ embedder tests, `core.config.config_registry`.

---

### **1.2 Budget Tracker Persistence**

**Goal:** Avoid overwriting spend logs during concurrent runs.
**Impact:** Data corruption risk for multi-agent or async use.
**Addressability:** High — localized state update.

**Codex Patch Plan**

```text
Task: Merge instead of overwrite JSON logs in core.utils.budget_tracker.
- Read existing JSON (if present) before writing.
- Merge per-key totals safely (atomic write via tempfile).
- Add pytest for concurrent write simulation.
```

---

### **1.3 FAISS Index Concurrency Safety**

**Goal:** Prevent simultaneous regeneration from deleting shared indices.
**Impact:** Medium-high — affects production stability.
**Addressability:** Moderate.

**Codex Patch Plan**

```text
Task: Add concurrency guard for FAISS index rebuild.
- Use file lock (fcntl or portalocker) around index write.
- Document lock behavior in purpose and .intent.
```

---

### **1.4 Embedder Client Reuse**

**Goal:** Refactor repeated OpenAI client instantiation.
**Impact:** Performance and test reliability.
**Addressability:** Moderate.

**Codex Patch Plan**

```text
Task: Introduce reusable embedding client.
- Create core.llm.client_pool with singleton-like access.
- Refactor embedder to acquire client from pool.
- Adjust budget tracker acquisition to inject client reference.
```

**Dependencies:** budget tracker, retriever, future agent hub.

---

## ⚙️ 2. Mid-Priority – Documentation & Drift Remediation

### **2.1 Refresh `.purpose.md` Files**

**Goal:** Synchronize declared dependencies with AST reality.
**Impact:** High for developer onboarding and automation.
**Addressability:** High — automated lint possible.

**Codex Patch Plan**

```text
Task: Update purpose docs for drifted modules.
Priority order:
1. core.embeddings.embedder
2. core.retrieval.retriever
3. core.workflows.main_commands
4. cli.parse / cli.pipeline
5. core.agent_hub
- Parse AST → extract imports → rewrite dependency bullets.
```

---

### **2.2 Prune Orphaned Purpose Docs**

**Goal:** Remove or archive `.purpose.md` with no AST/source match.
**Impact:** Moderate — reduces governance noise.
**Addressability:** Very high — scriptable.

**Codex Patch Plan**

```text
Task: Detect and remove orphaned purpose files.
- Compare purpose_files list vs src/*.py paths.
- Move obsolete files to /deprecated_purpose/ archive.
- Log changes in new .intent.
```

---

### **2.3 CLI Config Bootstrap Unification**

**Goal:** Consolidate repeated `get_path_config` usage.
**Impact:** Developer ergonomics, codebase clarity.
**Addressability:** Moderate — simple helper extract.

**Codex Patch Plan**

```text
Task: Extract shared CLI config initializer.
- Create cli/bootstrap_config.py with init_path_config().
- Replace duplicate calls in cli.parse, cli.pipeline, cli.embed, etc.
- Update purpose docs accordingly.
```

---

### **2.4 Agent Hub Alignment**

**Goal:** Match async/OpenAI orchestration promise or downgrade docs.
**Impact:** Architectural integrity, user expectation.
**Addressability:** Medium — branch task.

**Codex Patch Plan**

```text
Task: Either downgrade purpose.md or implement promised orchestration.
Option A: Mark stub as synchronous fallback.
Option B: Introduce async.run_agents() skeleton using anyio.
```

---

## 🧱 3. Lower-Priority but Strategic Enhancements

### **3.1 High Fan-Out Module Refactor**

**Goal:** Reduce coupling in `embedder` and `main_commands`.
**Impact:** Long-term maintainability.
**Addressability:** Low – refactor-scale.

**Codex Patch Plan**

```text
Task: Split orchestration and persistence responsibilities.
- embedder → embedder_core.py + embedder_store.py
- main_commands → ingest.py + summarize.py
- Adjust tests, imports, and purpose files.
```

---

### **3.2 Lambda Summary Modernization**

**Goal:** Replace `core_lib` remnants and add retry abstraction.
**Impact:** Cloud reliability.
**Addressability:** Medium.

**Codex Patch Plan**

```text
Task: Update Lambda summary to match config abstraction layer.
- Replace `core_lib.*` references with `core.configuration.remote_config`.
- Wrap boto3 client calls in retry/backoff utility.
```

---

### **3.3 Filename Normalization Hardening**

**Goal:** Eliminate chained `.replace()` anti-pattern.
**Impact:** Small but visible correctness fix.
**Addressability:** Very high — trivial PR.

**Codex Patch Plan**

```text
Task: Replace chained replace() calls with regex sanitization.
- Add re.sub(r"[^A-Za-z0-9_]", "_", filename)
- Write unit test for edge characters.
```

---

## 🧩 4. Automation & Linting (Long-Term)

### **4.1 Purpose–AST Drift Linter**

**Goal:** Automate future drift detection.
**Impact:** Prevents regression of doc accuracy.
**Addressability:** Medium — tool development.

**Codex Patch Plan**

```text
Task: Build tools/purpose_linter.py
- Parse purpose dependency bullets.
- Compare against ast_deps.csv.
- Emit drift report (JSON + markdown).
- Integrate in CI workflow.
```

---

## 📋 Summary Table

| Priority | Task                         | Type            | Modules                    | Addressability |
| -------- | ---------------------------- | --------------- | -------------------------- | -------------- |
| 🔥       | Chunk format alignment       | Bug             | embedder/retriever         | High           |
| 🔥       | Budget tracker persistence   | Bug             | core.utils                 | High           |
| 🔥       | FAISS concurrency guard      | Stability       | core.vectorstore           | Medium         |
| 🔥       | Embedder client reuse        | Perf/refactor   | core.embeddings            | Medium         |
| 🧩       | Purpose refresh              | Docs            | all                        | High           |
| 🧩       | Orphan cleanup               | Hygiene         | repo                       | Very High      |
| 🧩       | CLI config bootstrap         | Refactor        | cli.\*                     | Medium         |
| 🧩       | Agent hub alignment          | Arch fix        | core.agent\_hub            | Medium         |
| 🧱       | Fan-out split                | Refactor        | embedder/main\_commands    | Low            |
| 🧱       | Lambda summary modernization | Cloud stability | core.utils.lambda\_summary | Medium         |
| 🧱       | Filename normalization       | Bug             | core.workflows             | High           |
| 🧠       | Purpose–AST linter           | Automation      | tools.\*                   | Medium         |


---

## Phase 5: Polish (Open Source Ready)

- **Task 5.1: Update README.md**    
    - Add project description.        
    - Add install instructions.        
    - Add Quickstart example code.        
    - Add badges for CI, coverage (optional).        
- **Task 5.2: Add CONTRIBUTING.md**    
    - Document coding style (black, ruff).        
    - Document test workflow (`pytest`).        
    - Document branching/PR policy.        
- **Task 5.3: Add Purpose Docs**    
    - For each major module (`pipeline`, `lambda`, `cli`), create `purpose.md`.        
    - Explain the module’s role.        
- **Task 5.4: Add Type Hints & Docstrings**    
    - Add return type hints to public functions (`run_pipeline`, `classify_document`, etc.).        
    - Add docstrings explaining parameters and return values.        

---

## Execution Guidelines

- Each task should be completed and committed in a separate branch/PR.    
- Run pre-commit and tests before each commit.    
- Small, atomic changes are preferred (no mega-commits).    
- Human review required for architectural refactors (Phase 2).
