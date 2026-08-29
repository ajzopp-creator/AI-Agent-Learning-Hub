"""Regression tests for infrastructure/lms_client configuration and BOM handling."""

import json
from pathlib import Path
from infrastructure.lms_client import LMStudioClient
from schemas import AppConfig


def test_lms_client_loads_valid_config(tmp_path: Path) -> None:
    """Ensure AppConfig schema loads parameters accurately from disk."""
    cfg_file = tmp_path / "test_config.json"
    cfg_data = {
        "server": {
            "base_url": "http://127.0.0.1:1234/v1",
            "api_key": "custom-key",
            "timeout_seconds": 45.0,
        },
        "model_defaults": {
            "model_alias": "granite-4.1-8b",
            "temperature": 0.1,
            "top_p": 0.9,
            "max_tokens": 1024,
            "stream": False,
        },
    }
    with open(cfg_file, "w", encoding="utf-8") as f:
        json.dump(cfg_data, f)

    client = LMStudioClient(config_path=cfg_file)
    assert client.app_cfg.server.api_key == "custom-key"
    assert client.app_cfg.model_defaults.temperature == 0.1


def test_lms_client_handles_utf8_bom(tmp_path: Path) -> None:
    """Ensure config files written with UTF-8 BOM decode without JSONDecodeError."""
    cfg_file = tmp_path / "bom_config.json"
    raw_json = '{"server": {"base_url": "http://localhost:1234/v1"}}'

    # Write file explicitly with UTF-8 BOM
    with open(cfg_file, "w", encoding="utf-8-sig") as f:
        f.write(raw_json)

    client = LMStudioClient(config_path=cfg_file)
    assert client.app_cfg.server.base_url == "http://localhost:1234/v1"


def test_lms_client_fallback_on_missing_file(tmp_path: Path) -> None:
    """Ensure missing config path falls back cleanly to default AppConfig."""
    missing_file = tmp_path / "non_existent.json"
    client = LMStudioClient(config_path=missing_file)
    assert isinstance(client.app_cfg, AppConfig)
    assert client.app_cfg.server.base_url == "http://127.0.0.1:1234/v1"