import sqlite3
import os
from pathlib import Path

# P_300 Migration: Add data_origin_type to pattern_instances
DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\catalog.db")

def migrate_catalog():
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(pattern_instances)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'data_origin_type' in columns:
            print("Migration already applied: data_origin_type column exists.")
        else:
            print("Applying Migration: Adding data_origin_type column...")
            cursor.execute("ALTER TABLE pattern_instances ADD COLUMN data_origin_type TEXT")
            cursor.execute("UPDATE pattern_instances SET data_origin_type = 'PATTERN_IDENT'")
            conn.commit()
            print("Migration successful: Added column and backfilled historical data.")
            
    except sqlite3.Error as e:
        print(f"Migration Failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_catalog()