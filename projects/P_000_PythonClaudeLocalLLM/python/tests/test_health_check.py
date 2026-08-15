"""
LM Studio Wrapper — Health Check
Comprehensive verification: LM Studio running, config valid, model loads/unloads and responds.
Loads primary model, sends a test prompt, then unloads (cleanup).
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))        # python/
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))  # Hub root

from integrations.lm_studio.application.lm_studio_client import LMStudioClient
from integrations.lm_studio.domain.task_router import list_all_tasks
from integrations.lm_studio.config import MODELS


async def main():
    print("\n" + "="*70)
    print("LM STUDIO WRAPPER — HEALTH CHECK")
    print("="*70 + "\n")
    
    # 1. Initialize and verify LM Studio is responding
    client = LMStudioClient()
    print("▶ Step 1: Verifying LM Studio is running...")
    is_healthy = await client.startup()
    
    if not is_healthy:
        print("✗ LM Studio not responding at http://localhost:1234")
        print("  Launch: C:\\Program Files\\LM Studio\\LM Studio.exe")
        return False
    
    print("✓ LM Studio is responsive\n")
    
    # 2. Verify configuration
    print("▶ Step 2: Verifying configuration...")
    try:
        task_count = len(list_all_tasks())
        primary_model = MODELS["primary"]["id"]
        print(f"✓ Config valid: {task_count} task types\n")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False
    
    # 3. Load primary model
    print(f"▶ Step 3: Loading primary model ({primary_model})...")
    try:
        await client.switch_model(primary_model)
        print(f"✓ Model loaded successfully\n")
    except Exception as e:
        print(f"✗ Model load failed: {e}")
        return False
    
    # 4. Test the model with a simple prompt
    print("▶ Step 4: Testing model with a simple prompt...")
    try:
        test_prompt = "Respond with exactly: OK"
        response = await client.chat(
            messages=[{"role": "user", "content": test_prompt}],
            task_type="quick_coding"
        )
        
        if response and response.strip():
            print(f"✓ Model responded: {response[:60].strip()}...\n")
        else:
            print("✗ Model did not respond\n")
            return False
    except Exception as e:
        print(f"✗ Model test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Unload model (cleanup)
    print("▶ Step 5: Unloading model (cleanup)...")
    try:
        await client.switch_model(None)
        print("✓ Model unloaded\n")
    except Exception as e:
        print(f"⚠ Unload warning: {e}\n")
    
    # 6. Summary
    print("="*70)
    print("✓ HEALTH CHECK PASSED — System is fully operational")
    print("="*70)
    print(f"\nPrimary model: {primary_model}")
    print(f"Task routing: {task_count} task types available")
    print("\nReady to use:")
    print("  response = await client.chat(messages=[...], task_type='market_analysis')")
    print()
    
    return True


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
