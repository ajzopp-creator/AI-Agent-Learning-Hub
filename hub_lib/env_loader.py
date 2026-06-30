"""Locate and load the hub-root .env file.

Hub-wide environment variables (API keys, default model overrides) live in a
single .env file at C:\\Users\\Trader\\AI-Agent-Learning-Hub\\.env. This module
finds that file and loads it into os.environ.

Per-project .env files at the project root override hub-root values when both
are present.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .exceptions import ConfigError

HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
HUB_ENV_FILE = HUB_ROOT / ".env"


def load_hub_env(project_env: Optional[Path] = None) -> None:
    """Load hub-root .env, then optionally overlay a project-specific .env.

    Args:
        project_env: Optional path to a project-level .env file. If provided,
            its values override hub-root values for this process.

    Raises:
        ConfigError: If the hub-root .env file is missing.
    """
    if not HUB_ENV_FILE.exists():
        raise ConfigError(
            f"Hub-root .env file not found at {HUB_ENV_FILE}. "
            "Copy .env.example to .env and fill in your API keys."
        )
    load_dotenv(HUB_ENV_FILE, override=False)
    if project_env is not None and project_env.exists():
        load_dotenv(project_env, override=True)


def require_env(key: str) -> str:
    """Read an env var or raise ConfigError if missing or empty.

    Args:
        key: The environment variable name.

    Returns:
        The variable's value.

    Raises:
        ConfigError: If the variable is unset or empty.
    """
    value = os.environ.get(key, "").strip()
    if not value:
        raise ConfigError(f"Required environment variable {key!r} is not set.")
    return value
