"""One-off: close the 4 P_210 NDXP spread legs that expired worthless with
no closing transaction in the Schwab feed. 0DTE options settle same-day;
Schwab does not emit a TRADE-type transaction for expiration, so the normal
BOT/SOLD matching in the ingestion pipeline never closes these -- they sit
'open' forever with no exit recorded.

Confirmed via raw pull data:
data\\api_pulls\\ajz_strategies\\P_020_raw_AJZ_Strategies_2026-09-05_to_2026-09-12_20260912_113950.json
All 4 legs' instrument metadata shows closingPrice 0.0001 (Schwab's floor
value for expired-worthless) with expirationDate already past the pull
timestamp. See WO-P020-E1.018 for the general 0DTE-expiration ingestion
gap this script is a manual stopgap for -- this script is a data
correction, not the code fix; it does not touch schwab_mapper.py.

Dry-run by default. Pass --commit to write.
"""

import sys
import sqlite3
from datetime import date

sys.path.insert(0, r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database')

from config import DATABASE_FILE
from schemas_trade import Exit
from domain.trade_logic import calculate_exit_pnl, calculate_hold_days
from infrastructure.db_writer import insert_exit, update_trade_status

# trade_id -> (direction, entry_price, open_date, expiration_date)
TRADES = {
    3160: ("long",  6.05, date(2026, 9, 9),  date(2026, 9, 9)),   # NDXP 260909P29360000
    3162: ("short", 7.20, date(2026, 9, 9),  date(2026, 9, 9)),   # NDXP 260909P29370000
    3159: ("long",  3.90, date(2026, 9, 11), date(2026, 9, 11)),  # NDXP 260911C29490000
    3163: ("short", 4.99, date(2026, 9, 11), date(2026, 9, 11)),  # NDXP 260911C29500000
}
EXIT_PRICE = 0.0
MULTIPLIER = 100
QTY = 1.0


def main():
    dry_run = "--commit" not in sys.argv
    print("DRY RUN -- pass --commit to write changes" if dry_run else "COMMITTING")
    print()

    conn = sqlite3.connect(str(DATABASE_FILE))
    total_pnl = 0.0

    for trade_id, (direction, entry_price, open_date, exit_date) in TRADES.items():
        row = conn.execute(
            "SELECT status FROM trades WHERE trade_id = ?", (trade_id,)
        ).fetchone()
        if row is None:
            print(f"SKIP trade_id={trade_id}: not found")
            continue
        if row[0] != "open":
            print(f"SKIP trade_id={trade_id}: status is '{row[0]}', not 'open'")
            continue

        existing = conn.execute(
            "SELECT 1 FROM exits WHERE trade_id = ? AND exit_number = 1", (trade_id,)
        ).fetchone()
        if existing:
            print(f"SKIP trade_id={trade_id}: exit already recorded")
            continue

        pnl = calculate_exit_pnl(entry_price, EXIT_PRICE, QTY, direction, MULTIPLIER)
        hold_days = calculate_hold_days(open_date, exit_date)
        total_pnl += pnl

        print(
            f"trade_id={trade_id}  {direction:5s}  entry={entry_price:.2f}  "
            f"exit={EXIT_PRICE:.2f}  pnl={pnl:+.2f}  hold_days={hold_days}"
        )

        if not dry_run:
            exit_ = Exit(
                trade_id=trade_id,
                exit_number=1,
                exit_date=exit_date,
                exit_datetime=None,
                qty_exited=QTY,
                exit_price=EXIT_PRICE,
                exit_commissions=0.0,
                exit_pnl=pnl,
                hold_days=hold_days,
            )
            insert_exit(conn, exit_)
            update_trade_status(conn, trade_id, "closed")

    print()
    print(f"Total P&L across {len(TRADES)} legs: {total_pnl:+.2f}")

    if not dry_run:
        conn.commit()
        print("Committed.")
    conn.close()

    print()
    print("PASS")


if __name__ == "__main__":
    main()
