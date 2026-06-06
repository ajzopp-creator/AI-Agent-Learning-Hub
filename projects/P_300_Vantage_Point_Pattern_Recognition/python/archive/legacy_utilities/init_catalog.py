import sqlite3
from pathlib import Path

# Path resolution
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
DB_PATH = HUB_ROOT / "projects" / "catalog.db"

def initialize_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Define Schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS symbols (
            symbol_id INTEGER PRIMARY KEY, 
            ticker TEXT UNIQUE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_bars (
            bar_id INTEGER PRIMARY KEY, 
            symbol_id INTEGER, 
            bar_date TEXT, 
            open REAL, 
            high REAL, 
            low REAL, 
            close REAL, 
            volume INTEGER,
            FOREIGN KEY(symbol_id) REFERENCES symbols(symbol_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Schema initialized at {DB_PATH}")

if __name__ == "__main__":
    initialize_schema()