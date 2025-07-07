# core/embeddings/embedder.py
import json
from pathlib import Path
from typing import Dict, List, Literal

import openai

from core.config.config_registry import get_path_config, get_remote_config
from core.vectorstore.faiss_store import FaissStore


def embed_text(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Get OpenAI embedding for a given text.
    """
    remote = get_remote_config()
    openai.api_key = remote.openai_api_key

    response = openai.Embedding.create(
        input=text,
        model=model
    )
    return response['data'][0]['embedding']


def generate_embeddings(
    source_dir: Path = None,
    method: Literal["parsed", "summary", "raw", "meta"] = "parsed",
    out_path: Path = Path("rich_doc_embeddings.json"),
    model: str = "text-embedding-3-large"
) -> None:
    """
    Generate document embeddings from the specified source text.
    """
    paths = get_path_config()
    source_dir = source_dir or paths.parsed
    out_path = out_path or paths.vector / "rich_doc_embeddings.json"
    embeddings: Dict[str, List[float]] = {}
    store = FaissStore(dim=1536, path=paths.vector / "mosaic.index")

    for file in sorted(source_dir.glob("*.txt" if method != "meta" else "*.meta.json")):
        doc_id = file.stem

        if method == "parsed":
            text = file.read_text(encoding="utf-8")
        elif method == "raw":
            raw_path = paths.raw / file.name
            text = raw_path.read_text(encoding="utf-8") if raw_path.exists() else ""
        elif method == "summary" or method == "meta":
            try:
                meta = json.loads(file.read_text("utf-8"))
                text = meta.get("summary", "")
            except Exception:
                continue
        else:
            raise ValueError(f"Unsupported method: {method}")

        if not text.strip():
            print(f"⚠️ Skipping empty: {file.name}")
            continue

        try:
            vector = embed_text(text, model=model)
            embeddings[doc_id] = vector
            store.add([hash(doc_id)], [vector])
        except Exception as e:
            print(f"❌ Failed embedding {file.name}: {e}")

    out_path.write_text(json.dumps(embeddings, indent=2))
    store.persist()
    print(f"✅ Saved {len(embeddings)} embeddings to {out_path}")
