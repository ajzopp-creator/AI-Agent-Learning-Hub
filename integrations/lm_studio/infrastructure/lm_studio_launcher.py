"""
LM Studio Launcher
Handles LM Studio lifecycle: startup, model verification, model switching.

Responsibility boundary:
    - This file owns all state changes (launch, load, unload).
    - get_wrapper_status() is read-only -- never changes state.
    - Projects call ensure_lm_studio_ready() once at startup, then proceed.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\integrations\\lm_studio\\infrastructure\\lm_studio_launcher.py
"""

import asyncio
import subprocess
import time
import httpx
import logging
import sys
from pathlib import Path
from typing import Optional

# Ensure Hub root is on path when run directly or imported from any project
_HUB_ROOT = Path(__file__).parent.parent.parent.parent
if str(_HUB_ROOT) not in sys.path:
    sys.path.insert(0, str(_HUB_ROOT))

from integrations.lm_studio.config import (
    LM_STUDIO_MODELS_ENDPOINT,
    HTTP_TIMEOUT_SECONDS,
    MODELS,
)
from integrations.lm_studio.infrastructure.lm_studio_api import (
    get_wrapper_status,
    load_model,
    unload_model,
)

# -- CONSTANTS -----------------------------------------------------------------
LM_STUDIO_EXE = r"C:\Program Files\LM Studio\LM Studio.exe"
STARTUP_WAIT_SECONDS = 15
STARTUP_POLL_INTERVAL = 2

logger = logging.getLogger(__name__)


# -- INTERNAL HELPERS ----------------------------------------------------------

async def _wait_for_lm_studio(timeout: int = STARTUP_WAIT_SECONDS) -> bool:
    """Poll until LM Studio responds or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                response = await client.get(LM_STUDIO_MODELS_ENDPOINT)
                if response.status_code == 200:
                    return True
        except httpx.HTTPError:
            pass
        await asyncio.sleep(STARTUP_POLL_INTERVAL)
    return False


def _launch_lm_studio(silent: bool = False) -> bool:
    """Launch LM Studio as a background process."""
    exe = Path(LM_STUDIO_EXE)
    if not exe.exists():
        if not silent:
            print(f"  ERROR: LM Studio not found at {LM_STUDIO_EXE}")
            print("  Update LM_STUDIO_EXE in lm_studio_launcher.py if installed elsewhere.")
        return False
    try:
        subprocess.Popen([str(exe)], shell=False)
        logger.info("LM Studio process launched")
        return True
    except Exception as e:
        logger.error(f"Failed to launch LM Studio: {e}")
        return False


def _prompt_model_switch(current: str, expected: str) -> bool:
    """Ask operator whether to switch models. Returns True if confirmed."""
    print(f"\n  Wrong model loaded.")
    print(f"  Currently loaded : {current}")
    print(f"  Required         : {expected}")
    answer = input("\n  Switch to correct model now? (y/n): ").strip().lower()
    return answer == "y"


# -- PUBLIC INTERFACE ----------------------------------------------------------

async def ensure_lm_studio_ready(
    task_type: Optional[str] = None,
    silent: bool = False,
) -> bool:
    """
    Ensure LM Studio is running and the correct model is loaded for task_type.

    Flow:
        1. If LM Studio not running  -> auto-launch, wait for ready
        2. If wrong model loaded     -> prompt operator, switch if confirmed
        3. If correct model loaded   -> proceed immediately

    Args:
        task_type: Task type string (e.g. 'market_analysis').
                   If None, defaults to primary model.
        silent: If True, suppress all print() output. Used by --clean mode
                in Pipeline B so launcher messages don't appear in batch runs.
                Logging is controlled separately via logging.disable().

    Returns:
        True if LM Studio is ready with the correct model loaded.
        False if startup failed or operator declined model switch.
    """
    if not silent:
        print("\n> Checking LM Studio readiness...")

    status = await get_wrapper_status(task_type=task_type)

    # Step 1 -- launch if not running
    if not status['lm_studio_running']:
        if not silent:
            print("  LM Studio not running -- launching...")
        launched = _launch_lm_studio(silent=silent)
        if not launched:
            return False
        if not silent:
            print(f"  Waiting up to {STARTUP_WAIT_SECONDS}s for LM Studio to start...")
        ready = await _wait_for_lm_studio()
        if not ready:
            if not silent:
                print("  ERROR: LM Studio did not respond after launch. Start it manually.")
            return False
        if not silent:
            print("  LM Studio is up.")
        # Re-query status after launch
        status = await get_wrapper_status(task_type=task_type)

    # Step 2 -- handle model mismatch
    # Note: model switch prompt always shown regardless of silent --
    # operator input is required and cannot be silenced.
    if status['model_mismatch']:
        confirmed = _prompt_model_switch(
            current=status['current_model'] or "none",
            expected=status['expected_model'],
        )
        if not confirmed:
            if not silent:
                print("  Model switch declined. Exiting.")
            return False
        # Unload current model before loading the new one
        if not silent:
            print(f"  Unloading {status['current_model']}...")
        await unload_model(model_id=status['current_model'])
        await asyncio.sleep(2)  # allow LM Studio to complete unload
        if not silent:
            print(f"  Loading {status['expected_model']}...")
        switched = await load_model(status['expected_model'])
        if not switched:
            if not silent:
                print("  ERROR: Model failed to load. Check LM Studio.")
            return False
        if not silent:
            print("  Model loaded successfully.")
        await asyncio.sleep(3)  # allow LM Studio to update loaded_instances state

    # Step 3 -- confirm ready
    final = await get_wrapper_status(task_type=task_type)
    if final['lm_studio_running'] and not final['model_mismatch']:
        if not silent:
            print(f"  OK {final['message']}\n")
        return True

    if not silent:
        print(f"  ERROR: {final['action_required']}")
    return False


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LM Studio Launcher")
    parser.add_argument(
        "--task-type",
        default=None,
        help="Task type to route to correct model (e.g. market_analysis). Defaults to primary."
    )
    args = parser.parse_args()

    ready = asyncio.run(ensure_lm_studio_ready(task_type=args.task_type))
    sys.exit(0 if ready else 1)
