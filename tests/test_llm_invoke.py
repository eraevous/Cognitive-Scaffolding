import json
import sys
import types
from types import SimpleNamespace

import pytest


class _DummyEncoding:
    def encode(self, prompt: str, disallowed_special=()):
        return prompt.encode("utf-8")


def _encoding_for_model(model: str):
    return _DummyEncoding()


dummy_tiktoken = types.ModuleType("tiktoken")
dummy_tiktoken.encoding_for_model = _encoding_for_model
sys.modules.setdefault("tiktoken", dummy_tiktoken)

dummy_openai = types.ModuleType("openai")


class _DummyChoice:
    def __init__(self, content: str):
        self.message = SimpleNamespace(content=content)


class _DummyCompletionResponse:
    def __init__(self, content: str):
        self.choices = [_DummyChoice(content)]


class _DummyChatCompletions:
    def create(self, **kwargs):  # pragma: no cover - stub
        return _DummyCompletionResponse("{}")


class _DummyClient:
    def __init__(self, *args, **kwargs):  # pragma: no cover - stub
        self.chat = SimpleNamespace(completions=_DummyChatCompletions())


dummy_openai.OpenAI = _DummyClient
sys.modules.setdefault("openai", dummy_openai)

from core.llm import invoke


@pytest.fixture
def fake_config():
    return SimpleNamespace(openai_api_key="test-key")


def test_summarize_text_standard(monkeypatch, fake_config):
    def fake_load_prompt(name: str) -> str:
        assert name == "summary"
        return "Summarize: {text}"

    def fake_run_openai_completion(*, prompt, model, temperature, api_key):
        assert prompt == "Summarize: example"
        assert model == "gpt-4"
        assert temperature == 0.4
        assert api_key == "test-key"
        return json.dumps({"summary": "ok", "topics": ["ai", "skills"]})

    monkeypatch.setattr(invoke, "load_prompt", fake_load_prompt)
    monkeypatch.setattr(invoke, "run_openai_completion", fake_run_openai_completion)

    result = invoke.summarize_text("example", doc_type="standard", config=fake_config)

    assert result == {"summary": "ok", "topics": ["ai", "skills"]}


def test_summarize_text_chatlog(monkeypatch, fake_config):
    def fake_load_prompt(name: str) -> str:
        assert name == "chatlog_summary"
        return "Chatlog: {text}"

    def fake_run_openai_completion(*, prompt, model, temperature, api_key):
        assert prompt.startswith("Chatlog: User: I'm feeling stuck")
        assert model == "gpt-4"
        assert temperature == 0.4
        assert api_key == "test-key"
        return json.dumps({"summary": "chat summary", "category": "chatlog"})

    monkeypatch.setattr(invoke, "load_prompt", fake_load_prompt)
    monkeypatch.setattr(invoke, "run_openai_completion", fake_run_openai_completion)

    chat_text = """User: I'm feeling stuck about my job.\nAssistant: Let's talk."""
    result = invoke.summarize_text(chat_text, doc_type="chatlog", config=fake_config)

    assert result == {"summary": "chat summary", "category": "chatlog"}
