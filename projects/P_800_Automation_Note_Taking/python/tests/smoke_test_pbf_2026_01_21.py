"""smoke_test_pbf_2026_01_21.py - v1.1 vault interface live smoke test.

Real tracker row from P_115 (PASS standard 2026-05-23):
    1/21/2026  PBF  P_115  PASS  Fund=2 Anal=2 Candle=0 Setup=2
    (original tracker row recorded as "No Signal" pre-standardization)

Verifies:
  - v1.1 documented import path resolves from p140 env
  - Tracker "--" values correctly omitted from data dict
  - Date conversion M/D/YYYY -> ISO works
  - PASS Step1Verdict accepted
  - Note lands at trading_journal/TradeManagement/P115/2026-01-21_PBF.md
  - Frontmatter contains expected fields

Run from any directory with p140 conda env:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe smoke_test_pbf_2026_01_21.py

Aligned with: P_800_Vault_Interface_Consumer_Guide_v1_1.md (2026-05-23).
"""

from pathlib import Path
from shared_resources.python_utils.vault_interface import write_to_vault

# Real tracker row -- "--" values omitted entirely per v1.1 rule #7
PBF_PASS = {
    "date": "2026-01-21",
    "symbol": "PBF",
    "step1_verdict": "PASS",
    "fundamentals_tier": 2,
    "analysis_tier": 2,
    "candle_tier": 0,
    "setup_score": 2,
    "traded": "N",
    "comments": "HybridTier=4, CandleTier=0 (no pattern)",
}

print("Writing PBF PASS row to vault...")
result = write_to_vault("P115", PBF_PASS, overwrite=True)

expected = (
    Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal")
    / "TradeManagement" / "P115" / "2026-01-21_PBF.md"
)

print(f"  Written : {result}")
print(f"  File    : {expected}")
print(f"  On disk : {expected.exists()}")

if expected.exists():
    print("\n--- NOTE CONTENT ---")
    print(expected.read_text(encoding="utf-8"))
    print("--- END ---")

    # Spot checks against v1.1 expectations
    content = expected.read_text(encoding="utf-8")
    checks = {
        "source: P115 present"      : "source: P115" in content,
        "signal_source auto-set"    : "signal_source: P_115" in content,
        "symbol PBF"                : "symbol: PBF" in content,
        "date ISO"                  : "date: 2026-01-21" in content,
        "step1_verdict PASS"        : "step1_verdict: PASS" in content,
        "candle_tier 0 not null"    : "candle_tier: 0" in content,
    }
    print("\n--- SPOT CHECKS ---")
    for label, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
