import sys
from pathlib import Path

from core.retrieval import retriever as retriever_mod
from core.synthesis import summarize_documents
from core.synthesis.summarizer import synthesize_file, synthesize_query


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
    monkeypatch.setattr("core.synthesis.summarizer.summarize_text", fake_summarize)

    result = summarize_documents(["a", "b"], r)
    assert "text for a" in result and "text for b" in result


def test_synthesize_query_uses_retrieved_text(monkeypatch):
    r = retriever_mod.Retriever.__new__(retriever_mod.Retriever)

    def fake_query_rich(text, k=8, return_text=False, aggregate=False):
        assert text == "semantic drift"
        assert return_text is True
        assert aggregate is True
        return [
            {
                "doc_id": "conv_1",
                "title": "Semantic Drift",
                "score": 0.9,
                "text": "USER: idea\nASSISTANT: throughline",
            }
        ]

    def fake_summarize(text, doc_type="standard", prompt_override=None):
        assert "[S1] Semantic Drift" in text
        assert "conv_1" in text
        assert "throughline" in text
        assert prompt_override == "{text}"
        return {"summary": "synthesized throughline"}

    monkeypatch.setattr(r, "query_rich", fake_query_rich)
    monkeypatch.setattr("core.synthesis.summarizer.summarize_text", fake_summarize)

    assert synthesize_query("semantic drift", r) == "synthesized throughline"


def test_synthesize_query_caps_sources_to_budget(monkeypatch):
    r = retriever_mod.Retriever.__new__(retriever_mod.Retriever)

    def fake_query_rich(text, k=120, return_text=False, aggregate=False):
        return [
            {
                "doc_id": f"conv_{idx}",
                "title": f"Conversation {idx}",
                "score": 1.0,
                "text": "long source text " * 200,
            }
            for idx in range(120)
        ]

    captured = {}

    def fake_summarize(text, doc_type="standard", prompt_override=None):
        captured["text"] = text
        return {"summary": "budgeted"}

    monkeypatch.setattr(r, "query_rich", fake_query_rich)
    monkeypatch.setattr("core.synthesis.summarizer.summarize_text", fake_summarize)

    assert synthesize_query("familiar", r, k=120, max_input_tokens=6400) == "budgeted"
    assert "[S1]" in captured["text"]
    assert "[S49]" not in captured["text"]
    assert len(captured["text"]) <= 6400 * 4


def test_synthesize_file_uses_source_file_for_retrieval(tmp_path, monkeypatch):
    source = tmp_path / "source.md"
    source.write_text("familiar hearth notes", encoding="utf-8")
    r = retriever_mod.Retriever.__new__(retriever_mod.Retriever)

    def fake_query_file_rich(file_path, k=8, return_text=False, aggregate=False):
        assert Path(file_path) == source
        assert k == 4
        assert return_text is True
        assert aggregate is True
        return [
            {
                "doc_id": "conv_1",
                "title": "Familiar Notes",
                "score": 0.8,
                "text": "A relevant excerpt.",
            }
        ]

    def fake_summarize(text, doc_type="standard", prompt_override=None):
        assert "Source file: source.md" in text
        assert "[S1] Familiar Notes" in text
        return {"summary": "file synthesis"}

    monkeypatch.setattr(r, "query_file_rich", fake_query_file_rich)
    monkeypatch.setattr("core.synthesis.summarizer.summarize_text", fake_summarize)

    assert synthesize_file(source, r, k=4) == "file synthesis"
