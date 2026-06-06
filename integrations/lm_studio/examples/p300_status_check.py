# FILE: integrations/lm_studio/examples/p300_status_check.py
# VERSION: 1.0
# DATE: 2026-05-29
# AUTHOR: Claude (architect)
# LAYER: example / test harness
# DESCRIPTION: Standalone test for get_wrapper_status(). Run from Hub root.
#   Validates LM Studio status and confirms the import path works correctly.
#   Does NOT change any LM Studio state.
#
# USAGE (from Hub root in ISE):
#   python integrations\lm_studio\examples\p300_status_check.py
#
# CHANGELOG:
#   1.0 - 2026-05-29 - Initial version

import asyncio
import sys
import os

# Ensure Hub root is on sys.path so the import resolves correctly
HUB_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
))))
if HUB_ROOT not in sys.path:
    sys.path.insert(0, HUB_ROOT)

from integrations.lm_studio.infrastructure.lm_studio_api import get_wrapper_status


async def main():
    print("P_300 LM Studio Status Check")
    print("=" * 40)

    status = await get_wrapper_status()

    print(f"LM Studio running : {status['lm_studio_running']}")
    print(f"Expected model    : {status['expected_model']}")
    print(f"Current model     : {status['current_model']}")
    print(f"Model mismatch    : {status['model_mismatch']}")
    print(f"Message           : {status['message']}")

    if status['action_required']:
        print(f"\nACTION REQUIRED: {status['action_required']}")
        sys.exit(1)
    else:
        print("\nOK - LM Studio is ready for P_300.")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
