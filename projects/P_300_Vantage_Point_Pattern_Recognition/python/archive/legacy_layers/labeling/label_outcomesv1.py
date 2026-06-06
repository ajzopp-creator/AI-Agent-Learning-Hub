import sqlite3
import pandas as pd
import sys
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
DB_PATH = BASE_DIR / "models" / "050326geminicatalog.db"

def verify_and_heal_schema(conn):
    """Detects legacy corrupted schemas and automatically rebuilds them."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trade_outcomes'")
    
    if cursor.fetchone():
        # Table exists, check if it has the correct column
        cursor.execute("PRAGMA table_info(trade_outcomes)")
        cols = [row[1] for row in cursor.fetchall()]
        if 'pattern_instance_id' not in cols:
            print("Notice: Legacy trade_outcomes schema detected. Dropping and rebuilding...")
            cursor.execute("DROP TABLE trade_outcomes")
            conn.commit()

    # Rebuild the pristine, canonical schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trade_outcomes (
            pattern_instance_id INTEGER,
            horizon_days INTEGER,
            forward_return_pct REAL,
            win_label INTEGER,
            UNIQUE(pattern_instance_id, horizon_days)
        )
    """)
    conn.commit()

def calculate_forward_returns():
    if not DB_PATH.exists():
        print(f"CRITICAL ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    
    # 1. Self-Healing Schema Check
    verify_and_heal_schema(conn)

    # 2. Load the historical price bars into memory
    try:
        bars_df = pd.read_sql_query("SELECT symbol_id, bar_date, close FROM price_bars ORDER BY symbol_id, bar_date", conn)
    except Exception as e:
        print(f"CRITICAL ERROR: Could not read price_bars. {e}")
        sys.exit(1)
        
    # 3. Fetch all pattern instances
    patterns_df = pd.read_sql_query("SELECT pattern_instance_id, symbol_id, anchor_date FROM pattern_instances", conn)

    new_records = []
    
    # 4. Math Engine: Calculate forward returns
    for _, pattern in patterns_df.iterrows():
        p_id = pattern['pattern_instance_id']
        s_id = pattern['symbol_id']
        a_date = pattern['anchor_date']

        # Isolate the specific symbol's timeline
        sym_bars = bars_df[bars_df['symbol_id'] == s_id].reset_index(drop=True)
        
        # Find the row index of our pattern's anchor date
        anchor_idx_list = sym_bars.index[sym_bars['bar_date'] == a_date].tolist()
        
        if not anchor_idx_list:
            continue # Data missing for this anchor date
            
        anchor_idx = anchor_idx_list[0]
        anchor_close = sym_bars.iloc[anchor_idx]['close']

        # Look forward 5, 7, and 10 trading days
        for horizon in [5, 7, 10]:
            target_idx = anchor_idx + horizon
            
            # Ensure we actually have data that far into the future (avoids crashing on live patterns)
            if target_idx < len(sym_bars):
                target_close = sym_bars.iloc[target_idx]['close']
                
                # Formula: ((New - Old) / Old) * 100
                ret_pct = ((target_close - anchor_close) / anchor_close) * 100
                win = 1 if ret_pct > 0 else 0
                
                new_records.append((p_id, horizon, ret_pct, win))

    # 5. Save results to the database
    if new_records:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT OR REPLACE INTO trade_outcomes 
            (pattern_instance_id, horizon_days, forward_return_pct, win_label) 
            VALUES (?, ?, ?, ?)
        """, new_records)
        conn.commit()

    conn.close()
    print(f"--- Math Engine: Calculated and saved {len(new_records)} forward return labels ---")
    sys.exit(0)

if __name__ == "__main__":
    try:
        calculate_forward_returns()
    except Exception as e:
        print(f"CRITICAL ERROR in Math Engine: {e}")
        sys.exit(1)