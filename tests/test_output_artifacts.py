import json
from pathlib import Path

from typer.testing import CliRunner

from cli.search import app as search_app
from cli import search as search_cli
from cli import synthesize as synthesize_cli
from cli.synthesize import app as synthesize_app
from core.configuration.path_config import PathConfig
from core.output.artifacts import resolve_artifact_path, slugify, write_artifact


runner = CliRunner()


def _make_corpus(root: Path) -> None:
    parsed = root / "parsed" / "chatgpt"
    metadata = root / "metadata" / "chatgpt"
    parsed.mkdir(parents=True)
    metadata.mkdir(parents=True)
    (parsed / "a.txt").write_text(
        "USER: Tell me about cognitive scaffolding.\n"
        "ASSISTANT: Cognitive scaffolding organizes many conversations.",
        encoding="utf-8",
    )
    manifest = {
        "records": {
            "a": {
                "key": "a",
                "title": "Scaffold Notes",
                "parsed_path": "parsed/chatgpt/a.txt",
            }
        }
    }
    (metadata / "chatgpt_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


def test_slugify_keeps_filename_readable():
    assert slugify("Cognitive scaffolding + synthesis!") == (
        "cognitive-scaffolding-synthesis"
    )


def test_write_artifact_to_directory(tmp_path):
    paths = PathConfig(root=tmp_path)

    output_path = write_artifact(
        tmp_path / "exports",
        paths,
        "semantic-search",
        "cognitive scaffolding",
        ["# Result", "body"],
    )

    assert output_path.parent == tmp_path / "exports"
    assert output_path.name.endswith("__semantic-search__cognitive-scaffolding.md")
    assert output_path.read_text(encoding="utf-8") == "# Result\nbody\n"


def test_resolve_artifact_path_accepts_explicit_file(tmp_path):
    paths = PathConfig(root=tmp_path)
    explicit = tmp_path / "result.md"

    assert resolve_artifact_path(explicit, paths, "search", "query") == explicit


def test_lexical_search_out_writes_markdown(tmp_path):
    _make_corpus(tmp_path)
    out_dir = tmp_path / "saved"

    result = runner.invoke(
        search_app,
        [
            "lexical",
            "cognitive scaffolding",
            "--root",
            str(tmp_path),
            "--out",
            str(out_dir),
        ],
    )

    assert result.exit_code == 0
    saved = list(out_dir.glob("*__lexical-search__cognitive-scaffolding.md"))
    assert len(saved) == 1
    content = saved[0].read_text(encoding="utf-8")
    assert "# Lexical Search: cognitive scaffolding" in content
    assert "Scaffold Notes" in content


def test_file_search_out_writes_rich_markdown(tmp_path, monkeypatch):
    query_file = tmp_path / "query.txt"
    query_file.write_text("cognitive scaffold note", encoding="utf-8")
    out_dir = tmp_path / "saved"

    class FakeRetriever:
        def __init__(self, paths=None, vector_name="default"):
            self.paths = paths
            self.vector_name = vector_name

        def query_file_rich(
            self, file_path, k=5, return_text=False, aggregate=False
        ):
            assert Path(file_path) == query_file
            assert k == 2
            assert return_text is True
            assert aggregate is True
            return [
                {
                    "doc_id": "conv_1",
                    "chunk": "chunk00",
                    "title": "Scaffold Notes",
                    "score": 0.87,
                    "text": "Matched passage about cognitive scaffolding.",
                }
            ]

    monkeypatch.setattr(search_cli, "Retriever", FakeRetriever)

    result = runner.invoke(
        search_app,
        [
            "file",
            str(query_file),
            "--root",
            str(tmp_path),
            "--k",
            "2",
            "--text",
            "--aggregate",
            "--out",
            str(out_dir),
        ],
    )

    assert result.exit_code == 0
    saved = list(out_dir.glob("*__semantic-file-search__query.md"))
    assert len(saved) == 1
    content = saved[0].read_text(encoding="utf-8")
    assert "# Semantic File Search:" in content
    assert "Scaffold Notes" in content
    assert "Matched passage" in content


def test_file_synthesis_out_writes_markdown(tmp_path, monkeypatch):
    source = tmp_path / "source.md"
    source.write_text("familiar hearth notes", encoding="utf-8")
    out_dir = tmp_path / "saved"

    class FakeRetriever:
        def __init__(self, paths=None, vector_name="default"):
            self.paths = paths
            self.vector_name = vector_name

    def fake_synthesize_file(file_path, retriever, k=8, max_input_tokens=50000):
        assert Path(file_path) == source
        assert isinstance(retriever, FakeRetriever)
        assert k == 3
        assert max_input_tokens == 9000
        return "Synthesis from a source file."

    monkeypatch.setattr(synthesize_cli, "Retriever", FakeRetriever)
    monkeypatch.setattr(synthesize_cli, "synthesize_file", fake_synthesize_file)

    result = runner.invoke(
        synthesize_app,
        [
            "file",
            str(source),
            "--root",
            str(tmp_path),
            "--k",
            "3",
            "--max-input-tokens",
            "9000",
            "--out",
            str(out_dir),
        ],
    )

    assert result.exit_code == 0
    saved = list(out_dir.glob("*__semantic-file-synthesis__source.md"))
    assert len(saved) == 1
    content = saved[0].read_text(encoding="utf-8")
    assert "# Semantic File Synthesis: source" in content
    assert "Synthesis from a source file." in content
