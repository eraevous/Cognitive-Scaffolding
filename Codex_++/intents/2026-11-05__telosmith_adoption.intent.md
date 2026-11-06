# Intent · repo · Telosmith adoption (2026-11-05)

@ai-cadence: run
@ai-intent: bring this repo onto Telosmith records, the same way the other Kairos repos were brought on

Codex++ began here; Telosmith (formerly AEC) is its successor. This adds Telosmith in the form the other
repos use: `aec init` records (an authority, a provisional purpose `P0` anchored to the README), three
requirements linked to the code that implements them (parsing, embedding and retrieval, synthesis with memory
frames), a pointer record to the private decisions that govern the repo, the Claude Code hook, and a CI job
pinned to the Telosmith commit that generated it (f961902).

Trade-offs:
- The 42 Codex++ `.purpose.md` files were **not** imported. `aec import-purpose` would add 84 provisional
  records, and its dry run reports many purpose files whose declared dependencies no longer match the code or
  whose source has moved. Importing them would turn stale claims into records. Import selectively once a
  module's purpose file has been checked against its code.
- `.gitignore` ignores every `*.json`. The hook file is exempted, so the hook is actually committed.
- Pinned to a commit rather than a release tag, because v0.5.0 is not tagged yet. Move the pin to the tag
  when it exists.
