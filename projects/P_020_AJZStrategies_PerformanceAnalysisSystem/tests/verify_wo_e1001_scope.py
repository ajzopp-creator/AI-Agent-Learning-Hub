"""
verify_wo_e1001_scope.py -- Read-only acceptance check for WO-P020-E1.001.

Re-runs the qty-aware allocator (schwab_mapper.map_pull_file) against the
latest AJZ6348 raw pull, then compares each resulting trade dict's exits
against what is actually recorded in the DB. Flags any AJZ6348 open/partial
trade where the pull shows a close that the DB doesn't have.

Does NOT write to the database. Safe to run any time.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\tests\\
           verify_wo_e1001_scope.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe verify_wo_e1001_scope.py
"""
import sqlite3
import sys
from pathlib import Path

DB_ROOT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem"
)
DB_FILE = DB_ROOT / "data" / "database" / "P_020_trades.db"
LATEST_PULL = (
    DB_ROOT / "data" / "api_pulls" / "ajz_strategies"
    / "P_020_raw_AJZ_Strategies_2026-06-28_to_2026-07-05_20260705_132949.json"
)

sys.path.insert(0, str(DB_ROOT / "python" / "database"))
sys.path.insert(0, str(DB_ROOT / "python" / "database" / "infrastructure"))
sys.path.insert(0, str(DB_ROOT / "python" / "database" / "domain"))

from schwab_mapper import map_pull_file  # noqa: E402


def get_recorded_exit_numbers(conn: sqlite3.Connection, trade_id: int) -> set:
    """Return the set of exit_number values already stored for a trade_id."""
    rows = conn.execute(
        "SELECT exit_number FROM exits WHERE trade_id = ?", (trade_id,)
    ).fetchall()
    return {r[0] for r in rows}


def check_trade_dict(conn: sqlite3.Connection, trade: dict) -> str | None:
    """Return a flag string if this trade dict reveals an unrecorded close."""
    txn_id = trade.get("schwab_transaction_id")
    if not txn_id:
        return None

    row = conn.execute(
        "SELECT trade_id, status FROM trades "
        "WHERE schwab_transaction_id = ? AND account_id = 'AJZ6348'",
        (txn_id,),
    ).fetchone()
    if row is None:
        return None  # not yet in DB at all -- new insert, not this bug

    trade_id, status = row
    if status not in ("open", "partial"):
        return None  # already closed -- fine

    pull_exit_numbers = {n for n in (1, 2, 3) if trade.get(f"exit_{n}")}
    if not pull_exit_numbers:
        return None  # pull shows no exits for this entry -- fine

    recorded = get_recorded_exit_numbers(conn, trade_id)
    missing = pull_exit_numbers - recorded
    if missing:
        return (
            f"trade_id={trade_id} {trade.get('underlying_symbol')} "
            f"open_date={trade.get('open_date')} status={status} "
            f"pull_has_exits={sorted(pull_exit_numbers)} "
            f"recorded={sorted(recorded)} MISSING={sorted(missing)}"
        )
    return None


def main() -> int:
    if not LATEST_PULL.exists():
        print(f"FAIL: latest pull file not found: {LATEST_PULL}")
        return 1

    _, trade_dicts = map_pull_file(LATEST_PULL)
    conn = sqlite3.connect(DB_FILE)

    flags = []
    for trade in trade_dicts:
        flag = check_trade_dict(conn, trade)
        if flag:
            flags.append(flag)

    conn.close()

    print(f"Pull file: {LATEST_PULL.name}")
    print(f"Trade dicts checked: {len(trade_dicts)}")
    print(f"Unrecorded closes found: {len(flags)}")
    for f in flags:
        print(f"  FLAG: {f}")

    if flags:
        print("\nRESULT: FAIL -- unrecorded closes present.")
        return 1
    print("\nRESULT: PASS -- zero unrecorded closes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
