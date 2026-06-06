import sqlite3
import pandas as pd
import json
import argparse
import sys
import re
from pathlib import Path

# --- Configuration ---
MANIFEST_PATH = Path(__file__).parent / "ingest_manifest.json"
DATA_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\live")

def extract_ticker(filename):
    # Try to find text inside parentheses: (AAPL) -> AAPL
    match = re.search(r'\((.*?)\)', filename)
    if match: return match.group(1).upper()
    # Fallback to underscore split if parentheses not found
    parts = filename.split('_')
    return parts[0].upper()

def insert_safe(df, table_name, conn):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    valid_cols = [row[1] for row in cursor.fetchall()]
    cols_to_keep = [c for c in df.columns if c in valid_cols]
    if not cols_to_keep: return
    df_safe = df[cols_to_keep].copy()
    df_safe.to_sql(table_name, conn, if_exists='append', index=False)

def ingest_data(data_type, db_path):
    db_file = Path(db_path)
    if not db_file.exists(): sys.exit(1)

    with open(MANIFEST_PATH, 'r') as f:
        mapping = json.load(f)['mapping']
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    for file_path in DATA_DIR.glob("*.csv"):
        ticker = extract_ticker(file_path.name)
        print(f"Ingesting: {file_path.name} | Detected Symbol: {ticker}")
        
        df = pd.read_csv(file_path)
        df.columns = [c.lower().strip().replace(' ', '').replace('\n', '') for c in df.columns]
        df.rename(columns=mapping, inplace=True)
        
        # Get or Create Symbol ID
        cursor.execute("INSERT OR IGNORE INTO symbols (ticker) VALUES (?)", (ticker,))
        cursor.execute("SELECT symbol_id FROM symbols WHERE ticker=?", (ticker,))
        s_id = cursor.fetchone()[0]
            
        df['symbol_id'] = s_id
        df['data_origin_type'] = data_type
        
        # 1. Route raw price data to price_bars (ALL ROWS)
        insert_safe(df, 'price_bars', conn)
        
        # 2. Route ONLY the most recent day to pattern_instances (THE ANCHOR)
        df_pattern = df.copy()
        df_pattern.rename(columns={'bar_date': 'anchor_date', 'open': 'open_0', 'close': 'close_0'}, inplace=True)
        if 'close_0' in df_pattern.columns: df_pattern['close_price'] = df_pattern['close_0']
        
        # Sort chronologically and isolate the latest date
        df_pattern['temp_dt'] = pd.to_datetime(df_pattern['anchor_date'], format='mixed')
        latest_row = df_pattern.sort_values('temp_dt', ascending=True).tail(1).copy()
        latest_row.drop(columns=['temp_dt'], inplace=True)
            
        insert_safe(latest_row, 'pattern_instances', conn)
        
    conn.commit()
    conn.close()
    print("--- Ingestion successful ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=['PATTERN_IDENT', 'EVAL_SET'], required=True)
    parser.add_argument("--db-path", required=True)
    args = parser.parse_args()
    ingest_data(args.type, args.db_path)