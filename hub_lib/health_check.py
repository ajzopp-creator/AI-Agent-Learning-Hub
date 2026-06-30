"""Provider health checks (Canary).

Run verify_health() once at session startup to confirm that each provider
you plan to use is reachable. Raises ModelUnavailableError on the first
failure; the caller decides whether to abort or fall back.

Do NOT call check_provider() per-request - Gemini's free tier rate-limits
will exhaust quickly. Health checks are session-level, not request-level.
"""

import logging
from typing import Iterable

from .exceptions import ModelUnavailableError, ProviderError
from .model_manager import ModelManager

logger = logging.getLogger(__name__)

PING_PROMPT = "ping"


def check_provider(task: str) -> None:
    """Send a minimal prompt to the model for `task`.

    Args:
        task: Task name (e.g. "vp_pattern").

    Raises:
        ModelUnavailableError: If the provider fails the ping.
    """
    provider, model_id = ModelManager.get_model(task)
    logger.info("Health check: %s -> %s/%s", task, provider, model_id)
    try:
        ModelManager.generate(task, PING_PROMPT, max_tokens=10)
    except ProviderError as exc:
        raise ModelUnavailableError(
            f"Health check FAILED for task {task!r} "
            f"({provider}/{model_id}): {exc}"
        ) from exc
    logger.info("Health check OK: %s/%s", provider, model_id)


def verify_health(tasks: Iterable[str]) -> None:
    """Run check_provider() for each task in order.

    Args:
        tasks: Iterable of task names to verify.

    Raises:
        ModelUnavailableError: On the first failed task.
    """
    for task in tasks:
        check_provider(task)
