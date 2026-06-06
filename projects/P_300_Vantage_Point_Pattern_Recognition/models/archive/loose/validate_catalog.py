import sqlite3
import pandas as pd
import os

def validate_db():
    # Absolute Path to the new versioned database
    db_path = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db'
    
    if not os.path.exists(db_path):
        print(f"ERROR: File not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    
    print("--- VALIDATION REPORT ---")
    
    # 1. Count Records
    count = conn.execute('SELECT count(*) FROM forward_labels').fetchone()[0]
    print(f"Total Labels Generated: {count}")
    
    # 2. Sample Audit
    if count > 0:
        print("\n--- SAMPLE DATA (First 5 Rows) ---")
        df = pd.read_sql_query("SELECT * FROM forward_labels LIMIT 5", conn)
        print(df.to_string())
    else:
        print("WARNING: forward_labels table is empty.")

    # 3. Check for Anomalies (Nulls)
    null_count = conn.execute('SELECT count(*) FROM forward_labels WHERE return_pct IS NULL').fetchone()[0]
    print(f"\nNull return_pct values: {null_count}")
    
    conn.close()
    print("\n--- VALIDATION COMPLETE ---")

if __name__ == "__main__":
    validate_db()