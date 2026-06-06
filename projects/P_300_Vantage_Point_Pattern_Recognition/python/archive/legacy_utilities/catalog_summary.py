"""
FILE: catalog_summary.py
VERSION: 1.1
DATE: 2026-05-10
DESCRIPTION: Operational health check and Data Integrity scan for the P_300 Catalog.
"""
import sqlite3
import pandas as pd
import os
import sys

PROJECT_ROOT = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
try:
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "python"))
    from utilities.db_utils import get_latest_catalog
    db_path = get_latest_catalog()
except ImportError:
    db_path = os.path.join(PROJECT_ROOT, "051026geminicatalog.db")

def generate_health_summary():
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    
    # --- 1. VOLUME METRICS ---
    total_instances = pd.read_sql("SELECT COUNT(*) as count FROM pattern_instances", conn).iloc[0]['count']
    total_features = pd.read_sql("SELECT COUNT(*) as count FROM pattern_features", conn).iloc[0]['count']
    total_labels = pd.read_sql("SELECT COUNT(*) as count FROM forward_labels", conn).iloc[0]['count']
    
    latest_date_query = "SELECT MAX(anchor_date) as latest FROM pattern_instances"
    latest_date = pd.read_sql(latest_date_query, conn).iloc[0]['latest']
    
    new_records_query = f"SELECT COUNT(*) as count FROM pattern_instances WHERE anchor_date = '{latest_date}'"
    new_records = pd.read_sql(new_records_query, conn).iloc[0]['count']

    # --- 2. DATA INTEGRITY SCANS ---
    # Check for Orphaned Features (Features without a matching instance)
    orphan_features = pd.read_sql("""
        SELECT COUNT(*) as count FROM pattern_features 
        WHERE pattern_instance_id NOT IN (SELECT rowid FROM pattern_instances)
    """, conn).iloc[0]['count']

    # Check for Orphaned Labels (Labels without a matching instance)
    orphan_labels = pd.read_sql("""
        SELECT COUNT(*) as count FROM forward_labels 
        WHERE pattern_instance_id NOT IN (SELECT rowid FROM pattern_instances)
    """, conn).iloc[0]['count']

    # Check for Ghost Instances (Instances with ZERO features)
    ghost_instances = pd.read_sql("""
        SELECT COUNT(*) as count FROM pattern_instances 
        WHERE rowid NOT IN (SELECT DISTINCT pattern_instance_id FROM pattern_features)
    """, conn).iloc[0]['count']

    conn.close()

    # --- 3. EXECUTIVE OUTPUT ---
    print("\n" + "="*55)
    print(" P_300 CATALOG UPDATE SUMMARY (HEALTH & INTEGRITY)")
    print("="*55)
    print(f" Database:               {os.path.basename(db_path)}")
    print(f" Total Pattern Instances:{total_instances:,.0f}")
    print(f" Total Features Encoded: {total_features:,.0f}")
    print(f" Total Forward Labels:   {total_labels:,.0f}")
    print("-" * 55)
    print(f" Latest Anchor Date:     {latest_date}")
    print(f" New Patterns Added:     {new_records:,.0f}")
    print("="*55)
    
    # Integrity Alert Block
    if orphan_features == 0 and orphan_labels == 0 and ghost_instances == 0:
        print(" INTEGRITY CHECK:        [PASS] 0 Corrupted Links")
    else:
        print(" INTEGRITY CHECK:        [WARNING] Corruption Detected!")
        if orphan_features > 0:
            print(f"  -> Orphaned Features:  {orphan_features} (Require Cleanup)")
        if orphan_labels > 0:
            print(f"  -> Orphaned Labels:    {orphan_labels} (Require Cleanup)")
        if ghost_instances > 0:
            print(f"  -> Ghost Instances:    {ghost_instances} (Missing Feature Data)")
    print("="*55 + "\n")

if __name__ == "__main__":
    generate_health_summary()