#!/usr/bin/env python
"""Smoke test: run Pipeline B on VZ, capture output for Obsidian write"""

import sys
import os
from pathlib import Path

# Ensure imports work from project root
proj_python = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python"
if proj_python not in sys.path:
    sys.path.insert(0, proj_python)

from application.daily_evaluate_pipeline import run_daily_evaluate

symbol = "VZ"
proj_root = Path(proj_python).parent
xlsx_path = proj_root / "data" / "live" / f"History Grid ({symbol}).xlsx"

print(f"\n{'='*60}")
print(f"SMOKE TEST: {symbol} Pipeline B Evaluation")
print(f"{'='*60}")
print(f"Using: {xlsx_path.name}\n")

if not xlsx_path.exists():
    print(f"[SMOKE TEST FAIL]: File not found: {xlsx_path}\n")
    sys.exit(1)

try:
    result = run_daily_evaluate(xlsx_path)
    
    print(f"\n{'='*60}")
    print("EXTRACTION FOR OBSIDIAN WRITE:")
    print(f"{'='*60}")
    print(f"date:          {result.anchor_date.strftime('%Y-%m-%d')}")
    print(f"symbol:        {result.ticker}")
    print(f"source:        P_300")
    print(f"signal:        {result.signal_class.value}")
    print(f"anchor_date:   {result.anchor_date.strftime('%Y-%m-%d')}")
    print(f"signal_horizon: {result.chosen_horizon}")
    
    # Extract stats from the chosen horizon (Pydantic model, not dict)
    if result.chosen_horizon in result.per_horizon_stats:
        h_stats = result.per_horizon_stats[result.chosen_horizon]
        print(f"h{result.chosen_horizon}_win_rate: {h_stats.win_rate:.4f}")
        print(f"h{result.chosen_horizon}_mean_ret: {h_stats.mean_return_pct:.4f}")
        print(f"z_score:       {h_stats.z_score:.3f}")
    
    if result.volatility_divergence:
        print(f"vol_flag:      {result.volatility_divergence.severity.value}")
    
    if result.top_matches:
        print(f"top_analogs:   {[m.pattern_instance_id for m in result.top_matches[:3]]}")
    
    print(f"\n[SMOKE TEST PASS]\n")
    
except Exception as e:
    print(f"\n[SMOKE TEST FAIL]: {type(e).__name__}: {e}\n")
    import traceback
    traceback.print_exc()

