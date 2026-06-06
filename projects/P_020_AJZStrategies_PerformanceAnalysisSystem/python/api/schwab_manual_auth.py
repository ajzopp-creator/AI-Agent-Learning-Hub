#!/usr/bin/env python3
"""
Schwab Manual OAuth Test
Bypasses schwab-py entirely - talks directly to Schwab API
"""

import importlib.util
import urllib.parse
import webbrowser
from pathlib import Path

# Load credentials
CREDS_PATH = Path(__file__).parent / "schwab_credentials.py"
spec = importlib.util.spec_from_file_location("creds", CREDS_PATH)
creds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(creds)

APP_KEY      = creds.APP_KEY
APP_SECRET   = creds.APP_SECRET
CALLBACK_URL = creds.CALLBACK_URL

print("=" * 70)
print("SCHWAB MANUAL OAUTH TEST")
print("=" * 70)
print(f"App Key (first 8): {APP_KEY[:8]}...")
print(f"Callback URL: {CALLBACK_URL}")

# Step 1: Build the authorization URL manually
auth_url = (
    "https://api.schwabapi.com/v1/oauth/authorize"
    f"?client_id={urllib.parse.quote(APP_KEY)}"
    f"&redirect_uri={urllib.parse.quote(CALLBACK_URL)}"
    f"&response_type=code"
    f"&scope=readonly"
)

print("\n" + "=" * 70)
print("STEP 1: Copy this URL and paste it into your browser:")
print("=" * 70)
print(auth_url)
print("\n(Or it may open automatically in your browser)")

try:
    webbrowser.open(auth_url)
except:
    pass

print("\n" + "=" * 70)
print("STEP 2: Log in to Schwab with your BROKERAGE account credentials")
print("STEP 3: Authorize the app")  
print("STEP 4: You'll land on a blank/error page - copy the FULL URL from address bar")
print("STEP 5: Paste the full redirect URL below")
print("=" * 70)

redirect_response = input("\nPaste the full redirect URL here: ").strip()

# Step 2: Extract the authorization code
parsed = urllib.parse.urlparse(redirect_response)
params = urllib.parse.parse_qs(parsed.query)

if 'code' not in params:
    print(f"\nERROR: No 'code' found in URL")
    print(f"URL params found: {list(params.keys())}")
    exit(1)

auth_code = params['code'][0]
print(f"\nAuthorization code received (first 20 chars): {auth_code[:20]}...")

# Step 3: Exchange code for token
import base64
import json
try:
    import httpx
except ImportError:
    import urllib.request

print("\nStep 3: Exchanging code for token...")

credentials = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()

import urllib.request
import urllib.error

token_data = urllib.parse.urlencode({
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': CALLBACK_URL
}).encode()

req = urllib.request.Request(
    'https://api.schwabapi.com/v1/oauth/token',
    data=token_data,
    headers={
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    method='POST'
)

try:
    with urllib.request.urlopen(req) as response:
        token_response = json.loads(response.read().decode())
        print("\nSUCCESS! Token received:")
        print(f"  access_token (first 20): {token_response.get('access_token','')[:20]}...")
        print(f"  token_type: {token_response.get('token_type')}")
        print(f"  expires_in: {token_response.get('expires_in')} seconds")
        
        # Save token
        token_path = Path(__file__).parent / "schwab_token.json"
        with open(token_path, 'w') as f:
            json.dump(token_response, f, indent=2)
        print(f"\nToken saved to: {token_path}")
        print("\nAPI authentication CONFIRMED WORKING!")
        
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"\nHTTP Error {e.code}: {e.reason}")
    print(f"Response: {error_body}")
except Exception as e:
    print(f"\nError: {e}")
