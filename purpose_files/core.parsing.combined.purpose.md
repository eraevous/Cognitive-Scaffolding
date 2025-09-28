# Module: core.parsing
> Extract, chunk, and normalize document content for LLM-safe ingestion across file formats and workflows.

### 🎯 Intent & Responsibility
- Extract raw text from various file formats (.txt, .md, .pdf, .docx) for processing.
- Identify latent topic boundaries via embedding-based clustering before chunking.
- Produce semantic-aware text chunks and normalize filenames for safe downstream use.

### 📥 Inputs & 📤 Outputs
| Direction | Name         | Type            | Brief Description                                                                 |
|-----------|--------------|-----------------|------------------------------------------------------------------------------------|
| 📥 In     | filepath      | str             | Path to local document file                                                        |
| 📥 In     | text          | str             | Raw extracted text from file (for chunking)                                       |
| 📥 In     | name          | str             | Arbitrary string label to normalize                                               |
| 📤 Out    | raw_text      | str             | Cleaned full text extracted from file                                             |
| 📤 Out    | chunks        | List[str]       | Paragraph-preserving text chunks (within character limits)                        |
| 📤 Out    | normalized    | str             | Identifier-safe version of input string                                           |

### 🔗 Dependencies
- `fitz` (PyMuPDF), `python-docx`, `markdown`, `os`
- `openai`, `numpy`, `scikit-learn` for embedding-based segmentation

### ⚙️ AI-Memory Tags
- `@ai-assumes:` Input documents are well-formed and parsable by library of choice.
- `@ai-breakage:` PDF/Word libraries may fail silently if dependencies are missing or input is malformed.
- `@ai-risks:` Chunking by paragraph could overflow token limits if paragraphs are excessively long.

### 🗣 Dialogic Notes
- The parser uses different strategies per file extension, failing clearly if unsupported.
- Chunking preserves structure when possible; long paragraphs still split arbitrarily.
- Normalization is simple and irreversible (loss of case/formatting); designed for ID safety.
- Future extensions could add support for HTML/EPUB and fallback token-based chunking for edge cases.
- New `semantic_chunk_text` function performs window embedding, clustering, and boundary detection to create topic-coherent segments.
- `topic_segmenter` combines `semantic_chunk_text` with paragraph fallback for embedding workflows.

### 9 Pipeline Integration
- @ai-pipeline-order: inverse
- **Coordination Mechanics:** Parsing functions supply normalized filenames and semantic chunks consumed by `core.embeddings.embedder`.
- **Integration Points:** Outputs route through `core.retrieval.retriever` and Synthesizer modules; TokenMap Analyzer uses chunk metadata.
- **Risks:** Mis-segmented text may degrade embedding quality; large files increase clustering cost.
