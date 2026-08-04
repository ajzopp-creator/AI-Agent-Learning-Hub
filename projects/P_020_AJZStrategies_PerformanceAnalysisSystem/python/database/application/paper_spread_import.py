"""paper_spread_import.py -- imports multi-leg spread trades from a raw
paper AccountStatement.csv directly into the DB (WO-P020-E1.002).

Standalone script, NOT wired into P_020_Weekly_Update.bat -- run manually
per the WO's hard gate until Tony has reviewed real output against TOS.

Usage:
    python paper_spread_import.py <path_to_raw_AccountStatement.csv>
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from domain.spread_matcher import compute_realized_pnl, match_spread_opens_closes
from infrastructure.db_client import get_connection
from infrastructure.db_writer import (
    get_trade_id_by_schwab_id,
    insert_exit,
    insert_spread_legs,
    insert_trade,
)
from infrastructure.paper_spread_reader import read_spread_fills
from schemas import Exit, SpreadLeg, Trade

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python paper_spread_import.py <path_to_raw_AccountStatement.csv>")
        return 1

    csv_path = Path(sys.argv[1])
    fills = read_spread_fills(csv_path)
    matched = match_spread_opens_closes(fills)

    print(f"\nFound {len(matched)} spread position(s) to import:\n")

    conn = get_connection()
    imported = 0

    for pair in matched:
        open_fill = pair["open"]
        close_fill = pair["close"]
        legs = open_fill["parsed"]["legs"]
        direction = "long" if open_fill["parsed"]["container_action"] == "BOT" else "short"
        qty = abs(int(open_fill["parsed"]["container_qty"]))
        total_commissions = open_fill["fees"] + (close_fill["fees"] if close_fill else 0.0)

        trade = Trade(
            account_id="PAPER",
            system="TOS_Import",
            underlying_symbol=open_fill["parsed"]["symbol"],
            asset_type="spread",
            direction=direction,
            open_date=open_fill["datetime"].date(),
            open_datetime=open_fill["datetime"],
            qty=qty,
            entry_price=open_fill["parsed"]["net_price"],
            total_commissions=round(total_commissions, 2),
            status="closed" if close_fill else "open",
            source="tos_import",
            schwab_transaction_id=f"PAPER_SPREAD_{open_fill['ref']}",
        )

        trade_id = insert_trade(conn, trade)
        if trade_id is None:
            # Already exists (e.g. a prior run's crash left a partial
            # write -- trade inserted, legs/exit not reached yet).
            # Reuse the existing trade_id and backfill; insert_spread_legs
            # and insert_exit are both already dedup-safe, so this is a
            # no-op if the trade was already fully complete.
            trade_id = get_trade_id_by_schwab_id(conn, trade.schwab_transaction_id)
            if trade_id is None:
                print(f"  ERROR: duplicate detected but trade_id not found -- ref={open_fill['ref']}")
                continue
            print(f"  Existing trade_id={trade_id} found -- completing any missing legs/exit")

        spread_legs = [
            SpreadLeg(
                trade_id=trade_id,
                leg_number=leg["leg_number"],
                full_symbol=f"{trade.underlying_symbol} {leg['expiration']} {leg['strike']} {leg['put_call']}",
                put_call=leg["put_call"],
                direction=leg["direction"],
                qty=abs(leg["ratio"]),
                price=open_fill["parsed"]["net_price"],
            )
            for leg in legs
        ]
        insert_spread_legs(conn, trade_id, spread_legs)

        if close_fill:
            pnl = compute_realized_pnl(open_fill, close_fill)
            hold_days = (close_fill["datetime"].date() - open_fill["datetime"].date()).days
            exit_ = Exit(
                trade_id=trade_id,
                exit_number=1,
                exit_date=close_fill["datetime"].date(),
                exit_datetime=close_fill["datetime"],
                qty_exited=qty,
                exit_price=close_fill["parsed"]["net_price"],
                exit_commissions=close_fill["fees"],
                exit_pnl=pnl,
                hold_days=hold_days,
            )
            insert_exit(conn, exit_)
            print(f"  IMPORTED (closed): {trade.underlying_symbol} {trade.open_date} -> {exit_.exit_date}  "
                  f"P&L=${pnl:.2f}  {len(spread_legs)} legs  trade_id={trade_id}")
        else:
            print(f"  IMPORTED (open): {trade.underlying_symbol} {trade.open_date}  "
                  f"{len(spread_legs)} legs  trade_id={trade_id}")

        imported += 1

    conn.close()
    print(f"\nDone. {imported} spread trade(s) imported.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
