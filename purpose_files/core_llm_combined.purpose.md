# Module: core.llm
> Summarization and prompt-routing layer for OpenAI-powered document interpretation, supporting chatlogs and standard text inputs.

### 🎯 Intent & Responsibility
- Generate structured summaries of documents using OpenAI models.
- Dynamically select and format prompts based on document type (`standard` or `chatlog`).
- Encapsulate and test OpenAI interactions for consistency and reliability.

### 📥 Inputs & 📤 Outputs
| Direction | Name            | Type                  | Brief Description                                                   |
|-----------|-----------------|-----------------------|----------------------------------------------------------------------|
| 📥 In     | text             | str                   | Input document or conversation transcript                            |
| 📥 In     | doc_type         | Literal["standard", "chatlog"] | Determines the base prompt format to apply                  |
| 📥 In     | prompt_override  | Optional[str]         | User-defined prompt (with `{text}` placeholder)                     |
| 📥 In     | model            | str                   | OpenAI model (default: `gpt-4`)                                      |
| 📥 In     | config           | Optional[RemoteConfig]| API credentials and configuration                                   |
| 📤 Out    | result           | dict                  | Structured JSON summary with fields like `summary`, `topics`, etc.  |

### 🔗 Dependencies
- `openai`, `json`, `pathlib`
- `core.config.remote_config` – for OpenAI API key
- Local `prompts/` directory for standard and chatlog prompt templates

### ⚙️ AI-Memory Tags
- `@ai-assumes:` Prompt files exist and contain a `{text}` placeholder.
- `@ai-breakage:` Malformed prompt formatting or changes in OpenAI output structure can break parsing.
- `@ai-risks:` GPT response may fail to conform to JSON schema; may require retry logic or fallbacks.

### 🗣 Dialogic Notes
- Prompt routing enables flexible experimentation—use `prompt_override` to test new summarization styles.
- Parsing failures raise clearly surfaced exceptions, but no retry mechanism exists yet.
- This is the primary bridge between raw content and metadata extraction in the classification pipeline.
