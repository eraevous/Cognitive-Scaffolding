# .aec: purpose and justification records (Telosmith, formerly AEC)

- `records.jsonl`: append-only reasoning records (purpose, requirements, claims, evidence, decisions,
  authorities). Never edit a line; append a new version. Vocabulary:
  https://github.com/eraevous/Telosmith/blob/main/docs/reasoning-vocabulary.md
- `edges.jsonl`: the structural snapshot of the code (`aec edges`). Generated, so it is git-ignored
  (`.aec/.gitignore`): regenerate it rather than committing or hand-editing it.
- `snippets/`: a Claude Code hook and a CI job to copy into place. Nothing here is active until you do.

Start by replacing the purpose stub `P0` with a new version stating what this project is for, in your
own words (`"version": 2`, `"epistemic": "provisional"` while you are still discovering it,
`"committed"` once changes to it should need your authorization).

All Telosmith results are structural: they show what changed and what relied on it, not whether the
remaining evidence is good enough. That stays a review question.
