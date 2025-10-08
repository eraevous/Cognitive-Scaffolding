"""Regression tests for schema-aware path configuration."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli import pipeline as pipeline_cli
from core.configuration.path_config import PathConfig, validate_schema_path
from core.constants import DEFAULT_METADATA_SCHEMA_PATH

runner = CliRunner()


@pytest.fixture(autouse=True)
def restore_registry_state():
    """Reload the registry module between tests to avoid cross-test bleed."""
    module = importlib.reload(
        importlib.import_module("core.configuration.config_registry")
    )
    try:
        yield module
    finally:
        importlib.reload(importlib.import_module("core.configuration.config_registry"))


def test_configure_resets_to_default(tmp_path: Path):
    """Explicit ``None`` overrides should restore default config paths."""
    registry = importlib.import_module("core.configuration.config_registry")

    config_path = tmp_path / "path_config.json"
    config_path.write_text(
        json.dumps(
            {
                "root": str(tmp_path),
                "raw": "raw",
                "parsed": "parsed",
                "metadata": "metadata",
                "output": "output",
                "vector": "vector",
                "semantic_chunking": False,
            }
        )
    )

    registry.configure(path_config_path=config_path)
    loaded = registry.get_path_config(force_reload=True)
    assert loaded.root == Path(tmp_path)

    registry.configure(path_config_path=None)
    restored = registry.get_path_config(force_reload=True)
    assert registry.path_config == registry._DEFAULT_PATH_CONFIG_PATH
    assert validate_schema_path(restored.schema) == DEFAULT_METADATA_SCHEMA_PATH
    assert registry.get_path_config() is restored


def test_validate_schema_path_warns_and_falls_back(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """Missing schema files log a warning and fall back to the default path."""
    missing = tmp_path / "missing-schema.json"
    caplog.set_level("WARNING")

    resolved = validate_schema_path(missing)
    assert resolved == DEFAULT_METADATA_SCHEMA_PATH
    assert any(
        "Metadata schema not found" in record.message for record in caplog.records
    )


def test_cli_pipeline_uses_cached_schema(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """CLI invocation should reuse cached schema resolution when composing PathConfig."""
    caplog.set_level("INFO")
    base = PathConfig(root=tmp_path, schema=tmp_path / "nonexistent.json")

    input_dir = tmp_path / "incoming"
    input_dir.mkdir()

    captured: dict[str, Path] = {}

    def fake_run_pipeline(*, paths: PathConfig, **kwargs):
        captured["schema"] = paths.schema
        return None

    def fake_run_all_steps(**kwargs):
        return None

    registry = importlib.import_module("core.configuration.config_registry")
    registry.configure(path_config_path=None)

    original_get = pipeline_cli.get_path_config
    original_run_pipeline = pipeline_cli.run_pipeline
    original_run_all_steps = pipeline_cli.run_all_steps
    try:
        pipeline_cli.get_path_config = lambda: base  # type: ignore[assignment]
        pipeline_cli.run_pipeline = fake_run_pipeline  # type: ignore[assignment]
        pipeline_cli.run_all_steps = fake_run_all_steps  # type: ignore[assignment]

        result = runner.invoke(
            pipeline_cli.app,
            [
                "--input-dir",
                str(input_dir),
            ],
        )
    finally:
        pipeline_cli.get_path_config = original_get  # type: ignore[assignment]
        pipeline_cli.run_pipeline = original_run_pipeline  # type: ignore[assignment]
        pipeline_cli.run_all_steps = original_run_all_steps  # type: ignore[assignment]

    assert result.exit_code == 0
    assert captured["schema"] == base.schema
    assert base.schema == DEFAULT_METADATA_SCHEMA_PATH
    assert any(
        "Metadata schema not found" in record.message for record in caplog.records
    )
