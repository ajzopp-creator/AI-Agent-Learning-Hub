import sqlite3
import pandas as pd
from pathlib import Path

# Target the restored 050426 database
DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050426geminicatalog.db")

def run_report():
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # Query the instances table using the schema we validated
    query = """
    SELECT anchor_date, open_0, close_0, close_price 
    FROM pattern_instances 
    ORDER BY anchor_date DESC 
    LIMIT 20
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        print("--- P_300 PATTERN INGESTION REPORT (GROUND TRUTH) ---")
        if df.empty:
            print("No data found in pattern_instances.")
        else:
            print(df.to_string(index=False))
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        
    conn.close()

if __name__ == "__main__":
    run_report()