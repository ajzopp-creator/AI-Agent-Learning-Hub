import sys
import os
import pandas as pd
import sqlite3
from pathlib import Path

# Path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from matching.intelliscan import get_intelliscan_results

DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db")

def get_daily_target_ids(conn):
    """
    Retrieves the pattern_instance_ids ONLY for the most recent batch date.
    This ensures we only report on the specific CSVs just ingested.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pattern_instance_id 
        FROM pattern_instances 
        WHERE anchor_date = (SELECT MAX(anchor_date) FROM pattern_instances)
    """)
    return [row[0] for row in cursor.fetchall()]

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
    
    if not anchor_row:
        conn.close()
        return

    target_symbol = anchor_row[0]
    target_date = anchor_row[1]
    
    print(f"\n====================================================================")
    print(f"--- Running Confidence Report for Target: {target_symbol} ({target_date}) ---")
    print(f"====================================================================")
    
    # 2. Get Matches
    df_matches = get_intelliscan_results(anchor_id)
    if df_matches.empty:
        print(f"[!] No historical matches found for {target_symbol}.")
        print("ACTION: [ PASS ] - Insufficient data.")
        conn.close()
        return

    df_matches['confidence_score'] = 1 / (df_matches['distance'] + 0.01)
    df_results = df_matches.sort_values('confidence_score', ascending=False).head(10)
    
    # 3. Join Symbols, Dates, and Trade Outcomes
    ids_list = df_results['instance_id'].tolist()
    ids_tuple = tuple(ids_list) if len(ids_list) > 1 else f"({ids_list[0]})"
    
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
        
        overall_win_rate = 0.0
        
        # Calculate win rate if outcomes exist
        if 'outcome' in df_merged.columns and not df_merged['outcome'].isna().all():
            df_merged['win_rate_val'] = df_merged.groupby('symbol')['outcome'].transform('mean') * 100
            overall_win_rate = df_merged['outcome'].mean() * 100
            df_merged['win_rate'] = df_merged['win_rate_val'].fillna(0).round(2).astype(str) + '%'
        else:
            df_merged['win_rate'] = 'N/A'
        
        df_display = df_merged[['symbol', 'date', 'distance', 'confidence_score', 'win_rate']]
        print("\n--- Actionable Historical Analogs (With 5-Day Historical Win Rate) ---")
        print(df_display.sort_values('confidence_score', ascending=False).to_string(index=False))
        
        # 4. Generate AI Conclusion & Action Matrix
        top_match_symbol = df_display.iloc[0]['symbol'] if not df_display.empty else "historical analogs"
        
        print(f"\n[ AI Analysis & Conclusion ]")
        print(f"Because {target_symbol} today closely matches the historical structure of {top_match_symbol} on these dates, {target_symbol} has a {overall_win_rate:.1f}% probability of being profitable 5 days from now.")
        
        # Action Logic
        if overall_win_rate >= 70.0:
            print("ACTION: [ BUY INDICATOR ] - High-probability edge detected.")
        elif overall_win_rate >= 55.0:
            print("ACTION: [ WATCH LIST ] - Moderate edge detected. Monitor for confirmation.")
        else:
            print("ACTION: [ PASS ] - Insufficient historical edge.")
            
    except Exception as e:
        print(f"\n[!] Aggregation failed: {e}")

    conn.close()

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    target_ids = get_daily_target_ids(conn)
    conn.close()
    
    if not target_ids:
        print("No targets found in database.")
        sys.exit(1)
        
    for anchor_id in target_ids:
        run_aggregator(anchor_id)