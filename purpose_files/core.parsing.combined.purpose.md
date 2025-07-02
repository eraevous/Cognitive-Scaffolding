# Module: core.parsing
> Extract, chunk, and normalize document content for LLM-safe ingestion across file formats and workflows.

### 🎯 Intent & Responsibility
- Extract raw text from various file formats (.txt, .md, .pdf, .docx) for processing.
- Chunk large documents into manageable, paragraph-preserving segments for LLM input.
- Normalize filenames and document identifiers for safe downstream usage.

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
- Only standard libraries used for chunking and normalization

### ⚙️ AI-Memory Tags
- `@ai-assumes:` Input documents are well-formed and parsable by library of choice.
- `@ai-breakage:` PDF/Word libraries may fail silently if dependencies are missing or input is malformed.
- `@ai-risks:` Chunking by paragraph could overflow token limits if paragraphs are excessively long.

### 🗣 Dialogic Notes
- The parser uses different strategies per file extension, failing clearly if unsupported.
- Chunking preserves structure when possible; long paragraphs still split arbitrarily.
- Normalization is simple and irreversible (loss of case/formatting); designed for ID safety.
- Future extensions could add support for HTML/EPUB and fallback token-based chunking for edge cases.
