"""
FILE: P_300_EvaluateTrade.py
VERSION: 4.7 (SIGNAL ENGINE + AUTO-ADD PREP)
DATE: 2026-05-11
"""
import sys
import json
import pandas as pd
from pathlib import Path
import sqlite3

# Path Configuration
P300_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
DATA_SOURCE = P300_ROOT / "data" / "live" 
DB_PATH = P300_ROOT / "models" / "051126geminicatalog.db"
P010_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json")

def get_signal(z, wr, posture):
    if posture < -1.0: return "NOBUY (MARKET)"
    if z >= 1.2 and wr >= 0.68: return "BUY"
    if z >= 0.5 or wr >= 0.60: return "WATCH"
    return "NOBUY"

def main():
    with open(P010_PATH, 'r') as f:
        posture = json.load(f).get('avg_posture', 0.0)

    print("============================================================")
    print(f" P_300 DAILY WORKFLOW — v4.7 (POSTURE: {posture:.2f})")
    print("============================================================")
    
    files = list(DATA_SOURCE.glob("*.csv"))
    if not files: return

    print(f" {'SYMBOL':<10} | {'Z-SCORE':<8} | {'WIN%':<8} | {'SIGNAL':<15}")
    print("-" * 60)

    for f in files:
        symbol = f.stem.split("(")[1].split(")")[0] if "(" in f.stem else f.stem
        
        # Logic Placeholder: In production, these variables are populated by 
        # run_aggregator() for matched symbols and intelliscan for Agnostic.
        # CURRENT MOCK DATA BASED ON YOUR LAST RUN:
        mock_data = {
            "NVDA": (1.45, 0.72),
            "AEM": (0.85, 0.64),
            "KGC": (0.20, 0.45)
        }
        z, wr = mock_data.get(symbol, (0.0, 0.0))

        signal = get_signal(z, wr, posture)
        print(f" {symbol:<10} | {z:<8.2f} | {wr:<8.1%} | {signal:<15}")

    print("\n--- Workflow Complete ---")

if __name__ == "__main__":
    main()