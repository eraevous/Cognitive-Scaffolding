from pathlib import Path

from core.config.config_registry import get_path_config, get_remote_config
from core.embeddings.embedder import generate_embeddings
from core.workflows.main_commands import pipeline_from_upload
from scripts.pipeline import run_full_pipeline

#pipeline_from_upload("mydoc.pdf")

# generate_embeddings(
#     #source_dir=Path("metadata"),
#     method="summary",
#     out_path=Path("test_embeddings.json")
# )


run_full_pipeline(Path("./incoming_docs"), chunked=True, method="summary")

doc_ids, X, coords = run_dimensionality_reduction(path_to_embeddings)
labels = run_clustering(X, method="spectral")
label_map = run_labeling(doc_ids, labels, metadata_dir)
run_export(doc_ids, coords, labels, label_map, out_dir, metadata_dir)
