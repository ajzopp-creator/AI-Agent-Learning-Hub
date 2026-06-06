import sys
import os
import pandas as pd
import sqlite3
from pathlib import Path

# Path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from matching.intelliscan import get_intelliscan_results

DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db")

def get_latest_id(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(pattern_instance_id) FROM pattern_instances")
    return cursor.fetchone()[0]

def run_aggregator(anchor_id):
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Header Target Translation
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.ticker, p.anchor_date 
        FROM pattern_instances p
        JOIN symbols s ON p.symbol_id = s.symbol_id
        WHERE p.pattern_instance_id = ?
    """, (anchor_id,))
    anchor_row = cursor.fetchone()
    anchor_label = f"{anchor_row[0]} ({anchor_row[1]})" if anchor_row else f"ID {anchor_id}"
    print(f"\n--- Running Confidence Report for Target: {anchor_label} ---")
    
    # 2. Get Matches
    df_matches = get_intelliscan_results(anchor_id)
    if df_matches.empty:
        print("No matches found.")
        conn.close()
        return

    df_matches['confidence_score'] = 1 / (df_matches['distance'] + 0.01)
    df_results = df_matches.sort_values('confidence_score', ascending=False).head(10)
    
    # 3. Join Symbols, Dates, and Trade Outcomes
    ids_list = df_results['instance_id'].tolist()
    ids_tuple = tuple(ids_list) if len(ids_list) > 1 else f"({ids_list[0]})"
    
    # ARCHITECTURE FIX: 
    # Corrected legacy columns t.win_loss -> t.win_label
    # Corrected t.instance_id -> t.pattern_instance_id
    # Added horizon_days = 5 to prevent duplicate rows from our Math Engine
    query = f"""
        SELECT 
            p.pattern_instance_id as instance_id, 
            s.ticker as symbol, 
            p.anchor_date as date,
            t.win_label as outcome
        FROM pattern_instances p
        JOIN symbols s ON p.symbol_id = s.symbol_id
        LEFT JOIN trade_outcomes t ON p.pattern_instance_id = t.pattern_instance_id AND t.horizon_days = 5
        WHERE p.pattern_instance_id IN {ids_tuple}
    """
    
    try:
        df_final = pd.read_sql(query, conn)
        df_merged = pd.merge(df_results, df_final, on='instance_id')
        
        # Calculate win rate if outcomes exist (outcome is 1 or 0, so mean * 100 = win percentage)
        if 'outcome' in df_merged.columns:
            df_merged['win_rate'] = df_merged.groupby('symbol')['outcome'].transform('mean') * 100
            # Clean up the display format
            df_merged['win_rate'] = df_merged['win_rate'].fillna(0).round(2).astype(str) + '%'
        
        df_display = df_merged[['symbol', 'date', 'distance', 'confidence_score', 'win_rate']]
        print("\n--- Actionable Historical Analogs (With 5-Day Historical Win Rate) ---")
        print(df_display.sort_values('confidence_score', ascending=False).to_string(index=False))
        
    except Exception as e:
        print(f"\n[!] Aggregation failed: {e}")

    conn.close()

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    latest_id = get_latest_id(conn)
    conn.close()
    run_aggregator(latest_id)