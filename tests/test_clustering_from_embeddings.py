import json
import sys
import types
from pathlib import Path
from typing import Tuple

import pytest

if "tiktoken" not in sys.modules:
    try:  # pragma: no cover - exercise real dependency when available
        import tiktoken  # type: ignore  # noqa: F401
    except ModuleNotFoundError:  # pragma: no cover - optional dependency
        dummy_encoding = types.SimpleNamespace(
            encode=lambda text, disallowed_special=(): list(text),
            decode=lambda tokens: "".join(tokens),
        )
        sys.modules["tiktoken"] = types.SimpleNamespace(
            encoding_for_model=lambda model: dummy_encoding
        )

if "openai" not in sys.modules:

    class _DummyChat:  # pragma: no cover - optional dependency shim
        def __init__(self):
            self.completions = types.SimpleNamespace(
                create=lambda *a, **k: types.SimpleNamespace(
                    choices=[
                        types.SimpleNamespace(
                            message=types.SimpleNamespace(content="{}")
                        )
                    ]
                )
            )

    sys.modules["openai"] = types.SimpleNamespace(
        OpenAI=lambda *a, **k: types.SimpleNamespace(chat=_DummyChat())
    )

from core.clustering import algorithms
from core.clustering.clustering_steps import (
    run_clustering,
    run_dimensionality_reduction,
    run_export,
    run_labeling,
)
from core.config import config_registry
from core.config.path_config import PathConfig
from core.logger import get_logger
from core.workflows.main_commands import classify

logger = get_logger(__name__)

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "rich_doc_embeddings.json"


def _load_fixture(tmp_path: Path) -> Tuple[Path, Path]:
    if not FIXTURE_PATH.exists():
        pytest.skip("rich_doc_embeddings fixture missing")

    with FIXTURE_PATH.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)

    embedding_path = tmp_path / "rich_doc_embeddings.json"
    embedding_path.write_text(json.dumps(payload), encoding="utf-8")

    metadata_dir = tmp_path / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    for doc_id, record in payload.items():
        metadata = record.get("metadata", {})
        (metadata_dir / f"{doc_id}.meta.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )

    return embedding_path, metadata_dir


def test_clustering_from_embeddings(tmp_path, monkeypatch):
    if algorithms.umap is None or algorithms.hdbscan is None:
        pytest.skip("Clustering dependencies (umap, hdbscan) not available")

    logger.info("Testing clustering from fixture embeddings...")

    embedding_path, metadata_dir = _load_fixture(tmp_path)
    out_dir = tmp_path / "cluster_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    doc_ids, X, coords = run_dimensionality_reduction(embedding_path)
    labels = run_clustering(X, method="spectral")

    monkeypatch.setattr(
        "core.clustering.clustering_steps.label_clusters",
        lambda ids, lbls, md, model="gpt-4": {
            f"cluster_{int(label)}": f"Label {int(label)}"
            for label in sorted(set(int(lab) for lab in lbls if lab != -1))
        },
    )
    label_map = run_labeling(doc_ids, labels, metadata_dir)
    run_export(doc_ids, coords, labels, label_map, out_dir, metadata_dir)

    # exercise classification path on a minimal sample
    pc = PathConfig(root=tmp_path)
    pc.parsed.mkdir(parents=True, exist_ok=True)
    pc.metadata.mkdir(parents=True, exist_ok=True)
    sample_file = pc.parsed / "sample.txt"
    sample_file.write_text("Cats purr. " * 20 + "Dogs bark. " * 20)

    monkeypatch.setattr(config_registry, "get_path_config", lambda: pc)
    monkeypatch.setattr(
        "core.workflows.main_commands.segment_text", lambda text: [text[:50], text[50:]]
    )
    monkeypatch.setattr(
        "core.workflows.main_commands.summarize_text",
        lambda text, doc_type="standard": {
            "summary": text[:10],
            "topics": ["x"],
            "tags": [],
            "themes": [],
            "priority": 1,
            "tone": "info",
            "stage": "draft",
            "depth": "low",
            "category": doc_type,
        },
    )
    metadata = classify(sample_file.name, chunked=True, paths=pc)
    assert isinstance(metadata, dict)
    assert pc.metadata.joinpath(f"{sample_file.name}.meta.json").exists()

    assert out_dir.joinpath("cluster_map.json").exists()
    assert out_dir.joinpath("cluster_labels.json").exists()
    assert out_dir.joinpath("cluster_assignments.csv").exists()
    assert out_dir.joinpath("cluster_summary.csv").exists()
    assert out_dir.joinpath("umap_plot.png").exists()
    logger.info("Clustering from fixture embeddings succeeded.")


if __name__ == "__main__":
    test_clustering_from_embeddings()
