import json
from pathlib import Path

import pytest

from core.configuration import config_registry
from core.constants import DEFAULT_METADATA_SCHEMA_PATH


@pytest.fixture(autouse=True)
def reset_registry(monkeypatch):
    monkeypatch.delenv("METADATA_SCHEMA_PATH", raising=False)
    if hasattr(config_registry, "_path_instance"):
        config_registry._path_instance = None
    if hasattr(config_registry, "_set_schema_override"):
        config_registry._set_schema_override(None)
    yield
    monkeypatch.delenv("METADATA_SCHEMA_PATH", raising=False)
    if hasattr(config_registry, "_path_instance"):
        config_registry._path_instance = None
    if hasattr(config_registry, "_set_schema_override"):
        config_registry._set_schema_override(None)


def test_default_schema_resolution():
    cfg = config_registry.get_path_config(force_reload=True)
    assert cfg.schema == DEFAULT_METADATA_SCHEMA_PATH


def test_environment_override(monkeypatch, tmp_path):
    schema_file = tmp_path / "metadata_schema.json"
    schema_file.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("METADATA_SCHEMA_PATH", str(schema_file))

    cfg = config_registry.get_path_config(force_reload=True)

    assert cfg.schema == schema_file.resolve()


def test_missing_schema_warns_and_falls_back(caplog, tmp_path):
    missing = tmp_path / "missing_schema.json"
    config_registry.configure(metadata_schema_path=missing)

    with caplog.at_level("WARNING"):
        cfg = config_registry.get_path_config(force_reload=True)

    assert cfg.schema == DEFAULT_METADATA_SCHEMA_PATH
    assert "Metadata schema not found" in caplog.text


def test_path_config_json_has_no_schema_key():
    config_path = (
        Path(__file__).resolve().parents[1] / "src/core/configuration/path_config.json"
    )
    data = json.loads(config_path.read_text(encoding="utf-8"))

    assert "schema" not in data
