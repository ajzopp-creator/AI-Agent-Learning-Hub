"""
FILE: dry_run_ingest.py
VERSION: 1.13 (Dry-Run Mode)
DATE: 2026-05-06
DESCRIPTION: Simulates triple-routing logic to verify ingestion alignment 
             without writing to the production database.
"""
import pandas as pd
import json
import sys
import re
from pathlib import Path

# Config
MANIFEST_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\ingest\ingest_manifest.json")
DATA_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\historical_patterns")

def dry_run():
    if not MANIFEST_PATH.exists():
        print("[ERROR] Manifest file missing!")
        sys.exit(1)
        
    with open(MANIFEST_PATH, 'r') as f:
        mapping = json.load(f).get('mapping', {})

    print(f"--- SIMULATING BATCH INGESTION ---")
    
    for file_path in DATA_DIR.glob('*.csv'):
        ticker = file_path.name.split('_')[0].upper()
        df = pd.read_csv(file_path)
        
        # Simulate Pre-wash & Mapping
        df.columns = df.columns.str.lower().str.replace(r'\s+', '', regex=True)
        df.rename(columns=mapping, inplace=True)
        
        # Simulate Routing
        print(f"\n[Processing Ticker: {ticker}]")
        print(f"  -> Would route {len(df)} rows to 'price_bars'")
        
        df_pattern = df.copy()
        df_pattern.rename(columns={'bar_date': 'anchor_date', 'open': 'open_0', 'close': 'close_0'}, inplace=True)
        print(f"  -> Would route {len(df_pattern)} rows to 'pattern_instances'")
        print(f"  -> Would route {len(df)} rows to 'pattern_features'")
        
        # Verify Manifest Mapping
        missing = [c for c in ['bar_date', 'open', 'close'] if c not in df.columns]
        if missing:
            print(f"  [!] WARNING: Potential mapping mismatch. Missing columns post-rename: {missing}")
        else:
            print(f"  [✓] Mapping confirmed for {ticker}")

    print("\n--- SIMULATION COMPLETE. No data written to DB. ---")

if __name__ == "__main__":
    dry_run()