"""
Debug: Check what LM Studio actually returns for models endpoint
"""

import asyncio
import httpx
import json


async def main():
    print("\n" + "="*70)
    print("DEBUG: LM Studio /api/v1/models Response")
    print("="*70 + "\n")
    
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get('http://localhost:1234/api/v1/models')
            data = response.json()
            
            print("Raw response:")
            print(json.dumps(data, indent=2))
            
            print("\n" + "-"*70)
            print("Key fields:")
            if isinstance(data, dict):
                for key in data.keys():
                    print(f"  • {key}")
            
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(main())
