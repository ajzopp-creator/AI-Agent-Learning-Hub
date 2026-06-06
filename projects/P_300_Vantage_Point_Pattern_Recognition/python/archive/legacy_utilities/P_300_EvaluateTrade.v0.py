"""
FILE: P_300_EvaluateTrade.py
VERSION: 1.1
DESCRIPTION: Combined Decision Engine. Performs Conversion, Audit, and 
             Z-Score Statistical Validation in one pipeline.
"""
import sys
import os
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

# 1. PATH SETUP
BASE_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
sys.path.append(str(BASE_DIR / "python" / "utilities"))

import P_300_vantagepoint_batch_convert_v4 as converter
from db_utils import get_latest_catalog

def calculate_z_score(sample_win_rate, pop_mu, pop_sigma, n):
    if n < 2 or pop_sigma == 0: return 0
    return (sample_win_rate - pop_mu) / (pop_sigma / np.sqrt(n))

def main():
    print("--- P_300 EVALUATION PIPELINE START ---")
    
    # 2. CONVERT LIVE DATA (v4.0)
    converter.process_files()
    
    # 3. IDENTIFY LATEST POSTURE
    live_dir = BASE_DIR / "data" / "live"
    files = sorted(live_dir.glob("*.csv"), key=os.path.getmtime, reverse=True)
    if not files:
        print("[!] Error: No live CSV found after conversion.")
        return
    
    latest_csv = files[0]
    df_live = pd.read_csv(latest_csv)
    
    # Get Current Postures
    spy_p = df_live[df_live['Ticker'] == 'SPY']['Posture'].values[0]
    qqq_p = df_live[df_live['Ticker'] == 'QQQ']['Posture'].values[0]
    avg_p = (spy_p + qqq_p) / 2
    
    # 4. DATABASE CONNECT & POPULATION STATS
    db_path = get_latest_catalog()
    conn = sqlite3.connect(db_path)
    
    # Get Population Mean (mu) for 5-day horizon
    pop_df = pd.read_sql("SELECT win_label FROM trade_outcomes WHERE horizon_days = 5", conn)
    mu = pop_df['win_label'].mean()
    sigma = pop_df['win_label'].std()

    # 5. RUN INTELLISCAN AUDIT (n=15)
    query = f"""
    SELECT pi.anchor_date, AVG(pf.feature_value) as h_avg, tout.win_label
    FROM pattern_instances pi
    JOIN pattern_features pf ON pi.pattern_instance_id = pf.pattern_instance_id
    JOIN trade_outcomes tout ON pi.pattern_instance_id = tout.pattern_instance_id
    WHERE pf.feature_name = 'psi_0' AND tout.horizon_days = 5
    GROUP BY pi.anchor_date
    HAVING ABS(h_avg - {avg_p}) <= 1.5
    ORDER BY ABS(h_avg - {avg_p}) ASC LIMIT 15
    """
    df_audit = pd.read_sql_query(query, conn)
    n_matches = len(df_audit)
    sample_wr = df_audit['win_label'].mean()
    
    # Calculate Statistical Significance
    z_score = calculate_z_score(sample_wr, mu, sigma, n_matches)
    sig_label = "SIGNIFICANT" if z_score >= 1.96 else "NOISE"

    # 6. ACCOUNT SIZING (P_000)
    balance = 32812.00
    base_max = balance * 0.05
    # Reduce size if result is "Noise"
    final_spend = base_max if z_score >= 1.96 else base_max * 0.5

    # 7. FINAL AUDIT REPORT
    print("\n" + "="*45)
    print(f" P_300 EVALUATION: {latest_csv.name}")
    print("="*45)
    print(f"POSTURE:        {avg_p:.2f} (Avg SPY/QQQ)")
    print(f"WIN PROB:       {sample_wr:.1%} (Based on n={n_matches})")
    print(f"Z-SCORE:        {z_score:.2f} ({sig_label})")
    print("-" * 45)
    print(f"RISK PERMISSION: FULL (P_010)")
    print(f"ACTIONABLE SPEND: ${final_spend:,.2f}")
    print("="*45)
    
    if sig_label == "NOISE":
        print("[NOTE] Confidence is low due to sample size/variance. Spend reduced by 50%.")

if __name__ == "__main__":
    main()