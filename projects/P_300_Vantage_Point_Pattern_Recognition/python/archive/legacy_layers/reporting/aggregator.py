"""
FILE: aggregator.py
VERSION: 2.3
DATE: 2026-05-07
DESCRIPTION: Enhanced Confidence Report with Z-Score Statistical Significance.
CHANGELOG:
    - v2.3: Integrated optimization_config.json and Z-Score math.
    - v2.2: Enforced Data Integrity for NaN outcomes (Treat as Error).
"""
import sys
import os
import pandas as pd
import sqlite3
import json
import numpy as np
from pathlib import Path

# Force absolute path injection
PROJECT_ROOT = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
sys.path.insert(0, os.path.join(PROJECT_ROOT, "python"))

from matching.intelliscan import get_intelliscan_results
from utilities.db_utils import get_latest_catalog

CONFIG_PATH = os.path.join(PROJECT_ROOT, "parameters", "optimization_config.json")

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def get_population_stats(conn, horizon):
    query = f"SELECT is_profitable FROM forward_labels WHERE horizon_days = {horizon}"
    df = pd.read_sql(query, conn).dropna()
    return df['is_profitable'].mean(), df['is_profitable'].std()

def run_aggregator(anchor_id):
    config = load_config()
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
    if not anchor_row: return
    target_symbol, target_date = anchor_row

    df_matches = get_intelliscan_results(anchor_id)
    if df_matches.empty:
        conn.close()
        return

    dist_thresh = config['matching_parameters']['distance_threshold']
    df_filtered = df_matches[df_matches['distance'] <= dist_thresh].copy()
    
    report_data = []
    for h in config['horizons']:
        mu, sigma = get_population_stats(conn, h)
        match_ids = tuple(df_filtered['instance_id'].tolist())
        
        if not match_ids:
            report_data.append({'Horizon': f"{h}D", 'Matches': 0, 'Win_Rate': "0%", 'Z_Score': 0, 'Status': "NO_MATCHES"})
            continue

        query = f"SELECT is_profitable FROM forward_labels WHERE pattern_instance_id IN {match_ids} AND horizon_days = {h}"
        df_sample = pd.read_sql(query, conn).dropna()
        
        n = len(df_sample)
        if n > 1 and sigma > 0:
            x_bar = df_sample['is_profitable'].mean()
            z = (x_bar - mu) / (sigma / np.sqrt(n))
        else:
            x_bar, z = 0, 0
        
        report_data.append({
            'Horizon': f"{h}D",
            'Matches': n,
            'Win_Rate': f"{x_bar:.2%}",
            'Z_Score': round(z, 2),
            'Status': "SIGNIFICANT" if abs(z) >= config['significance_thresholds']['z_score_confidence'] else "NOISE"
        })

    print(f"\n--- P_300 EXECUTIVE REPORT: {target_symbol} ({target_date}) ---")
    print(pd.DataFrame(report_data).to_csv(sep='\t', index=False))
    conn.close()

if __name__ == "__main__":
    db_path = get_latest_catalog()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT pattern_instance_id FROM pattern_instances ORDER BY anchor_date DESC LIMIT 1")
    tid = cursor.fetchone()
    conn.close()
    if tid: run_aggregator(tid[0])