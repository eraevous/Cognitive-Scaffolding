"""Unit tests for the S3 helper utilities ensure AWS calls are mocked."""

from __future__ import annotations

import json
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import call

from core.storage.s3_utils import (
    clear_s3_folders,
    download_file_from_s3,
    load_metadata_s3,
    save_metadata_s3,
)


def test_save_metadata_s3_serializes_and_uploads(mocker) -> None:
    """Metadata should be validated and uploaded via the injected S3 client."""
    metadata = {"title": "example"}
    validate_stub = mocker.patch("core.storage.s3_utils.validate_metadata")
    s3_client = mocker.Mock()
    mocker.patch("core.storage.s3_utils.get_s3_client", return_value=s3_client)

    save_metadata_s3("bucket", "metadata/key.json", metadata)

    validate_stub.assert_called_once_with(metadata)
    s3_client.put_object.assert_called_once()
    kwargs = s3_client.put_object.call_args.kwargs
    assert kwargs["Bucket"] == "bucket"
    assert kwargs["Key"] == "metadata/key.json"
    assert json.loads(kwargs["Body"].decode("utf-8")) == metadata


def test_load_metadata_s3_fetches_and_validates(mocker) -> None:
    """Loaded metadata should be parsed to dict and re-validated."""
    metadata = {"answer": 42}
    mocker.patch("core.storage.s3_utils.validate_metadata")
    s3_client = mocker.Mock()
    s3_client.get_object.return_value = {
        "Body": BytesIO(json.dumps(metadata).encode("utf-8"))
    }
    mocker.patch("core.storage.s3_utils.get_s3_client", return_value=s3_client)

    result = load_metadata_s3("bucket", "metadata/key.json")

    s3_client.get_object.assert_called_once_with(
        Bucket="bucket", Key="metadata/key.json"
    )
    assert result == metadata


def test_download_file_from_s3_uses_remote_config(mocker, tmp_path) -> None:
    """Downloads should derive the bucket from the remote configuration."""
    remote = SimpleNamespace(bucket_name="fixture-bucket")
    mocker.patch("core.storage.s3_utils.RemoteConfig.from_file", return_value=remote)
    s3_client = mocker.Mock()
    mocker.patch("core.storage.s3_utils.get_s3_client", return_value=s3_client)
    destination = tmp_path / "downloaded.txt"

    message = download_file_from_s3("source.txt", str(destination), prefix="uploads/")

    s3_client.download_file.assert_called_once_with(
        Bucket="fixture-bucket",
        Key="uploads/source.txt",
        Filename=str(destination),
    )
    assert str(destination) in message


def test_clear_s3_folders_deletes_listed_objects(mocker) -> None:
    """Clearing folders should delete each object discovered in the listing."""
    remote = SimpleNamespace(bucket_name="fixture-bucket")
    mocker.patch("core.storage.s3_utils.RemoteConfig.from_file", return_value=remote)
    s3_client = mocker.Mock()
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "raw/doc1"},
            {"Key": "raw/doc2"},
        ]
    }
    mocker.patch("core.storage.s3_utils.get_s3_client", return_value=s3_client)

    clear_s3_folders(["raw/"])

    s3_client.list_objects_v2.assert_called_once_with(
        Bucket="fixture-bucket", Prefix="raw/"
    )
    s3_client.delete_object.assert_has_calls(
        [
            call(Bucket="fixture-bucket", Key="raw/doc1"),
            call(Bucket="fixture-bucket", Key="raw/doc2"),
        ]
    )
