import sqlite3
from pathlib import Path

db = Path("models/060326catalog.db")
with sqlite3.connect(db) as conn:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables:", tables)
    
    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        print(f"\n{table}: {cols}")
