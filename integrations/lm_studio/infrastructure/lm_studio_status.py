"""
FILE: lm_studio_status.py
VERSION: 1.2
DATE: 2026-05-30
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Hub-level LM Studio readiness check. Any project that uses LM Studio
    calls this module rather than implementing its own status gate.

    Wraps get_wrapper_status() and returns a clean bool to the caller.
    The application layer never touches asyncio or LM Studio internals.

    Usage (from any Hub project):
        from integrations.lm_studio.infrastructure.lm_studio_status import check
        if not check(task_type='vantagepoint_analysis'):
            return 1

CHANGELOG:
    - 2026-05-30 v1.2: Removed diag_log param and stdout/stderr redirect
      block — suppression approach did not work (LM Studio server writes
      to the process console handle, not Python stdout). Simplified to
      a clean asyncio.run() wrapper with no file handle management.
    - 2026-05-30 v1.1: Moved from P_300 infrastructure/ to Hub-level.
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
import sys

# Hub root bootstrap — resolve from this file's location.
# Path: lm_studio_status.py → infrastructure/ → lm_studio/ → integrations/ → Hub root
_HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_HUB_ROOT) not in sys.path:
    sys.path.insert(0, str(_HUB_ROOT))

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

    Returns:
        True  — LM Studio running, correct model loaded.
        False — not running, wrong model, or query failed.
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
