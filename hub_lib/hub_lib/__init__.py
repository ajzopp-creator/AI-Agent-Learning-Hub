"""hub_lib - shared model-routing facade for the AI-Agent-Learning-Hub.

Public API:
    ModelManager.get_model(task) -> (provider, model_id)
    ModelManager.generate(task, prompt) -> str
    verify_health([tasks])           - Canary, run once per session
    load_hub_env()                   - load hub-root .env
"""

from .env_loader import load_hub_env, require_env
from .exceptions import (
    ConfigError,
    HubLibError,
    ModelUnavailableError,
    ProviderError,
)
from .health_check import check_provider, verify_health
from .model_manager import MODEL_MAP, ModelManager

__version__ = "0.1.0"

__all__ = [
    "ModelManager",
    "MODEL_MAP",
    "verify_health",
    "check_provider",
    "load_hub_env",
    "require_env",
    "HubLibError",
    "ConfigError",
    "ModelUnavailableError",
    "ProviderError",
]
