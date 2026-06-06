#!/usr/bin/env python
"""Smoke test: run Pipeline B on SPY, capture output for Obsidian write"""

import sys
import os
from pathlib import Path

# Ensure imports work from project root
proj_python = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python"
if proj_python not in sys.path:
    sys.path.insert(0, proj_python)

from application.daily_evaluate_pipeline import run_daily_evaluate

symbol = "SPY"
proj_root = Path(proj_python).parent
xlsx_path = proj_root / "data" / "live" / f"History Grid ({symbol}).xlsx"

print(f"\n{'='*60}")
print(f"SMOKE TEST: {symbol} Pipeline B Evaluation")
print(f"{'='*60}")
print(f"Looking for: {xlsx_path}\n")

if not xlsx_path.exists():
    print(f"[SMOKE TEST FAIL]: File not found: {xlsx_path}\n")
    sys.exit(1)

try:
    result = run_daily_evaluate(xlsx_path)
    
    print(f"\n{'='*60}")
    print("OUTPUT FOR OBSIDIAN WRITE:")
    print(f"{'='*60}")
    print(f"Symbol:        {result.ticker}")
    print(f"Signal:        {result.signal_class.value}")
    print(f"Anchor Date:   {result.anchor_date}")
    print(f"Horizon:       {result.chosen_horizon}d")
    
    if result.per_horizon_stats:
        h_stats = result.per_horizon_stats.get(result.chosen_horizon, {})
        print(f"Win Rate:      {h_stats.get('win_rate', 0):.2%}")
        print(f"Mean Return:   {h_stats.get('mean_return', 0):.2%}")
        print(f"Z-Score:       {h_stats.get('z_score', 0):.3f}")
    
    if result.volatility_divergence:
        print(f"Vol Flag:      {result.volatility_divergence.severity.value}")
    
    if result.top_matches:
        print(f"Top 5 Analogs: {[m.pattern_instance_id for m in result.top_matches[:5]]}")
    
    print(f"\n[SMOKE TEST PASS]\n")
    
except Exception as e:
    print(f"\n[SMOKE TEST FAIL]: {type(e).__name__}: {e}\n")
    import traceback
    traceback.print_exc()
