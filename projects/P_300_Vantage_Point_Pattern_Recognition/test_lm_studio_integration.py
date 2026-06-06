"""
P_300 — LM Studio Integration Test
Simple test to verify status check works with P_300.

Run from P_300 folder:
  python test_lm_studio_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Add Hub root to path for imports
hub_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(hub_root))

from integrations.lm_studio.infrastructure.lm_studio_api import get_wrapper_status


async def main():
    print("\n" + "="*70)
    print("P_300 — LM Studio Status Check Test")
    print("="*70 + "\n")
    
    # Get LM Studio status
    print("▶ Checking LM Studio readiness...")
    status = await get_wrapper_status()
    
    # Display results
    print(f"\n  LM Studio running: {status['lm_studio_running']}")
    print(f"  Current model:    {status['current_model']}")
    print(f"  Expected model:   {status['expected_model']}")
    print(f"  Model mismatch:   {status['model_mismatch']}")
    
    # Handle errors
    if not status['lm_studio_running']:
        print(f"\n✗ ERROR: {status['action_required']}")
        return False
    
    if status['model_mismatch']:
        print(f"\n✗ ERROR: {status['action_required']}")
        return False
    
    # Success
    print(f"\n✓ {status['message']}")
    print("\n✓ P_300 is ready to use local LLM")
    return True


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
