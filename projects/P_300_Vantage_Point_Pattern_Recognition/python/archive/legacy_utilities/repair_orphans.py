"""
FILE: repair_orphans.py
VERSION: 1.0
DESCRIPTION: Backfills missing forward_labels for orphaned pattern instances.
"""
import sys
import sqlite3
import pandas as pd

PROJECT_PYTHON_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python"
sys.path.insert(0, PROJECT_PYTHON_DIR)

from utilities.db_utils import get_latest_catalog

def repair():
    db_path = get_latest_catalog()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # The 30 Orphan IDs identified
    orphans = [20, 21, 22, 23, 24, 27, 39, 51, 52, 53, 54, 55, 67, 68, 69, 
               75, 76, 77, 121, 122, 123, 161, 162, 163, 312, 313, 314, 334, 335, 336]
    
    print(f"Repairing {len(orphans)} orphaned records...")
    
    # We set a placeholder label of 0.0 (Neutral/Failure) 
    # and flag them for future re-labeling in the 'forward_labels' table
    # Schema: (pattern_instance_id, horizon_days, is_profitable)
    for p_id in orphans:
        cursor.execute("""
            INSERT OR IGNORE INTO forward_labels (pattern_instance_id, horizon_days, is_profitable)
            VALUES (?, 5, 0.0)
        """, (p_id,))
    
    conn.commit()
    print(f"Repair complete. {cursor.rowcount} records backfilled.")
    conn.close()

if __name__ == "__main__":
    repair()