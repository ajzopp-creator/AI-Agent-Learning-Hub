"""p820_capture.py -- Application layer.

Loads the P_820 lookup and applies overrides to a batch of trade dicts.
Mirrors application/live_thinklog.py's shape exactly, one layer higher
in priority -- called AFTER apply_thinklog_overrides() in the ingest
pipeline, since P_820 wins over ThinkLog too.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\application\\p820_capture.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application
"""
from __future__ import annotations

import logging
from typing import Dict, List

from config import P820_MATCH_FORWARD_DAYS
from domain.p820_override import get_override
from infrastructure.p820_reader import load_p820_lookup

logger = logging.getLogger(__name__)


def apply_p820_overrides(
    trades: List[Dict], p820_lookup: Dict, audit: List[str]
) -> int:
    """Apply P_820 overrides to a batch of trade dicts, in place.

    Highest-priority source -- wins over whatever ThinkLog/tracker/
    default already set. Only touches trades where a dictated entry was
    actually found within the forward window; every other trade is left
    exactly as the caller's prior resolution set it.

    Args:
        trades: Trade dicts -- need 'underlying_symbol', 'open_date',
                'system'. Mutated in place.
        p820_lookup: Lookup from infrastructure.p820_reader.
                load_p820_lookup(). Empty dict is a safe no-op.
        audit: Audit log line list -- one line appended per override.

    Returns:
        Number of trades overridden.
    """
    if not p820_lookup:
        return 0
    overridden = 0
    for trade in trades:
        override = get_override(
            trade.get("underlying_symbol", ""),
            trade.get("open_date"),
            p820_lookup,
            trade.get("system", ""),
            forward_days=P820_MATCH_FORWARD_DAYS,
        )
        if override is None:
            continue
        trade["system"] = override.system
        trade["reason"] = override.why_code
        trade["signal_strength"] = override.sig_code
        overridden += 1
        gap_note = f" (dictated {override.entry_date}, {override.gap_days}d earlier)" if override.gap_days else ""
        audit.append(
            f"P820 OVERRIDE: {trade.get('underlying_symbol')} {trade.get('open_date')} "
            f"system {override.previous_system} -> {override.system}{gap_note}"
        )
    return overridden
