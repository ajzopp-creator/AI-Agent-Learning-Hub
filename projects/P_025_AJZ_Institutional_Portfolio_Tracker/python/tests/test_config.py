"""Permanent tests for Hub-root resolution in config.py."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _drop_config_after_test():
    """Do not leave a tmp-HUB_ROOT config in sys.modules for later imports."""
    yield
    sys.modules.pop("config", None)


def _reload_config(hub: str | None) -> object:
    if hub is None:
        os.environ.pop("HUB_ROOT", None)
    else:
        os.environ["HUB_ROOT"] = hub
    os.environ.pop("OneDrive", None)
    sys.modules.pop("config", None)
    return importlib.import_module("config")


def test_default_hub_root_is_hub_not_onedrive(tmp_path, monkeypatch):
    monkeypatch.delenv("HUB_ROOT", raising=False)
    monkeypatch.setenv("OneDrive", r"D:\OneDrive")
    # Importing config mkdir's OUTPUT_DIR; point HUB_ROOT at tmp after
    # verifying the default *expression* via a isolated helper.
    from config import _DEFAULT_HUB_ROOT

    assert _DEFAULT_HUB_ROOT == r"C:\Users\Trader\AI-Agent-Learning-Hub"
    assert "OneDrive" not in _DEFAULT_HUB_ROOT


def test_hub_root_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("HUB_ROOT", str(tmp_path))
    sys.modules.pop("config", None)
    cfg = importlib.import_module("config")
    assert Path(cfg.HUB_ROOT) == tmp_path
