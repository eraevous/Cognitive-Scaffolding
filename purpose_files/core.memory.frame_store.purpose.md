- @ai-path: core.memory
- @ai-source-files: [frame_store.py, memory_proxy.py]
- @ai-role: memory
- @ai-intent: "Store and simulate memory elements to support reflective and context-aware AI behavior."
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: low
- @ai-risk-drift: "May surface outdated or conflicting `.intent.md` fragments — recommend validation."
- @ai-used-by: core.prompting.orchestrator, core.retriever.query_router
- @ai-downstream: core.analysis.intent_scanner

# Module: core.memory
> Provides cognitive memory scaffolding for AI systems, including ephemeral frame injection and structured memory recall via `.intent.md` fragments.

---

### 🎯 Intent & Responsibility

- Persist short text frames for prompt augmentation (`FrameStore`)
- Load and inject saved memory into active prompts
- Parse and surface `.intent.md` fragments that match task context (`Memory Proxy Mode`)
- Enable simulated recall, tradeoff re-surfacing, and drift alerts in Codex-style workflows

---

### 📥 Inputs & 📤 Outputs

| Direction | Name         | Type             | Description |
|-----------|--------------|------------------|-------------|
| 📥 In     | frame_id     | str              | Identifier for short text memory frame |
| 📥 In     | text         | str              | Content to persist in memory |
| 📥 In     | frame_ids    | list[str]        | Multiple frame IDs to inject |
| 📥 In     | prompt       | str              | Active user/system prompt to match against `.intent.md` |
| 📤 Out    | combined     | str              | Prompt with memory prepended |
| 📤 Out    | file_path    | Path             | Saved frame file path |
| 📤 Out    | intent_hits  | list[Dict]       | Relevant `.intent.md` fragment metadata and content |

---

### 🔗 Dependencies

- `core.config.config_registry`
- `core.utils.template` (for prompt injection)
- `json`, `pathlib`, `re`, `datetime`

---

### 🗣 Dialogic Notes

- This is not a full vector search system — it uses keyword relevance or RAG plug-ins
- `Memory Proxy` can be Codex-facing or used in pipelines (e.g. `drift` reconciliation)
- Outputs should be validated when surfaced to prevent outdated logic being reused
- Memory fragments may be embedded or quoted as Codex prompt scaffolds

---

### 9 Pipeline Integration

- **Coordination Mechanics:**
  - `FrameStore`: Used before LLM invocation to insert summary/notes into prompts
  - `Memory Proxy`: Called during Drift to recover and surface prior reasoning
  - Compatible with `Run/Drift Tracker`, `DriftDiff`, `Fork Agent`

- **Integration Points:**
  - Upstream: `summarize_documents`, `.intent.md` writers
  - Downstream: `Codex prompt engine`, `reconciliation routines`

- **Risks:**
  - Injected memory may contain outdated tradeoffs — always cite with timestamps
  - Future expansion may require intent embedding or retrieval confidence scoring

---

### 🧠 Tags

@ai-role: memory  
@ai-intent: support reflective, memory-aware agent behaviors  
@ai-cadence: drift-preferred  
@ai-risk-recall: medium  
@ai-semantic-scope: .intent.md, prompt context  
@ai-coordination: simulated memory injection + recall  
