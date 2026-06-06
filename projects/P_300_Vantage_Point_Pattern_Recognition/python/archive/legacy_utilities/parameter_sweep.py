"""
FILE: parameter_sweep.py
VERSION: 1.3
DATE: 2026-05-07
DESCRIPTION: Iterates through adjusted normalized distance thresholds (50-100).
"""
import sys
import os
import sqlite3
import pandas as pd
import numpy as np

# Absolute Path Injection
ROOT = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
sys.path.insert(0, os.path.join(ROOT, "python"))

from matching.intelliscan import get_intelliscan_results
from reporting.aggregator import get_population_stats
from utilities.db_utils import get_latest_catalog

def run_sweep(anchor_id):
    db_path = get_latest_catalog()
    conn = sqlite3.connect(db_path)
    
    # Get all potential matches unfiltered
    df_all_matches = get_intelliscan_results(anchor_id)
    
    sweep_results = []
    # NEW BASELINE: Test distances from tight (50.0) to loose (100.0)
    for dist in np.arange(50.0, 105.0, 5.0):
        dist = round(dist, 2)
        df_filtered = df_all_matches[df_all_matches['distance'] <= dist]
        
        row = {'Distance': dist, 'Match_Count': len(df_filtered)}
        
        for h in [5, 7, 10]:
            mu, sigma = get_population_stats(conn, h)
            match_ids = tuple(df_filtered['instance_id'].tolist())
            
            if len(match_ids) < 2:
                row[f'{h}D_Z'] = 0.0
                continue
                
            query = f"SELECT is_profitable FROM forward_labels WHERE pattern_instance_id IN {match_ids} AND horizon_days = {h}"
            df_sample = pd.read_sql(query, conn).dropna()
            
            n = len(df_sample)
            if n > 1 and sigma > 0:
                x_bar = df_sample['is_profitable'].mean()
                z = (x_bar - mu) / (sigma / np.sqrt(n))
                row[f'{h}D_Z'] = round(z, 2)
            else:
                row[f'{h}D_Z'] = 0.0
                
        sweep_results.append(row)
    
    conn.close()
    print("\n--- P_300 PARAMETER SWEEP: FINDING PEAK SIGNAL (NORMALIZED) ---")
    print(pd.DataFrame(sweep_results).to_csv(sep='\t', index=False))

if __name__ == "__main__":
    conn = sqlite3.connect(get_latest_catalog())
    cursor = conn.cursor()
    cursor.execute("SELECT pattern_instance_id FROM pattern_instances ORDER BY anchor_date DESC LIMIT 1")
    tid = cursor.fetchone()
    conn.close()
    if tid: run_sweep(tid[0])