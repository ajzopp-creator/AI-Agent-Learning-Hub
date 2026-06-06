"""
P_300 Integration Example: Status Check Only

Shows how P_300 can check LM Studio state without changing anything.
No imports of the full client, no async startup, no side effects.

This is the MINIMAL change P_300 needs to handle LM Studio errors gracefully.
"""

import asyncio
from integrations.lm_studio.infrastructure.lm_studio_api import get_wrapper_status


async def check_lm_studio_ready() -> bool:
    """
    P_300 calls this once at startup.
    Returns True if ready, False if needs action.
    """
    status = await get_wrapper_status()
    
    if not status['lm_studio_running']:
        print(f"⚠ {status['action_required']}")
        return False
    
    if status['model_mismatch']:
        print(f"⚠ {status['action_required']}")
        return False
    
    print(f"✓ {status['message']}")
    return True


# ── USAGE IN P_300 ────────────────────────────────────────────────────────────
# Just add this to P_300's main startup:
#
#   from integrations.lm_studio.examples.p300_status_check import check_lm_studio_ready
#
#   if not await check_lm_studio_ready():
#       print("Fix the issue above, then re-run")
#       sys.exit(1)
#
# P_300 does NOT need:
#   - LMStudioClient import
#   - startup() or switch_model() calls
#   - Any async event loop management
#
# This single query tells P_300 everything it needs to know.
# ──────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    # Demo: Run this to see the status check in action
    result = asyncio.run(check_lm_studio_ready())
    print(f"\nReady: {result}")
