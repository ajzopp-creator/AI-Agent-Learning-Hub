"""
FILE: ingest_vp_catalog.py
VERSION: 1.13
DATE: 2026-05-06
DESCRIPTION: Batch ingestion script. Triple-routes data to price_bars, 
             pattern_instances, and pattern_features. Includes dynamic 
             schema validation (insert_safe) and path discovery.
"""
import sqlite3
import pandas as pd
import json
import argparse
import sys
import re
from pathlib import Path

# Add utilities directory to path
sys.path.append(str(Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities")))
from db_utils import get_latest_catalog

# Configuration
MANIFEST_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\ingest\ingest_manifest.json")
DATA_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\historical_patterns")

def insert_safe(df, table_name, conn):
    """Dynamically insert only valid columns to prevent schema mismatch."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    valid_cols = [row[1] for row in cursor.fetchall()]
    cols_to_keep = [c for c in df.columns if c in valid_cols]
    if not cols_to_keep: return
    df_safe = df[cols_to_keep].copy()
    df_safe.to_sql(table_name, conn, if_exists='append', index=False)

def ingest_data(data_type):
    if not MANIFEST_PATH.exists():
        print("[ERROR] Manifest file missing!")
        sys.exit(1)
        
    with open(MANIFEST_PATH, 'r') as f:
        mapping = json.load(f).get('mapping', {})

    db_path = get_latest_catalog()
    print(f"Ingesting into: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for file_path in DATA_DIR.glob('*.csv'):
        # Extract ticker from filename
        ticker = file_path.name.split('_')[0].upper()
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower().str.replace(r'\s+', '', regex=True)
        df.rename(columns=mapping, inplace=True)
        
        # Symbol Handling
        cursor.execute("INSERT OR IGNORE INTO symbols (ticker) VALUES (?)", (ticker,))
        cursor.execute("SELECT symbol_id FROM symbols WHERE ticker=?", (ticker,))
        s_id = cursor.fetchone()[0]
        
        df['symbol_id'] = s_id
        df['data_origin_type'] = data_type
        
        # 1. Route raw price data to price_bars
        insert_safe(df, 'price_bars', conn)
        
        # 2. Route metadata to pattern_instances
        df_pattern = df.copy()
        df_pattern.rename(columns={'bar_date': 'anchor_date', 'open': 'open_0', 'close': 'close_0'}, inplace=True)
        if 'close_0' in df_pattern.columns: df_pattern['close_price'] = df_pattern['close_0']
        insert_safe(df_pattern, 'pattern_instances', conn)

        # 3. Route feature data to pattern_features
        insert_safe(df, 'pattern_features', conn)
        
        print(f"Processed {file_path.name} for {ticker}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P_300 Batch Ingestion")
    parser.add_argument("--type", default="VP_HISTORICAL", help="Data origin type")
    args = parser.parse_args()
    ingest_data(args.type)