import sqlite3
import pandas as pd
import glob
import os
from pathlib import Path

# Path resolution: Utilizing your HUB_ROOT logic
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
DB_PATH = HUB_ROOT / "projects" / "catalog.db"

def ingest_historical_data(source_dir='data/raw/'):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Path to raw data
    raw_path = HUB_ROOT / "projects" / "P_300_Vantage_Point_Pattern_Recognition" / source_dir
    files = glob.glob(os.path.join(raw_path, 'HistoryGrid*SPY*.csv'))
    
    if not files:
        print(f"No files found in {raw_path}")
        return

    for file in files:
        print(f"Ingesting {file}...")
        df = pd.read_csv(file)
        df.columns = [c.lower().replace(' ', '_') for c in df.columns]
        
        # Tag with symbol_id (Ensure 'SPY' exists in symbols)
        cursor.execute("INSERT OR IGNORE INTO symbols (ticker) VALUES (?)", ('SPY',))
        cursor.execute("SELECT symbol_id FROM symbols WHERE ticker='SPY'")
        s_id = cursor.fetchone()[0]
        
        df['symbol_id'] = s_id
        
        # Insert into price_bars
        df.to_sql('price_bars', conn, if_exists='append', index=False)
        conn.commit()
        print(f"Ingested {len(df)} bars.")
        
    conn.close()

if __name__ == "__main__":
    ingest_historical_data()