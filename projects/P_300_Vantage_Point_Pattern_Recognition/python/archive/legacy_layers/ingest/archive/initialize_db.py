import sqlite3
from pathlib import Path

# V1.0 - Schema Initializer
# Explicitly defines the schema to prevent 'no such column' errors.

DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\catalog.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing table
    cursor.execute("DROP TABLE IF EXISTS price_bars")
    
    # Create master table
    cursor.execute("""
    CREATE TABLE price_bars (
        bar_id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol_id INTEGER,
        bar_date TEXT,
        open REAL, high REAL, low REAL, close REAL, volume REAL,
        stdiff REAL, mtdiff REAL, ltdiff REAL,
        neuralx REAL, neuralx_max REAL,
        pred_high REAL, pred_low REAL, pred_range REAL,
        williams_emai REAL, psi REAL, roc REAL,
        triple_cross_short REAL, triple_cross_medium REAL, triple_cross_long REAL
    )
    """)
    
    # Ensure symbols table exists
    cursor.execute("CREATE TABLE IF NOT EXISTS symbols (symbol_id INTEGER PRIMARY KEY, ticker TEXT UNIQUE)")
    
    conn.commit()
    conn.close()
    print("Schema initialized successfully.")

if __name__ == "__main__":
    init_db()