import json
import random
import time

from core.config import REMOTE_CONFIG_PATH, RemoteConfig

from core.logger import get_logger
from core.storage.aws_clients import get_lambda_client, get_s3_client

"""
📦 Module: core_lib.utils.lambda_summary
- @ai-path: core_lib.utils.lambda_summary
- @ai-source-file: combined_utils.py
- @ai-role: Lambda Summarizer
- @ai-intent: "Trigger AWS Lambda summarization using Claude for either standard or chat-style documents."

🔍 Module Summary:
This module enables asynchronous document summarization by invoking a Claude-connected AWS Lambda. 
It supports both standard document input and specialized chat log summarization with prompt formatting. 
It includes retry logic, structured result unpacking, and error handling for malformed Lambda responses.

🗂️ Contents:

| Name                   | Type     | Purpose                                                   |
|:------------------------|:---------|:----------------------------------------------------------|
| invoke_summary          | Function | Summarize standard documents via Lambda.                  |
| invoke_chatlog_summary  | Function | Summarize chat logs with structured Claude prompt design.  |
| unpack_lambda_claude_result | Function | Safely parse Lambda payloads into usable metadata.     |

🧠 For AI Agents:
- @ai-dependencies: boto3, json, time, random
- @ai-uses: remote, BUCKET_NAME, LAMBDA_NAME, get_s3_client, decode, encode
- @ai-tags: lambda, summarization, retry, json-parsing, AWS

⚙️ Meta:
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add Lambda Claude summarization logic with fallback handling
- @change-summary: Introduced dual-mode summarization functions + result unpacking
- @notes: ""

👤 Human Overview:
    - Context: Used when documents or chat logs need automatic summarization without local inference costs.
    - Change Caution: AWS limits on payload size or malformed JSON responses could cause failures.
    - Future Hints: Add circuit-breaker logic after repeated Lambda failures to prevent downstream corruption.
"""

remote = RemoteConfig.from_file(REMOTE_CONFIG_PATH)

lambda_client = get_lambda_client(region=remote.region)
logger = get_logger(__name__)


def invoke_summary(s3_filename: str, override_text: str = None) -> str:
    key = f"{remote.prefixes['parsed']}{s3_filename}"

    payload = {
        "bucket": remote.bucket_name,
        "key": key,
    }

    if override_text:
        payload["text"] = override_text

    for attempt in range(5):
        try:
            response = lambda_client.invoke(
                FunctionName=remote.lambda_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload).encode("utf-8"),
                LogType="Tail",
            )
            return response["Payload"].read().decode("utf-8")
        except Exception as e:
            wait = 2 + random.random() * 2
            logger.warning("Retrying (%d/5) after error: %s", attempt + 1, e)
            time.sleep(wait)

    return json.dumps({"error": "Exceeded retries", "key": key})


def invoke_chatlog_summary(s3_filename: str) -> str:
    s3 = get_s3_client()
    key = f"{s3_filename}"

    prompt_text = (
        s3.get_object(Bucket=remote.bucket_name, Key=key)["Body"].read().decode("utf-8")
    )

    body = {
        "messages": [
            {
                "role": "user",
                "content": f"""
                This is a conversation between a user and ChatGPT. Summarize the overall interaction.

                Return JSON with:
                - summary
                - topics (list of covered topics)
                - category (should be \"chatlog\")
                - tags (list)
                - themes (list of emotional, intellectual, or philosophical topics)
                - priority (0–5, with 5 being the most important and 0 showing no imperatives or required actions in the conversation)  
                - tone (reflective / playful / analytical / etc.)
                - depth (personal / technical / philosophical)
                - stage (e.g., question, exploration, resolution)

                Text:

                {prompt_text}
                """,
            }
        ],
        "max_tokens": 700,
        "temperature": 0.4,
        "anthropic_version": "bedrock-2023-05-31",
    }

    response = lambda_client.invoke(
        FunctionName="remote.lambda_name",
        InvocationType="RequestResponse",
        Payload=json.dumps({"bucket": remote.bucket_name, "key": key}).encode("utf-8"),
        LogType="Tail",
    )

    return response["Payload"].read().decode("utf-8")


def unpack_lambda_claude_result(raw_payload: str):
    try:
        parsed = json.loads(raw_payload)

        if (
            isinstance(parsed, dict)
            and "body" in parsed
            and isinstance(parsed["body"], str)
        ):
            try:
                return json.loads(parsed["body"])
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse Lambda 'body' JSON: {e}")

        return parsed

    except Exception as e:
        raise ValueError(f"Failed to parse Claude payload: {e}\nRaw:\n{raw_payload}")
