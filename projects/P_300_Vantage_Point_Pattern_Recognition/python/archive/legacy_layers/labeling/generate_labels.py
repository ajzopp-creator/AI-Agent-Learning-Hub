"""
FILE: generate_labels.py
VERSION: 1.13
DATE: 2026-05-06
DESCRIPTION: Generates 5d, 7d, and 10d forward return labels for newly ingested, 
             unlabeled pattern instances. Utilizes dynamic pathing.
"""
import sqlite3
import pandas as pd
from datetime import timedelta
import sys
from pathlib import Path

# Add utilities directory to path for dynamic DB discovery
sys.path.append(str(Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities")))
from db_utils import get_latest_catalog

def run_labeling():
    db_path = get_latest_catalog()
    print(f"--- P_300 LABEL GENERATION STARTING ---")
    print(f"Target DB: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    # Ensure schema exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS forward_labels (
            pattern_instance_id INTEGER,
            horizon_days INTEGER,
            future_date TEXT,
            return_pct REAL,
            is_profitable INTEGER
        )
    """)
    
    # 1. Target only new, unlabeled instances
    query_instances = """
        SELECT p.pattern_instance_id, p.symbol_id, p.anchor_date, p.close_0 
        FROM pattern_instances p
        LEFT JOIN forward_labels f ON p.pattern_instance_id = f.pattern_instance_id
        WHERE f.pattern_instance_id IS NULL
    """
    instances = pd.read_sql_query(query_instances, conn)
    
    if instances.empty:
        print("All pattern instances are already labeled. No new labels to generate.")
        conn.close()
        return

    print(f"Found {len(instances)} new pattern instances to label.")
    print("Loading price action and normalizing date formats...")
    
    # 2. Load all price bars and use Pandas for robust datetime conversion
    prices = pd.read_sql_query("SELECT symbol_id, bar_date, close FROM price_bars", conn)
    prices['bar_date_dt'] = pd.to_datetime(prices['bar_date'], format='mixed')
    prices = prices.sort_values(by=['symbol_id', 'bar_date_dt'])
    
    labels = []
    
    # 3. Compute Labels
    print("Computing forward returns (5d, 7d, 10d)...")
    for row in instances.itertuples():
        try:
            anchor_dt = pd.to_datetime(row.anchor_date)
        except Exception:
            continue  # Skip if date is entirely unreadable
            
        # Filter prices for the specific symbol
        symbol_prices = prices[prices['symbol_id'] == row.symbol_id]
        
        for horizon in [5, 7, 10]:
            target_dt = anchor_dt + timedelta(days=horizon)
            
            # Find the first price bar on or after the target date
            future_bars = symbol_prices[symbol_prices['bar_date_dt'] >= target_dt]
            
            if not future_bars.empty:
                future_bar = future_bars.iloc[0]
                future_price = future_bar['close']
                actual_future_date = future_bar['bar_date'] # Preserve original format string
                
                pct_return = (future_price - row.close_0) / row.close_0
                
                # Format variables safely for SQLite insertion
                labels.append((
                    int(row.pattern_instance_id), 
                    int(horizon), 
                    str(actual_future_date), 
                    float(pct_return), 
                    1 if pct_return > 0 else 0
                ))
    
    # 4. Write to Database
    if labels:
        conn.executemany("INSERT INTO forward_labels VALUES (?, ?, ?, ?, ?)", labels)
        conn.commit()
        print(f"Successfully generated and inserted {len(labels)} new labels.")
    else:
        print("No future price data found to generate labels (likely due to dates at the edge of the dataset).")

    conn.close()
    print("--- LABEL GENERATION COMPLETE ---")

if __name__ == "__main__":
    run_labeling()