import sys
from pathlib import Path

from core.retrieval import retriever as retriever_mod
from core.synthesis import summarize_documents


class DummyIndex:
    def __init__(self, *a, **k):
        pass


class DummyFaiss:
    IndexIDMap = IndexFlatIP = DummyIndex


sys.modules["faiss"] = DummyFaiss()

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_summarize_documents(monkeypatch):
    monkeypatch.setattr(
        retriever_mod.Retriever,
        "__init__",
        lambda self, store=None, model=None, chunk_dir=None: None,
    )
    r = retriever_mod.Retriever()

    def fake_query(text, k=1, return_text=False):
        return [(text, 0.0, f"text for {text}")]

    def fake_summarize(text, doc_type="standard"):
        return {"summary": text}

    monkeypatch.setattr(r, "query", fake_query)
    monkeypatch.setattr(r, "get_chunk_text", lambda identifier: f"text for {identifier}")
    monkeypatch.setattr("core.synthesis.summarizer.summarize_text", fake_summarize)

    result = summarize_documents(["a", "b"], r)
    assert "text for a" in result and "text for b" in result
