"""
FILE: audit_missing_labels.py
VERSION: 1.1
DATE: 2026-05-06
DESCRIPTION: Identifies orphaned pattern instances missing their forward_labels entry.
"""
import sys
import sqlite3
import pandas as pd

# Force absolute path injection so 'utilities' is found regardless of cwd
PROJECT_PYTHON_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python"
sys.path.insert(0, PROJECT_PYTHON_DIR)

from utilities.db_utils import get_latest_catalog

def run_audit():
    db_path = get_latest_catalog()
    conn = sqlite3.connect(db_path)
    
    # Query to find orphans (in instances but not in labels)
    query = """
        SELECT p.pattern_instance_id, s.ticker, p.anchor_date
        FROM pattern_instances p
        JOIN symbols s ON p.symbol_id = s.symbol_id
        LEFT JOIN forward_labels f ON p.pattern_instance_id = f.pattern_instance_id
        WHERE f.is_profitable IS NULL
    """
    
    df_orphans = pd.read_sql(query, conn)
    conn.close()
    
    if not df_orphans.empty:
        print(f"[!] FOUND {len(df_orphans)} ORPHANED RECORDS:")
        print(df_orphans)
    else:
        print("[+] NO ORPHANED RECORDS FOUND.")

if __name__ == "__main__":
    run_audit()