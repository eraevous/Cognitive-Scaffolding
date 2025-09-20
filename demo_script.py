from pathlib import Path

import pytest

from src.core.clustering.clustering_steps import (
    run_clustering,
    run_dimensionality_reduction,
    run_export,
    run_labeling,
)
from src.core.config.config_registry import get_path_config
from src.scripts.pipeline import run_full_pipeline

pytest.skip("Demo script not meant for pytest", allow_module_level=True)

# pipeline_from_upload("mydoc.pdf")

# generate_embeddings(
#     #source_dir=Path("metadata"),
#     method="summary",
#     out_path=Path("test_embeddings.json")
# )


def run_demo():
    run_full_pipeline(
        Path("./incoming_docs"),
        chunked=True,
        method="summary",
        segmentation="semantic",
    )

    paths = get_path_config()
    path_to_embeddings = paths.root / "rich_doc_embeddings.json"
    metadata_dir = paths.metadata
    out_dir = paths.output / "test_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not path_to_embeddings.exists():
        print("⚠️ Embedding file missing; demo skipped.")
        return

    doc_ids, X, coords = run_dimensionality_reduction(path_to_embeddings)
    labels = run_clustering(X, method="spectral")
    label_map = run_labeling(doc_ids, labels, metadata_dir)
    run_export(doc_ids, coords, labels, label_map, out_dir, metadata_dir)


if __name__ == "__main__":
    run_demo()
