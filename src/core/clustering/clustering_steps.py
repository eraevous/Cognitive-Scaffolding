"""Composable steps used by the clustering tests."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import matplotlib
import numpy as np

from core.clustering import algorithms

matplotlib.use("Agg")  # Ensure headless rendering.
import matplotlib.pyplot as plt  # noqa: E402  # isort:skip


def run_dimensionality_reduction(embedding_path: Path) -> Tuple[List[str], np.ndarray, np.ndarray]:
    payload = json.loads(Path(embedding_path).read_text(encoding="utf-8"))
    doc_ids = sorted(payload.keys())
    if not doc_ids:
        return [], np.empty((0, 0)), np.empty((0, 0))
    vectors = np.asarray([payload[doc]["embedding"] for doc in doc_ids], dtype=np.float32)
    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)
    if algorithms.umap is not None and vectors.shape[0] > 50:
        reducer = algorithms.umap.UMAP(n_components=2, random_state=42)
        coords = reducer.fit_transform(vectors)
    else:
        if vectors.shape[1] < 2:
            coords = np.pad(vectors, ((0, 0), (0, 2 - vectors.shape[1])), mode="constant")
        else:
            coords = vectors[:, :2]
    return doc_ids, vectors, coords


def run_clustering(X: np.ndarray, *, method: str = "spectral") -> np.ndarray:
    if X.size == 0:
        return np.asarray([], dtype=int)
    if method == "hdbscan" and algorithms.hdbscan is not None:
        clusterer = algorithms.hdbscan.HDBSCAN(min_cluster_size=2)
        return clusterer.fit_predict(X)
    if algorithms.SpectralClustering is not None:
        n_clusters = max(1, min(5, X.shape[0]))
        clusterer = algorithms.SpectralClustering(
            n_clusters=n_clusters,
            assign_labels="discretize",
            random_state=42,
        )
        return clusterer.fit_predict(X)
    return np.zeros(X.shape[0], dtype=int)


def label_clusters(
    doc_ids: Sequence[str], labels: Sequence[int], metadata_dir: Path, *, model: str = "gpt-4"
) -> Dict[str, str]:  # pragma: no cover - exercised via monkeypatch in tests
    unique = sorted({int(label) for label in labels if int(label) != -1})
    return {f"cluster_{cluster}": f"Cluster {cluster}" for cluster in unique}


def run_labeling(
    doc_ids: Sequence[str], labels: Sequence[int], metadata_dir: Path, *, model: str = "gpt-4"
) -> Dict[str, str]:
    return label_clusters(doc_ids, labels, metadata_dir, model=model)


def run_export(
    doc_ids: Sequence[str],
    coords: np.ndarray,
    labels: Sequence[int],
    label_map: Dict[str, str],
    out_dir: Path,
    metadata_dir: Path,
) -> None:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    cluster_map: dict[str, List[str]] = defaultdict(list)
    summary_rows: list[Tuple[str, int, str, str]] = []

    for doc_id, label in zip(doc_ids, labels):
        label_int = int(label)
        cluster_key = f"cluster_{label_int}" if label_int != -1 else "unassigned"
        cluster_map[cluster_key].append(doc_id)
        meta_path = Path(metadata_dir) / f"{doc_id}.meta.json"
        summary_text = ""
        if meta_path.exists():
            meta_payload = json.loads(meta_path.read_text(encoding="utf-8"))
            summary_text = str(meta_payload.get("summary", ""))
        summary_rows.append((doc_id, label_int, label_map.get(cluster_key, ""), summary_text))

    (out_path / "cluster_map.json").write_text(
        json.dumps(cluster_map, indent=2), encoding="utf-8"
    )
    (out_path / "cluster_labels.json").write_text(
        json.dumps(label_map, indent=2), encoding="utf-8"
    )

    assignments_path = out_path / "cluster_assignments.csv"
    with assignments_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["doc_id", "cluster_id", "label"])
        for doc_id, cluster_id, label, _ in summary_rows:
            writer.writerow([doc_id, cluster_id, label])

    summary_path = out_path / "cluster_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["doc_id", "cluster_id", "label", "summary"])
        for doc_id, cluster_id, label, summary in summary_rows:
            writer.writerow([doc_id, cluster_id, label, summary])

    if coords.size:
        fig, ax = plt.subplots(figsize=(6, 4))
        scatter = ax.scatter(coords[:, 0], coords[:, 1], c=labels, cmap="tab10")
        ax.set_title("UMAP projection")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        plt.colorbar(scatter, ax=ax)
        fig.savefig(out_path / "umap_plot.png", dpi=150)
        plt.close(fig)
    else:
        (out_path / "umap_plot.png").write_bytes(b"")


__all__ = [
    "run_dimensionality_reduction",
    "run_clustering",
    "run_labeling",
    "run_export",
    "label_clusters",
]
