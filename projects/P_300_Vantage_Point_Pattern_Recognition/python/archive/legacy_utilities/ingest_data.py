import sqlite3
import pandas as pd
from pathlib import Path

# Path resolution
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
# This is your verified path
DATA_DIR = HUB_ROOT / "projects" / "P_300_Vantage_Point_Pattern_Recognition" / "data" / "historical"
DB_PATH = HUB_ROOT / "projects" / "catalog.db"

def ingest_files():
    if not DATA_DIR.exists():
        print(f"Error: Directory not found at {DATA_DIR}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Iterate through all CSVs in your historical folder
    for file_path in DATA_DIR.glob("*.csv"):
        print(f"Ingesting: {file_path.name}")
        
        # Determine ticker from filename (e.g., if file contains "NVDA")
        # Logic: Simple heuristic based on filename presence
        ticker = "UNKNOWN"
        if "NVDA" in file_path.name.upper(): ticker = "NVDA"
        elif "SPY" in file_path.name.upper(): ticker = "SPY"
        elif "BIREF" in file_path.name.upper(): ticker = "BIREF"
        elif "ENTG" in file_path.name.upper(): ticker = "ENTG"
        
        df = pd.read_csv(file_path)
        
        # Ensure Ticker exists in symbols table
        cursor.execute("INSERT OR IGNORE INTO symbols (ticker) VALUES (?)", (ticker,))
        cursor.execute("SELECT symbol_id FROM symbols WHERE ticker=?", (ticker,))
        symbol_id = cursor.fetchone()[0]
        
        # Cleanup
        df_clean = df.iloc[1:].copy()
        df_clean = df_clean.rename(columns={
            'Date': 'bar_date',
            'Open\nPrice': 'open',
            'High\nPrice': 'high',
            'Low\nPrice': 'low',
            'Close\nPrice': 'close',
            'Volume': 'volume'
        })
        
        # Convert columns
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Load
        df_clean['symbol_id'] = symbol_id
        final_df = df_clean[['symbol_id', 'bar_date', 'open', 'high', 'low', 'close', 'volume']].dropna()
        final_df.to_sql('price_bars', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_files()