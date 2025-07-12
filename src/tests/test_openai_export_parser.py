import json
import zipfile
import sys
from pathlib import Path

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
