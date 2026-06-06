"""
FILE: inspect_catalog.py
VERSION: 1.1
DATE: 2026-05-06
DESCRIPTION: Inspects catalog row counts using dynamic path discovery.
"""
import sqlite3
import sys
from pathlib import Path

# Add utilities directory to path
sys.path.append(str(Path(__file__).parent))
from db_utils import get_latest_catalog

def inspect_catalog():
    try:
        db_path = get_latest_catalog()
        print(f"Inspecting: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM pattern_instances")
        count = cursor.fetchone()[0]
        print(f"pattern_instances row count: {count}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_catalog()