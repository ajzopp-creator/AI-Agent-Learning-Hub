"""
run_this_P300_20260829_verify.py
WO-P300-E5.006 pre-work -- before deciding between a full 9-day
uncached walk-forward re-run and a much cheaper incremental one, check
whether the existing eval_cache (42,959 patterns, 2026-08-26,
threshold defaults unchanged since 2026-06-28) can actually be reused
for those patterns. Only valid if catalog growth since 08-26 has been
pure forward-append -- no pattern with anchor_date <= the cache's own
max covered anchor_date was inserted afterward (that would change an
already-cached pattern's corpus and invalidate its result).

Read-only. Opens the cache JSON and the live catalog DB, both mode=ro
equivalent (JSON is just read, DB opened via sqlite3 mode=ro). No
writes anywhere.
"""
import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

CACHE_PATH = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
    r"\models\eval_cache\catalog_42955_42959_282886144_default.json"
)
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
    if not CACHE_PATH.exists():
        print(f"FAIL: cache not found at {CACHE_PATH}")
        write_done("FAIL", 1)
        sys.exit(1)
    if not DB_PATH.exists():
        print(f"FAIL: DB not found at {DB_PATH}")
        write_done("FAIL", 1)
        sys.exit(1)

    print("Loading cache JSON (52.9MB, may take a few seconds)...")
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        cache = json.load(f)

    results = cache.get("results", [])
    cached_pids = {r["pattern_instance_id"] for r in results}
    cached_dates = [r["anchor_date"] for r in results]
    cache_max_date = max(cached_dates)
    print(f"Cache: n_patterns={cache.get('n_patterns')}, "
          f"actual result rows={len(results)}, "
          f"distinct pids={len(cached_pids)}")
    print(f"Cache threshold_overrides: {cache.get('threshold_overrides')}")
    print(f"Cache max anchor_date: {cache_max_date}")

    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()

    cur.execute("SELECT pattern_instance_id, anchor_date FROM pattern_instances")
    live = cur.fetchall()
    conn.close()

    live_pids = {pid for pid, _ in live}
    new_pids = live_pids - cached_pids
    missing_from_live = cached_pids - live_pids

    print(f"Live catalog: {len(live_pids)} pattern_instance_ids")
    print(f"New pids (in live, not in cache): {len(new_pids)}")
    print(f"Cached pids no longer in live catalog (should be 0): "
          f"{len(missing_from_live)}")

    # The real question: do ANY of the new pids have anchor_date <=
    # the cache's max covered anchor_date? If yes, backfilling
    # happened and the cache is NOT safely reusable as-is.
    new_pid_dates = {pid: d for pid, d in live if pid in new_pids}
    backfilled = {
        pid: d for pid, d in new_pid_dates.items() if d <= cache_max_date
    }

    print(f"New patterns with anchor_date <= cache max ({cache_max_date}): "
          f"{len(backfilled)}")
    if backfilled:
        sample = list(backfilled.items())[:10]
        print(f"Sample backfilled pids/dates: {sample}")
        print("RESULT: NOT safely reusable as-is -- backfilling detected. "
              "Full re-run (or a more careful partial invalidation) is "
              "needed, not a simple append-only extension.")
    else:
        print("RESULT: Pure forward-append confirmed. Cache IS safely "
              "reusable for its 42,959 patterns -- only the "
              f"{len(new_pids)} new patterns need fresh scoring.")

    print("PASS")
    write_done("PASS", 0)


if __name__ == "__main__":
    main()
