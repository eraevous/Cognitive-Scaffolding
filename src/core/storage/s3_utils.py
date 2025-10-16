"""Helpers for interacting with S3-stored metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from core.configuration import config_registry
from core.configuration.remote_config import RemoteConfig
from core.metadata.schema import validate_metadata

try:  # pragma: no cover - boto3 optional in tests
    import boto3  # type: ignore[import]
except Exception:  # pragma: no cover
    boto3 = None  # type: ignore[assignment]


def get_s3_client():  # pragma: no cover - thin wrapper
    if boto3 is None:
        raise RuntimeError("boto3 is not installed")
    return boto3.client("s3")


def _load_remote_config() -> RemoteConfig:
    config_path = Path(config_registry.remote_config)
    if config_path.exists():
        return RemoteConfig.from_file(config_path)
    return RemoteConfig()


def save_metadata_s3(bucket: str, key: str, metadata: dict) -> None:
    validate_metadata(metadata)
    client = get_s3_client()
    body = json.dumps(metadata).encode("utf-8")
    client.put_object(Bucket=bucket, Key=key, Body=body)


def load_metadata_s3(bucket: str, key: str) -> dict:
    client = get_s3_client()
    response = client.get_object(Bucket=bucket, Key=key)
    body = response["Body"].read().decode("utf-8")
    metadata = json.loads(body)
    validate_metadata(metadata)
    return metadata


def download_file_from_s3(source: str, destination: str | Path, *, prefix: str = "") -> str:
    remote = _load_remote_config()
    if not remote.bucket_name:
        raise ValueError("Remote configuration missing bucket name")
    client = get_s3_client()
    key = f"{prefix}{source}"
    dest = Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    client.download_file(Bucket=remote.bucket_name, Key=key, Filename=str(dest))
    return f"Downloaded {key} to {dest}"


def clear_s3_folders(prefixes: Iterable[str]) -> None:
    remote = _load_remote_config()
    if not remote.bucket_name:
        raise ValueError("Remote configuration missing bucket name")
    client = get_s3_client()
    for prefix in prefixes:
        response = client.list_objects_v2(Bucket=remote.bucket_name, Prefix=prefix)
        for entry in response.get("Contents", []):
            client.delete_object(Bucket=remote.bucket_name, Key=entry["Key"])


__all__ = [
    "save_metadata_s3",
    "load_metadata_s3",
    "download_file_from_s3",
    "clear_s3_folders",
    "get_s3_client",
]
