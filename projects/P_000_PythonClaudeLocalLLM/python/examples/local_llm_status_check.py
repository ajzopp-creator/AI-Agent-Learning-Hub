"""
Local LLM Status Check Example

Shows how any Hub project can check LM Studio readiness at startup.
No changes to project code required — just one status query.

Usage:
    from integrations.lm_studio.examples.local_llm_status_check import check_lm_studio_ready
    
    if not await check_lm_studio_ready():
        sys.exit(1)  # Operator needs to fix LM Studio
    
    # Continue with your project's workflow
"""

import asyncio
from integrations.lm_studio.infrastructure.lm_studio_api import get_wrapper_status


async def check_lm_studio_ready() -> bool:
    """
    Check if LM Studio is running and the primary model is loaded.
    
    Call this once at project startup.
    Returns True if ready, False if operator action is required.
    """
    status = await get_wrapper_status()
    
    if not status['lm_studio_running']:
        print(f"⚠ LM Studio not ready:\n  {status['action_required']}")
        return False
    
    if status['model_mismatch']:
        print(f"⚠ Model issue:\n  {status['action_required']}")
        return False
    
    print(f"✓ {status['message']}")
    return True


# ── INTEGRATION IN YOUR PROJECT ───────────────────────────────────────────────
#
# Add to your project's main startup function:
#
#   from integrations.lm_studio.examples.local_llm_status_check import check_lm_studio_ready
#   
#   async def main():
#       # Pre-flight check
#       if not await check_lm_studio_ready():
#           print("Fix the error above, then re-run")
#           sys.exit(1)
#       
#       # Project continues normally
#       # (No need to import LMStudioClient or manage async loops)
#
# ──────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    # Demo: Run to see the status check output
    result = asyncio.run(check_lm_studio_ready())
    print(f"\n→ LM Studio ready: {result}")
