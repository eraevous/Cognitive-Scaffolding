import json
import sys
from pathlib import Path

import pytest

from core.config import config_registry
from core.config.path_config import PathConfig
from core.embeddings import embedder

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

pytest.importorskip("faiss")


def test_generate_embeddings_no_overflow(tmp_path, monkeypatch):
    # setup custom paths
    paths = PathConfig(root=tmp_path)
    paths.raw = tmp_path / "raw"
    paths.parsed = tmp_path / "parsed"
    paths.metadata = tmp_path / "metadata"
    paths.output = tmp_path / "output"
    paths.vector = tmp_path / "vector"
    paths.raw.mkdir()
    paths.parsed.mkdir()
    paths.vector.mkdir()

    # create a sample text file
    (paths.parsed / "example.txt").write_text("hello world", encoding="utf-8")

    # patch configuration and embedding function
    monkeypatch.setattr(
        config_registry, "get_path_config", lambda force_reload=False: paths
    )
    monkeypatch.setattr(embedder, "get_path_config", lambda force_reload=False: paths)
    monkeypatch.setattr(
        embedder,
        "embed_text",
        lambda text, model="text-embedding-3-small": [0.0] * embedder.MODEL_DIMS[model],
    )

    embedder.generate_embeddings(model="text-embedding-3-small")

    id_map_path = paths.vector / "id_map.json"
    assert id_map_path.exists()
    id_map = json.loads(id_map_path.read_text())
    for hashed in id_map.keys():
        assert int(hashed) < 2**63


def test_generate_embeddings_with_segments(tmp_path, monkeypatch):
    paths = PathConfig(root=tmp_path)
    paths.parsed = tmp_path / "parsed"
    paths.vector = tmp_path / "vector"
    paths.parsed.mkdir()
    paths.vector.mkdir()
    (paths.parsed / "example.txt").write_text("hello world", encoding="utf-8")

    monkeypatch.setattr(
        config_registry, "get_path_config", lambda force_reload=False: paths
    )
    monkeypatch.setattr(embedder, "get_path_config", lambda force_reload=False: paths)

    dummy_chunk = {
        "text": "hello world",
        "embedding": [0.0] * embedder.MODEL_DIMS["text-embedding-3-large"],
        "topic": "topic_0",
        "start": 0,
        "end": 2,
        "cluster_id": 0,
    }
    import importlib

    sc_module = importlib.import_module("core.parsing.semantic_chunk")
    monkeypatch.setattr(
        sc_module,
        "semantic_chunk",
        lambda text, model="text-embedding-3-large", **k: [dummy_chunk],
    )

    embedder.generate_embeddings(model="text-embedding-3-large", segment_mode=True)

    chunk_file = paths.vector / "chunks" / "example_chunk00.json"
    assert chunk_file.exists()
    data = json.loads(chunk_file.read_text())
    assert data["text"] == "hello world"
    assert "embedding" in data


def test_generate_embeddings_named_vector_profile(tmp_path, monkeypatch):
    paths = PathConfig(root=tmp_path)
    paths.parsed = tmp_path / "parsed"
    paths.vector = tmp_path / "vector"
    paths.parsed.mkdir()
    paths.vector.mkdir()
    (paths.parsed / "example.txt").write_text("hello world", encoding="utf-8")

    monkeypatch.setattr(embedder, "get_path_config", lambda force_reload=False: paths)
    monkeypatch.setattr(
        embedder,
        "embed_text_batch",
        lambda texts, model="text-embedding-3-small", **kwargs: [
            [0.0] * embedder.MODEL_DIMS[model] for _ in texts
        ],
    )

    embedder.generate_embeddings(
        model="text-embedding-3-small",
        vector_name="semantic",
        out_path=None,
    )

    assert (paths.vector / "semantic" / "mosaic.index").exists()
    assert (paths.vector / "semantic" / "id_map.json").exists()
    assert (paths.vector / "semantic" / "rich_doc_embeddings.json").exists()


def test_embed_text_batch_splits_large_batches(monkeypatch):
    calls = []

    class DummyEncoding:
        def encode(self, text, disallowed_special=()):
            return [0] * int(text)

    class DummyEmbeddings:
        def create(self, input, model):
            calls.append(list(input))

            class Response:
                data = [type("Embedding", (), {"embedding": [1.0]})() for _ in input]

            return Response()

    class DummyClient:
        embeddings = DummyEmbeddings()

    monkeypatch.setattr(embedder, "_get_encoding", lambda model: DummyEncoding())
    monkeypatch.setattr(embedder, "_get_client", lambda: DummyClient())
    monkeypatch.setattr(embedder, "get_budget_tracker", lambda: None)
    monkeypatch.setattr(embedder, "MAX_EMBED_BATCH_TOKENS", 10)

    vectors = embedder.embed_text_batch(["6", "6", "3"], model="text-embedding-3-small")

    assert len(vectors) == 3
    assert calls == [["6"], ["6", "3"]]
