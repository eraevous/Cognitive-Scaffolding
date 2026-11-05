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

## Revision: extraction instead of redaction (same day)

After a cross-model review, the owner chose that the public library publishes reusable artifacts
*extracted* from conversations rather than the conversations themselves; Dreaming stages
candidates privately; adoption is recorded per claim, with a document-level middle position.
The contract now separates origin, staging, publication and adoption as four steps with four
authorities, and adds `document_type`, `adoption` and `reviewed` to the header.

Trade-off: the public library starts smaller (seven artifacts) and loses the conversational
lineage that showed how ideas formed. That lineage is kept privately, where it can be richer than
any public text without exposing context. Redaction remains only for small details in otherwise
reusable texts; a text built around personal or private-coordination substance is extracted from
or kept private, because removing identifiers does not remove private meaning.
