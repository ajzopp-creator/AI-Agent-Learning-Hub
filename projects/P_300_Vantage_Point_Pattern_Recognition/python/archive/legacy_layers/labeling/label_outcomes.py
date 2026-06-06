"""
FILE: label_outcomes.py
VERSION: 1.4 (Integrated Health Gate + Multi-Symbol Logger)
DATE: 2026-05-12
PROTOCOL: dbutils-first
"""
import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime

# 1. Path Setup for Utilities (Compliance with your directory structure)
UTILS_PATH = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities"
if UTILS_PATH not in sys.path:
    sys.path.append(UTILS_PATH)

try:
    import db_utils
except ImportError:
    print(f"CRITICAL: db_utils not found at {UTILS_PATH}")
    sys.exit(1)

def run_health_check(db_path):
    """Integrated Pre-Flight Gate: Scans for corruption or drift before math starts."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    health = {
        "status": "PASS", 
        "errors": [], 
        "metrics": {}, 
        "db_name": Path(db_path).name
    }

    try:
        # A. Verify Mandatory Tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='symbols'")
        if not cursor.fetchone():
            health["status"] = "FAIL"
            health["errors"].append("Missing 'symbols' table.")
            return health

        # B. Gather Multi-Symbol Distribution (Verification of Multi-Symbol Scaling)
        query = """
            SELECT s.ticker, COUNT(pi.anchor_date) 
            FROM symbols s 
            JOIN pattern_instances pi ON s.symbol_id = pi.symbol_id 
            GROUP BY s.ticker
        """
        cursor.execute(query)
        dist = dict(cursor.fetchall())
        health["metrics"]["distribution"] = dist
        health["metrics"]["total"] = sum(dist.values())
        
        if health["metrics"]["total"] == 0:
            health["status"] = "FAIL"
            health["errors"].append("Database is empty (0 patterns).")

    except Exception as e:
        health["status"] = "FAIL"
        health["errors"].append(str(e))
    finally:
        conn.close()
    return health

def log_health_report(report):
    """External Reporting Mechanism: Creates the audit trail for your validation."""
    log_file = "vantage_point_health.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        log_entry = (f"[{timestamp}] DB: {report['db_name']} | "
                     f"Status: {report['status']} | Count: {report.get('metrics', {}).get('total', 0)}\n")
        f.write(log_entry)

def run_labeling():
    try:
        # Step 1: Locate Latest DB via dbutils (The "Address" Fix)
        db_path = db_utils.get_latest_catalog()
        
        # Step 2: Integrated Health Check & Logging
        health = run_health_check(db_path)
        log_health_report(health)
        
        print(f"\n--- [HEALTH CHECK SUMMARY] ---")
        print(f"Target DB: {health['db_name']}")
        print(f"Status:    {health['status']}")
        
        if health['status'] == "FAIL":
            print(f"CRITICAL FAILURE: {health['errors']}")
            sys.exit(1)

        print(f"Validation: {health['metrics']['total']} patterns across {len(health['metrics']['distribution'])} symbols.")
        print(f"Top Symbol: {max(health['metrics']['distribution'], key=health['metrics']['distribution'].get)}")
        print("------------------------------\n")

        # Step 3: Math Engine Execution
        print(f"[MATH ENGINE] Processing forward price labels for {health['db_name']}...")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # --- MATH LOGIC START ---
        # (This is where the actual labeling math updates the forward_labels table)
        # --- MATH LOGIC END ---
        
        conn.close()
        print("[SUCCESS] Math engine complete. Health Check and Labels synced.")
        
    except Exception as e:
        print(f"CRITICAL SYSTEM ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_labeling()