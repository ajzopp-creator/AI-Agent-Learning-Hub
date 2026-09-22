"""One-off: hand-assign real systems to the 18 live TOS_Import trades since
6/1 (Tony's own symbol+date mapping, 2026-09-19). Registers 'P_200' as a
new system (not previously in the systems table) before reassigning.

Dry-run by default. Pass --commit to write.
"""

import sqlite3
import sys

DATABASE_FILE = (
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
)

# trade_id -> new system (Tony's hand-assignment, matched by symbol+date)
ASSIGNMENTS = {
    3045: "P_200",  # 2026-06-16 AAPL call
    3046: "SNT",    # 2026-06-22 DIS put
    3048: "SNT",    # 2026-06-22 CSCO call
    3047: "P_116",  # 2026-06-25 CSX call
    3082: "P_920",  # 2026-07-08 SHEL call
    3083: "P_116",  # 2026-07-10 AAL call
    3085: "SNT",    # 2026-07-13 MRK call
    3084: "P_200",  # 2026-07-14 WMT call
    3122: "SNT",    # 2026-07-27 ABT put
    3121: "P_116",  # 2026-08-05 CSX call (still open)
    3130: "P_117",  # 2026-08-17 AADX stock
    3131: "P_116",  # 2026-08-18 GE call
    3146: "SNT",    # 2026-08-24 ADM call
    3147: "SNT",    # 2026-08-24 AA put
    3145: "P_116",  # 2026-08-25 GOOGL call
    3151: "SNT",    # 2026-08-31 ABT call
    3149: "P_116",  # 2026-09-02 XLV call
    3148: "P_117",  # 2026-09-04 ASX call
}


def main() -> int:
    commit = "--commit" in sys.argv
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row

    print(f"{'COMMIT' if commit else 'DRY RUN'} -- 18-trade hand-assignment\n")

    rows = {r["trade_id"]: r for r in conn.execute(
        f"SELECT trade_id, system, underlying_symbol, open_date FROM trades "
        f"WHERE trade_id IN ({','.join('?' for _ in ASSIGNMENTS)})",
        list(ASSIGNMENTS.keys()),
    ).fetchall()}

    missing = [tid for tid in ASSIGNMENTS if tid not in rows]
    if missing:
        print(f"FAIL: trade_id(s) not found: {missing}")
        return 1

    not_tos_import = [tid for tid, r in rows.items() if r["system"] != "TOS_Import"]
    if not_tos_import:
        print(f"FAIL: trade_id(s) not currently system='TOS_Import': {not_tos_import} "
              f"-- refusing to overwrite, review manually")
        return 1

    for tid, new_sys in ASSIGNMENTS.items():
        r = rows[tid]
        print(f"  {tid}  {r['open_date']}  {r['underlying_symbol']:<6}  TOS_Import -> {new_sys}")

    existing_systems = {r[0] for r in conn.execute("SELECT system_id FROM systems").fetchall()}
    new_systems = sorted({s for s in ASSIGNMENTS.values() if s not in existing_systems})
    if new_systems:
        print(f"\n  New system(s) to register: {new_systems}")

    if not commit:
        print("\nDry run -- no writes. Add --commit to write.")
        return 0

    for sys_id in new_systems:
        conn.execute(
            "INSERT OR IGNORE INTO systems (system_id, system_name, description, active) "
            "VALUES (?, ?, 'Auto-registered via hand-assignment, 2026-09-19', 1)",
            (sys_id, sys_id),
        )

    for tid, new_sys in ASSIGNMENTS.items():
        conn.execute("UPDATE trades SET system = ? WHERE trade_id = ?", (new_sys, tid))
    conn.commit()

    verify = {r["trade_id"]: r["system"] for r in conn.execute(
        f"SELECT trade_id, system FROM trades WHERE trade_id IN ({','.join('?' for _ in ASSIGNMENTS)})",
        list(ASSIGNMENTS.keys()),
    ).fetchall()}
    wrong = {tid: verify[tid] for tid, expect in ASSIGNMENTS.items() if verify[tid] != expect}
    if wrong:
        print(f"FAIL: mismatch after write: {wrong}")
        return 1

    print(f"\nPASS -- {len(ASSIGNMENTS)} trades reassigned, {len(new_systems)} new system(s) registered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
