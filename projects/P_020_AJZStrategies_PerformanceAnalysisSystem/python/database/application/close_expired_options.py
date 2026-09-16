"""close_expired_options.py -- Application layer.

Standalone, opt-in command to auto-close 0DTE cash-settled option trades
that expired with no closing Schwab transaction (WO-P020-E1.018). Manual
stopgap this generalizes: application/close_p210_expired_worthless_20260913.py.

Deliberately NOT wired into the weekly ingest -- it writes synthetic P&L
off an inferred settlement price, not a real transaction. Tony runs this
as its own step until it's been observed clean a few times (2026-09-15
design decision, see WO-P020-E1.018).

Dry-run by default (Hub-wide rule: dry-run before any DB write, always).

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\application\\close_expired_options.py

Usage:
    python P_020_Trade_Manager.py close-expired-options [--commit]

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application
"""
from __future__ import annotations

import logging
from datetime import date
from typing import Dict, List

from config import CASH_SETTLED_OPTION_ROOTS, EXPIRATION_CLOSE_BUFFER_DAYS, load_params
from domain.expiration_closer import find_expiration_closes
from infrastructure.db_client import get_connection
from infrastructure.db_writer import insert_exit, update_trade_status
from infrastructure.expiration_reader import get_expired_open_option_trades
from schemas import Exit

logger = logging.getLogger(__name__)


def print_preview(closes: List[Dict]) -> None:
    """Print a preview table of pending expiration closes."""
    if not closes:
        print("No open trades eligible for expiration auto-close.")
        return
    print(f"\n{'Trade':<8} {'Symbol':<8} {'Exit':<8} {'Qty':<6} {'P&L':<10} {'Hold':<6}")
    print("-" * 50)
    total_pnl = 0.0
    for c in closes:
        ex = c["exit"]
        total_pnl += ex["exit_pnl"]
        print(
            f"{c['trade_id']:<8} {c['underlying_symbol']:<8} "
            f"{ex['exit_price']:<8.4f} {ex['qty_exited']:<6.1f} "
            f"{ex['exit_pnl']:<+10.2f} {ex['hold_days']:<6}"
        )
    print(f"\n{len(closes)} trade(s) would close. Total P&L: {total_pnl:+.2f}")


def apply_closes(conn, closes: List[Dict]) -> int:
    """Write the exit + status update for each close. Caller gates dry-run.

    Args:
        conn: Active SQLite connection.
        closes: Output of domain.expiration_closer.find_expiration_closes().

    Returns:
        Number of trades actually closed.
    """
    closed = 0
    for c in closes:
        ex = c["exit"]
        exit_ = Exit(
            trade_id=c["trade_id"],
            exit_number=1,
            exit_date=ex["exit_date"],
            exit_datetime=ex["exit_datetime"],
            qty_exited=ex["qty_exited"],
            exit_price=ex["exit_price"],
            exit_commissions=ex["exit_commissions"],
            exit_pnl=ex["exit_pnl"],
            hold_days=ex["hold_days"],
        )
        exit_id = insert_exit(conn, exit_)
        if exit_id is None:
            logger.warning(f"Skip trade_id={c['trade_id']}: exit already recorded")
            continue
        update_trade_status(conn, c["trade_id"], "closed")
        closed += 1

    logger.info(f"Expiration auto-close: {closed} trade(s) closed.")
    return closed


def run_close_expired_options(commit: bool = False, as_of: date = None) -> int:
    """Entry point called by P_020_Trade_Manager.py's `close-expired-options`
    subcommand.

    Args:
        commit: Write changes if True; preview only if False (default).
        as_of: Date to evaluate expiration against -- defaults to today.
               Exposed as a parameter for testability, not a CLI flag.

    Returns:
        Number of trades closed (0 on dry-run, always).
    """
    as_of = as_of or date.today()
    params = load_params()
    multiplier = params["options_multiplier"]

    conn = get_connection()
    try:
        candidates = get_expired_open_option_trades(conn)
        closes = find_expiration_closes(
            candidates, CASH_SETTLED_OPTION_ROOTS, as_of,
            EXPIRATION_CLOSE_BUFFER_DAYS, multiplier,
        )
        print_preview(closes)
        if not commit or not closes:
            print("\nDry run -- no DB writes. Add --commit to write.")
            return 0
        return apply_closes(conn, closes)
    finally:
        conn.close()
