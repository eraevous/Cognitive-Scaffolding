import sys
from pathlib import Path

from core.retrieval import retriever as retriever_mod

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


class DummyStore:
    def search(self, vec, k):
        return [(10, 0.9)]


def test_query_file(tmp_path, monkeypatch):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello")

    r = retriever_mod.Retriever.__new__(retriever_mod.Retriever)
    r.store = DummyStore()
    r.model = "dummy"
    r.id_map = {10: "docA"}
    r.chunk_dir = None

    monkeypatch.setattr(retriever_mod, "embed_text", lambda text, model="dummy": [0.0])

    results = r.query_file(file_path, k=1)
    assert results == [("docA", 0.9)]
