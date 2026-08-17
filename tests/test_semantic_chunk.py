import hashlib
import sys
import types
from typing import List

import numpy as np
import pytest


class DummyEncoding:
    def encode(self, text: str, disallowed_special=()):  # noqa: D401
        del disallowed_special
        return text.split()

    def decode(self, tokens: List[str]):
        return " ".join(tokens)


sys.modules.setdefault(
    "tiktoken",
    types.SimpleNamespace(
        encoding_for_model=lambda model: DummyEncoding(),
        get_encoding=lambda name: DummyEncoding(),
    ),
)


from core.parsing import semantic_chunk as sc  # noqa: E402


def _patch_tokenizer(monkeypatch):
    monkeypatch.setattr(sc, "_get_tokenizer", lambda model: DummyEncoding())


def _patch_embeddings(monkeypatch, fn):
    monkeypatch.setattr(sc, "embed_text_batch", fn)
    monkeypatch.setattr(sc, "embed_text", lambda text, model="": fn([text], model=model)[0])


def test_short_doc_single_chunk(monkeypatch):
    _patch_tokenizer(monkeypatch)

    def stub(texts, model="", embedder=None):
        del model, embedder
        return [[float(len(text)), 0.0] for text in texts]

    _patch_embeddings(monkeypatch, stub)

    chunks = sc.semantic_chunk("short text", window_tokens=8, step_tokens=4)
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk["start"] == 0
    assert chunk["end"] == 2
    assert chunk["cluster_id"] is None
    assert chunk["window_ids"] == [0]
    assert chunk["topic_change_score"] == pytest.approx(0.0)
    assert chunk["sha256"] == hashlib.sha256("short text".encode("utf-8")).hexdigest()


def test_digression_preserved(monkeypatch):
    _patch_tokenizer(monkeypatch)

    def stub(texts, model="", embedder=None):
        del model, embedder
        vectors = []
        for text in texts:
            if "digress" in text.lower():
                vectors.append([0.0, 1.0])
            else:
                vectors.append([1.0, 0.0])
        return vectors

    _patch_embeddings(monkeypatch, stub)

    text = "main topic flow main topic flow digress tiny note main topic flow"
    chunks = sc.semantic_chunk(
        text,
        window_tokens=4,
        step_tokens=2,
        change_point_cosine_tau=0.5,
    )
    assert any("digress" in chunk["text"].lower() for chunk in chunks)
    digression = next(chunk for chunk in chunks if "digress" in chunk["text"].lower())
    assert digression["topic_change_score"] >= 0.5


def test_max_chunk_tokens_guard_split(monkeypatch):
    _patch_tokenizer(monkeypatch)

    def stub(texts, model="", embedder=None):
        del model, embedder
        return [[1.0, 0.0] for _ in texts]

    _patch_embeddings(monkeypatch, stub)

    text = " ".join(f"t{i}" for i in range(12))
    chunks = sc.semantic_chunk(
        text,
        window_tokens=2,
        step_tokens=2,
        change_point_cosine_tau=1.0,
        max_chunk_tokens=4,
        min_chunk_tokens=2,
    )
    assert len(chunks) == 3
    for chunk in chunks:
        assert (chunk["end"] - chunk["start"]) <= 4


def test_adaptive_mode_assigns_clusters(monkeypatch):
    _patch_tokenizer(monkeypatch)

    def stub(texts, model="", embedder=None):
        del model, embedder
        return [[1.0, 0.0] for _ in texts]

    _patch_embeddings(monkeypatch, stub)

    class DummyUMAP:
        def __init__(self, *args, **kwargs):
            pass

        def fit_transform(self, X):
            return X

    class DummySpectral:
        def __init__(self, *args, **kwargs):
            pass

        def fit_predict(self, X):
            return np.asarray([0, 1, 1, 0])

    class DummyHDBSCAN:
        def __init__(self, *args, **kwargs):
            pass

        def fit_predict(self, X):
            return np.asarray([-1, 1, 1, 2])

    monkeypatch.setattr(sc, "umap", type("UmapNS", (), {"UMAP": lambda *a, **k: DummyUMAP()})())
    monkeypatch.setattr(sc, "SpectralClustering", DummySpectral)
    monkeypatch.setattr(sc, "hdbscan", type("HDB", (), {"HDBSCAN": lambda *a, **k: DummyHDBSCAN()})())

    text = " ".join(f"t{i}" for i in range(16))
    base_kwargs = dict(
        window_tokens=2,
        step_tokens=2,
        change_point_cosine_tau=1.0,
        max_chunk_tokens=4,
        min_chunk_tokens=2,
        mode="adaptive",
    )

    spectral_chunks = sc.semantic_chunk(text, cluster_method="spectral", **base_kwargs)
    assert len(spectral_chunks) == 4
    assert [chunk["cluster_id"] for chunk in spectral_chunks] == [0, 1, 1, 0]

    hdbscan_chunks = sc.semantic_chunk(text, cluster_method="hdbscan", **base_kwargs)
    assert len(hdbscan_chunks) == 4
    assert [chunk["cluster_id"] for chunk in hdbscan_chunks] == [0, 1, 1, 2]


def test_batching_respects_batch_size(monkeypatch):
    _patch_tokenizer(monkeypatch)
    call_sizes: List[int] = []

    def stub(texts, model="", embedder=None):
        del model, embedder
        call_sizes.append(len(texts))
        return [[float(len(text))] for text in texts]

    _patch_embeddings(monkeypatch, stub)

    text = " ".join(f"t{i}" for i in range(12))
    sc.semantic_chunk(
        text,
        window_tokens=2,
        step_tokens=2,
        change_point_cosine_tau=1.0,
        max_chunk_tokens=4,
        min_chunk_tokens=2,
        batch_size=2,
    )
    assert call_sizes == [2, 2, 2, 2, 1]
