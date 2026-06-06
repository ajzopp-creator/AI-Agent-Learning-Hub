"""
FILE: clean_database_dates.py
VERSION: 1.2
DATE: 2026-05-06
DESCRIPTION: Surgically sweeps the SQLite database, targeting all date columns.
             FIX: Aliased rowid to 'rid' in SQL to prevent Pandas index collisions.
"""
import sqlite3
import pandas as pd
import sys
from pathlib import Path

# Add utilities directory to path to use dynamic DB locator
sys.path.append(str(Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities")))
from db_utils import get_latest_catalog

def clean_dates():
    db_path = get_latest_catalog()
    print(f"--- DATABASE DATE CLEANUP INITIATED ---")
    print(f"Target DB: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    targets = {
        'pattern_instances': ['anchor_date'],
        'price_bars': ['bar_date'],
        'forward_labels': ['future_date']
    }
    
    for table, columns in targets.items():
        # Verify the table exists
        cursor.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cursor.fetchone()[0] == 0:
            continue
            
        for col in columns:
            print(f"Scanning {table}.{col}...")
            
            # Using alias 'rid' to guarantee column name consistency in Pandas
            query = f"SELECT rowid AS rid, {col} FROM {table} WHERE {col} IS NOT NULL"
            df = pd.read_sql_query(query, conn)
            
            # Pandas 'mixed' parser for safety
            df['clean_date'] = pd.to_datetime(df[col], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d')
            
            # Filter for rows that need changing
            df_to_update = df[df[col] != df['clean_date']].dropna(subset=['clean_date'])
            
            if df_to_update.empty:
                print(f"  -> All dates already clean.")
                continue
                
            print(f"  -> Reformatting {len(df_to_update)} rows...")
            
            # Use 'rid' (the aliased column)
            update_data = list(zip(df_to_update['clean_date'], df_to_update['rid']))
            
            update_sql = f"UPDATE {table} SET {col} = ? WHERE rowid = ?"
            cursor.executemany(update_sql, update_data)
            
    conn.commit()
    conn.close()
    print("--- DATABASE DATE CLEANUP COMPLETE ---")

if __name__ == "__main__":
    clean_dates()