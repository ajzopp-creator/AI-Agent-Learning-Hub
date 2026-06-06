"""
Debug: Test unload endpoint and verify models response updates correctly.
Run from P_000 folder with LM Studio running and a model loaded.

python python/tests/debug_unload_endpoint.py
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))  # Hub root

from integrations.lm_studio.config import (
    LM_STUDIO_MODELS_ENDPOINT,
    LM_STUDIO_UNLOAD_ENDPOINT,
)


async def get_loaded_models():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(LM_STUDIO_MODELS_ENDPOINT)
        data = r.json()
        loaded = [
            m['loaded_instances'][0]['id']
            for m in data.get('models', [])
            if m.get('loaded_instances')
        ]
        return loaded


async def main():
    print("\n" + "="*60)
    print("DEBUG: Unload endpoint + models response timing")
    print("="*60 + "\n")

    print("Before unload:")
    print(f"  Loaded: {await get_loaded_models()}\n")

    print("Calling unload for qwen2.5-coder-32b-instruct-abliterated...")
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            LM_STUDIO_UNLOAD_ENDPOINT,
            json={"instance_id": "qwen2.5-coder-32b-instruct-abliterated"},
            headers={"Content-Type": "application/json"},
        )
        print(f"  Status: {r.status_code}")
        try:
            print(f"  Body  : {json.dumps(r.json(), indent=2)}")
        except Exception:
            print(f"  Body  : {r.text}")

    for wait in [1, 2, 3, 5, 8]:
        await asyncio.sleep(1)
        loaded = await get_loaded_models()
        print(f"  After {wait}s: Loaded = {loaded}")
        if not loaded:
            print("  ✓ Unload confirmed by API")
            break


if __name__ == "__main__":
    asyncio.run(main())
