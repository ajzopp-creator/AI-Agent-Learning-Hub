import sqlite3
import pandas as pd
import os

# IMMUTABLE PATH: Pointing to your latest versioned database
DB_PATH = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db'

def run_dashboard():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT horizon_days, is_profitable, return_pct FROM forward_labels", conn)
    
    print("--- P_300 PERFORMANCE DASHBOARD ---")
    summary = df.groupby('horizon_days').agg({
        'is_profitable': ['mean', 'count'],
        'return_pct': 'mean'
    })
    
    # Rename columns for clarity
    summary.columns = ['Win Rate', 'Sample Size', 'Avg Return']
    print(summary)
    conn.close()

if __name__ == "__main__":
    run_dashboard()