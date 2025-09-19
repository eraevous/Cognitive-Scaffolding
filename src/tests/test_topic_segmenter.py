import logging
import os
import sys
import types
from pathlib import Path

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

from core.parsing.semantic_chunk import semantic_chunk


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
    import importlib

    sc_module = importlib.import_module("core.parsing.semantic_chunk")
    monkeypatch.setattr(sc_module, "embed_text", stub_embed_text)

    class DummyUMAP:
        def fit_transform(self, X):
            return X

    class DummySC:
        def __init__(self, *a, **k):
            pass

        def fit_predict(self, X):
            half = len(X) // 2
            import numpy as np

            return np.asarray([0] * half + [1] * (len(X) - half))

    import importlib

    sc_module = importlib.import_module("core.parsing.semantic_chunk")
    monkeypatch.setattr(
        sc_module, "umap", types.SimpleNamespace(UMAP=lambda *a, **k: DummyUMAP())
    )
    monkeypatch.setattr(sc_module, "SpectralClustering", DummySC)
    monkeypatch.setattr(
        sc_module, "hdbscan", types.SimpleNamespace(HDBSCAN=lambda *a, **k: DummySC())
    )

    sample_text = ("Cats purr. " * 20) + ("Python codes. " * 20)
    with caplog.at_level(logging.DEBUG):
        chunks = semantic_chunk(
            sample_text,
            window_tokens=10,
            step_tokens=5,
        )
    assert len(chunks) >= 2
    assert chunks[0]["cluster_id"] == 0
    assert chunks[-1]["cluster_id"] == 1
    assert any("segments" in r.message for r in caplog.records)
