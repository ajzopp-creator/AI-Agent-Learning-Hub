import sqlite3
import pandas as pd
import os
from datetime import datetime

# Config
DB_PATH = '../models/catalog.db'
SOURCE_DIR = '../data/historical/'  # Your SPY/QQQ CSVs here
FEATURE_SET_ID = 1  # baseline5barv1 from featuresets.csv

conn = sqlite3.connect(DB_PATH)

# Step 1: Insert/update symbols
symbols = ['SPY', 'QQQ']
for sym in symbols:
    conn.execute("INSERT OR IGNORE INTO symbols (symbol) VALUES (?)", (sym,))
conn.commit()

# Step 2: Process source file (add more filenames as needed)
filename = 'History-Grid-050324_051324_SPY_5day.csv'
source_path = os.path.join(SOURCE_DIR, filename)
if os.path.exists(source_path):
    df_raw = pd.read_csv(source_path)
    df_raw['Date'] = pd.to_datetime(df_raw['Date'], format='%m%d%Y')  # Fix DateShort
    df_raw = df_raw.sort_values('Date')
    
    # Step 3: Insert sourcefile
    sourcefileid = conn.execute(
        "INSERT OR IGNORE INTO sourcefiles (filename, symbol, holddays, importedat) VALUES (?, ?, ?, ?)",
        (filename, 'SPY', 5, datetime.now().isoformat())
    ).lastrowid
    
    # Step 4: Insert pricebars (OHLCV core)
    symbolid = conn.execute("SELECT symbolid FROM symbols WHERE symbol='SPY'").fetchone()[0]
    for _, row in df_raw.iterrows():
        conn.execute("""
            INSERT OR IGNORE INTO pricebars (symbolid, bardate, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (symbolid, row['Date'].date().isoformat(), row['Open Price'], row['High Price'], 
              row['Low Price'], row['Close Price'], row.get('Volume', 0)))
    
    # Step 5: Create patterninstances (5-bar windows, baseline anchor)
    dates = df_raw['Date'].dt.date.unique()
    for i in range(4, len(dates)):  # Min 5 bars
        anchor_date = dates[i]
        window_dates = [dates[j].isoformat() for j in range(i-4, i+1)]
        patterninstanceid = conn.execute("""
            INSERT INTO patterninstances (symbolid, sourcefileid, anchordate, featuresetid)
            VALUES (?, ?, ?, ?)
        """, (symbolid, sourcefileid, anchor_date.isoformat(), FEATURE_SET_ID)).lastrowid
        
        # Step 6: baseline5barv1 features (OHLC diffs, simple for v1)
        window_df = df_raw[df_raw['Date'].dt.date.isin([pd.to_datetime(d).date() for d in window_dates])]
        for bar_idx, (_, bar) in enumerate(window_df.iterrows()):
            feat_name = f'bar{bar_idx+1}_close_pct_chg'
            feat_val = (bar['Close Price'] - window_df.iloc[0]['Close Price']) / window_df.iloc[0]['Close Price']
            conn.execute("""
                INSERT INTO patternfeatures (patterninstanceid, featurename, featurevalue)
                VALUES (?, ?, ?)
            """, (patterninstanceid, feat_name, feat_val))
        
        # Step 7: Forward labels (5-day hold)
        if i + 5 < len(dates):
            future_close = df_raw[df_raw['Date'].dt.date == dates[i+5]]['Close Price'].iloc[0]
            pct_ret = (future_close - bar['Close Price']) / bar['Close Price']
            direction = 'up' if pct_ret > 0 else 'down'
            conn.execute("""
                INSERT INTO forwardlabels (patterninstanceid, holddays, absolutereturn, percentreturn, direction, profitable)
                VALUES (?, 5, ?, ?, ?, ?)
            """, (patterninstanceid, future_close - bar['Close Price'], pct_ret, direction, 1 if pct_ret > 0 else 0))
    
    print(f"Ingested {filename}: {len(dates)-4} patterns")

conn.commit()
conn.close()
print("SPY 5-day ingested. Run dump_catalog_fast.py to verify.")