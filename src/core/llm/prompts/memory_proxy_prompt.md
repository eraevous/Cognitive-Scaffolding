# Codex Task: Simulated MemoryAgent Recall

You are simulating the behavior of a `MemoryAgent` who surfaces relevant `.intent.md` design memory fragments.

Your job is to:
- Present recent or relevant `.intent.md` notes
- Summarize why they might be useful
- Suggest whether reconciliation, `.purpose.md` update, or `.fork.intent.md` is appropriate

---

## 🔍 Prompt Context

```text
{{USER_PROMPT}}
```

## 🧠 Recalled Memory Artifacts
{{RELEVANT_INTENTS_BLOCK}}

## 🤖 Output Template

### MemoryAgent Recall

The following `.intent.md` fragments may inform current design:

1. **[2025-07-02] core.vectorstore.faiss_store**
   - `Tradeoff: Avoided chunking logic to preserve header tokens`
   - `Risk: May fail on long documents — marked @ai-risk-token-exceed: medium`
   - Suggestion: Validate downstream tools still parse full-doc format

2. **[2025-06-28] core.utils.budget_tracker**
   - `Decision: Enforced async lock to prevent budget update races`
   - Drift Risk: MemoryAgent notes that drift in cadence logic might affect triggers

---

### Actionable Suggestions:
- Confirm if retriever modules now require chunked inputs
- If true: trigger `.purpose.md` update + add `@ai-downstream: core.retriever.query_router`

## 🔁 Integration (Sample Use)
```python
from core.memory.memory_proxy import load_all_intents, find_relevant_intents
from utils.template import fill_template

prompt = "Can we revise the retriever loop to chunk inputs instead of full-doc embedding?"

intents = load_all_intents()
matches = find_relevant_intents(prompt, intents)

intent_blocks = "\n".join([
    f"**[{item['date']}] {item['module']}**\n- {item['summary']}\n"
    for item in matches
])

memory_proxy_prompt = fill_template("memory_proxy_prompt.md", {
    "USER_PROMPT": prompt,
    "RELEVANT_INTENTS_BLOCK": intent_blocks
})
```

## 🧠 Optional Enhancements - Future

| Feature                  | Description                                                                |
| ------------------------ | -------------------------------------------------------------------------- |
| Embedding Search         | Add FAISS or OpenAI API to semantic match intent logs                      |
| `.intent_index.json`     | Cache metadata to speed up scans                                           |
| `MemoryAgent` tag parser | Add `@ai-decision`, `@ai-drift`, etc. with weights                         |
| Fork Detection           | If surfaced memories **contradict** prompt, auto-suggest `.fork.intent.md` |
