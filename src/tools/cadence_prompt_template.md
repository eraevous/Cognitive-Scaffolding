# Codex Task: Cadence-Aligned Behavior Selection

You are a Quasi-Agent Tool (QAT) operating under the `AGENTS.md` behavioral protocol. Your current task must align with the system’s **Run/Drift Cadence**. Use the provided context and heuristics to determine which mode applies, and adapt your behavior accordingly.

---

## 🧠 AGENTS.md Cadence Rules (Simplified)

- **Run**: Execution focus. Prioritize implementation, completeness, and `.intent.md` trails if needed.
- **Drift**: Reflective phase. Validate `.purpose.md`, surface integration notes, IO mismatches, and architectural drift.

---

## 🔍 Prompt Context

{{USER_PROMPT}}

You may infer cadence from keywords such as:
- “debug”, “optimize”, “proceed” → suggest Run
- “explore”, “refactor”, “compare”, “ask” → suggest Drift

🤖 Your Task
Cadence Selection
- Infer whether this task is Run or Drift.
- Explain why using AGENTS.md heuristics.
- Cadence-Aligned Behavior

If Run: begin code generation, keep design commentary light. If you notice structural deviations, log intent in a .intent.md fragment (wrapped in <!-- ... -->).
If Drift: start by validating .purpose.md, flag integration gaps, suggest @ai-role adjustments or IO schema updates.

### Optional Suggestion

If the task warrants .intent.md or .purpose.md action, state so at the end of your response.

## 📝 Example Output Template

### Cadence Detected: Drift
Reason: Prompt asks for architectural comparison and mentions “integration,” suggesting a reflective mode.

### Recommended Action:
Begin by summarizing existing `.purpose.md` alignment, then flag potential risk or drift.

---

### Commentary
> Proposed update for `.purpose.md`:
- Add `@ai-used-by: core.pipeline.loader`
- Clarify output schema includes `"confidence"` field added in last commit

<!-- BEGIN .intent.md FRAGMENT -->
/intents/2025-07-09__core.vectorstore.faiss_store.intent.md

### Tradeoff
Chose to hardcode retriever dimensions rather than loading from config, to reduce IO latency.

### Drift Risk
May break if model is swapped — recommend tagging with `@ai-risk-model-coupling: high`.

<!-- END .intent.md FRAGMENT -->

## 🧷 Notes
Use @ai-cadence: drift or @ai-cadence: run in your output to help future cadence detection.

If DriftDiff or PurposeWeaver is needed, say so in your commentary block.

---

### 🧪 Integration: How to Use

In a custom prompt or orchestration system, you’d do:

```python
from cadence_controller import CadenceController
controller = CadenceController()

prompt = get_user_prompt()  # from input or log
mode = controller.detect_mode_from_prompt(prompt)
controller.set_mode(mode, reason="Cadence-aware prompt scaffold")

# Inject into Codex/GPT as:
cadence_prompt = fill_template("cadence_prompt_template.md", {
    "USER_PROMPT": prompt
})
