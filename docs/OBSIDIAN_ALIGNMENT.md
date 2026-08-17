# Obsidian Alignment Notes

This document distills project-relevant thoughts from the local Obsidian vault into concrete Cognitive Scaffold direction. It is not a dump of the vault; it is a working alignment layer for product framing, roadmap choices, and future implementation tasks.

## Source Notes Reviewed

- `AI Workflow/Dev/Cognitive Scaffold/PHASE 0 - Strategic Alignment.md`
- `AI Workflow/Dev/Cognitive Scaffold/What we have and where we're going.md`
- `AI Workflow/Cognitive-Scaffolding/VISION.md`
- `AI Workflow/Cognitive-Scaffolding/Notes and Next-Steps - Mid-July Pause.md`
- `AI Workflow/Minimalist Cognitive Scaffold Schema.md`
- `AI Workflow/Cognitive-Scaffolding/New Schema.md`
- `AI Workflow/Cognitive-Scaffolding/Project Architecture - Unified Master Document.md`
- `AI Workflow/Cognitive-Scaffolding/Notes on the project.md`
- `AI Workflow/Cognitive-Scaffolding/QAT_Quickstart.md`

## Product Thesis

Cognitive Scaffold should be framed as a semantic compass for nonlinear thought: a tool for refinding, reassembling, and synthesizing ideas that drift across notes, conversations, documents, and code.

The core user problem is not simple file search. The problem is conceptual drift: valuable thoughts often begin in one context and end somewhere else. The project should preserve that wandering while making the latent connections recoverable.

## Alignment Principles

- Preserve nonlinear thought instead of forcing premature taxonomy.
- Treat metadata as memory: summaries, topics, tags, provenance, counts, dates, and exploration trails should make recall easier later.
- Support progressive disclosure: simple CLI defaults first, with deeper schema and configuration hooks available for power users.
- Prefer affordable cloud AI calls with caching, budget tracking, and fallback behavior.
- Keep the tool portfolio-grade: the demo should show product thinking, RAG architecture, AI workflow design, and user empathy.
- Keep QAT and purpose files AI-readable: tool contracts should distinguish strict fields, optional fields, and safe inferred fields.

## Roadmap Implications

1. Obsidian/vault ingestion
   - Add recursive directory crawl for Markdown-heavy vaults.
   - Preserve source paths, headings, frontmatter, modified timestamps, and backlinks where possible.
   - Extract only new or modified conversations/documents when rerunning ingestion.

2. Richer metadata schema
   - Expand metadata beyond summary/topics/tags to include token count, word count, prompt/message counts, dates, source file, parsed file, stage, tone, depth, and exploration trails.
   - Pass metadata into clustering and synthesis instead of treating it as a side artifact.

3. Corpus-wide deduplication
   - Move deduplication from isolated prompt files toward whole-corpus repeated text and repeated conversation fragments.
   - Track provenance instead of deleting evidence blindly.

4. Drift-aware retrieval and synthesis
   - Support "where did this idea show up elsewhere?" queries across unrelated source titles.
   - Add cluster-based synthesis first, then graph-based synthesis once the relationship model is stable.
   - Expose concept trails that show how an idea evolves across files, topics, or time.

5. Cognitive episode support
   - Add lightweight run/session records that capture immediate goal, assumptions, inputs, outputs, dependencies, and end-of-session distillation.
   - Keep this optional so the system remains useful for ordinary batch ingestion.

## Near-Term Documentation Tasks

- Update README language to emphasize conceptual refinding, drift resolution, and Obsidian/vault use.
- Add purpose-file guidance for field modes: `strict`, `optional`, and `inferred`.
- Add a demo narrative that shows a query starting from an unrelated title and ending in a latent conceptual throughline.
- Add an implementation intent for Obsidian recursive ingestion and incremental modified-file extraction.
