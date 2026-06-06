import sqlite3
import pandas as pd
import shutil
from datetime import datetime, timedelta

def run_sync():
    # 1. Configuration
    base_db = 'catalog.db'
    date_str = datetime.now().strftime("%m%d%y")
    output_db = f"{date_str}geminicatalog.db"
    
    print(f"--- P_300 Sync Starting ---")
    
    # 2. Copy the file (Safety)
    shutil.copy(base_db, output_db)
    
    # 3. Connect to the versioned copy
    conn = sqlite3.connect(output_db)
    
    # 4. Ensure schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS forward_labels (
            pattern_instance_id INTEGER,
            horizon_days INTEGER,
            future_date TEXT,
            return_pct REAL,
            is_profitable INTEGER
        )
    """)
    
    # 5. Processing
    print("Computing forward labels (5d, 7d, 10d)...")
    instances = pd.read_sql_query("SELECT pattern_instance_id, anchor_date, close_0 FROM pattern_instances", conn)
    
    labels = []
    for row in instances.itertuples():
        try:
            anchor_dt = datetime.strptime(row.anchor_date, '%Y-%m-%d')
        except ValueError:
            continue
            
        for horizon in [5, 7, 10]:
            target_date = (anchor_dt + timedelta(days=horizon)).strftime('%Y-%m-%d')
            query = "SELECT close FROM price_bars WHERE bar_date >= ? ORDER BY bar_date ASC LIMIT 1"
            res = conn.execute(query, (target_date,)).fetchone()
            
            if res:
                future_price = res[0]
                pct_return = (future_price - row.close_0) / row.close_0
                labels.append((row.pattern_instance_id, horizon, target_date, pct_return, 1 if pct_return > 0 else 0))
    
    # 6. Commit
    conn.executemany("INSERT INTO forward_labels VALUES (?, ?, ?, ?, ?)", labels)
    conn.commit()
    conn.close()
    print(f"--- SYNC COMPLETE ---")
    print(f"New labeled database created: {output_db}")

if __name__ == "__main__":
    run_sync()