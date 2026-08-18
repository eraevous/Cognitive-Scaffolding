import json
import zipfile
from pathlib import Path

from core.workflows import chatgpt_corpus


def _write_export(path: Path, assistant_text: str = "Useful answer") -> Path:
    conversations = [
        {
            "id": "conv-1",
            "title": "Semantic Drift",
            "create_time": 1710000000.0,
            "update_time": 1710000100.0,
            "current_node": "3",
            "mapping": {
                "1": {
                    "id": "1",
                    "parent": None,
                    "message": {
                        "author": {"role": "system"},
                        "content": {"parts": ["System prompt"]},
                    },
                },
                "2": {
                    "id": "2",
                    "parent": "1",
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Where did this idea go?"]},
                    },
                },
                "3": {
                    "id": "3",
                    "parent": "2",
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": [assistant_text]},
                    },
                },
            },
        }
    ]
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("conversations.json", json.dumps(conversations))
    return path


def test_ingest_chatgpt_export_manifest_and_skip(tmp_path, monkeypatch):
    calls = []

    def fake_generate_embeddings(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(
        chatgpt_corpus, "generate_embeddings", fake_generate_embeddings
    )

    export_path = _write_export(tmp_path / "export.zip")
    root = tmp_path / "corpus"

    first = chatgpt_corpus.ingest_chatgpt_export(export_path, root)

    assert first.total == 1
    assert first.written == 1
    assert first.skipped == 0
    assert first.embedded is True
    assert calls[0]["source_dir"] == root / "parsed" / "chatgpt"
    assert calls[0]["segment_mode"] is True
    assert calls[0]["vector_name"] == "default"

    manifest = json.loads(first.manifest_path.read_text(encoding="utf-8"))
    record = manifest["records"]["conv_1"]
    parsed_path = root / record["parsed_path"]
    assert parsed_path.exists()
    assert "USER: Where did this idea go?" in parsed_path.read_text(encoding="utf-8")
    assert record["message_count"] == 2

    (root / "vector").mkdir(exist_ok=True)
    (root / "vector" / "mosaic.index").write_text("stub", encoding="utf-8")
    calls.clear()

    second = chatgpt_corpus.ingest_chatgpt_export(export_path, root)

    assert second.written == 0
    assert second.skipped == 1
    assert second.embedded is False
    assert calls == []


def test_ingest_chatgpt_export_rewrites_changed_conversation(tmp_path, monkeypatch):
    monkeypatch.setattr(chatgpt_corpus, "generate_embeddings", lambda **kwargs: None)

    export_path = _write_export(tmp_path / "export.zip", assistant_text="First")
    root = tmp_path / "corpus"
    chatgpt_corpus.ingest_chatgpt_export(export_path, root)

    _write_export(export_path, assistant_text="Second")
    result = chatgpt_corpus.ingest_chatgpt_export(export_path, root)

    assert result.written == 1
    assert result.skipped == 0


def test_repair_chatgpt_embeddings_appends_missing_vectors(tmp_path, monkeypatch):
    calls = []

    def fake_generate_embeddings(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(
        chatgpt_corpus, "generate_embeddings", fake_generate_embeddings
    )

    failure_path = chatgpt_corpus.repair_chatgpt_embeddings(tmp_path)

    assert failure_path == tmp_path / "vector" / "embedding_failures.json"
    assert calls[0]["source_dir"] == tmp_path / "parsed" / "chatgpt"
    assert calls[0]["reset_index"] is False
    assert calls[0]["segment_mode"] is True


def test_semantic_chunking_uses_named_vector_profile(tmp_path, monkeypatch):
    calls = []

    def fake_generate_embeddings(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(
        chatgpt_corpus, "generate_embeddings", fake_generate_embeddings
    )

    export_path = _write_export(tmp_path / "export.zip")
    root = tmp_path / "corpus"

    chatgpt_corpus.ingest_chatgpt_export(
        export_path,
        root,
        semantic_chunking=True,
        index_name="semantic",
    )

    assert calls[0]["segment_mode"] is True
    assert calls[0]["vector_name"] == "semantic"
    assert calls[0]["chunk_dir"] == root / "vector" / "semantic" / "chunks"
    assert calls[0]["out_path"] == (
        root / "vector" / "semantic" / "rich_doc_embeddings.json"
    )


def test_rebuild_chatgpt_embeddings_resets_index(tmp_path, monkeypatch):
    calls = []

    def fake_generate_embeddings(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(
        chatgpt_corpus, "generate_embeddings", fake_generate_embeddings
    )

    failure_path = chatgpt_corpus.rebuild_chatgpt_embeddings(
        tmp_path,
        semantic_chunking=False,
        index_name="regular",
    )

    assert failure_path == tmp_path / "vector" / "regular" / "embedding_failures.json"
    assert calls[0]["source_dir"] == tmp_path / "parsed" / "chatgpt"
    assert calls[0]["reset_index"] is True
    assert calls[0]["segment_mode"] is False
    assert calls[0]["vector_name"] == "regular"
