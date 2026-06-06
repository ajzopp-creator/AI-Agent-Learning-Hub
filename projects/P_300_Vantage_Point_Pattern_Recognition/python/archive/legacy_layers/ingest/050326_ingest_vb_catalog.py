import sqlite3
import pandas as pd
import json
import argparse
import sys
from pathlib import Path

# --- Configuration ---
MANIFEST_PATH = Path(__file__).parent / "ingest_manifest.json"
DATA_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\historical")

def insert_safe(df, table_name, conn):
    """
    Dynamically checks the target SQLite table and ONLY inserts columns 
    that actually exist in the table, preventing OperationalErrors.
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    valid_cols = [row[1] for row in cursor.fetchall()]
    
    cols_to_keep = [c for c in df.columns if c in valid_cols]
    
    if not cols_to_keep:
        return # Table exists but no columns match our data; skip safely.
        
    df_safe = df[cols_to_keep].copy()
    df_safe.to_sql(table_name, conn, if_exists='append', index=False)

def ingest_data(data_type, db_path):
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"CRITICAL ERROR: Database not found at {db_path}")
        sys.exit(1)

    with open(MANIFEST_PATH, 'r') as f:
        mapping = json.load(f)['mapping']
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Schema Parity Check
    cursor.execute("PRAGMA table_info(pattern_instances)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'data_origin_type' not in columns:
        cursor.execute("ALTER TABLE pattern_instances ADD COLUMN data_origin_type TEXT")
    
    for file_path in DATA_DIR.glob("Pattern_*.csv"):
        ticker = file_path.stem.split('_')[-1].replace('.csv', '')
        print(f"Ingesting: {file_path.name} | Type: {data_type} | Symbol: {ticker}")
        
        df = pd.read_csv(file_path)
        df.columns = [c.lower().strip().replace(' ', '').replace('\n', '') for c in df.columns]
        df.rename(columns=mapping, inplace=True)
        
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS symbols (symbol_id INTEGER PRIMARY KEY, ticker TEXT UNIQUE)")
            cursor.execute("INSERT OR IGNORE INTO symbols (ticker) VALUES (?)", (ticker,))
            cursor.execute("SELECT symbol_id FROM symbols WHERE ticker=?", (ticker,))
            s_id = cursor.fetchone()[0]
        except Exception:
            s_id = 1
            
        df['symbol_id'] = s_id
        df['data_origin_type'] = data_type
        
        # --- DYNAMIC ROUTING ---
        
        # 1. Route raw price data to price_bars
        insert_safe(df, 'price_bars', conn)
        
        # 2. Route pattern metadata to pattern_instances
        df_pattern = df.copy()
        # Map fields to match the instance schema explicitly
        df_pattern.rename(columns={
            'bar_date': 'anchor_date',
            'open': 'open_0',
            'close': 'close_0'
        }, inplace=True)
        
        # Ensure parity with previous seed data scripts
        if 'close_0' in df_pattern.columns:
            df_pattern['close_price'] = df_pattern['close_0']
            
        insert_safe(df_pattern, 'pattern_instances', conn)

        # 3. Route feature data to pattern_features (if applicable)
        insert_safe(df, 'pattern_features', conn)
        
    conn.commit()
    conn.close()
    print(f"--- Ingestion successful for {data_type} ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P_300 Unified Ingest Engine")
    parser.add_argument("--type", choices=['PATTERN_IDENT', 'EVAL_SET'], required=True)
    parser.add_argument("--db-path", required=True)
    
    args = parser.parse_args()
    ingest_data(args.type, args.db_path)