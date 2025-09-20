"""Tests for the pipeline orchestration entrypoint."""

import json
import os
# Stub optional heavy dependencies before importing the pipeline module.
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("PROJECT_ROOT", str(PROJECT_ROOT))

_temp_config_dir = Path(tempfile.mkdtemp(prefix="pipeline-config-"))
path_config_path = _temp_config_dir / "path_config.json"
remote_config_path = _temp_config_dir / "remote_config.json"
path_config_path.write_text(
    json.dumps(
        {
            "root": str(PROJECT_ROOT),
            "raw": "raw",
            "parsed": "parsed",
            "metadata": "metadata",
            "output": "output",
            "vector": "vector",
            "schema": "config/metadata_schema.json",
            "semantic_chunking": False,
        }
    )
)
remote_config_path.write_text(
    json.dumps(
        {
            "bucket_name": "test-bucket",
            "lambda_name": "test-lambda",
            "region": "us-east-1",
            "root": str(PROJECT_ROOT),
            "openai_api_key": "sk-test",
            "prefixes": {
                "raw": "raw/",
                "parsed": "parsed/",
                "stub": "stub/",
                "metadata": "metadata/",
            },
        }
    )
)
os.environ.setdefault("CONFIG_DIR", str(_temp_config_dir))
os.environ.setdefault("PATH_CONFIG_PATH", str(path_config_path))
os.environ.setdefault("REMOTE_CONFIG_PATH", str(remote_config_path))


class _DummyEncoder:
    def encode(self, text: str, disallowed_special: tuple[str, ...] = ()) -> list[int]:
        return [0]

    def decode(self, tokens: list[int]) -> str:
        return ""


tiktoken_stub = ModuleType("tiktoken")
tiktoken_stub.encoding_for_model = lambda _model: _DummyEncoder()
sys.modules.setdefault("tiktoken", tiktoken_stub)


class _DummyFlatIP:
    def __init__(self, dim: int) -> None:
        self.d = dim


class _DummyIndexIDMap:
    def __init__(self, base: _DummyFlatIP) -> None:
        self.base = base
        self.d = base.d

    def add_with_ids(self, _vecs, _ids) -> None:  # pragma: no cover - defensive stub
        return None

    def search(self, _vec, k: int):  # pragma: no cover - defensive stub
        return [[0.0] * k], [[-1] * k]


faiss_stub = ModuleType("faiss")
faiss_stub.IndexFlatIP = _DummyFlatIP  # type: ignore[attr-defined]
faiss_stub.IndexIDMap = _DummyIndexIDMap  # type: ignore[attr-defined]
faiss_stub.write_index = lambda *_args, **_kwargs: None
faiss_stub.read_index = lambda *_args, **_kwargs: _DummyIndexIDMap(_DummyFlatIP(0))
sys.modules.setdefault("faiss", faiss_stub)


class _DummyEmbeddings:
    @staticmethod
    def create(*_args, **_kwargs):  # pragma: no cover - defensive stub
        raise NotImplementedError


class _DummyOpenAI:
    def __init__(self, *_args, **_kwargs) -> None:  # pragma: no cover - defensive stub
        self.embeddings = _DummyEmbeddings()


openai_stub = ModuleType("openai")
openai_stub.OpenAI = _DummyOpenAI  # type: ignore[attr-defined]
sys.modules.setdefault("openai", openai_stub)

from core.configuration.path_config import PathConfig
from scripts import pipeline


@pytest.fixture()
def sample_paths(tmp_path: Path) -> PathConfig:
    """Build a PathConfig pointing to temp directories with sample files."""
    input_dir = tmp_path / "input"
    parsed_dir = tmp_path / "parsed"
    metadata_dir = tmp_path / "metadata"
    output_dir = tmp_path / "output"
    vector_dir = tmp_path / "vector"

    for path in (input_dir, parsed_dir, metadata_dir, output_dir, vector_dir):
        path.mkdir()

    # Create a sample raw document and its parsed counterpart.
    (input_dir / "example.md").write_text("raw content", encoding="utf-8")
    (parsed_dir / "example.txt").write_text("parsed content", encoding="utf-8")

    return PathConfig(
        root=tmp_path,
        raw=input_dir,
        parsed=parsed_dir,
        metadata=metadata_dir,
        output=output_dir,
        vector=vector_dir,
        schema=tmp_path / "config" / "metadata_schema.json",
        semantic_chunking=True,
    )


def test_run_pipeline_happy_path(sample_paths: PathConfig) -> None:
    """The pipeline should upload, classify, and embed documents in order."""
    with (
        patch.object(pipeline, "upload_and_prepare") as upload_mock,
        patch.object(pipeline, "classify") as classify_mock,
        patch.object(pipeline, "generate_embeddings") as embed_mock,
    ):
        pipeline.run_full_pipeline(
            input_dir=sample_paths.raw,
            chunked=False,
            overwrite=True,
            method="summary",
            segmentation="semantic",
            paths=sample_paths,
        )

    upload_mock.assert_called_once()
    (uploaded_path,) = upload_mock.call_args.args
    assert uploaded_path == sample_paths.raw / "example.md"
    assert upload_mock.call_args.kwargs == {"paths": sample_paths}

    classify_mock.assert_called_once_with(
        "example.txt",
        chunked=False,
        segmentation="semantic",
        paths=sample_paths,
    )

    embed_mock.assert_called_once_with(
        source_dir=sample_paths.parsed,
        method="summary",
        out_path=sample_paths.root / "rich_doc_embeddings.json",
        segment_mode=sample_paths.semantic_chunking,
    )
