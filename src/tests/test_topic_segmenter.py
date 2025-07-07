import os
import logging
import sys
from pathlib import Path
import pytest

import types

sys.modules.setdefault(
    "faiss",
    types.SimpleNamespace(
        IndexIDMap=object,
        IndexFlatIP=object,
        write_index=lambda *a, **k: None,
        read_index=lambda *a, **k: None,
    ),
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tiktoken
from core.parsing.semantic_chunk import semantic_chunk_text


def stub_embed_text(text: str, model: str = "text-embedding-3-small"):
    if "Cats" in text:
        return [0.0]
    return [10.0]


def test_boundary_detection_and_logging(monkeypatch, caplog):
    os.environ["LOG_LEVEL"] = "DEBUG"
    class DummyEncoding:
        def encode(self, text, disallowed_special=()):
            return text.split()

        def decode(self, tokens):
            return " ".join(tokens)

    monkeypatch.setattr(tiktoken, "encoding_for_model", lambda model: DummyEncoding())
    monkeypatch.setattr("core.parsing.semantic_chunk.embed_text", stub_embed_text)
    sample_text = ("Cats purr. " * 20) + ("Python codes. " * 20)
    with caplog.at_level(logging.DEBUG):
        chunks = semantic_chunk_text(
            sample_text,
            window_tokens=10,
            step_tokens=5,
            n_clusters=2,
        )
    assert len(chunks) >= 2
    assert "Cats" in chunks[0]
    assert "Python" in chunks[-1]
    assert any("Detected boundaries" in r.message for r in caplog.records)
