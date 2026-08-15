"""Quick read-only check: does the live catalog have a populated topk_cache table.
Staged for WO-P300-E4.006 status verification (M-054 -- status header claims
unverified, WO body claims live-verified; checking the live artifact directly).
Read-only. No writes. Ref: session 2026-08-12.
"""
import sqlite3
import sys
from pathlib import Path

CATALOG = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\080526catalog.db"

try:
    conn = sqlite3.connect(f"file:{CATALOG}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='topk_cache'")
    exists = cur.fetchone() is not None
    if not exists:
        print("RESULT: topk_cache table DOES NOT EXIST on live catalog")
        sys.exit(0)
    cur.execute("SELECT COUNT(*) FROM topk_cache")
    topk_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM pattern_instances")
    pattern_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT pattern_instance_id) FROM topk_cache")
    distinct_pids = cur.fetchone()[0]
    print(f"RESULT: topk_cache EXISTS")
    print(f"topk_cache rows: {topk_count}")
    print(f"pattern_instances rows: {pattern_count}")
    print(f"distinct pattern_instance_id in topk_cache: {distinct_pids}")
    print(f"avg rows/pattern (covered pids only): {topk_count/distinct_pids if distinct_pids else 0:.2f}")
    conn.close()
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)
