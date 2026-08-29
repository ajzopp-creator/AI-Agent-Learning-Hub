"""
run_this_P300_20260827_163813.py
WO-P300-E5.006 NEXT STEPS step 1 -- read-only query of sector_stats in
bulk_research.db. Purpose: find out whether this table already answers
the sector win-rate stratification question before any new measurement
pass gets built. Read-only. Does not modify production files, does not
touch the live *catalog.db.
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

DB_PATH = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
    r"\models\research\bulk_research.db"
)
SCRIPT_PATH = Path(__file__).resolve()
DONE_PATH = SCRIPT_PATH.with_suffix(SCRIPT_PATH.suffix + ".done")
DUMP_PATH = SCRIPT_PATH.parent / "sector_stats_dump_20260827_163813.csv"


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

    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='sector_stats'"
    )
    if cur.fetchone() is None:
        print("FAIL: sector_stats table does not exist in bulk_research.db")
        write_done("FAIL", 1)
        sys.exit(1)

    cur.execute("SELECT COUNT(*) FROM sector_stats")
    total_rows = cur.fetchone()[0]
    print(f"sector_stats row count: {total_rows}")

    cur.execute("SELECT MIN(computed_at), MAX(computed_at) FROM sector_stats")
    min_ts, max_ts = cur.fetchone()
    print(f"computed_at range: {min_ts} to {max_ts}")

    cur.execute("SELECT DISTINCT sector_label FROM sector_stats ORDER BY sector_label")
    sectors = [r[0] for r in cur.fetchall()]
    print(f"Distinct sector_label values ({len(sectors)}): {sectors}")

    cur.execute("SELECT DISTINCT horizon_days FROM sector_stats ORDER BY horizon_days")
    horizons = [r[0] for r in cur.fetchall()]
    print(f"Distinct horizon_days values: {horizons}")

    cur.execute("SELECT DISTINCT detection_tier FROM sector_stats ORDER BY detection_tier")
    tiers = [r[0] for r in cur.fetchall()]
    print(f"Distinct detection_tier values: {tiers}")

    cur.execute(
        """
        SELECT sector_label, detection_tier, horizon_days, n, win_rate,
               mean_return_pct, std_return_pct, below_min_n, computed_at
        FROM sector_stats
        ORDER BY sector_label, detection_tier, horizon_days
        """
    )
    rows = cur.fetchall()

    with open(DUMP_PATH, "w", encoding="utf-8") as f:
        f.write(
            "sector_label,detection_tier,horizon_days,n,win_rate,"
            "mean_return_pct,std_return_pct,below_min_n,computed_at\n"
        )
        for row in rows:
            f.write(",".join("" if x is None else str(x) for x in row) + "\n")

    print(f"Full dump written to: {DUMP_PATH}")
    print(f"Dump row count: {len(rows)}")

    conn.close()

    if total_rows != len(rows):
        print("FAIL: row count mismatch between COUNT(*) and fetched rows")
        write_done("FAIL", 1)
        sys.exit(1)

    print("PASS")
    write_done("PASS", 0)


if __name__ == "__main__":
    main()
