"""smoke_test_v1_1.py - Verify P_800 Vault Interface v1.1 import pattern.

Run from p140 conda env:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe smoke_test_v1_1.py

Tests the guide's documented import path. No vault writes occur.
Result written to smoke_test_v1_1.log next to this file.
"""
import inspect
from pathlib import Path

LOG = Path(__file__).parent / "smoke_test_v1_1.log"

results = []
try:
    from shared_resources.python_utils.vault_interface import write_to_vault
    results.append("IMPORT_OK")
    results.append(f"SIGNATURE: {inspect.signature(write_to_vault)}")
    results.append(f"MODULE: {write_to_vault.__module__}")
except Exception as e:
    results.append(f"IMPORT_FAIL: {type(e).__name__}: {e}")

output = "\n".join(results)
LOG.write_text(output, encoding="utf-8")
print(output)
