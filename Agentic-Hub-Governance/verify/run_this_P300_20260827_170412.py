"""
run_this_P300_20260827_170412.py
WO-P300-E5.006 -- diagnostic pass BEFORE step 3 (the actual measurement
script). Purpose: find out whether the live catalog already contains
enough to reconstruct historical avg_posture WITHOUT a fresh VP export,
by checking whether SPY and QQQ are cataloged symbols and, if so, what
date range their pattern_bars mtdiff/ltdiff fields cover relative to the
rest of the catalog's anchor dates.

Read-only against the live catalog (082626catalog.db, current newest per
mmddyy-digit-first convention as of this run). No writes. Does not touch
Pipeline B, does not touch topk_cache.
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

DB_PATH = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
    r"\models\082626catalog.db"
)
SCRIPT_PATH = Path(__file__).resolve()
DONE_PATH = SCRIPT_PATH.with_suffix(SCRIPT_PATH.suffix + ".done")


def write_done(status, exit_code):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    DONE_PATH.write_text(f"{ts}\n{status}\nexit_code={exit_code}\n", encoding="utf-8")


def main():
    if not DB_PATH.exists():
        print(f"FAIL: DB not found at {DB_PATH}")
        write_done("FAIL", 1)
        sys.exit(1)

    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()

    # 1. Overall catalog anchor_date range (all symbols)
    cur.execute("SELECT MIN(anchor_date), MAX(anchor_date), COUNT(*) FROM pattern_instances")
    overall_min, overall_max, overall_n = cur.fetchone()
    print(f"Catalog-wide anchor_date range: {overall_min} to {overall_max} ({overall_n} pattern_instances)")

    # 2. Does symbols table contain SPY / QQQ?
    cur.execute("SELECT symbol_id, ticker FROM symbols WHERE ticker IN ('SPY','QQQ')")
    found = cur.fetchall()
    print(f"SPY/QQQ present in symbols table: {found}")

    if not found:
        print("RESULT: Neither SPY nor QQQ is a cataloged symbol. "
              "Historical posture cannot be reconstructed from the live "
              "catalog -- a fresh VP History Grid export for SPY and QQQ "
              "is required.")
        conn.close()
        print("PASS")
        write_done("PASS", 0)
        return

    # 3. For each found symbol, date range + row count on pattern_bars
    #    (bar_offset=0, the anchor bar, avoids double-counting a date that
    #    also appears as a preceding bar inside a different pattern window)
    for symbol_id, ticker in found:
        cur.execute(
            """
            SELECT MIN(pb.bar_date), MAX(pb.bar_date), COUNT(*)
            FROM pattern_bars pb
            JOIN pattern_instances pi ON pb.pattern_instance_id = pi.pattern_instance_id
            WHERE pi.symbol_id = ? AND pb.bar_offset = 0
            """,
            (symbol_id,),
        )
        bmin, bmax, bn = cur.fetchone()
        print(f"{ticker} (symbol_id={symbol_id}): anchor-bar date range {bmin} to {bmax}, {bn} rows")

        # sample 3 rows to confirm mtdiff/ltdiff are real, non-null values
        cur.execute(
            """
            SELECT pb.bar_date, pb.mtdiff, pb.ltdiff
            FROM pattern_bars pb
            JOIN pattern_instances pi ON pb.pattern_instance_id = pi.pattern_instance_id
            WHERE pi.symbol_id = ? AND pb.bar_offset = 0
            ORDER BY pb.bar_date
            LIMIT 3
            """,
            (symbol_id,),
        )
        sample = cur.fetchall()
        print(f"  sample rows (bar_date, mtdiff, ltdiff): {sample}")

    conn.close()
    print("PASS")
    write_done("PASS", 0)


if __name__ == "__main__":
    main()
