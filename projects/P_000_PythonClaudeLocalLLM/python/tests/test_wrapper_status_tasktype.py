"""
Smoke Test — get_wrapper_status(task_type=...)
Verifies that expected_model resolves correctly for each model tier.
Does NOT switch models — read-only status checks only.

Run from P_000 folder:
  python test_wrapper_status_tasktype.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))        # python/
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))  # Hub root

from integrations.lm_studio.infrastructure.lm_studio_api import get_wrapper_status
from integrations.lm_studio.config import MODELS


async def main():
    print("\n" + "="*70)
    print("SMOKE TEST — get_wrapper_status(task_type=...)")
    print("="*70 + "\n")

    # Three test cases — one per tier
    test_cases = [
        ("market_analysis",        "primary",      MODELS["primary"]["id"]),
        ("trade_journal_analysis", "batch",        MODELS["batch"]["id"]),
        ("full_document_ingestion","long_context", MODELS["long_context"]["id"]),
        (None,                     "primary",      MODELS["primary"]["id"]),  # default
    ]

    all_passed = True

    for task_type, expected_tier, expected_model_id in test_cases:
        label = f'task_type="{task_type}"' if task_type else "task_type=None (default)"
        print(f"▶ {label}")
        print(f"  Expected tier:  {expected_tier}")
        print(f"  Expected model: {expected_model_id}")

        status = await get_wrapper_status(task_type=task_type)

        actual = status['expected_model']
        match = actual == expected_model_id

        if match:
            print(f"  ✓ expected_model correct: {actual}")
        else:
            print(f"  ✗ MISMATCH — got: {actual}")
            all_passed = False

        print(f"  LM Studio running: {status['lm_studio_running']}")
        print(f"  Current model:     {status['current_model']}")
        print(f"  Model mismatch:    {status['model_mismatch']}")
        print()

    print("="*70)
    if all_passed:
        print("✓ ALL TESTS PASSED — task_type routing is correct")
    else:
        print("✗ SOME TESTS FAILED — check output above")
    print("="*70 + "\n")

    return all_passed


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
