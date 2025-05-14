# core/embeddings/embedder.py
import json
from typing import List, Dict, Literal
from pathlib import Path
import openai
from core.config.config_registry import get_remote_config, get_path_config


def embed_text(text: str, model: str = "text-embedding-3-small") -> list[float]:
    config = get_remote_config()
    client = openai.OpenAI(api_key=config.openai_api_key)
    response = client.embeddings.create(input=text, model=model)
    return response.data[0].embedding


def generate_embeddings(
    source_dir: Path = None,
    method: Literal["parsed", "summary", "raw", "meta"] = "parsed",
    out_path: Path = None,
    model: str = "text-embedding-3-small"
) -> None:
    paths = get_path_config()

    # Use correct directories from config
    if method in ["summary", "meta"]:
        source_dir = source_dir or paths.metadata
    elif method == "parsed":
        source_dir = source_dir or paths.parsed
    elif method == "raw":
        source_dir = source_dir or paths.raw
    else:
        raise ValueError(f"Unknown method: {method}")
    
    print(f"Generating embeddings from {source_dir} using method: {method}")


    out_path = out_path or (paths.output / "rich_doc_embeddings.json")

    embeddings: Dict[str, List[float]] = {}

    pattern = "*.meta.json" if method in ["meta", "summary"] else "*.txt"
    for file in sorted(source_dir.glob(pattern)):
        doc_id = file.stem

        if method == "parsed":
            text = file.read_text(encoding="utf-8")
        elif method == "raw":
            raw_path = paths.raw / file.name
            text = raw_path.read_text(encoding="utf-8") if raw_path.exists() else ""
        elif method == "summary" or method == "meta":
            try:
                print(f"🔍 Reading metadata from {file.name}...")
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
        except Exception as e:
            print(f"❌ Failed embedding {file.name}: {e}")

    out_path.write_text(json.dumps(embeddings, indent=2))
    print(f"✅ Saved {len(embeddings)} embeddings to {out_path}")