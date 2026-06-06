import sqlite3
import pandas as pd
import sys
import os
import json
from pathlib import Path

# Project paths
BASE_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
DB_PATH = BASE_DIR / "models" / "050326geminicatalog.db"
INBOX_DIR = BASE_DIR / "data" / "inbox"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Fallback mapping if ingest_manifest.json is missing
DEFAULT_FEATURE_MAP = {
    'Close': 'close',
    'Predicted Neural Index': 'neuralx',
    'Predicted RSI': 'psi', 
    'Predicted Short Term Diff': 'stdiff',
    'Predicted Med Term Diff': 'mtdiff',
    'Predicted Long Term Diff': 'ltdiff'
}

def load_manifest():
    manifest_path = BASE_DIR / "python" / "ingest" / "ingest_manifest.json"
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            return json.load(f)
    return DEFAULT_FEATURE_MAP

def process_file(file_path, feature_map):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Load data
    df = pd.read_csv(file_path)
    
    for _, row in df.iterrows():
        ticker = row['Symbol']
        anchor_date = row['Date']
        
        # 1. Get symbol_id
        cursor.execute("SELECT symbol_id FROM symbols WHERE ticker = ?", (ticker,))
        result = cursor.fetchone()
        if not result:
            print(f"[!] Symbol {ticker} not found in database. Skipping row.")
            continue
        symbol_id = result[0]
        
        # 2. Deduplication check (Fail-Fast)
        cursor.execute("""
            SELECT pattern_instance_id FROM pattern_instances 
            WHERE symbol_id = ? AND anchor_date = ?
        """, (symbol_id, anchor_date))
        
        existing = cursor.fetchone()
        if existing:
            print(f"[!] Duplicate detected: {ticker} on {anchor_date}. Skipping to prevent drift.")
            continue # We skip the row instead of aborting the whole batch, so RYCEY still runs if IVR fails
        
        # 3. Insert record (RESTORED LOGIC)
        cursor.execute("""
            INSERT INTO pattern_instances (symbol_id, anchor_date) 
            VALUES (?, ?)
        """, (symbol_id, anchor_date))
        
        # Grab the ID we just created
        instance_id = cursor.lastrowid
        
        # 4. Extract and Insert Features (RESTORED LOGIC)
        for csv_col, db_feature in feature_map.items():
            if csv_col in row:
                val = row[csv_col]
                if pd.notna(val):  # Ensure it's not a blank cell
                    cursor.execute("""
                        INSERT INTO pattern_features (pattern_instance_id, feature_name, feature_value)
                        VALUES (?, ?, ?)
                    """, (instance_id, db_feature, float(val)))
            
    conn.commit()
    conn.close()
    
    print(f"--- Ingested and Features Extracted: {file_path.name} ---")

def run_batch():
    # Ensure directories exist
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    files = list(INBOX_DIR.glob("*.csv"))
    
    # Fail-Fast if the inbox is empty
    if not files:
        print("No files in inbox. Halting pipeline to prevent ghost reporting.")
        sys.exit(1) 
        
    feature_map = load_manifest()
        
    for file in files:
        process_file(file, feature_map)

if __name__ == "__main__":
    run_batch()