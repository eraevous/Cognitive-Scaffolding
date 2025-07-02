 # Module: core.utils.lambda_summary
> Invokes AWS Lambda functions for Claude-powered summarization of documents and chat logs, with robust payload handling and retry logic.

### 🎯 Intent & Responsibility
- Submit document content to a Claude-connected AWS Lambda for summarization.
- Handle both standard documents and conversational chatlogs with distinct prompt structures.
- Parse, retry, and safely decode potentially malformed Lambda responses.

### 📥 Inputs & 📤 Outputs
| Direction | Name             | Type         | Brief Description                                                                 |
|-----------|------------------|--------------|------------------------------------------------------------------------------------|
| 📥 In     | s3_filename       | str          | S3 key or filename of parsed text in cloud storage                                |
| 📥 In     | override_text     | Optional[str]| Raw text to substitute instead of pulling from S3                                 |
| 📤 Out    | raw_response      | str          | Claude-generated JSON string returned by Lambda                                   |
| 📤 Out    | unpacked_metadata | dict         | Parsed and structured metadata result (summary, tags, tone, etc.)                 |

### 🔗 Dependencies
- `boto3`, `json`, `time`, `random`
- `core.storage.aws_clients.get_lambda_client`, `get_s3_client`
- `core.config.remote_config.RemoteConfig`

### ⚙️ AI-Memory Tags
- `@ai-assumes:` AWS Lambda function is deployed correctly and can accept the provided payload structure.
- `@ai-breakage:` Hardcoded field names in `prompt` or payloads may desync with model/lambda expectations.
- `@ai-risks:` Lambda failure or invalid JSON responses may corrupt pipeline unless caught with fallback logic.

### 🗣 Dialogic Notes
- This system enables LLM-powered summaries without incurring local inference costs.
- Claude-specific prompting logic is embedded in `invoke_chatlog_summary`, while `invoke_summary` is general-purpose.
- `unpack_lambda_claude_result` anticipates nested or malformed payloads and attempts safe recovery.
- Useful for cost-splitting summarization workflows across local/cloud compute.
