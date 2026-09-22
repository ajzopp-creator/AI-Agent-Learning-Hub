"""shared_resources/python_utils/p020_order_writer.py -- P_020 order-submit bridge.

Lets P_400 (or any other project) write a new order into P_020's orders
table at submit time, without needing its own copy of P_020's
schemas.Order or infrastructure.db_order_writer -- one function call,
same pattern as vault_interface.write_to_vault() but for the orders
table instead of the Obsidian vault.

P_020's python\\database\\ folder isn't part of the Hub's installed
package (unlike obsidian_writers/shared_resources/hub_lib, which are
importable from anywhere) -- it's sys.path-inserted here the same lazy
way schwab_order_puller.py's _get_client() reaches into its own
project's api\\ folder, just crossing a project boundary instead of a
subfolder.

Usage (from P_400 or any sending project):

    from shared_resources.python_utils.p020_order_writer import submit_order

    order_id = submit_order(
        account_id="AJZ6348", symbol="AAPL", side="long", qty=100,
        why_code="P_115", sig_code="BTD_SIGNAL",
        planned_entry_price=150.00, planned_stop_price=145.00,
        source_project="P400",
    )
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_P_020_DATABASE_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
)

# Package names P_020's database\ folder uses ("infrastructure", "domain")
# that a calling project may ALSO have as its own top-level package (P_400
# does, for both). sys.modules caches by name, so once a caller has loaded
# its own infrastructure/domain, "from infrastructure.db_client import
# ..." resolves against THAT cached package regardless of the sys.path
# insert below, and fails -- confirmed live 2026-09-07 (WO-P400-E6.001
# file-10 handoff, P_400 calling this bridge). Same collision hit "config"
# 2026-09-09 (P_400's own config.py has no DATABASE_DIR, P_020's does;
# recording a live TER order failed the P_020 sync until "config" was
# added to this tuple). Same collision hit "schemas" 2026-09-11 (P_400's
# own schemas.py has no Order/Trade/Exit, P_020's does; recording a live
# EXPD paper order failed the P_020 sync -- db_order_writer.py's
# "from schemas import Exit, Order, Trade" resolved against P_400's
# already-cached schemas module -- until "schemas" was added to this
# tuple).
#
# "schemas" REMOVED, "schemas_ops" ADDED 2026-09-21: P_020 split its
# monolithic schemas.py into schemas_ops.py/schemas_trade.py/
# schemas_tracker.py on 2026-09-19 (Order moved to schemas_ops, Exit/
# Trade to schemas_trade). This bridge's own "import schemas" was never
# updated for that split -- P_020's dir no longer has a schemas.py at
# all, so the import silently fell through past it to P_400's own
# unrelated schemas.py (still present on sys.path just behind P_020's
# dir), which loaded fine but has no Order attribute. No exception on
# the missing file, so it surfaced as a confusing AttributeError instead
# of a clean ModuleNotFoundError -- found live via a real AMZN option
# record. db_order_writer.py itself was already updated for the split
# ("from schemas_ops import Order"); only this external bridge lagged.
_COLLIDING_PACKAGES = ("infrastructure", "domain", "config", "schemas_ops")


def _load_p020():
    """Sys.path-insert P_020's database folder and import what's needed.

    Done lazily, inside this function, so importing p020_order_writer.py
    itself never touches P_020's sys.path or opens a connection -- same
    lazy-acquisition discipline schwab_order_puller.py's _get_client()
    uses for the Schwab client.

    Stashes and restores any sys.modules entries under _COLLIDING_PACKAGES
    around the import: the caller's own infrastructure/domain modules are
    removed from the cache first (forcing Python to re-resolve against
    sys.path, where P_020's dir now comes first), then P_020's freshly-
    imported copies under those same names are discarded and the caller's
    original stash is restored -- so the caller's own infrastructure/
    domain keep working normally for the rest of that process. "schemas_ops"
    IS stashed too (added 2026-09-11 as "schemas", renamed 2026-09-21 to
    match P_020's schemas.py -> schemas_ops.py split) -- P_400 has its own
    top-level schemas.py (Pydantic models for its own trade specs),
    unrelated in content to P_020's Order/Trade/Exit schemas but colliding
    on the bare module name the same way infrastructure/domain/config did.
    """
    if str(_P_020_DATABASE_DIR) not in sys.path:
        sys.path.insert(0, str(_P_020_DATABASE_DIR))

    def _colliding_names():
        return [
            name for name in sys.modules
            if name in _COLLIDING_PACKAGES
            or any(name.startswith(pkg + ".") for pkg in _COLLIDING_PACKAGES)
        ]

    stashed = {name: sys.modules.pop(name) for name in _colliding_names()}
    try:
        import schemas_ops
        from infrastructure.db_client import get_connection
        from infrastructure.db_order_writer import insert_order
    finally:
        for name in _colliding_names():
            del sys.modules[name]
        sys.modules.update(stashed)

    return schemas_ops, get_connection, insert_order


def submit_order(
    account_id: str,
    symbol: str,
    side: str,
    qty: float,
    why_code: Optional[str] = None,
    sig_code: Optional[str] = None,
    planned_entry_price: Optional[float] = None,
    planned_stop_price: Optional[float] = None,
    planned_target_price: Optional[float] = None,
    schwab_order_id: Optional[str] = None,
    council_verdict: Optional[str] = None,
    source_project: str = "P400",
    confidence_tier: str = "CONFIRMED",
    trade_mode: str = "REAL",
) -> Optional[int]:
    """Submit a new order into P_020's orders table.

    Args mirror the fields a sending project actually has at submit time
    (before Schwab confirms anything). Reconciliation-time fields
    (entry_date/close_date/realized_pnl/entry_fill_price/asset_type/
    put_call) are deliberately not exposed here -- P_020's own
    reconcile_command.reconcile_live_orders() fills those in later, once
    the order actually fills.

    Args:
        account_id: P_020 database account_id, e.g. 'AJZ6348'.
        symbol: Underlying or full option symbol.
        side: 'long' or 'short'.
        qty: Order quantity.
        why_code: Signal Source ID (WO-P000-E22.001 vocabulary).
        sig_code: More specific signal detail.
        planned_entry_price: Planned entry price at submit time.
        planned_stop_price: Planned stop price at submit time.
        planned_target_price: Planned target price at submit time.
        schwab_order_id: Schwab's own order ID once known, if available
            at submit time (may still be None for a just-queued order).
        council_verdict: P_400 council decision that authorized this order.
        source_project: Which project originated this order. Default 'P400'.
        confidence_tier: 'CONFIRMED' | 'INFERRED' | 'UNRESOLVED'.
        trade_mode: 'REAL' or 'PAPER'.

    Returns:
        The new order_id, or None if insert_order() skipped it as a
        duplicate (schwab_order_id already present).
    """
    schemas_ops, get_connection, insert_order = _load_p020()

    order = schemas_ops.Order(
        account_id=account_id,
        symbol=symbol,
        side=side,
        qty=qty,
        submitted_ts=datetime.now(timezone.utc).replace(tzinfo=None),
        why_code=why_code,
        sig_code=sig_code,
        planned_entry_price=planned_entry_price,
        planned_stop_price=planned_stop_price,
        planned_target_price=planned_target_price,
        schwab_order_id=schwab_order_id,
        council_verdict=council_verdict,
        source_project=source_project,
        confidence_tier=confidence_tier,
        trade_mode=trade_mode,
    )

    conn = get_connection()
    try:
        return insert_order(conn, order)
    finally:
        conn.close()
