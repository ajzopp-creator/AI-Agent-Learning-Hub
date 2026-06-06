import sqlite3
import pandas as pd
import re
from pathlib import Path
from datetime import datetime

# Path Configuration
MODELS_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models")

def get_latest_db():
    """Dynamically finds the most recent .db file."""
    db_files = list(MODELS_DIR.glob('*.db'))
    if not db_files:
        return None
    # Sort by modification time to get the absolute latest
    return max(db_files, key=lambda p: p.stat().st_mtime)

def verify():
    db_path = get_latest_db()
    if not db_path:
        print("[ERROR] No database files found in models folder.")
        return

    print(f"[VERIFICATION] Targeting Dynamic Path: {db_path.name}")
    
    try:
        conn = sqlite3.connect(db_path)
        print("--- P_300 DATABASE VERIFICATION ---")
        
        tables = ['symbols', 'price_bars', 'pattern_instances']
        
        for table in tables:
            try:
                count = conn.execute(f'SELECT count(*) FROM {table}').fetchone()[0]
                print(f"Total rows in {table}: {count}")
            except sqlite3.OperationalError:
                print(f"Table '{table}' does not exist.")
                
        print("\n--- SAMPLE: RECENT PATTERN INSTANCES ---")
        # Querying the latest 5 instances
        sample_df = pd.read_sql_query(
            "SELECT pattern_instance_id, symbol_id, anchor_date, close_price, data_origin_type FROM pattern_instances ORDER BY pattern_instance_id DESC LIMIT 5", 
            conn
        )
        print(sample_df.to_string(index=False))

        conn.close()
        print("\n--- VERIFICATION COMPLETE ---")
    except Exception as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    verify()