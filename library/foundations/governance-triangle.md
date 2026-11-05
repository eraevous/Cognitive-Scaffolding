---
title: "Governance Triangle — review of AGENTS / CHARTER / Codex instructions"
source: "vault: Governance Triangle.md"
captured: "unknown"
author: "model:chatgpt"
document_type: review
evidence_class: "interpretation"
edited_by: "model:claude (library builder and CS lane, 2026-11-05)"
edits: "added header only"
status: interpretation
adoption: unconfirmed
note: "A model review of the repo's governance documents at an earlier version. The file names and commands it suggests (e.g. purposefmt, tests/purpose/...) are proposals, not things that exist."
reviewed: "a GPT reviewer @ 7e07409 (full read); later edits re-read by a Claude reviewer"
---

# High-level verdict

- You’ve got a **coherent governance triangle**: _behavioral protocol_ (AGENTS), _engineering guardrails_ (CHARTER), and a _task adapter for Codex_ (Instructions). Together they’re strong enough to standardize `.purpose.md` at scale.
    
- Main gaps: a few **enforcement specifics** and **failure modes** aren’t fully nailed down (e.g., header field validation paths, AST↔IO mismatch severity levels, and “what to do when inference fails”). These are fixable with lightweight additions.
    

---

# Per-file observations

## 1) AGENTS.md — operational protocol (Run/Drift, governance, enrichment)

**What’s working**

- Clear cognitive contract: **Run vs Drift cadence**, dual-channel output, and explicit role taxonomy. That’s exactly what turns purpose files into living contracts rather than static docs.
    
- Governance rules (G-series) explicitly require `.purpose.md` presence and enrichment (IO/deps/risks) and forbid drift (AST IO ≠ doc). That’s the muscle you need for enforcement.
    
- An explicit **enrichment protocol** for `.purpose.md` (expand outputs, coordination mechanics, integration points) is gold for consistent generation.
    

**What could be tighter**

- Define **severity levels** for violations (e.g., missing `@ai-version` = fail CI, unknown `@ai-role` = warn). Right now it says “trigger validation / raise,” but not how hard to fail each class.
    
- Add a short **“error recovery” recipe** for Codex: If required header fields can’t be inferred, emit a _stub_ with a machine-readable `@ai-generated: true` and open TODOs (and block merge).
    
- The Run/Drift heuristics are great; consider one **explicit cadence tag** you expect in PR descriptions so CI can verify cadence alignment.
    

**Net**: Ideal **behavioral spine** for both human and AI contributors. Minimal tweaks needed.

---

## 2) CHARTER.md — engineering guardrails (principles → enforceability)

**What’s working**

- Rules **map cleanly to checks**: thin CLIs, single config source, retrieval as interface, single logger, schema-validated artifacts, budgeted LLM calls, etc. This gives you concrete lints/tests to bind Purpose to implementation.
    
- “Docs-as-contracts (QAT)” explicitly requires `.purpose.md` with IO/deps/risks and an AST vs purpose test. That closes the loop from spec → code.
    
- Anti-patterns list is actionable (ban raw vendor calls/FAISS direct, ad-hoc env/paths, one-off CSVs), letting you write simple static checks.
    

**What could be tighter**

- Where the Charter says “Enforce: test/lint,” add **file paths or task names** (e.g., `tests/purpose/test_ast_purpose_contract.py`, `tools/purposefmt lint-meta`) so contributors know exactly where the lever is.
    
- Add a **header schema pin** (e.g., `@schema-version: 0.3`) to the DoD checklist so CI can fail on mismatches explicitly (the rule exists conceptually, but wiring it into DoD helps).
    
- Retrieval interface rule is great; consider a **deny-list** linter that forbids `import faiss` outside the store module and fails CI with a helpful message.
    

**Net**: Excellent **enforcement blueprint**; just needs the last mile of **named tests/linters** so teams can implement without interpretation.

---

## 3) Instructions to Codex.md — adapter between schema and agent

**What’s working**

- Unambiguous stance: QAT behavior, follow Run/Drift, dual-channel output, and **mandatory purpose enrichment** (output schema, coordination, integration, ecosystem anchoring).
    
- Strong “reject or defer” list (e.g., missing schema version, ambiguous IO contracts), which you can map to failure codes in the formatter/linter.
    

**What could be tighter**

- Add the **strict header field order** and the **role enum** directly here (mirror the canonical spec) so Codex has zero wiggle room.
    
- Provide **fallback inference table** for `@ai-role` and `@ai-source-file` (you’ve discussed this in our schema; duplicating a brief version here reduces Codex errors).
    
- Include a **single canonical template** for `.purpose.md` in this file, so Codex doesn’t hunt across docs.
    

**Net**: Solid operational adapter; add **mechanical details** (order, enum, template, failure modes) to reduce ambiguity at generation time.

---

# Cross-file alignment with your Purpose schema

- **Alignment**: All three reinforce the same worldview—Purpose as a **contract** (inputs/outputs/deps/risks), with agents obligated to enrich and CI obligated to reject drift.
    
- **Gaps to close**:
    
    1. **Header strictness** (order + required keys + role enum) lives outside these three; mirror it in Codex Instructions and reference in AGENTS governance.
        
    2. **Operational error handling**: define how Codex/CI behaves on each class of error (warn vs hard fail).
        
    3. **Test names / linter entry points**: CHARTER references checks; provide filenames or command names.
        

---

# Concrete improvements (fast wins)

1. **Pin the header schema in all three docs**  
    Add a short block naming the required keys & order and the `@ai-role` enum. (Reduces drift between spec and agents.)
    
2. **Define CI tasks explicitly**  
    In CHARTER’s “Enforce” lines, mention commands:
    
    - `purposefmt lint-meta path` (validates header order/enum/version)
        
    - `purposefmt check path` (format/style idempotence)
        
    - `tests/purpose/test_ast_contract.py` (AST↔IO)
        
    - `tests/purpose/test_cli_thinness.py` (cyclomatic threshold)
        
    - `lint/denylist_faiss.py` (for “Retrieval is an interface”)
        
3. **Codex failure modes**  
    Extend _Instructions_ with a tiny matrix:
    
    - Missing required header field → **emit stub + fail CI**
        
    - Unknown `@ai-role` → **warn + suggest closest enum**
        
    - Ambiguous IO contracts → **emit TODOs + block merge**
        
4. **Add a one-page Purpose Template**  
    Put the canonical markdown template at the bottom of _Instructions to Codex.md_ so the generator has a single source of truth.
    
5. **Governance severity ladder**  
    In AGENTS.md, add severity tags (INFO/WARN/ERROR/BLOCK) for the common checks; let the **Fork Agent** auto-open an `.intent.md` on WARN/ERROR during Drift.
    

---

# Suggested acceptance criteria (to wire into CI right away)

- **Every module** has a `.purpose.md` with the strict header **in exact order**; `purposefmt lint-meta` passes.
    
- AST import graph matches **🔗 Dependencies** (allowlisted diffs only); otherwise PR fails.
    
- If a PR touches module code without touching `.purpose.md`, CI requires either:  
    a) **No contract change**, or b) an accompanying `.intent.md` that explains drift.
    
- No direct vendor calls or FAISS imports outside sanctioned modules; deny-list linter enforced.
    
- Budgeted client is used for all LLM calls (spot via pattern matching in tests).
    

---

# Bottom line

- The **bones are great**: philosophy, rules, and adapter all point the same way.
    
- Add **mechanical precision** (schema order/enum hard-pinned, command names, severity/failure modes) and you’ll have a zero-drift system where `.purpose.md` is _actually_ a contract—not an aspiration.
