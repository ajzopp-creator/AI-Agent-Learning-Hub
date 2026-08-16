"""Hub-wide model routing facade.

ModelManager decouples application code from specific model IDs and providers.
Projects call ModelManager.generate(task, prompt) without knowing or caring
whether the task routes to LM Studio, Claude, or Gemini.

Update routing in one place (MODEL_MAP) or via env-var override; every
project picks up the change on next run.
"""

import logging
import os
from typing import Tuple

from . import machine_capability, providers
from .exceptions import ConfigError

logger = logging.getLogger(__name__)

# Default routing - (provider, model_id) per task name.
# Override any task at runtime via env var:
#   HUBLIB_TASK_<TASKNAME_UPPER>=provider:model_id
# Example:  HUBLIB_TASK_VP_PATTERN=google:gemini-2.5-pro
MODEL_MAP: dict[str, Tuple[str, str]] = {
    "local_fast":    ("lmstudio",  "qwen2.5-7b-instruct"),
    "local_smart":   ("lmstudio",  "qwen2.5-32b-instruct"),
    "cloud_fast":    ("anthropic", "claude-haiku-4-5-20251001"),
    "cloud_smart":   ("anthropic", "claude-opus-4-7"),
    "vp_pattern":    ("google",    "gemini-2.5-flash"),
    "vp_reasoning":  ("google",    "gemini-2.5-pro"),
}

_DISPATCH = {
    "lmstudio":  providers.call_lmstudio,
    "anthropic": providers.call_anthropic,
    "google":    providers.call_google,
}


class ModelManager:
    """Facade for routing tasks to the correct provider and model."""

    @classmethod
    def get_model(cls, task: str) -> Tuple[str, str]:
        """Return (provider, model_id) for a task name.

        Resolution order: env-var override, then machine-capability
        substitution (local_* -> cloud_* if this machine has no local LLM
        tier), then MODEL_MAP lookup.

        Args:
            task: Task name (key in MODEL_MAP).

        Returns:
            Tuple of (provider, model_id).

        Raises:
            ConfigError: If the task is not defined and no override is set,
                or if a local_* task needs cloud substitution but no
                matching cloud_* task exists in MODEL_MAP.
        """
        override = os.environ.get(f"HUBLIB_TASK_{task.upper()}", "").strip()
        if override:
            if ":" not in override:
                raise ConfigError(
                    f"Env override for {task!r} must be 'provider:model_id', "
                    f"got {override!r}."
                )
            provider, model_id = override.split(":", 1)
            return provider.strip(), model_id.strip()

        if task.startswith("local_") and not machine_capability.has_local_llm():
            cloud_task = task.replace("local_", "cloud_", 1)
            if cloud_task not in MODEL_MAP:
                raise ConfigError(
                    f"No local LLM tier on this machine and no cloud "
                    f"equivalent {cloud_task!r} defined in MODEL_MAP for "
                    f"{task!r}."
                )
            logger.info(
                "No local LLM tier on this machine -- routing %r to %r.",
                task, cloud_task,
            )
            task = cloud_task

        if task not in MODEL_MAP:
            raise ConfigError(
                f"Task {task!r} not in MODEL_MAP. "
                f"Known tasks: {sorted(MODEL_MAP)}"
            )
        return MODEL_MAP[task]

    @classmethod
    def generate(cls, task: str, prompt: str, **kwargs) -> str:
        """Send a prompt to the model resolved for this task.

        Args:
            task: Task name (e.g. "vp_pattern", "local_fast").
            prompt: User prompt text.
            **kwargs: Provider-specific overrides (temperature, max_tokens,
                base_url for lmstudio).

        Returns:
            The model's response text.

        Raises:
            ConfigError: If the task or provider is unknown.
            ProviderError: If the provider call fails.
        """
        provider, model_id = cls.get_model(task)
        if provider not in _DISPATCH:
            raise ConfigError(
                f"Unknown provider {provider!r} for task {task!r}. "
                f"Known providers: {sorted(_DISPATCH)}"
            )
        call = _DISPATCH[provider]
        return call(model_id, prompt, **kwargs)
