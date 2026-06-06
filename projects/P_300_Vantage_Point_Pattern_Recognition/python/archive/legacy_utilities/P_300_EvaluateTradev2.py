"""
FILE: P_300_EvaluateTrade.py
VERSION: 2.3 (Final Documented)
DATE: 2026-05-10
DESCRIPTION: Master Daily Decision Engine. 
Uses CSV candidate files and Global Risk Configs.
"""
import sys
import os
import json
import pandas as pd
from pathlib import Path

# 1. Path Configuration
P300_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
P010_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json")

sys.path.insert(0, str(P300_ROOT / "python"))

try:
    from matching.intelliscan import get_intelliscan_results
    from reporting.aggregator import run_aggregator
    from utilities.db_utils import get_latest_catalog
except ImportError as e:
    print(f"[!] CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

def get_latest_instance_id(symbol):
    import sqlite3
    db = get_latest_catalog()
    if not os.path.exists(db): return None
    conn = sqlite3.connect(db)
    res = conn.execute(f"SELECT rowid FROM pattern_instances WHERE symbol_id = '{symbol}' ORDER BY anchor_date DESC LIMIT 1").fetchone()
    conn.close()
    return res[0] if res else None

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*68)
    print("           P_300 EXECUTIVE TRADE EVALUATION (v2.3)")
    print("="*68)

    # STEP 1: Load Global Posture (P_010)
    try:
        with open(P010_PATH, 'r') as f:
            risk_data = json.load(f)
        avg_posture = risk_data.get('avg_posture', 0)
        risk_mode = risk_data.get('risk_mode', 'UNKNOWN')
        posture_date = risk_data.get('spy_grid_date', 'N/A')
    except:
        avg_posture, risk_mode, posture_date = 0, "ERROR", "N/A"

    # STEP 2: Account Parameters (P_000)
    BASE_POS = 1640.60
    risk_multiplier = 1.0
    if risk_mode == "OFF": risk_multiplier = 0.50
    elif risk_mode == "HALF": risk_multiplier = 0.75
    
    current_pos_limit = BASE_POS * risk_multiplier

    print(f" MARKET POSTURE ({posture_date}): {avg_posture:>8.2f}")
    print(f" RISK MODE: {risk_mode:<15} | POSITION LIMIT: ${current_pos_limit:,.2f}")
    print("-" * 68)

    # STEP 3: Process .csv Candidates in live folder
    live_dir = P300_ROOT / "data" / "live"
    files = list(live_dir.glob("History Grid (*).csv"))
    
    if not files:
        print("\n [!] NO CSV CANDIDATE FILES FOUND IN DATA\\LIVE")
        print("     Ensure converter has processed your .xlsx files first.")
    else:
        print(f"\n PATTERN INTELLIGENCE ({len(files)} Candidates):")
        print(f"{'SYMBOL':<10} | {'Z-SCORE':<10} | {'WIN RATE':<10} | {'STATUS'}")
        print("-" * 68)
        
        for f in files:
            symbol = str(f.name).split("(")[1].split(")")[0]
            
            anchor_id = get_latest_instance_id(symbol)
            if not anchor_id:
                print(f" {symbol:<10} | {'---':<10} | {'---':<10} | NOT IN CATALOG")
                continue

            # Run Silent Math Engines
            stats = run_aggregator(anchor_id)

            if not stats.empty:
                z_score = stats.iloc[0]['Z_Score']
                status = stats.iloc[0]['Status']
                win_rate = stats.iloc[0]['Win_Rate']
                print(f" {symbol:<10} | {z_score:>10} | {win_rate:>10} | {status}")
            else:
                print(f" {symbol:<10} | {'---':<10} | {'---':<10} | NO ANALOGS")

    print("\n" + "="*68)
    print(" EVALUATION COMPLETE")
    print("="*68 + "\n")

if __name__ == "__main__":
    main()