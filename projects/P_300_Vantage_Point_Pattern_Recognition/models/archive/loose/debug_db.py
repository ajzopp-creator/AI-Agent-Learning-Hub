import sqlite3
import os

def debug_database():
    # Force the path to be the current directory
    db_name = 'catalog.db'
    abs_path = os.path.abspath(db_name)
    
    print(f"--- DEBUGGING CONNECTION ---")
    print(f"Attempting to connect to: {abs_path}")
    
    if not os.path.exists(abs_path):
        print("CRITICAL: No file found at that path.")
        return

    conn = sqlite3.connect(abs_path)
    try:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print(f"Tables found: {tables}")
    except Exception as e:
        print(f"Error reading DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_database()