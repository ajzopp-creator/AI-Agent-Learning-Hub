"""
FILE: P_300_EvaluateTrade.py
VERSION: 1.4.7 (Full Schema Alignment)
LOCATION: /python/utilities/
DESCRIPTION: Follows Single-Symbol Export Schema. Ticker from Filename. 
             Posture from Column Index 1.
"""
import sys
import os
import pandas as pd
import re
from pathlib import Path

# GROUND TRUTH PATHS
ROOT = "C:/Users/Trader/AI-Agent-Learning-Hub/projects/P_300_Vantage_Point_Pattern_Recognition"
CONVERTER_FOLDER = f"{ROOT}/python"
LIVE_DIR = Path(f"{ROOT}/data/live")

if CONVERTER_FOLDER not in sys.path:
    sys.path.insert(0, CONVERTER_FOLDER)

try:
    import P_300_vantagepoint_batch_convert_v4 as converter
except ImportError:
    print(f"[!] CRITICAL ERROR: Could not find converter at {CONVERTER_FOLDER}")
    sys.exit(1)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("====================================================")
    print("          P_300 DAILY EVALUATION REPORT")
    print("====================================================\n")
    
    # 1. RUN CONVERSION (v4.0 Hub)
    converter.process_all_files()
    
    # 2. SCAN FOR EVALUATION CSVs
    eval_files = list(LIVE_DIR.glob("History Grid*.csv"))
    
    if not eval_files:
        print(f"[!] NO DATA: Ensure History Grid files are in OneDrive.")
        return

    # Track results based on Schema (Ticker: Posture)
    posture_map = {}

    for eval_file in eval_files:
        try:
            # SCHEMA RULE: Identity is in the Filename Parentheses
            match = re.search(r'\((.*?)\)', eval_file.name)
            ticker = match.group(1) if match else None
            
            if not ticker: continue

            # SCHEMA RULE: Single-symbol file. Grab Row 0, Column 1 (Posture)
            # Use header=None if your CSVs have no header row, or keep default
            df = pd.read_csv(eval_file)
            
            # Grabbing posture from the first data row, second column
            p_val = float(df.iloc[0, 1]) 
            
            posture_map[ticker] = p_val
            print(f"IDENTIFIED: {ticker:<6} | POSTURE: {p_val:>8.2f}")

        except Exception as e:
            print(f"[!] Schema Error in {eval_file.name}: {e}")

    # 3. FINAL AGGREGATION (Per P_010 Strategy)
    print("-" * 52)
    if 'SPY' in posture_map and 'QQQ' in posture_map:
        avg_p = (posture_map['SPY'] + posture_map['QQQ']) / 2
        print(f"FINAL AVG POSTURE (SPY/QQQ): {avg_p:>8.2f}")
        
        # Position Sizing Logic (P_000)
        balance = 32812.00
        max_pos = balance * 0.05
        print(f"ACTIONABLE SPEND:           ${max_pos:,.2f}")
    else:
        print("[!] INCOMPLETE DATA: SPY and QQQ required for Avg Posture.")
        print(f"Found: {list(posture_map.keys())}")

    print("\n--- WORKFLOW COMPLETE ---")

if __name__ == "__main__":
    main()