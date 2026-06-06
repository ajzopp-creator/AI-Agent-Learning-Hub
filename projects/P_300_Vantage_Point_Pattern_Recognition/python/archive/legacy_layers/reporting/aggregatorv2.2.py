"""
FILE: aggregator.py
VERSION: 2.2
DATE: 2026-05-06
DESCRIPTION: Runs the Confidence Report using the dynamic DB catalog.
CHANGELOG:
    - v2.2: Enforced Data Integrity for NaN outcomes (Treat as Error).
    - v2.1: Enforced absolute sys.path injection.
"""
import sys
import os
import pandas as pd
import sqlite3
from pathlib import Path

# Force absolute path injection
PROJECT_PYTHON_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python"
sys.path.insert(0, PROJECT_PYTHON_DIR)

from matching.intelliscan import get_intelliscan_results
from utilities.db_utils import get_latest_catalog

def get_daily_target_ids(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT pattern_instance_id FROM pattern_instances WHERE anchor_date = (SELECT MAX(anchor_date) FROM pattern_instances)")
    return [row[0] for row in cursor.fetchall()]

def run_aggregator(anchor_id):
    db_path = get_latest_catalog()
    conn = sqlite3.connect(db_path)
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.ticker, p.anchor_date 
        FROM pattern_instances p
        JOIN symbols s ON p.symbol_id = s.symbol_id
        WHERE p.pattern_instance_id = ?
    """, (anchor_id,))
    anchor_row = cursor.fetchone()
    
    if not anchor_row:
        conn.close()
        return

    target_symbol, target_date = anchor_row
    print(f"\n--- Running Report for {target_symbol} ({target_date}) ---")
    
    df_matches = get_intelliscan_results(anchor_id)
    if df_matches.empty:
        print(f"[!] No matches found.")
        conn.close()
        return

    df_matches['confidence_score'] = 1 / (df_matches['distance'] + 0.01)
    df_results = df_matches.sort_values('confidence_score', ascending=False).head(10)
    
    ids_list = df_results['instance_id'].tolist()
    ids_tuple = tuple(ids_list) if len(ids_list) > 1 else f"({ids_list[0]})"
    
    query = f"""
        SELECT p.pattern_instance_id as instance_id, s.ticker as symbol, f.is_profitable as outcome
        FROM pattern_instances p
        JOIN symbols s ON p.symbol_id = s.symbol_id
        LEFT JOIN forward_labels f ON p.pattern_instance_id = f.pattern_instance_id AND f.horizon_days = 5
        WHERE p.pattern_instance_id IN {ids_tuple}
    """
    
    # Retrieve data
    df_final = pd.read_sql(query, conn)
    
    # --- P_300 FIX: DATA INTEGRITY ERROR HANDLING ---
    # NaN outcomes are errors (missing labels). 
    error_count = df_final['outcome'].isna().sum()
    
    if error_count > 0:
        print(f"[!] DATA INTEGRITY ERROR: {error_count} records dropped due to NaN outcomes.")
    
    # Strictly filter out the errors
    df_final_clean = df_final.dropna(subset=['outcome'])
    
    # Merge using strictly clean data
    df_merged = pd.merge(df_results, df_final_clean, on='instance_id')
    # ----------------------------------------

    print(df_merged[['symbol', 'outcome']])
    conn.close()

if __name__ == "__main__":
    # Test execution for the first valid ID
    db_path = get_latest_catalog()
    conn = sqlite3.connect(db_path)
    test_ids = get_daily_target_ids(conn)
    conn.close()
    if test_ids:
        run_aggregator(test_ids[0])