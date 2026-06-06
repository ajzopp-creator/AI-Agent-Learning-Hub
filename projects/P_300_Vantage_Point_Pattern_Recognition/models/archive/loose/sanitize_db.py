import sqlite3
import sys

# Protocol: Find latest DB
UTILS_PATH = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities"
sys.path.append(UTILS_PATH)
import db_utils

def sanitize_vault():
    db_path = db_utils.get_latest_catalog()
    print(f"--- [CLEANUP] Targeting: {db_path} ---")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Clear Orphaned Labels (The 43 rows with no parent)
        cursor.execute("""
            DELETE FROM forward_labels 
            WHERE pattern_instance_id NOT IN (SELECT pattern_instance_id FROM pattern_instances)
        """)
        orphans_cleared = cursor.rowcount
        
        # 2. Clear Ghost Instances (The 6 new rows with no features)
        # We delete them so we can re-ingest them CLEANLY with features.
        cursor.execute("""
            DELETE FROM pattern_instances 
            WHERE pattern_instance_id NOT IN (SELECT pattern_instance_id FROM pattern_features)
        """)
        ghosts_cleared = cursor.rowcount
        
        conn.commit()
        print(f"[SUCCESS] Cleared {orphans_cleared} Orphans and {ghosts_cleared} Ghosts.")
        print("[STATUS] Database is now CLEAN and ready for re-ingestion.")
        
    except Exception as e:
        conn.rollback()
        print(f"[FAILURE] Cleanup aborted: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    sanitize_vault()