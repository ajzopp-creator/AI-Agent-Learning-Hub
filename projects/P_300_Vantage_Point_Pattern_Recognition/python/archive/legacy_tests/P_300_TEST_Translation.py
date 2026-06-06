"""
FILE: P_300_TEST_Translation.py
VERSION: 1.4
DATE: 2026-05-11
DESCRIPTION: 
    Isolated test for Symbol ID to Ticker translation logic. 
    Located in python/tests/ per SKILL.txt architecture.
"""
import sys
import os
import sqlite3
from pathlib import Path

# 1. Align with P_300 Project Root
# Root is two levels up from python/tests/
P300_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
sys.path.insert(0, str(P300_ROOT / "python"))

try:
    # Use the canonical utility to find the database
    from utilities.db_utils import get_latest_catalog
except ImportError as e:
    print(f"[!] CRITICAL IMPORT ERROR: {e}")
    print(f"Check if {P300_ROOT / 'python'} contains the utilities folder.")
    sys.exit(1)

def test_lookup():
    print(f"--- STARTING TRANSLATION TEST (v1.4) ---")
    
    # Get path via infrastructure utility
    db_path = get_latest_catalog()
    print(f"Targeting DB via db_utils: {db_path}")

    if not db_path or not os.path.exists(db_path):
        print(f"[!] FAILED: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    try:
        # 1. Check table existence
        res = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='symbols'").fetchone()
        if not res:
            print("[!] FAILED: 'symbols' table does not exist in this DB.")
            return
        
        # 2. Test Translation Logic
        cursor = conn.execute("SELECT symbol_id, ticker FROM symbols LIMIT 5")
        rows = cursor.fetchall()
        
        print(f"[SUCCESS] Found {len(rows)} symbol mappings.")
        print("-" * 40)
        for row in rows:
            print(f"ID: {row[0]:<5} -> TICKER: {row[1]}")
        print("-" * 40)
        
    except Exception as e:
        print(f"[!] ERROR DURING TEST: {e}")
    finally:
        conn.close()
        print(f"--- TEST COMPLETE ---")

if __name__ == "__main__":
    test_lookup()