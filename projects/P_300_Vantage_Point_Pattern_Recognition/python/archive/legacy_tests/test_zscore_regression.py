"""
FILE: test_zscore_regression.py
VERSION: 1.0
DATE: 2026-05-07
DESCRIPTION: Regression test for Z-Score statistical significance logic.
"""
import sys
import os
import sqlite3
import pandas as pd
import numpy as np

# Absolute Path Injection
ROOT = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
sys.path.insert(0, os.path.join(ROOT, "python"))

from reporting.aggregator import get_population_stats, calculate_z_score
from utilities.db_utils import get_latest_catalog

def run_test():
    db_path = get_latest_catalog()
    conn = sqlite3.connect(db_path)
    
    print(f"[TEST] Database: {os.path.basename(db_path)}")
    
    for h in [5, 7, 10]:
        mu, sigma = get_population_stats(conn, h)
        
        # Validation 1: Ensure stats are not null
        if mu is None or sigma is None:
            print(f"[FAIL] Horizon {h}D: Stats returned None. Check forward_labels table.")
            continue
            
        print(f"[PASS] Horizon {h}D: Population Mean={mu:.4f}, StdDev={sigma:.4f}")
        
        # Validation 2: Test Z-Score calculation with a hypothetical sample
        # If sample mean is 70% and population is 50% with stddev 0.5, n=40
        test_z = calculate_z_score(0.70, mu, sigma, 40)
        print(f"       Hypothetical 70% Win-Rate Z-Score: {test_z:.2f}")

    conn.close()
    print("[TEST COMPLETE]")

if __name__ == "__main__":
    run_test()