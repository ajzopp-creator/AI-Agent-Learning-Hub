"""
FILE: db_cleanup.py
VERSION: 1.0
DATE: 2026-05-10
DESCRIPTION: Surgical removal of corrupted links (Ghosts and Orphans).
"""
import sqlite3
import os
import sys

PROJECT_ROOT = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
try:
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "python"))
    from utilities.db_utils import get_latest_catalog
    db_path = get_latest_catalog()
except ImportError:
    db_path = os.path.join(PROJECT_ROOT, "051026geminicatalog.db")

def run_cleanup():
    print(f"Connecting to {os.path.basename(db_path)} for cleanup...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Delete Orphaned Labels
    cursor.execute("""
        DELETE FROM forward_labels 
        WHERE pattern_instance_id NOT IN (SELECT rowid FROM pattern_instances)
    """)
    orphans_deleted = cursor.rowcount

    # 2. Delete Ghost Instances (Instances with no features)
    cursor.execute("""
        DELETE FROM pattern_instances 
        WHERE rowid NOT IN (SELECT DISTINCT pattern_instance_id FROM pattern_features)
    """)
    ghosts_deleted = cursor.rowcount

    # Commit changes
    conn.commit()
    conn.close()

    print("\n" + "="*45)
    print(" P_300 CATALOG CLEANUP COMPLETE")
    print("="*45)
    print(f" Orphaned Labels Removed: {orphans_deleted}")
    print(f" Ghost Instances Removed: {ghosts_deleted}")
    print("="*45 + "\n")

if __name__ == "__main__":
    run_cleanup()