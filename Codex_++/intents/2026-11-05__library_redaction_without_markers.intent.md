# Intent · library/ · redaction without markers (2026-11-05)

@ai-cadence: run
@ai-intent: keep removed personal details unguessable in a public library

The first library contract marked each redaction in place and named its category in the note's
`edits` field. Read together with the surrounding sentence, a marker plus a category lets a reader
infer what was removed, so the redaction protects less than it appears to.

Changed to: remove the detail so the sentence reads on its own, no in-place marker, and record only a
count in `edits`. Trade-off: a reader loses the signal that the text was altered at that exact spot;
the `edits` count keeps the alteration honest at the note level, which is enough for provenance.

A note whose substance is a model's reading of the owner as a person is left out of the public
library entirely rather than redacted; it belongs in a private instantiation if anywhere.
