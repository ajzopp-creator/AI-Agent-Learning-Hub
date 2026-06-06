"""
FILE: diagnostic_intelliscan.py
VERSION: 1.1
DATE: 2026-05-07
DESCRIPTION: Bypasses filters and dynamically handles DataFrame columns to expose raw distances.
"""
import sys
import os
import sqlite3
import pandas as pd

# Absolute Path Injection
ROOT = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
sys.path.insert(0, os.path.join(ROOT, "python"))

from matching.intelliscan import get_intelliscan_results
from utilities.db_utils import get_latest_catalog

def run_diagnostics():
    db_path = get_latest_catalog()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Get the latest anchor
    cursor.execute("SELECT pattern_instance_id, symbol_id, anchor_date FROM pattern_instances ORDER BY anchor_date DESC LIMIT 1")
    anchor = cursor.fetchone()
    if not anchor:
        return
        
    anchor_id, sym_id, anchor_date = anchor
    
    cursor.execute("SELECT ticker FROM symbols WHERE symbol_id = ?", (sym_id,))
    ticker = cursor.fetchone()[0]
    
    print(f"\n--- P_300 DIAGNOSTIC REPORT v1.1 ---")
    print(f"Target Anchor: {ticker} ({anchor_date}) [ID: {anchor_id}]")
    
    # 2. Force raw IntelliScan pull
    print("Fetching raw IntelliScan matches (Unfiltered)...")
    try:
        df_matches = get_intelliscan_results(anchor_id)
        
        if df_matches.empty:
            print("[CRITICAL ERROR] get_intelliscan_results() returned empty.")
        else:
            print(f"Total historical patterns evaluated: {len(df_matches)}")
            print("\nTop 5 Closest Matches (Regardless of Distance):")
            
            # Sort by distance
            top_5 = df_matches.sort_values('distance', ascending=True).head(5)
            
            # v1.1 Fix: Dynamically select columns that actually exist
            safe_cols = [c for c in ['instance_id', 'distance', 'confidence_score'] if c in top_5.columns]
            print(top_5[safe_cols].to_string(index=False))
            
            min_dist = top_5['distance'].iloc[0]
            if min_dist > 1.0:
                print(f"\n[DIAGNOSIS] Scaling Failure Confirmed. Minimum distance is {min_dist:.2f}.")
                print("ACTION REQUIRED: The features require percentage normalization.")
            else:
                print(f"\n[DIAGNOSIS] Distances are normalized. Minimum distance is {min_dist:.2f}.")
                
    except Exception as e:
        print(f"\n[CRITICAL ERROR] IntelliScan crashed: {str(e)}")

    conn.close()

if __name__ == "__main__":
    run_diagnostics()