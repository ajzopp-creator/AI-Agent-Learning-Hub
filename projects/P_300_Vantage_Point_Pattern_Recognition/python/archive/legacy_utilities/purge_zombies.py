"""
FILE: purge_zombies.py
VERSION: 1.0
DESCRIPTION: Removes corrupted records (NaN anchor dates) from pattern_instances.
"""
import sys
import sqlite3

# Absolute path injection
PROJECT_PYTHON_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python"
sys.path.insert(0, PROJECT_PYTHON_DIR)

from utilities.db_utils import get_latest_catalog

def purge():
    db_path = get_latest_catalog()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # IDs confirmed as having NaN anchor dates
    zombie_ids = range(395, 411)
    
    print(f"Purging {len(list(zombie_ids))} records...")
    cursor.execute(f"DELETE FROM pattern_instances WHERE pattern_instance_id IN ({','.join(map(str, zombie_ids))})")
    conn.commit()
    print(f"Purge complete. Records removed: {cursor.rowcount}")
    conn.close()

if __name__ == "__main__":
    purge()