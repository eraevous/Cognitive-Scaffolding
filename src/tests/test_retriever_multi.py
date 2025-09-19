import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from core.retrieval import retriever as retriever_mod


class DummyStore:
    def search(self, vec, k):
        val = float(vec.flatten()[0])
        if val == 0.0:
            return [(10, 0.9), (20, 0.5)]
        else:
            return [(20, 0.8), (30, 0.4)]


def test_query_multi_aggregate(tmp_path, monkeypatch):
    r = retriever_mod.Retriever.__new__(retriever_mod.Retriever)
    r.store = DummyStore()
    r.model = "dummy"
    r.id_map = {10: "docA_chunk00", 20: "docA_chunk01", 30: "docB_chunk00"}
    r.chunk_dir = tmp_path

    (tmp_path / "docA_chunk00.txt").write_text("A00")
    (tmp_path / "docA_chunk01.txt").write_text("A01")
    (tmp_path / "docB_chunk00.txt").write_text("B00")

    def fake_embed(text, model="dummy"):
        return [0.0] if text == "foo" else [1.0]

    monkeypatch.setattr(retriever_mod, "embed_text", fake_embed)

    results = r.query_multi(["foo", "bar"], k=2, return_text=True, aggregate=True)

    assert results[0][0] == "docA"
    assert "A00" in results[0][2] and "A01" in results[0][2]
    assert results[1][0] == "docB"
