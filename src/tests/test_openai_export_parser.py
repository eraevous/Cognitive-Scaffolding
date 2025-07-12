import json
import zipfile
import sys
import pytest
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from core.parsing.openai_export import parse_chatgpt_export


def make_export_zip(tmp_path: Path) -> Path:
    conversations = [
        {
            "title": "Test Chat",
            "current_node": "3",
            "mapping": {
                "1": {
                    "id": "1",
                    "parent": None,
                    "children": ["2"],
                    "message": {
                        "author": {"role": "system"},
                        "content": {"content_type": "text", "parts": ["You are ChatGPT"]},
                    },
                },
                "2": {
                    "id": "2",
                    "parent": "1",
                    "children": ["3"],
                    "message": {
                        "author": {"role": "user"},
                        "content": {"content_type": "text", "parts": ["Hello"]},
                    },
                },
                "3": {
                    "id": "3",
                    "parent": "2",
                    "children": [],
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"content_type": "text", "parts": ["Hi!"]},
                    },
                },
            },
        }
    ]
    export_zip = tmp_path / "export.zip"
    with zipfile.ZipFile(export_zip, "w") as zf:
        zf.writestr("conversations.json", json.dumps(conversations))
    return export_zip


def make_nested_export_zip(tmp_path: Path) -> Path:
    """Create a zip where conversations.json is under a folder."""
    conversations: List[Dict[str, object]] = [
        {"title": "Nested", "current_node": None, "mapping": {}}
    ]
    export_zip = tmp_path / "nested.zip"
    with zipfile.ZipFile(export_zip, "w") as zf:
        zf.writestr(
            "ChatGPT Export/conversations.json", json.dumps(conversations)
        )
    return export_zip


def test_parse_export(tmp_path: Path):
    export_zip = make_export_zip(tmp_path)
    out_dir = tmp_path / "out"
    results = parse_chatgpt_export(export_zip, out_dir)
    assert len(results) == 1
    convo_file = out_dir / "0000_test_chat.txt"
    prompt_file = out_dir / "prompts" / "0000_test_chat_prompts.txt"
    assert convo_file.exists()
    assert prompt_file.exists()
    assert "USER: Hello" in convo_file.read_text()
    assert prompt_file.read_text().strip() == "Hello"
    
def test_parse_export_markdown(tmp_path: Path):
    export_zip = make_export_zip(tmp_path)
    out_dir = tmp_path / "out_md"
    results = parse_chatgpt_export(export_zip, out_dir, markdown=True)
    assert len(results) == 1
    convo_file = out_dir / "0000_test_chat.md"
    assert convo_file.exists()
    text = convo_file.read_text()
    assert "**User:** Hello" in text or "**USER:** Hello" in text


def test_parse_export_nested_dir(tmp_path: Path):
    export_zip = make_nested_export_zip(tmp_path)
    out_dir = tmp_path / "out_nested"
    results = parse_chatgpt_export(export_zip, out_dir)
    assert len(results) == 1
    convo_file = out_dir / "0000_nested.txt"
    assert convo_file.exists()


def test_parse_export_handles_missing_messages(tmp_path: Path, monkeypatch):
    export_zip = make_export_zip(tmp_path)

    def fake_extract_messages(_):
        return None

    monkeypatch.setattr(
        "core.parsing.openai_export._extract_messages", fake_extract_messages
    )
    out_dir = tmp_path / "out_err"
    with pytest.raises(ValueError):
        parse_chatgpt_export(export_zip, out_dir)


def test_extract_messages_skips_invalid_nodes(tmp_path: Path):
    export_zip = make_export_zip(tmp_path)
    # modify export to include a malformed node
    with zipfile.ZipFile(export_zip, "a") as zf:
        conversations = json.loads(zf.read("conversations.json"))
        malformed = conversations[0]
        malformed["mapping"]["3"]["message"] = None
        zf.writestr("conversations.json", json.dumps(conversations))
    out_dir = tmp_path / "out_skip"
    parse_chatgpt_export(export_zip, out_dir)
    convo_file = out_dir / "0000_test_chat.txt"
    assert convo_file.exists()
    text = convo_file.read_text().strip()
    assert text == "USER: Hello"

def test_extract_messages_ignores_nonstring_parts(tmp_path: Path):
    export_zip = make_export_zip(tmp_path)
    # modify export to include a dict part representing an image
    with zipfile.ZipFile(export_zip, "a") as zf:
        conversations = json.loads(zf.read("conversations.json"))
        convo = conversations[0]
        convo["mapping"]["3"]["message"]["content"]["parts"] = [
            {"content_type": "image"},
            "Hi!",
        ]
        zf.writestr("conversations.json", json.dumps(conversations))
    out_dir = tmp_path / "out_img"
    parse_chatgpt_export(export_zip, out_dir)
    convo_file = out_dir / "0000_test_chat.txt"
    assert convo_file.exists()
    lines = [line.strip() for line in convo_file.read_text().splitlines()]
    assert lines[-1] == "ASSISTANT: Hi!"

