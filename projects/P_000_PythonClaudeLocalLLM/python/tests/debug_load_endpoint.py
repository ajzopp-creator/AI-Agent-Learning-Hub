"""
Debug: What does the load endpoint actually return?
Run from P_000 folder with LM Studio running.

python python/tests/debug_load_endpoint.py
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))  # Hub root

from integrations.lm_studio.config import LM_STUDIO_LOAD_ENDPOINT, MODELS


async def main():
    model_id = MODELS["batch"]["id"]  # qwen2.5-coder-32b-instruct

    print(f"\nEndpoint : {LM_STUDIO_LOAD_ENDPOINT}")
    print(f"Model    : {model_id}")
    print(f"Payload  : {{\"model\": \"{model_id}\"}}\n")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                LM_STUDIO_LOAD_ENDPOINT,
                json={"model": model_id}
            )
            print(f"Status code : {response.status_code}")
            print(f"Response    :\n{json.dumps(response.json(), indent=2)}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error  : {e.response.status_code}")
        print(f"Body        : {e.response.text}")
    except Exception as e:
        print(f"Exception   : {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
