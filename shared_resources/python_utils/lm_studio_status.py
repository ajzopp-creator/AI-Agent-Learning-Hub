"""
FILE: lm_studio_status.py
VERSION: 1.0
DATE: 2026-08-11
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure (shared hub utility)
DESCRIPTION:
    LM Studio readiness check -- shared hub interface (WO-P000-E5.001).

    Ported from integrations/lm_studio/infrastructure/lm_studio_status.py
    (a Hub-level module with no project owner) to shared_resources/python_utils/
    so every consuming project imports a real Hub interface instead of
    reaching into another module's internals -- mirrors the precedent
    already set for Obsidian writes (vault_interface.py, M-038) and ATR
    (atr.py, M-049).

    Each consuming project adds its own thin infrastructure/lm_studio_status.py
    wrapper that calls check() below. application/ layers never import this
    module directly (Process Boundary Standard).

    Usage (from a project's own infrastructure/ wrapper, never from
    application/ directly):
        from shared_resources.python_utils.lm_studio_status import check
        if not check(task_type='vantagepoint_analysis'):
            return 1

CHANGELOG:
    - 2026-08-11 v1.0: Ported from integrations/lm_studio/infrastructure/
      lm_studio_status.py v1.2 (WO-P000-E5.001). No behavior change --
      same get_wrapper_status() call, same return contract, no sys.path
      manipulation needed here (resolves via the Hub's editable install).
      Old location deleted, not shimmed, once P_300 migrated to its own
      infrastructure/ wrapper importing this module (Tony's call).
"""
from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)


def check(
    clean: bool = False,
    task_type: str | None = None,
) -> bool:
    """Query LM Studio status. Return True if ready, False otherwise.

    Args:
        clean: If True, failure messages use compact [NARRATOR UNAVAILABLE]
               prefix. If False, full multi-line message.
        task_type: Optional task type for model routing
                   (e.g. 'vantagepoint_analysis'). None uses primary model.
                   Routing table lives in integrations/lm_studio/config.py
                   (Hub-level, single source of truth) -- not duplicated
                   here or in any consuming project's own config.py.

    Returns:
        True  -- LM Studio running, correct model loaded.
        False -- not running, wrong model, or query failed.
    """
    from integrations.lm_studio.infrastructure.lm_studio_api import (
        get_wrapper_status,
    )

    status = asyncio.run(get_wrapper_status(task_type=task_type))

    if not status["lm_studio_running"]:
        msg = (
            "LM Studio is not running.\n"
            "Run the launcher to start it:\n"
            "  python C:\\Users\\Trader\\AI-Agent-Learning-Hub"
            "\\integrations\\lm_studio\\infrastructure\\lm_studio_launcher.py"
        )
        print(f"[NARRATOR UNAVAILABLE] {msg}" if clean else msg)
        logger.warning("LM Studio not running.")
        return False

    if status["model_mismatch"]:
        msg = (
            f"Wrong model loaded: {status['current_model']}\n"
            f"Required: {status['expected_model']}\n"
            "Run the launcher to switch models:\n"
            "  python C:\\Users\\Trader\\AI-Agent-Learning-Hub"
            "\\integrations\\lm_studio\\infrastructure\\lm_studio_launcher.py"
        )
        print(f"[NARRATOR UNAVAILABLE] {msg}" if clean else msg)
        logger.warning("LM Studio model mismatch: %s", status["current_model"])
        return False

    logger.info("LM Studio ready: %s", status["current_model"])
    return True
