import json
from pathlib import Path
from core.config.remote_config import RemoteConfig
from core.config.path_config import PathConfig
from core.parsing.extract_text import extract_text
from core.storage.aws_clients import get_s3_client


def upload_file_to_s3(
    file_path: Path,
    parsed_name: str = None,
    paths: PathConfig = None,
    remote: RemoteConfig = None
) -> dict:
    """
    Alias for push_document_to_s3.
    Maintained for compatibility with legacy calls.
    """
    return push_document_to_s3(file_path, parsed_name, paths, remote)


def push_document_to_s3(
    file_path: Path,
    parsed_name: str = None,
    paths: PathConfig = None,
    remote: RemoteConfig = None
) -> dict:
    """
    Upload raw + parsed file to S3, along with a metadata stub.

    Args:
        file_path (Path): Full path to local document
        parsed_name (str): Optional name override for parsed .txt
        paths (PathConfig): Local path configuration
        remote (RemoteConfig): AWS config

    Returns:
        dict: Uploaded stub metadata
    """
    paths = paths or PathConfig.from_file()
    remote = remote or RemoteConfig.from_file()
    s3 = get_s3_client(region=remote.region)

    original_name = file_path.name
    parsed_name = parsed_name or file_path.stem.replace(" ", "_").replace("-", "_").lower() + ".txt"

    text = extract_text(str(file_path))

    # Upload raw
    s3.upload_file(str(file_path), remote.bucket_name, f"{remote.prefixes['raw']}{original_name}")

    # Upload parsed
    s3.put_object(
        Bucket=remote.bucket_name,
        Key=f"{remote.prefixes['parsed']}{parsed_name}",
        Body=text.encode("utf-8")
    )

    stub = {
        "source_file": f"s3://{remote.bucket_name}/{remote.prefixes['raw']}{original_name}",
        "parsed_file": f"s3://{remote.bucket_name}/{remote.prefixes['parsed']}{parsed_name}",
        "source_ext": file_path.suffix.lower().lstrip(".")
    }

    s3.put_object(
        Bucket=remote.bucket_name,
        Key=f"{remote.prefixes['stub']}{parsed_name}.stub.json",
        Body=json.dumps(stub, indent=2).encode("utf-8")
    )

    return stub

