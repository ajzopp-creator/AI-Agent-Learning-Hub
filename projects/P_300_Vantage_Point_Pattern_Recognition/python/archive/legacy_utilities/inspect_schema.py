import sqlite3
from pathlib import Path

DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\catalog.db")

def inspect_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(price_bars)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns in 'price_bars': {columns}")
    conn.close()

if __name__ == "__main__":
    inspect_schema()