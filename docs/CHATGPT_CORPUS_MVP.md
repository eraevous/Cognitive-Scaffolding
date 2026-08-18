# ChatGPT Corpus MVP

This is the narrow MVP path for turning a ChatGPT data export into a singular, searchable, synthesis-supporting local corpus.

## Local-First Recrawl

```powershell
kairos chatgpt ingest "C:\path\to\export.zip" --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --no-embed
```

The ingest command:

- reads modern sharded ChatGPT exports such as `conversations-000.json`
- writes parsed transcripts to `parsed/chatgpt`
- writes per-conversation metadata to `metadata/chatgpt`
- writes `metadata/chatgpt/chatgpt_manifest.json`
- skips unchanged conversations on rerun using content hashes
- skips title-only or empty conversations

## Private Local Search

```powershell
kairos search lexical "cognitive scaffolding" --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --k 10
```

This command does not call an external API. It searches parsed transcripts on disk and returns scored conversation IDs, titles, and snippets.

Save the output as an inspectable Markdown artifact:

```powershell
kairos search lexical "cognitive scaffolding" --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --k 10 --out "C:\Users\Admin\Documents\Kairos\chatgpt_corpus\output\lexical-search"
```

## Private Extractive Synthesis

```powershell
kairos synthesize lexical "cognitive scaffolding" --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --k 8
```

This command does not call an external API. It produces an extractive throughline from the top local hits.

Save the output:

```powershell
kairos synthesize lexical "cognitive scaffolding" --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --k 8 --out "C:\Users\Admin\Documents\Kairos\chatgpt_corpus\output\lexical-synthesis"
```

## Semantic Search Opt-In

Semantic FAISS search requires embeddings. For this private ChatGPT corpus, that means sending transcript chunks to the configured embedding provider. Only run this after explicitly accepting that data egress.

Estimated size for the 2026-05-04 export tested during the MVP pass:

- conversations in export: 2,836
- parsed non-empty transcripts: 2,834
- approximate embedding tokens: 45.1M
- estimated `text-embedding-3-small` embedding cost: about $0.90

Once embeddings are built, semantic search can use:

```powershell
kairos search semantic "cognitive scaffolding" --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --text --aggregate --k 10
```

Semantic results include the score, stable conversation ID, chunk number when applicable, conversation title, and snippet text when `--text` is set.

Save semantic results:

```powershell
kairos search semantic "cognitive scaffolding" --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --text --aggregate --k 10 --out "C:\Users\Admin\Documents\Kairos\chatgpt_corpus\output\semantic-search"
```

## Semantic Chunking Default

New ChatGPT corpus embedding builds use semantic topic-boundary chunking by default. To rebuild the default index from already parsed transcripts:

```powershell
kairos chatgpt rebuild-embeddings --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus"
```

To compare against regular size/window chunks without overwriting the default index, build a named regular profile:

```powershell
kairos chatgpt rebuild-embeddings --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --no-semantic-chunking --index-name regular
```

Search or synthesize against a named profile with:

```powershell
kairos search semantic "cognitive scaffolding" --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --index-name regular --text --aggregate --k 10
```

```powershell
kairos synthesize query "cognitive scaffolding" --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --index-name regular --k 20 --max-input-tokens 50000
```

Semantic chunking changes retrieval behavior: results should align better to topic boundaries and synthesis should receive cleaner excerpts, but long conversations may produce fewer, larger chunks and some exact local context can shift. A rebuild requires a fresh embedding pass. For the 2026-05-04 export, expect roughly another `$0.90` of `text-embedding-3-small` embedding cost.

If an embedding run fails on one or more files, the failed items are written to:

```text
C:\Users\Admin\Documents\Kairos\chatgpt_corpus\vector\embedding_failures.json
```

After lowering the batch token cap or fixing the cause, repair only the missing embeddings without rebuilding the whole index:

```powershell
kairos chatgpt repair-embeddings --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus"
```

For synthesis over semantic hits, use:

```powershell
kairos synthesize query "cognitive scaffolding" --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --k 8 --max-input-tokens 50000
```

This sends only the selected, token-budgeted search-hit excerpts to the configured chat model and asks for cited synthesis using source labels like `[S1]`.

Save semantic synthesis:

```powershell
kairos synthesize query "cognitive scaffolding" --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --k 8 --max-input-tokens 50000 --out "C:\Users\Admin\Documents\Kairos\chatgpt_corpus\output\semantic-synthesis"
```

Use a source file as the synthesis basis:

```powershell
kairos synthesize file "C:\path\to\source.docx" --root "C:\Users\Admin\Documents\Kairos\chatgpt_corpus" --k 20 --max-input-tokens 50000 --out "C:\Users\Admin\Documents\Kairos\chatgpt_corpus\output\semantic-file-synthesis"
```

This extracts text from `.txt`, `.md`, `.pdf`, or `.docx`, embeds the extracted source text, retrieves related corpus conversations, and synthesizes those retrieved hits.

When `--out` points to a directory, Kairos creates a timestamped Markdown file. When `--out` includes a filename extension, Kairos writes exactly to that file.

## Next Execution Steps

1. Add a reranker or hybrid lexical+semantic mode after the basic output is reliable.

2. Harden operations
   - Rotate any API key that appeared in local config.
   - Prefer `OPENAI_API_KEY` or an untracked local config file.
   - Add a secret scan check before publishing.

3. Package the MVP
   - Document the exact ingest/search/synthesis demo flow.
   - Add a small sample export fixture for tests.
   - Create a portfolio-ready demo script that uses a non-private toy corpus.
