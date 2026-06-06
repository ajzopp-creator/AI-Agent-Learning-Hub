"""
LM Studio Connection Test
Tests your connection to the local LM Studio server

Run this AFTER:
1. Starting LM Studio
2. Loading a model
3. Starting the local server

Author: AI Agent Learning Hub
"""

import requests
import json
from datetime import datetime

# Configuration
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
BACKUP_URL = "http://127.0.0.1:1234/v1/chat/completions"

def test_connection(url):
    """
    Test if LM Studio is responding
    """
    print(f"\n🔍 Testing connection to {url}...")
    
    try:
        # Simple test prompt
        test_data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Respond in one short sentence."
                },
                {
                    "role": "user",
                    "content": "Say 'Connection successful' if you can read this."
                }
            ],
            "temperature": 0.7,
            "max_tokens": 50
        }
        
        # Make the request
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30  # 30 second timeout
        )
        
        # Check if successful
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print("✅ SUCCESS! LM Studio is responding.")
            print(f"📝 Response: {message}")
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused. Is LM Studio running?")
        print("   Make sure:")
        print("   1. LM Studio is open")
        print("   2. A model is loaded")
        print("   3. Local server is started")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Model might be loading...")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_with_trading_prompt():
    """
    Test with a trading-related prompt
    """
    print("\n📊 Testing with a trading question...")
    
    try:
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a financial education assistant. Keep responses brief."
                },
                {
                    "role": "user",
                    "content": "What is a stop loss order in one sentence?"
                }
            ],
            "temperature": 0.3,  # Lower for factual responses
            "max_tokens": 100
        }
        
        response = requests.post(
            LM_STUDIO_URL,
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            print(f"✅ Response: {answer}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def display_system_info():
    """
    Display system information and next steps
    """
    print("\n" + "="*60)
    print("🎯 LM STUDIO CONNECTION TEST")
    print("="*60)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Test URL: {LM_STUDIO_URL}")
    print("="*60)

def main():
    """
    Main test function
    """
    display_system_info()
    
    # Test primary URL
    success = test_connection(LM_STUDIO_URL)
    
    # If failed, try backup URL
    if not success:
        print("\n🔄 Trying backup URL...")
        success = test_connection(BACKUP_URL)
    
    # If connected, run additional test
    if success:
        test_with_trading_prompt()
        
        print("\n" + "="*60)
        print("🎉 CONNECTION SUCCESSFUL!")
        print("="*60)
        print("\n✅ You're ready to build AI agents!")
        print("\nNext steps:")
        print("1. Check out basic_chat.py for an interactive chat")
        print("2. Try financial_agent.py for stock analysis")
        print("3. Build your own agent!")
        print("\n💡 Tip: Keep LM Studio running while developing")
        
    else:
        print("\n" + "="*60)
        print("❌ CONNECTION FAILED")
        print("="*60)
        print("\n🔧 Troubleshooting steps:")
        print("\n1. Open LM Studio")
        print("2. Go to 'Local Server' tab")
        print("3. Click 'Start Server'")
        print("4. Make sure a model is loaded in the 'Chat' tab")
        print("5. Check that the port is 1234 (default)")
        print("6. Run this test again")
        print("\n📚 Need more help? Check:")
        print("   - 05-Documentation/troubleshooting.md")
        print("   - LM Studio documentation")
        print("   - This folder's README.md")

if __name__ == "__main__":
    main()

# ============================================
# DEBUGGING TIPS
# ============================================

"""
Common Issues and Solutions:

1. "Connection refused"
   → LM Studio server isn't running
   → Start it in LM Studio → Local Server tab

2. "Timeout" error
   → Model is still loading (wait 30-60 seconds)
   → Model is too large for your system
   → Try a smaller model (7B instead of 13B)

3. Empty or weird responses
   → Model not fully loaded
   → Restart LM Studio
   → Try different model

4. "Port already in use"
   → Another app is using port 1234
   → Change port in LM Studio settings
   → Update URL in this script

5. Slow responses
   → Normal for large models
   → Close other applications
   → Use GPU acceleration if available
   → Try smaller model

Need more help?
→ Discord: https://discord.gg/aPQfnNkxGC
→ Docs: https://lmstudio.ai/docs
"""

# ============================================
# ADVANCED: Check Model Info
# ============================================

def check_model_info():
    """
    Get information about the loaded model
    (Advanced - requires LM Studio API v1)
    """
    try:
        # This endpoint may not work in all LM Studio versions
        info_url = "http://localhost:1234/v1/models"
        response = requests.get(info_url)
        
        if response.status_code == 200:
            models = response.json()
            print("\n📦 Loaded Models:")
            print(json.dumps(models, indent=2))
        else:
            print("ℹ️ Model info not available")
            
    except:
        pass  # Not critical if this fails

# Uncomment to test model info:
# check_model_info()
