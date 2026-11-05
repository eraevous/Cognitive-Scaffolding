# Library

A persistent, public home for the owner's **foundation artifacts**: framework notes, syntheses,
interpretations and captured threads. Until now these were re-assembled on demand from
ChatGPT memory-synthesis ("Dreaming") requests. Here they get a fixed text, a provenance header
and an index, so that people and agents can cite a file instead of re-asking a model.

This folder holds documents only. Nothing in `src/` reads it, and the engineering rules in
[CHARTER.md](../CHARTER.md) do not apply to it. [AGENTS.md](../AGENTS.md) still governs how agents
work here, and this contract adds to it.

## What belongs here

- **Foundation artifacts**: framework notes and specs the owner treats as reference points
  (for example GATE-M, Dual-Channel Coding, Adaptive Cognitive Scaffolding).
- **Syntheses**: model or mixed write-ups that pull several sources together.
- **Interpretations**: readings of the owner's work, his intent or another artifact, by a model
  or a person.
- **Captured threads** that the owner chooses to publish.

## What never belongs here

- Private coordination records: handoffs, ledgers, decision or challenge logs, or their text
  and ids.
- Thread or session URLs, and anything carrying a session id.
- Personal data about anyone, including the owner: health, finances, contact details,
  location, family, employment specifics. Remove it so the sentence still reads, with no
  marker at the spot, and record only the count in `edits` ("removed two personal details"),
  never the category. A marker or a category next to the text it replaced tells a reader what
  was taken out. If a note is built around such details, leave the whole note out.
- Names of private individuals. Model names are fine; name reviewers by role ("a GPT reviewer",
  "a Claude reviewer").
- Credentials, API keys and tokens, and private repository paths.

If you are unsure, leave it out and ask the owner.

## Layout

```
library/
  README.md        this contract
  INDEX.md         one row per artifact
  foundations/     framework notes and their source conversations
  syntheses/       later cross-source syntheses and studies
```

File names are kebab-case and stable. If an artifact is replaced, keep the old file and set
its `status` to `superseded`.

## Provenance header (required)

Every artifact starts with YAML front matter:

```yaml
---
title: "Human-readable title"
source: "vault: <note name>"  |  "thread: <thread name>"  |  "Dreaming request <YYYY-MM-DD>"
captured: "YYYY-MM-DD"        # date of the content if the content shows it, else "unknown"
author: zach | model:<name> | mixed
evidence_class: source-grounded | model-synthesis | mixed | interpretation
edited_by: "<who>"            # who changed the text after capture
edits: "<what was changed>"   # e.g. "added header only", "redacted one personal detail"
status: foundation | synthesis | interpretation | superseded
owner_position: true | false | unconfirmed
note: "<optional one-line caution>"
---
```

Field meanings:

- **author**: who wrote the *text*. `model:<name>` covers text a model wrote, even when it
  articulates the owner's ideas. Use `mixed` when both voices are present (a conversation, or a
  prompt the owner and a model drafted together). Say in a preface which parts are whose.
- **evidence_class**:
  - `source-grounded`: the claims rest on cited primary material.
  - `model-synthesis`: a model assembled or articulated the ideas.
  - `mixed`: both of the above.
  - `interpretation`: a reading of someone's intent or work, which may be wrong.
- **status**:
  - `foundation`: a reference artifact.
  - `synthesis`: a working combination of sources.
  - `interpretation`: a reading.
  - `superseded`: replaced, and kept for lineage.
- **edits**: list every change made after capture, including redactions and Markdown repairs.
  Content is otherwise copied verbatim.

## Model text is not the owner's position

A note with `author: model:*` or `evidence_class: model-synthesis | interpretation` is **not**
the owner's position, however confidently it is written or however much it addresses him as
"you". It becomes his position only if he marks it so, by setting `owner_position: true` in a
commit he makes or approves. Quote such notes as "a model synthesis says…", never as "the owner
holds…".

## How new items arrive

1. **The owner pastes or commits the item.** He adds the file with its header and an
   `INDEX.md` row.
2. **An authorized agent opens a PR.** The agent commits on a branch with the header filled,
   the redactions listed in `edits`, and the `INDEX.md` row added. It opens a PR and does not
   merge it; the owner reviews and merges. *Agent write path: authorization pending under the owner's rule that information crosses freely between agents but authority never crosses implicitly.*
   Until that is settled, each agent PR needs the owner's explicit request.

Before any item is published, someone must read all of it. Do not publish what nobody has read.

## Index convention

`INDEX.md` has one row per artifact, ordered by folder and then by title. Its columns are:
title (linked), status, author, source, date (`captured`) and a one-line gist. The gist says
what the artifact *is*, not whether it is right. Update the index in the same commit that adds,
renames or supersedes an artifact.
