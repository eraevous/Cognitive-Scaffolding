#__________________________________________________________________
# File: __init__.py
# No docstring found


#__________________________________________________________________
# File: budget_tracker.py
# No docstring found

from pathlib import Path
import json
import time
import os


class BudgetTracker:
    """Track and limit API spending across operations."""

    def __init__(self, max_usd: float, log_path: Path | None = None):
        self.max_usd = max_usd
        self.log_path = log_path
        self.spent = 0.0
        self.month = time.strftime("%Y-%m")

    def check(self, cost: float) -> bool:
        now = time.strftime("%Y-%m")
        if now != self.month:
            self.reset(now)
        if self.spent + cost > self.max_usd:
            return False
        self.spent += cost
        self._persist()
        return True

    def reset(self, month: str | None = None) -> None:
        self.month = month or time.strftime("%Y-%m")
        self.spent = 0.0
        self._persist()

    def _persist(self) -> None:
        if not self.log_path:
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump({"month": self.month, "spent": self.spent}, f)


_instance: "BudgetTracker | None" = None


def get_budget_tracker() -> "BudgetTracker | None":
    """Return a singleton ``BudgetTracker`` from environment variables.

    Environment variables:
    - ``OPENAI_BUDGET_USD``: monthly budget limit in dollars.
    - ``OPENAI_BUDGET_LOG``: optional path to persist spend log.
    """
    global _instance
    if _instance is None:
        budget = os.getenv("OPENAI_BUDGET_USD")
        if budget:
            log_path = Path(os.getenv("OPENAI_BUDGET_LOG", "budget_log.json"))
            _instance = BudgetTracker(float(budget), log_path=log_path)
        else:
            _instance = None
    return _instance
#__________________________________________________________________
# File: dedup.py
# No docstring found

from pathlib import Path


def dedup_lines_in_folder(folder: Path, output_file: Path) -> None:
    """Collect unique lines from all *.txt files in ``folder`` and write them.

    Lines are stripped of trailing newlines. Empty lines are ignored.
    The resulting file is sorted alphabetically.
    """
    unique = set()
    for txt_file in folder.glob("*.txt"):
        with txt_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    unique.add(line)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as out:
        for line in sorted(unique):
            out.write(line + "\n")

#__________________________________________________________________
# File: lambda_summary.py
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


import json
import random
import time
from pathlib import Path

from config.remote_config import RemoteConfig

from core.storage.aws_clients import get_lambda_client, get_s3_client

remote = RemoteConfig.from_file()

lambda_client = get_lambda_client(region=remote.region)


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
                LogType="Tail"
            )
            return response["Payload"].read().decode("utf-8")
        except Exception as e:
            wait = 2 + random.random() * 2
            print(f"[red]Retrying ({attempt+1}/5) after error: {e}[/red]")
            time.sleep(wait)

    return json.dumps({"error": "Exceeded retries", "key": key})


def invoke_chatlog_summary(s3_filename: str) -> str:
    s3 = get_s3_client()
    key = f"{PARSED_PREFIX}{s3_filename}"

    prompt_text = s3.get_object(Bucket=remote.bucket_name, Key=key)['Body'].read().decode('utf-8')

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
"""
            }
        ],
        "max_tokens": 700,
        "temperature": 0.4,
        "anthropic_version": "bedrock-2023-05-31"
    }

    response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps({"bucket": BUCKET_NAME, "key": key}).encode("utf-8"),
        LogType="Tail"
    )
    return response["Payload"].read().decode("utf-8")


def unpack_lambda_claude_result(raw_payload: str):
    try:
        parsed = json.loads(raw_payload)

        if isinstance(parsed, dict) and "body" in parsed and isinstance(parsed["body"], str):
            try:
                return json.loads(parsed["body"])
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse Lambda 'body' JSON: {e}")

        return parsed

    except Exception as e:
        raise ValueError(f"Failed to parse Claude payload: {e}\nRaw:\n{raw_payload}")#__________________________________________________________________
# File: logger.py
# No docstring found

import logging
import os


def setup_logging() -> None:
    """Configure basic logging once."""
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=getattr(logging, level, logging.INFO),
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger with standard config."""
    setup_logging()
    return logging.getLogger(name)
