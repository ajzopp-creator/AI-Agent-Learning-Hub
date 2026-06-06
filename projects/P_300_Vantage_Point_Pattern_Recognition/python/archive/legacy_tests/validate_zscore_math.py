"""
FILE: validate_zscore_math.py
VERSION: 1.1
DATE: 2026-05-07
DESCRIPTION: Self-contained statistical validator. No external project imports required.
"""
import sys
import os
import sqlite3
import pandas as pd
import numpy as np

# Absolute Path Injection for DB Utilities
ROOT = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
sys.path.insert(0, os.path.join(ROOT, "python"))

from utilities.db_utils import get_latest_catalog

def local_calculate_z_score(sample_mean, pop_mean, pop_std, n):
    """Internal math logic to avoid ImportErrors during testing."""
    if n < 2 or pop_std == 0: return 0
    # Standard Error = sigma / sqrt(n)
    return (sample_mean - pop_mean) / (pop_std / np.sqrt(n))

def run_validation():
    db_path = get_latest_catalog()
    if not os.path.exists(db_path):
        print(f"[!] Critical Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    print(f"--- P_300 STATISTICAL AUDIT ---")
    print(f"Database: {os.path.basename(db_path)}")
    
    for h in [5, 7, 10]:
        df = pd.read_sql(f"SELECT is_profitable FROM forward_labels WHERE horizon_days = {h}", conn)
        df_clean = df.dropna()
        
        if df_clean.empty:
            print(f"\n[!] Horizon {h}D: No data found.")
            continue

        mu = df_clean['is_profitable'].mean()
        sigma = df_clean['is_profitable'].std()
        n_total = len(df_clean)
        
        print(f"\nHorizon: {h}D")
        print(f"  Population Size: {n_total} labels")
        print(f"  Market Avg (mu): {mu:.2%}")
        print(f"  Market StdDev (sigma): {sigma:.4f}")
        
        # Test Case: If we find 25 matches with a 70% win rate
        test_n = 25
        test_win_rate = 0.70
        z = local_calculate_z_score(test_win_rate, mu, sigma, test_n)
        
        status = "SIGNIFICANT" if abs(z) >= 1.96 else "NOISE"
        print(f"  TEST: {test_win_rate:.0%} Win Rate (n={test_n}) -> Z-Score: {z:.2f} ({status})")

    conn.close()
    print("\n--- AUDIT COMPLETE ---")

if __name__ == "__main__":
    run_validation()