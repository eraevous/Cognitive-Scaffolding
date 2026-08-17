# Intent: Align Cognitive Scaffold with kAIros Obsidian Notes

## Trigger

The project needed an explicit alignment pass against relevant thoughts from the local kAIros Obsidian vault, especially notes about Cognitive Scaffold, QAT, metadata schemas, recursive vault ingestion, and conceptual drift.

## Decision

Treat Cognitive Scaffold as a semantic compass for nonlinear thought, not merely a document search pipeline. The roadmap should prioritize refinding ideas across drifted titles, preserving provenance, enriching metadata, and making Obsidian/vault ingestion a first-class use case.

## Scope

- Add `docs/OBSIDIAN_ALIGNMENT.md` as the distilled bridge from vault notes to repo direction.
- Update README framing to mention refinding drifting ideas and link to the alignment note.
- Update VISION to name conceptual refinding and drift-aware retrieval explicitly.
- Update TASKS with Obsidian-aligned implementation tasks.

## Follow-Up Work

- Implement recursive Markdown/vault ingestion with incremental modified-file extraction.
- Expand metadata schema for counts, dates, source paths, stages, tone/depth, and exploration trails.
- Add corpus-wide deduplication with provenance-preserving references.
- Add concept-trail synthesis over retrieved chunks, clusters, paths, and timestamps.
- Define QAT field modes: `strict`, `optional`, and `inferred`.
