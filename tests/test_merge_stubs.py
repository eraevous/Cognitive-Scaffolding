import json

import pytest

from core.config.path_config import PathConfig
from core.metadata.schema import validate_metadata
from core.workflows.main_commands import merge_stubs

BASE = {
    "summary": "s",
    "topics": ["t"],
    "tags": [],
    "category": "standard",
    "priority": 1,
    "tone": "info",
    "depth": "low",
    "stage": "draft",
}


def _paths(tmp_path):
    pc = PathConfig(root=tmp_path)
    pc.metadata.mkdir(parents=True, exist_ok=True)
    return pc


def _write_stub(pc, name, stub):
    (pc.metadata / f"{name}.stub.json").write_text(json.dumps(stub), encoding="utf-8")


def test_s3_style_stub_fills_file_info(tmp_path):
    """Upload stubs keep source_file at the top level; it must reach file_info."""
    pc = _paths(tmp_path)
    _write_stub(
        pc,
        "doc.txt",
        {
            "source_file": "s3://bucket/raw/doc.pdf",
            "parsed_file": "doc.txt",
            "source_ext": "pdf",
            "file_info": {},
        },
    )
    merged = merge_stubs("doc.txt", dict(BASE), pc)
    assert merged["file_info"]["source_file"] == "s3://bucket/raw/doc.pdf"
    assert merged["file_info"]["source_ext"] == "pdf"
    validate_metadata(merged)


def test_empty_file_info_is_left_out(tmp_path):
    """A stub with no file details must not add an empty file_info block."""
    pc = _paths(tmp_path)
    _write_stub(pc, "doc.txt", {"file_info": {}})
    merged = merge_stubs("doc.txt", dict(BASE), pc)
    assert "file_info" not in merged
    validate_metadata(merged)


def test_file_info_without_source_file_still_fails(tmp_path):
    """The schema rule stands: a file_info block without source_file is invalid."""
    pc = _paths(tmp_path)
    _write_stub(pc, "doc.txt", {"file_info": {"word_count": 3}})
    merged = merge_stubs("doc.txt", dict(BASE), pc)
    with pytest.raises(Exception):
        validate_metadata(merged)
