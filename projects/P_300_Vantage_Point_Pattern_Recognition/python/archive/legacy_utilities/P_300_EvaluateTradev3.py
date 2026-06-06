"""
FILE: P_300_EvaluateTrade.py
VERSION: 3.2 (Virtual Anchor & Shortcut Pause Integration)
DATE: 2026-05-10
DESCRIPTION: Master Daily Decision Engine. 
Evaluates both Catalog Symbols and New/Agnostic Symbols via Virtual Anchors.
"""
import sys
import os
import json
import pandas as pd
from pathlib import Path
import sqlite3

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
    """Checks if symbol exists in the database and returns the latest rowid."""
    db = get_latest_catalog()
    if not os.path.exists(db): 
        return None
    
    conn = sqlite3.connect(db)
    query = f"SELECT rowid FROM pattern_instances WHERE symbol_id = '{symbol}' ORDER BY anchor_date DESC LIMIT 1"
    res = conn.execute(query).fetchone()
    conn.close()
    
    return res[0] if res else None


def extract_virtual_anchor(csv_path):
    """
    Scrapes the most recent feature vector from a VP History Grid CSV.
    Allows matching for symbols NOT in the local catalog.
    """
    try:
        df = pd.read_csv(csv_path)
        if df.empty: 
            return None
        # Capture the last row as the 'Live Vector'
        return df.iloc[-1].to_dict()
    except Exception as e:
        print(f" [!] Error extracting vector from {csv_path.name}: {e}")
        return None


def main():
    # STEP 1: Load Global Risk Posture
    if not P010_PATH.exists():
        print(f"[!] ERROR: Risk Config not found at {P010_PATH}")
        sys.exit(1)

    with open(P010_PATH, 'r') as f:
        risk_data = json.load(f)

    risk_mode = risk_data.get("risk_mode", "UNKNOWN")
    avg_posture = risk_data.get("avg_posture", 0.0)
    
    # Determine sizing based on Risk Mode
    base_max_pos = 1640.60
    if risk_mode == "OFF / CORRECTION":
        current_pos_limit = base_max_pos * 0.50
    elif risk_mode == "HALF":
        current_pos_limit = base_max_pos * 0.75
    else:
        current_pos_limit = base_max_pos

    # STEP 2: Print System Header
    print("\n" + "=" * 68)
    print(" P_300 VANTAGE POINT PATTERN EVALUATOR v3.2")
    print("=" * 68)
    print(f" GLOBAL POSTURE: {avg_posture:>8.2f}")
    print(f" RISK MODE: {risk_mode:<15} | POSITION LIMIT: ${current_pos_limit:,.2f}")
    print("-" * 68)

    # STEP 3: Process .csv Candidates in live folder
    live_dir = P300_ROOT / "data" / "live"
    files = list(live_dir.glob("History Grid (*).csv"))
    
    if not files:
        print("\n [!] NO CSV CANDIDATE FILES FOUND IN DATA\\LIVE")
        print("     Ensure converter has processed your .xlsx files first.")
        return

    print(f"\n PATTERN INTELLIGENCE ({len(files)} Candidates):")
    print(f"{'SYMBOL':<10} | {'Z-SCORE':<10} | {'WIN RATE':<10} | {'STATUS'}")
    print("-" * 68)
    
    db_path = get_latest_catalog()

    for f in files:
        symbol = str(f.name).split("(")[1].split(")")[0]
        anchor_id = get_latest_instance_id(symbol)
        
        if anchor_id:
            # Flow A: Standard Catalog Symbol (e.g., SPY, QQQ)
            stats = run_aggregator(anchor_id)
            if not stats.empty:
                z_score = stats.iloc[0].get('Z_Score', 0.0)
                status = stats.iloc[0].get('Status', 'UNKNOWN')
                win_rate = stats.iloc[0].get('Win_Rate', 0.0)
                print(f" {symbol:<10} | {z_score:<10.2f} | {win_rate:<10.1%} | {status}")
        else:
            # Flow B: Agnostic Matching for New Symbols (Virtual Anchor)
            live_vector = extract_virtual_anchor(f)
            
            if not live_vector:
                print(f" {symbol:<10} | {'---':<10} | {'---':<10} | DATA ERROR: Could not extract vector")
                continue
            
            # Fetch Top 5 Analogs globally
            top_matches = get_intelliscan_results(live_vector, db_path, top_n=5)
            
            if not top_matches.empty:
                # Format string: "AAPL (2024), GLD (2023), etc."
                analogs = [f"{row['symbol_id']} ({str(row['anchor_date'])[:4]})" for _, row in top_matches.iterrows()]
                analog_str = ", ".join(analogs)
                
                print(f" {symbol:<10} | {'---':<10} | {'---':<10} | NEW SYMBOL DETECTED (VIRTUAL ANCHOR)")
                print(f" {'':<10} -> Top 5 Market Analogs: [{analog_str}]")
            else:
                print(f" {symbol:<10} | {'---':<10} | {'---':<10} | ENGINE ERROR: No analogs found")

if __name__ == "__main__":
    main()
    input("\nPress ENTER to close this window...")