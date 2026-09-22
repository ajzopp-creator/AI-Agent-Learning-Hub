"""One-off: backfill spread_group_id for the 8 existing P_210 NDXP live
legs (WO-P020-E1.021) -- these were ingested before spread grouping existed,
each leg as its own independent trade. Pairs them by open_date, matching
the real Schwab account statement (each date is one vertical spread's two
legs, confirmed against 2026-09-19-AccountStatement_NDX.csv).

Dry-run by default. Pass --commit to write.
"""

import sqlite3
import sys

DATABASE_FILE = (
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
)

# open_date -> (group_id, [trade_id, trade_id])
GROUPS = {
    "2026-09-09": ("SG_BACKFILL_20260909", [3160, 3162]),
    "2026-09-11": ("SG_BACKFILL_20260911", [3159, 3163]),
    "2026-09-17": ("SG_BACKFILL_20260917", [3165, 3168]),
    "2026-09-18": ("SG_BACKFILL_20260918", [3166, 3167]),
}


def main() -> int:
    commit = "--commit" in sys.argv
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row

    print(f"{'COMMIT' if commit else 'DRY RUN'} -- P_210 spread_group_id backfill\n")

    all_trade_ids = [tid for _, ids in GROUPS.values() for tid in ids]
    placeholders = ",".join("?" for _ in all_trade_ids)
    rows = conn.execute(
        f"SELECT trade_id, system, underlying_symbol, open_date, spread_group_id "
        f"FROM trades WHERE trade_id IN ({placeholders})",
        all_trade_ids,
    ).fetchall()
    found = {r["trade_id"]: r for r in rows}

    missing = [tid for tid in all_trade_ids if tid not in found]
    if missing:
        print(f"FAIL: trade_id(s) not found: {missing}")
        return 1

    already_set = [tid for tid, r in found.items() if r["spread_group_id"] is not None]
    if already_set:
        print(f"FAIL: trade_id(s) already have spread_group_id set: {already_set} "
              f"-- refusing to overwrite, review manually")
        return 1

    non_p210 = [tid for tid, r in found.items() if r["system"] != "P_210"]
    if non_p210:
        print(f"FAIL: trade_id(s) not tagged system='P_210': {non_p210}")
        return 1

    for open_date, (group_id, trade_ids) in GROUPS.items():
        for tid in trade_ids:
            r = found[tid]
            print(f"  {tid}  {r['open_date']}  {r['underlying_symbol']}  -> {group_id}")
            if r["open_date"] != open_date:
                print(f"    FAIL: expected open_date={open_date}, got {r['open_date']}")
                return 1

    if not commit:
        print("\nDry run -- no writes. Add --commit to write.")
        return 0

    for open_date, (group_id, trade_ids) in GROUPS.items():
        for tid in trade_ids:
            conn.execute(
                "UPDATE trades SET spread_group_id = ? WHERE trade_id = ?",
                (group_id, tid),
            )
    conn.commit()

    # Verify
    rows = conn.execute(
        f"SELECT trade_id, spread_group_id FROM trades WHERE trade_id IN ({placeholders})",
        all_trade_ids,
    ).fetchall()
    for r in rows:
        print(f"  Verified: trade_id={r['trade_id']} spread_group_id={r['spread_group_id']}")

    still_null = [r["trade_id"] for r in rows if r["spread_group_id"] is None]
    if still_null:
        print(f"FAIL: still NULL after commit: {still_null}")
        return 1

    print("\nPASS -- 4 spread groups backfilled (8 legs).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
