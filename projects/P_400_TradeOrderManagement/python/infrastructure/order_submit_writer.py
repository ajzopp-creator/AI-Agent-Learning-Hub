"""order_submit_writer.py -- writes a submitted P_400 order into P_020's
orders table via the shared p020_order_writer bridge (WO-P400-E6.001).

Infrastructure layer: I/O only. Called by application/record_commands.py's
cmd_record_submit(), right after the existing Obsidian vault write.
Independent of it -- a P_020 write failure here never blocks or is
blocked by the vault write, matching record_writer.py's "vault I/O never
blocks the eval result" philosophy, applied to this second write target.

Every P_400 structure currently is a debit position (stock buys, long
options, debit spreads -- confirmed live via spread_sizer.py/
build_spread_spec.py, nothing sold-to-open exists in this codebase), so
side is always 'long' here -- not a guess, there is no short/credit
mechanism in P_400 to derive it from.
"""

from __future__ import annotations

import logging
from typing import Optional

from config import ACCOUNT_ID

logger = logging.getLogger("p400.order_submit_writer")


def write_order_to_p020(
    symbol: str,
    order_id: str,
    verdict: str,
    entry_price: float,
    stop_price: float,
    target_1: float,
    position_size: int,
    signal_source: str,
    trade_mode_value: str,
) -> Optional[int]:
    """Submit a P_400 order into P_020's orders table for reconciliation.

    Never raises -- a failure here is logged and returns None, exactly
    like record_writer.write_p400_record()'s own error handling, so a
    P_020-side problem never blocks cmd_record_submit()'s vault write or
    vice versa.

    Args:
        symbol: Underlying or full option symbol.
        order_id: Broker order ID (Schwab order ID once known).
        verdict: Council verdict (APPROVED/APPROVED_WITH_CAUTION/
            APPROVED_WITH_SEVERE_WARNING) -- becomes council_verdict.
        entry_price: Planned entry price.
        stop_price: Planned stop price.
        target_1: Planned first target price.
        position_size: Share/contract quantity, same value the vault
            record stores -- passed through as-is, no unit conversion.
        signal_source: Signal Source ID (e.g. 'P_115') -- becomes why_code.
        trade_mode_value: 'REAL' or 'PAPER' (config.TradeMode.value).

    Returns:
        P_020's new order_id (its own primary key, distinct from the
        broker order_id passed in), or None on failure/duplicate.
    """
    try:
        # Local import so a caller (or test) can patch
        # p020_order_writer.submit_order and have it take effect -- a
        # top-level `from ... import submit_order` binds the name once
        # at import time and ignores later patches.
        from shared_resources.python_utils.p020_order_writer import submit_order

        p020_order_id = submit_order(
            account_id=ACCOUNT_ID,
            symbol=symbol,
            side="long",
            qty=position_size,
            why_code=signal_source,
            planned_entry_price=entry_price,
            planned_stop_price=stop_price,
            planned_target_price=target_1,
            schwab_order_id=order_id,
            council_verdict=verdict,
            source_project="P400",
            trade_mode=trade_mode_value,
        )
    except Exception as e:
        logger.warning(
            f"P_020 order write failed for {symbol} (order_id={order_id}): {e}"
        )
        return None

    if p020_order_id is None:
        logger.info(
            f"P_020 order write skipped (duplicate?) for {symbol} "
            f"(order_id={order_id})"
        )
    return p020_order_id
