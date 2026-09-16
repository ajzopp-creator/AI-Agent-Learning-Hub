"""Domain logic -- eligibility and synthetic-exit computation for 0DTE
cash-settled options that expire with no closing Schwab transaction.

Pure logic, no I/O. See WO-P020-E1.018.

Schwab never emits a closing TRADE transaction for an expired 0DTE option
-- there is nothing to trade, the position just ceases to exist. The
instrument's own expirationDate/closingPrice snapshot (captured once, at
whatever moment the entry transaction is first parsed -- see
infrastructure.schwab_instrument_parser) is the only signal available.
Scoped to cash-settled index options only (config.CASH_SETTLED_OPTION_ROOTS)
-- an equity/ETF option past expiration can be assigned/exercised into a
stock position instead of a cash close, which this module must never do.
"""

import logging
from datetime import date as date_type
from typing import Dict, List

from domain.trade_logic import calculate_exit_pnl, calculate_hold_days

logger = logging.getLogger(__name__)


def is_eligible_for_expiration_close(
    trade: Dict,
    cash_settled_roots: frozenset,
    as_of_date: date_type,
    buffer_days: int,
) -> bool:
    """True if an open trade should be auto-closed on expiration.

    All of the following must hold:
      1. status is 'open' (caller already filters to no-exit-rows via the
         DB query this feeds from -- see infrastructure.db_writer.
         get_expired_open_option_trades()).
      2. asset_type is 'call' or 'put' -- never stock/etf/spread.
      3. underlying_symbol is in the explicit cash-settled allowlist.
      4. expiration_date is set and is at least buffer_days in the past
         relative to as_of_date -- never same-day, guards against closing
         before Schwab's settlement data is final (WO-P020-E1.018
         Acceptance Criteria: "just hasn't been pulled yet" false positive).
      5. settlement_price is set (the synthetic exit price source).

    Args:
        trade: Trade row as a dict (status, asset_type, underlying_symbol,
               expiration_date, settlement_price).
        cash_settled_roots: Allowlisted underlying symbols, e.g. {"NDXP"}.
        as_of_date: Date to evaluate against (normally date.today()).
        buffer_days: Minimum whole days past expiration required.

    Returns:
        True if eligible for a synthetic auto-close.
    """
    if trade.get("status") != "open":
        return False
    if trade.get("asset_type") not in ("call", "put"):
        return False
    if trade.get("underlying_symbol") not in cash_settled_roots:
        return False

    expiration_date = trade.get("expiration_date")
    settlement_price = trade.get("settlement_price")
    if expiration_date is None or settlement_price is None:
        return False

    days_past = (as_of_date - expiration_date).days
    return days_past >= buffer_days


def build_expiration_exit(trade: Dict, exit_date: date_type, multiplier: int) -> Dict:
    """Compute the synthetic exit dict for an expired option trade.

    Uses the same calculate_exit_pnl()/calculate_hold_days() math as every
    other exit in the pipeline -- an expiration close is not a special
    P&L case, only the price source (settlement_price instead of a real
    SOLD/BOT transaction) differs.

    Args:
        trade: Trade row dict -- must already have passed
               is_eligible_for_expiration_close().
        exit_date: Date to record as the exit (the trade's own
                   expiration_date -- the option settled that day, even
                   though we're recording it later once the buffer clears).
        multiplier: Options multiplier (100).

    Returns:
        Dict shaped for schemas.Exit: exit_price, qty_exited, exit_date,
        exit_pnl, hold_days. exit_commissions is 0.0 -- expiration has no
        Schwab fee (confirmed by the manual 2026-09-13 stopgap case).
    """
    exit_price = trade["settlement_price"]
    qty = trade["qty"]
    direction = trade["direction"]
    entry_price = trade["entry_price"]

    pnl = calculate_exit_pnl(entry_price, exit_price, qty, direction, multiplier)
    hold_days = calculate_hold_days(trade["open_date"], exit_date)

    return {
        "exit_price": exit_price,
        "qty_exited": qty,
        "exit_date": exit_date,
        "exit_datetime": None,
        "exit_commissions": 0.0,
        "exit_pnl": pnl,
        "hold_days": hold_days,
    }


def find_expiration_closes(
    open_trades: List[Dict],
    cash_settled_roots: frozenset,
    as_of_date: date_type,
    buffer_days: int,
    multiplier: int,
) -> List[Dict]:
    """Filter open trades to expiration-close candidates and compute exits.

    Args:
        open_trades: Candidate open option trade rows (already pre-filtered
                     by the DB query to asset_type in (call, put) with an
                     expiration_date set -- see infrastructure.db_writer.
                     get_expired_open_option_trades()).
        cash_settled_roots: Allowlisted underlying symbols.
        as_of_date: Date to evaluate against (normally date.today()).
        buffer_days: Minimum whole days past expiration required.
        multiplier: Options multiplier (100).

    Returns:
        List of dicts: {"trade_id", "underlying_symbol", "exit": <exit dict>}
        for every trade eligible to close, ready for the application layer
        to write (dry-run preview or commit).
    """
    results = []
    for trade in open_trades:
        if not is_eligible_for_expiration_close(
            trade, cash_settled_roots, as_of_date, buffer_days
        ):
            continue

        exit_dict = build_expiration_exit(trade, trade["expiration_date"], multiplier)
        results.append({
            "trade_id": trade["trade_id"],
            "underlying_symbol": trade["underlying_symbol"],
            "exit": exit_dict,
        })

    logger.info(f"Found {len(results)} trade(s) eligible for expiration auto-close.")
    return results
