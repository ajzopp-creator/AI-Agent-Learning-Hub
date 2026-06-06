"""
FILE: inspect_labels.py
VERSION: 1.2
DATE: 2026-05-06
DESCRIPTION: Outputs recent forward labels, joined with the symbols table
             so human-readable tickers are displayed instead of raw symbol IDs.
"""
import sqlite3
import pandas as pd
import sys
from pathlib import Path

# Add utilities directory to path to use dynamic DB locator
sys.path.append(str(Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities")))
from db_utils import get_latest_catalog

def inspect():
    db_path = get_latest_catalog()
    print(f"Inspecting: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    # SQL JOIN to attach the human-readable ticker string to the label data
    query = """
        SELECT 
            f.pattern_instance_id, 
            s.ticker, 
            p.anchor_date, 
            f.horizon_days, 
            f.future_date, 
            ROUND(f.return_pct, 2) AS return_pct, 
            f.is_profitable
        FROM forward_labels f
        JOIN pattern_instances p ON f.pattern_instance_id = p.pattern_instance_id
        JOIN symbols s ON p.symbol_id = s.symbol_id
        ORDER BY f.pattern_instance_id DESC, f.horizon_days ASC
        LIMIT 30
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        if df.empty:
            print("No labels found in the database.")
        else:
            print("--- RECENT FORWARD LABELS ---")
            print(df.to_string(index=False))
    except Exception as e:
        print(f"Error querying database: {e}")
        
    conn.close()

if __name__ == "__main__":
    inspect()