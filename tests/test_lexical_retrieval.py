import json
from pathlib import Path

from core.retrieval.lexical import search_chatgpt_corpus
from core.synthesis.extractive import synthesize_lexical_query


def _make_corpus(root: Path) -> None:
    parsed = root / "parsed" / "chatgpt"
    metadata = root / "metadata" / "chatgpt"
    parsed.mkdir(parents=True)
    metadata.mkdir(parents=True)

    (parsed / "a.txt").write_text(
        "USER: Tell me about cognitive scaffolding.\n"
        "ASSISTANT: Cognitive scaffolding helps organize memory and recall.",
        encoding="utf-8",
    )
    (parsed / "b.txt").write_text(
        "USER: Dinner ideas?\nASSISTANT: Pasta is quick.",
        encoding="utf-8",
    )
    manifest = {
        "records": {
            "a": {
                "key": "a",
                "title": "Cognitive Scaffold Notes",
                "parsed_path": "parsed/chatgpt/a.txt",
            },
            "b": {
                "key": "b",
                "title": "Dinner",
                "parsed_path": "parsed/chatgpt/b.txt",
            },
        }
    }
    (metadata / "chatgpt_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


def test_search_chatgpt_corpus_local(tmp_path):
    _make_corpus(tmp_path)

    hits = search_chatgpt_corpus(tmp_path, "cognitive scaffolding", k=3)

    assert len(hits) == 1
    assert hits[0].doc_id == "a"
    assert "Cognitive Scaffold Notes" == hits[0].title
    assert "scaffolding" in hits[0].snippet.lower()


def test_synthesize_lexical_query(tmp_path):
    _make_corpus(tmp_path)

    synthesis = synthesize_lexical_query(tmp_path, "cognitive scaffolding", k=3)

    assert "Extractive throughline" in synthesis
    assert "Cognitive Scaffold Notes" in synthesis
