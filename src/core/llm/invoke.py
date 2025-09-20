""" Module: core.llm.invoke 
- @ai-path: core.llm.invoke
- @ai-source-file: core/llm/invoke.py     
- @ai-module: invoke     
- @ai-role: summarizer     
- @ai-entrypoint: false     
- @ai-intent: "Summarizes input text using a GPT model, formatted by standard or chatlog-style prompts."

🔍 Summary: 
This utility function generates a summary for a given `text` input using an OpenAI model, applying either a default or custom prompt template. 
It supports special formatting for chatlog-style documents and dynamically loads the appropriate prompt template from disk. 
The function sends the prompt to the OpenAI API and parses the result as a JSON object. If parsing fails, it raises a descriptive error.

📦 Inputs:

- text (str): The full string content to be summarized.
- doc_type (Literal["standard", "chatlog"]): Determines which base prompt to use.
- model (str): The model ID to use for OpenAI completion (e.g., "gpt-4").
- prompt_override (Optional[str]): A custom prompt template with a `{text}` placeholder.
- config (Optional[RemoteConfig]): Configuration object with OpenAI API key access.

📤 Outputs:

- dict: Parsed JSON summary returned by the OpenAI completion.

🔗 Related Modules:

- load_prompt
- run_openai_completion
- RemoteConfig.from_file
- json.loads

🧠 For AI Agents:

- @ai-dependencies: json, openai, core.config.remote_config
- @ai-calls: load_prompt, run_openai_completion, json.loads, RemoteConfig.from_file
- @ai-uses: config.openai_api_key, json.JSONDecodeError
- @ai-tags: summarization, LLM, prompt, OpenAI, completion

⚙️ Meta:     
- @ai-version: 0.2.0     
- @ai-generated: true     
- @ai-verified: false

📝 Human Collaboration:     
- @human-reviewed: false     
- @human-edited: false     
- @last-commit:     
- @change-summary: Initial AI-generated docstring with static + semantic alignment     
- @notes: """

import json
from pathlib import Path
from typing import Literal, Optional

import tiktoken
from openai import OpenAI

from core.config.remote_config import RemoteConfig
from core.constants import (
    ERROR_BUDGET_EXCEEDED,
    ERROR_OPENAI_RESPONSE_NOT_JSON,
    ERROR_PROMPT_FILE_NOT_FOUND,
)
from core.utils.budget_tracker import get_budget_tracker

PROMPT_DIR = Path(__file__).parent / "prompts"

LLM_PROMPT_COST_PER_1K = {
    "gpt-4": 0.03,
    "gpt-4o": 0.005,
}
LLM_COMPLETION_COST_PER_1K = {
    "gpt-4": 0.06,
    "gpt-4o": 0.015,
}


def load_prompt(prompt_name: str) -> str:
    path = PROMPT_DIR / f"{prompt_name}.txt"
    if not path.exists():
        raise FileNotFoundError(
            ERROR_PROMPT_FILE_NOT_FOUND.format(path=path)
        )
    return path.read_text(encoding="utf-8")


def run_openai_completion(
    prompt: str,
    model: str = "gpt-4",
    temperature: float = 0.4,
    max_tokens: int = 700,
    api_key: Optional[str] = None,
) -> str:
    client = OpenAI(api_key=api_key or RemoteConfig.from_file().openai_api_key)
    tracker = get_budget_tracker()

    if tracker:
        enc = tiktoken.encoding_for_model(model)
        prompt_tokens = len(enc.encode(prompt, disallowed_special=()))
        est_cost = prompt_tokens / 1000 * LLM_PROMPT_COST_PER_1K.get(
            model, 0
        ) + max_tokens / 1000 * LLM_COMPLETION_COST_PER_1K.get(model, 0)
        if not tracker.check(est_cost):
            raise RuntimeError(ERROR_BUDGET_EXCEEDED)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def summarize_text(
    text: str,
    doc_type: Literal["standard", "chatlog"] = "standard",
    model: str = "gpt-4",
    prompt_override: Optional[str] = None,
    config: Optional[RemoteConfig] = None,
) -> dict:
    config = config or RemoteConfig.from_file()

    if prompt_override:
        prompt = prompt_override.format(text=text)
    else:
        prompt_file = "chatlog_summary" if doc_type == "chatlog" else "summary"
        base_prompt = load_prompt(prompt_file)
        prompt = base_prompt.format(text=text)

    raw_response = run_openai_completion(
        prompt=prompt, model=model, temperature=0.4, api_key=config.openai_api_key
    )

    try:
        return json.loads(raw_response)
    except json.JSONDecodeError as e:
        raise ValueError(
            ERROR_OPENAI_RESPONSE_NOT_JSON.format(response=raw_response)
        ) from e


# test_core_llm_invoke.py


def test_summarize_text_standard():
    example_text = """
    This document describes the future of automation and how workers can adapt to changes in the economy. It touches on AI ethics, retraining, and the emotional journey of letting go of obsolete skills.
    """
    result = summarize_text(example_text, doc_type="standard")
    assert isinstance(result, dict)
    assert "summary" in result
    assert isinstance(result.get("topics", []), list)


def test_summarize_text_chatlog():
    example_chat = """
    User: I'm feeling stuck about my job.
    Assistant: Can you tell me more about what's been happening?
    User: I just feel like I'm not valued anymore. My company is automating everything.
    Assistant: That sounds really difficult. Do you feel like your skills are being overlooked?
    """
    result = summarize_text(example_chat, doc_type="chatlog")
    assert isinstance(result, dict)
    assert result.get("category") == "chatlog"
    assert "summary" in result
