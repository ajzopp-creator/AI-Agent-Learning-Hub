"""
FILE: P_300_Final_Validator.py
VERSION: 1.0 (CONSOLIDATED PROTOCOL)
DATE: 2026-05-12
DESCRIPTION: Merges Integrity Checks (Orphans/Ghosts) with Math Validation (Return %).
"""
import sqlite3
import pandas as pd
import sys
from pathlib import Path

# 1. Setup Dynamic Discovery
UTILS_PATH = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities"
if UTILS_PATH not in sys.path:
    sys.path.append(UTILS_PATH)

try:
    import db_utils
except ImportError:
    print("CRITICAL: db_utils.py not found in utilities folder.")
    sys.exit(1)

def run_full_validation():
    # Find latest DB automatically
    db_path = db_utils.get_latest_catalog()
    print(f"\n--- [INTEGRITY REPORT] Targeting: {Path(db_path).name} ---")
    
    conn = sqlite3.connect(db_path)
    
    # --- STAGE 1: SCHEMA & LINKAGE INTEGRITY ---
    orphans = conn.execute("""
        SELECT COUNT(*) FROM forward_labels 
        WHERE pattern_instance_id NOT IN (SELECT pattern_instance_id FROM pattern_instances)
    """).fetchone()[0]
    
    ghosts = conn.execute("""
        SELECT COUNT(*) FROM pattern_instances 
        WHERE pattern_instance_id NOT IN (SELECT pattern_instance_id FROM pattern_features)
    """).fetchone()[0]
    
    total_patterns = conn.execute("SELECT COUNT(*) FROM pattern_instances").fetchone()[0]
    
    # --- STAGE 2: MATH VALIDATION (Return %) ---
    null_returns = conn.execute("SELECT COUNT(*) FROM forward_labels WHERE return_pct IS NULL").fetchone()[0]
    
    # --- STAGE 3: OUTPUT RESULTS ---
    print(f"1. Pattern Count:   {total_patterns}")
    print(f"2. Orphaned Labels: {orphans} {'[OK]' if orphans == 0 else '[!! CORRUPTED !!]'}")
    print(f"3. Ghost Instances: {ghosts} {'[OK]' if ghosts == 0 else '[!! CORRUPTED !!]'}")
    print(f"4. Null Math Rows:  {null_returns} {'[OK]' if null_returns == 0 else '[!! WARNING !!]'}")
    
    if orphans == 0 and ghosts == 0:
        print("\n--- SAMPLE DATA (Verification) ---")
        df = pd.read_sql_query("SELECT * FROM forward_labels LIMIT 5", conn)
        print(df.to_string())
        print("\n[RESULT] STATUS GREEN: Database is healthy and synchronized.")
    else:
        print("\n[RESULT] STATUS RED: Corruption detected. Run sanitize_db.py immediately.")

    conn.close()

if __name__ == "__main__":
    run_full_validation()