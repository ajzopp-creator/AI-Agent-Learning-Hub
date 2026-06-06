"""
Smoke Test — lm_studio_launcher.ensure_lm_studio_ready()
Run with LM Studio already running and deepseek-r1-distill-qwen-14b loaded.

Run from P_000 folder:
  python test_launcher.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))        # python/
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))  # Hub root

from integrations.lm_studio.infrastructure.lm_studio_launcher import ensure_lm_studio_ready


async def main():
    print("\n" + "="*70)
    print("SMOKE TEST — ensure_lm_studio_ready()")
    print("="*70)

    # Test: correct model already loaded — should pass with no prompt
    result = await ensure_lm_studio_ready(task_type="market_analysis")

    print("="*70)
    print(f"Result: {'✓ PASSED' if result else '✗ FAILED'}")
    print("="*70 + "\n")
    return result


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
