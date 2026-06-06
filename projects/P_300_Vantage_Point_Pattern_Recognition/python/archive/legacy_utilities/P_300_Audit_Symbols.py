"""
FILE: P_300_Audit_Symbols.py
VERSION: 1.2 (FULL VAULT AUDIT)
DESCRIPTION: Lists EVERY symbol and EVERY pattern in the DB. 
             Provides the baseline before the new 13 files are added.
"""
import sqlite3
import sys
from pathlib import Path

# Setup Pathing to find db_utils
sys.path.append(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities")
import db_utils

def run_audit():
    db_path = db_utils.get_latest_catalog()
    print(f"\n--- [FULL DATABASE AUDIT] ---")
    print(f"Targeting Database: {Path(db_path).name}")
    
    conn = sqlite3.connect(db_path)
    
    # 1. Get the list of all symbols and count their patterns
    # Using a LEFT JOIN so we see symbols even if they have 0 patterns
    query = """
    SELECT s.ticker, COUNT(pi.pattern_instance_id) 
    FROM symbols s
    LEFT JOIN pattern_instances pi ON s.symbol_id = pi.symbol_id
    GROUP BY s.ticker
    ORDER BY s.ticker ASC;
    """
    
    results = conn.execute(query).fetchall()
    total_patterns = 0
    
    print(f"\n{'TICKER':<10} | {'PATTERNS'}")
    print("-" * 25)
    
    for ticker, count in results:
        print(f"{ticker:<10} | {count}")
        total_patterns += count
        
    print("-" * 25)
    print(f"TOTAL PATTERNS IN VAULT: {total_patterns}")
    print(f"--- END OF AUDIT ---\n")
    
    conn.close()

if __name__ == "__main__":
    run_audit()