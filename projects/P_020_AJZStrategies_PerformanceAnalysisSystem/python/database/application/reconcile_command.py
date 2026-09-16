"""application/reconcile_command.py -- live and paper order reconciliation.

Pulls open P_400 orders from the orders table (trade_mode='REAL' for
live, 'PAPER' for paper), gets their current state (a live Schwab pull
for real orders, a parsed TOS/paperMoney Account Statement for paper),
walks each into an OrderChain, reconciles (Tier 1 -- chain linkage --
then Tier 2 fallback via the existing exit_allocator), and promotes
closed positions into the trades table.

Paper and live share _index_pulled_orders()/_reconcile_one() completely
unchanged -- both just consume Schwab-shaped dicts (Tony's explicit
requirement, WO-P400-E6.001: same reconciliation logic for both, not a
parallel paper-only pipeline). Only the SOURCE of those dicts differs
(schwab_order_puller.get_orders_for_account() vs
paper_order_history_parser.parse_order_history()).

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application (orchestration)
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def reconcile_live_orders(
    conn,
    account_hash: str,
    from_entered_datetime: str,
    to_entered_datetime: str,
) -> Dict[str, int]:
    """Reconcile all open REAL orders against a live Schwab pull.

    Args:
        conn: Active SQLite connection (infrastructure.db_client.get_connection()).
        account_hash: Schwab account hash to pull orders for.
        from_entered_datetime: ISO datetime, inclusive lower bound for the pull.
        to_entered_datetime: ISO datetime, inclusive upper bound for the pull.

    Returns:
        Dict with counts: {"reconciled": N, "still_open": N, "not_in_pull": N}.
        An order not found in the pull window is not an error -- widening
        the date range is the caller's job, not this function's.
    """
    from infrastructure.db_reader import get_open_real_orders
    from infrastructure.schwab_order_puller import get_orders_for_account

    open_orders = get_open_real_orders(conn)
    if not open_orders:
        logger.info("No open REAL orders to reconcile.")
        return {"reconciled": 0, "still_open": 0, "not_in_pull": 0}

    raw_orders = get_orders_for_account(
        account_hash,
        from_entered_datetime=from_entered_datetime,
        to_entered_datetime=to_entered_datetime,
    )
    if raw_orders is None:
        logger.error("Schwab orders pull failed -- aborting reconciliation.")
        return {"reconciled": 0, "still_open": 0, "not_in_pull": len(open_orders)}

    chains_by_id, standalone_by_symbol = _index_pulled_orders(raw_orders)

    counts = {"reconciled": 0, "still_open": 0, "not_in_pull": 0}
    for order_row in open_orders:
        _reconcile_one(conn, order_row, chains_by_id, standalone_by_symbol, counts)

    logger.info(
        f"Live reconciliation done: {counts['reconciled']} closed, "
        f"{counts['still_open']} still open, "
        f"{counts['not_in_pull']} not in pull window."
    )
    return counts


def reconcile_paper_orders(conn, statement_path: str) -> Dict[str, int]:
    """Reconcile all open PAPER orders against a parsed TOS/paperMoney
    Account Statement export.

    Reuses _index_pulled_orders()/_reconcile_one() completely unchanged
    from the live path above -- they operate on Schwab-shaped dicts and
    have no idea whether those came from a live Schwab pull or
    paper_order_history_parser.py's translation of a raw TOS statement.

    Args:
        conn: Active SQLite connection.
        statement_path: Path to a raw TOS/paperMoney Account Statement CSV.

    Returns:
        Dict with counts: {"reconciled": N, "still_open": N, "not_in_pull": N}.
    """
    from infrastructure.db_reader import get_open_paper_orders
    from infrastructure.paper_order_history_parser import parse_order_history

    open_orders = get_open_paper_orders(conn)
    if not open_orders:
        logger.info("No open PAPER orders to reconcile.")
        return {"reconciled": 0, "still_open": 0, "not_in_pull": 0}

    raw_orders = parse_order_history(Path(statement_path))
    if not raw_orders:
        logger.error(f"No orders parsed from statement: {statement_path}")
        return {"reconciled": 0, "still_open": 0, "not_in_pull": len(open_orders)}

    chains_by_id, standalone_by_symbol = _index_pulled_orders(raw_orders)

    counts = {"reconciled": 0, "still_open": 0, "not_in_pull": 0}
    for order_row in open_orders:
        _reconcile_one(conn, order_row, chains_by_id, standalone_by_symbol, counts)

    logger.info(
        f"Paper reconciliation done: {counts['reconciled']} closed, "
        f"{counts['still_open']} still open, "
        f"{counts['not_in_pull']} not in statement."
    )
    return counts


def run_reconcile_command(
    account: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    paper: bool = False,
    statement: Optional[str] = None,
) -> None:
    """CLI-facing wrapper for both live and paper reconciliation.

    Live path (paper=False, the default): resolves account -> Schwab
    hash, pulls a live date window -- start/end are required.
    Paper path (paper=True): parses a raw TOS/paperMoney Account
    Statement CSV instead -- statement is required, start/end are
    ignored.

    Args:
        account: CLI --account value (e.g. 'AJZ', 'IRA') -- live path only.
        start: ISO date/datetime, inclusive lower bound -- live path only.
        end: ISO date/datetime, inclusive upper bound -- live path only.
        paper: If True, reconcile PAPER orders against a statement file
            instead of pulling live Schwab orders.
        statement: Path to a raw TOS/paperMoney Account Statement CSV --
            required when paper=True.

    Prints results and exits(1) on a missing required argument or an
    unresolvable account hash.
    """
    from infrastructure.db_client import get_connection

    conn = get_connection()
    try:
        if paper:
            if not statement:
                print("--statement is required with --paper.")
                sys.exit(1)
            counts = reconcile_paper_orders(conn, statement)
        else:
            from application.import_command import resolve_account_id
            from infrastructure.schwab_positions import get_account_hash

            if not (start and end):
                print("--start and --end are required for live reconciliation.")
                sys.exit(1)

            account_id = resolve_account_id(account, account_label="")
            last4 = account_id[-4:]
            account_hash = get_account_hash(last4)
            if account_hash is None:
                print(f"Could not resolve Schwab account hash for {account_id} (last4={last4}).")
                sys.exit(1)

            counts = reconcile_live_orders(conn, account_hash, start, end)
    finally:
        conn.close()

    print(
        f"\nReconcile complete -- closed: {counts['reconciled']}  "
        f"still open: {counts['still_open']}  "
        f"not in pull window: {counts['not_in_pull']}"
    )


def _index_pulled_orders(raw_orders: List[dict]):
    """Build (chains_by_schwab_id, standalone_filled_chains_by_symbol)
    from a raw orders pull -- live Schwab or parsed paper, identical
    either way.

    standalone_by_symbol only includes FILLED, childless chains -- the
    Tier-2 candidate pool for naked entries with no bracket of their own.
    A malformed order (no orderId) is logged and skipped, not fatal to
    the rest of the pull.
    """
    from domain.order_linkage import build_order_chain

    chains_by_id = {}
    standalone_by_symbol: Dict[str, list] = {}
    for raw in raw_orders:
        try:
            chain = build_order_chain(raw)
        except ValueError as exc:
            logger.warning(f"Skipping malformed order in pull: {exc}")
            continue
        chains_by_id[chain.root.order_id] = chain
        if (
            not chain.descendants
            and chain.root.status == "FILLED"
            and chain.root.symbol
        ):
            standalone_by_symbol.setdefault(chain.root.symbol, []).append(chain)
    return chains_by_id, standalone_by_symbol


def _reconcile_one(conn, order_row, chains_by_id: dict, standalone_by_symbol: dict, counts: dict) -> None:
    """Reconcile a single open order row against the indexed pull data,
    updating counts in place (dict mutated -- avoids a 4th return value
    threaded through every caller). Identical for live and paper -- the
    order_row/chains_by_id shapes are the same either way."""
    from domain.order_reconciler import reconcile_order
    from infrastructure.db_order_writer import promote_order_to_trade, update_order_status

    order_id = order_row["order_id"]
    try:
        schwab_id = int(order_row["schwab_order_id"])
    except (TypeError, ValueError):
        logger.warning(
            f"order #{order_id}: invalid schwab_order_id="
            f"{order_row['schwab_order_id']!r}, skipping"
        )
        counts["not_in_pull"] += 1
        return

    chain = chains_by_id.get(schwab_id)
    if chain is None:
        logger.warning(
            f"order #{order_id} (schwab_order_id={schwab_id}) not found in "
            f"this pull -- widen the date window/statement to include it"
        )
        counts["not_in_pull"] += 1
        return

    candidates = [
        c for c in standalone_by_symbol.get(chain.root.symbol, [])
        if c.root.order_id != chain.root.order_id
    ]

    result = reconcile_order(order_row["side"], chain, candidate_exit_chains=candidates)
    if result is None:
        counts["still_open"] += 1
        return

    update_order_status(
        conn, order_id, status="closed",
        entry_date=str(result.entry_date) if result.entry_date else None,
        close_date=str(result.close_date) if result.close_date else None,
        realized_pnl=result.realized_pnl,
        entry_fill_price=result.entry_fill_price,
        asset_type=result.asset_type,
        put_call=result.put_call,
    )
    trade_id = promote_order_to_trade(conn, order_id)
    if trade_id is None:
        logger.warning(
            f"order #{order_id}: reconciled but promote_order_to_trade "
            f"failed or was skipped (duplicate?)"
        )
    counts["reconciled"] += 1
