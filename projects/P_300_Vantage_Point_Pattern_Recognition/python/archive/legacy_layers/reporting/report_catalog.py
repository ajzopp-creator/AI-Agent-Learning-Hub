import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050426geminicatalog.db")

def run_clean_report():
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # Query to show unique entries by Symbol and Date
    query = """
    SELECT 
        s.ticker, 
        p.anchor_date, 
        p.close_price 
    FROM pattern_instances p
    JOIN symbols s ON p.symbol_id = s.symbol_id
    ORDER BY s.ticker, p.anchor_date DESC
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        print("--- P_300 CLEAN CATALOG REPORT ---")
        if df.empty:
            print("Catalog is empty.")
        else:
            # We use to_string to ensure we see the full list
            print(df.to_string(index=False))
            print(f"\nTotal Unique Records: {len(df)}")
    except Exception as e:
        print(f"[ERROR] Report generation failed: {e}")
        
    conn.close()

if __name__ == "__main__":
    run_clean_report()