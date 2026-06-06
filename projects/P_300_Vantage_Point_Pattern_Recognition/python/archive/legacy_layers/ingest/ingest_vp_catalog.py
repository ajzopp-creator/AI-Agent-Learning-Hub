"""
FILE: ingest_vp_catalog.py
VERSION: 6.0 (STABLE - AUTO-REGISTRATION)
CHANGELOG: 
  - Locked to VAULT_DIR only (Path B).
  - Added 'INSERT OR IGNORE' into 'symbols' table to fix Math Engine blindness.
  - Retained 'DELETE' logic to prevent duplicate pattern instances.
"""
import sqlite3
import pandas as pd
import json
import re
import sys
from pathlib import Path

# --- ARCHITECTURE LOCKS ---
MANIFEST_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\schema\ingest_manifest.json")
DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\051126geminicatalog.db")
VAULT_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\historical_patterns")

def parse_symbol(filename):
    """Source: Standard VantagePoint naming convention (SYMBOL)"""
    match = re.search(r"\((.*?)\)", filename)
    return match.group(1).upper() if match else None

def main():
    if not MANIFEST_PATH.exists(): 
        print(f"FATAL: Manifest missing at {MANIFEST_PATH}"); sys.exit(1)

    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)['mapping']
    
    csv_to_db = {v: k for k, v in manifest.items()}
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"--- [INGEST v6.0] SYNCING VAULT TO CATALOG ---")
    
    processed_count = 0
    for csv_file in VAULT_DIR.glob("*.csv"):
        symbol = parse_symbol(csv_file.name)
        if not symbol: continue
        
        try:
            # 1. AUTO-REGISTRATION: Admitting the symbol to the system list
            cursor.execute("INSERT OR IGNORE INTO symbols (symbol_id, status) VALUES (?, 'active')", (symbol,))
            
            # 2. ATOMIC CLEAN: Removing existing data for this symbol
            cursor.execute("DELETE FROM pattern_instances WHERE symbol_id = ?", (symbol,))
            
            # 3. DATA LOAD
            df = pd.read_csv(csv_file)
            df = df.rename(columns=csv_to_db)
            final_cols = [c for c in df.columns if c in manifest.keys()]
            df_final = df[final_cols].copy()
            df_final['symbol_id'] = symbol
            
            df_final.to_sql("pattern_instances", conn, if_exists="append", index=False)
            processed_count += 1
            print(f"[v6.0 SUCCESS] {symbol} Synced & Registered.")
        except Exception as e:
            print(f"[ERROR] {symbol}: {e}")

    conn.commit()
    conn.close()
    print(f"--- FINISHED: {processed_count} symbols processed. ---")

if __name__ == "__main__":
    main()