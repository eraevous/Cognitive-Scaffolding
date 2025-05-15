from core.workflows.main_commands import pipeline_from_upload
from core.config.config_registry import get_path_config, get_remote_config
from core.embeddings.embedder import generate_embeddings
from pathlib import Path

#pipeline_from_upload("mydoc.pdf")

# generate_embeddings(
#     #source_dir=Path("metadata"),
#     method="summary",
#     out_path=Path("test_embeddings.json")
# )

from scripts.pipeline import run_full_pipeline
from pathlib import Path

run_full_pipeline(Path("./incoming_docs"), chunked=True, method="summary")