"""test_p115_write.py - v1.1 smoke test for the P_800 vault interface.

Run from any directory with p140 conda env:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe test_p115_write.py

Verifies the v1.1 guide's documented import path and writes one sample
P_115 note to the vault. Safe to re-run -- uses overwrite=True.

Aligned with: P_800_Vault_Interface_Consumer_Guide_v1_1.md (2026-05-23).
"""

from pathlib import Path
from shared_resources.python_utils.vault_interface import write_to_vault

SAMPLE = {
    "date": "2026-05-22",
    "symbol": "AAPL",
    "step1_verdict": "BUY",
    "market_direction": "FULL",   # P_010 risk_mode JSON value
    "fundamentals_tier": 3,
    "analysis_tier": 3,
    "candle_tier": 2,
    "setup_score": 5,
    "traded": "N",
    "account_balance": 32812,
    "comments": "Smoke test - safe to delete",
}

print("Writing sample P_115 note to vault...")
result = write_to_vault("P115", SAMPLE, overwrite=True)

expected = (
    Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal")
    / "TradeManagement" / "P115" / "2026-05-22_AAPL.md"
)

print(f"  Written : {result}")
print(f"  File    : {expected}")
print(f"  On disk : {expected.exists()}")

if expected.exists():
    print("\n--- NOTE CONTENT ---")
    print(expected.read_text(encoding="utf-8"))
    print("--- END ---")
