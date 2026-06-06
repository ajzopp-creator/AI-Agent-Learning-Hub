import sqlite3
import pandas as pd
import os

DB_PATH = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db'

def run_dashboard():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    query = '''
    SELECT 
        horizon_days,
        ROUND(AVG(is_profitable) * 100, 2) as Win_Rate_Pct,
        COUNT(pattern_instance_id) as Sample_Size,
        ROUND(AVG(return_pct) * 100, 2) as Avg_Return_Pct
    FROM forward_labels
    GROUP BY horizon_days
    ORDER BY horizon_days ASC
    '''
    
    try:
        df = pd.read_sql_query(query, conn)
        print("\n" + "="*50)
        print("     P_300 REAL PERFORMANCE DASHBOARD")
        print("="*50)
        if not df.empty:
            print(df.to_string(index=False))
        else:
            print("No label data found to aggregate.")
        print("="*50 + "\n")
    except Exception as e:
        print(f"Error reading database: {e}")
        
    conn.close()

if __name__ == '__main__':
    run_dashboard()
