"""spec_commands.py -- `spec` CLI command (split out of commands.py,
WO-P400-E3.009, to keep commands.py under the 300-line cap and to give
spec its own same-day cache-hit fast path).

On a same-day cache hit (evaluate already ran for this symbol today and
was APPROVED), prints the cached spec text and returns -- no packet
lookup, no archive call, no second evaluate_signal() run. Falls through
to a full evaluate+build+archive pass on any cache miss (stale, missing,
or spec run standalone without a prior evaluate today), preserving
today's existing standalone behavior exactly.
"""

from __future__ import annotations

import json
import logging

from config import SIGNALS_DIR, TradeMode
from application.read_signals import read_signals
from application.stock_fields import build_stock_fields
from application.spec_cache import cache_spec_text, read_cached_spec_text

logger = logging.getLogger("p400.spec_commands")


def _find_packet(symbol: str):
    result = read_signals()
    matches = [s for s in result.load.valid if s.symbol.upper() == symbol.upper()]
    return matches[0] if matches else None


def cmd_spec(symbol: str, snapshot_path: str, cash: float, trade_mode: TradeMode,
             target_override: float = None, pre_market: bool = False,
             qty_override: int = None) -> int:
    from application.evaluate_signal import evaluate_signal
    from application.build_order_spec import build_spec
    from infrastructure.signal_archiver import archive_packet

    cached_text = read_cached_spec_text(symbol)
    if cached_text is not None:
        print(cached_text)
        print("[INFO] Served from today's evaluate cache -- no packet re-read, no archive call.")
        return 0

    packet = _find_packet(symbol)
    if packet is None:
        print(f"[ERROR] No valid v2 packet found for {symbol} in {SIGNALS_DIR}")
        return 1

    if target_override is not None:
        packet = packet.model_copy(update={"guideline_target": target_override})

    snapshot = json.loads(open(snapshot_path, encoding="utf-8").read())
    if pre_market:
        snapshot["market_open"] = True

    result = evaluate_signal(packet, snapshot, cash_available=cash,
                             trade_mode=trade_mode, qty_override=qty_override)
    spec_text = build_spec(result, packet, snapshot)
    print(spec_text)

    fields = build_stock_fields(result, packet, trade_mode.value)
    cache_spec_text(result.symbol, spec_text, fields)

    archive_packet(packet.symbol, packet.signal_metadata.session_date)

    return 0