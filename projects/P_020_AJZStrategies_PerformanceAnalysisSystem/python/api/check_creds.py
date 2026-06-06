import importlib.util
from pathlib import Path

CREDS_PATH = Path(__file__).parent / "schwab_credentials.py"
spec = importlib.util.spec_from_file_location("creds", CREDS_PATH)
creds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(creds)

key = creds.APP_KEY
secret = creds.APP_SECRET
url = creds.CALLBACK_URL

print("=== CREDENTIALS CHECK ===")
print(f"APP_KEY    length: {len(key)}")
print(f"APP_KEY    first8: [{key[:8]}]")
print(f"APP_KEY    last4:  [{key[-4:]}]")
print(f"APP_SECRET length: {len(secret)}")
print(f"APP_SECRET first4: [{secret[:4]}]")
print(f"APP_SECRET last4:  [{secret[-4:]}]")
print(f"CALLBACK_URL: [{url}]")

# Check for hidden characters
print(f"\nAPP_KEY    repr (first 20): {repr(key[:20])}")
print(f"APP_SECRET repr (first 10): {repr(secret[:10])}")

# Check if there are any whitespace characters
if key != key.strip():
    print("WARNING: APP_KEY has leading/trailing whitespace!")
if secret != secret.strip():
    print("WARNING: APP_SECRET has leading/trailing whitespace!")
if '\n' in key or '\r' in key:
    print("WARNING: APP_KEY contains newline characters!")
if '\n' in secret or '\r' in secret:
    print("WARNING: APP_SECRET contains newline characters!")

print("\nAll looks clean!" if key == key.strip() and secret == secret.strip() else "")
