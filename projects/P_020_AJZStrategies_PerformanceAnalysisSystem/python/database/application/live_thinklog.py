"""live_thinklog.py -- Application layer.

Shared by two callers: the live weekly ingest hook (application/
ingest_pipeline.py) and the backfill command (application/
thinklog_backfill.py). Both need the same two things: load a live
ThinkLog CSV into a lookup, and apply tag overrides to a batch of
trade dicts.

Uses build_multi_entry_lookup() (not build_lookup()) -- live ThinkLog
notes accumulate multiple dated [WHY][SIG] lines in one running note per
symbol, unlike paper's one-tag-per-note assumption. See
domain/thinklog_parser.py and infrastructure/thinklog_reader.py
docstrings for the full reasoning (Tony, live session 2026-08-16).

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\application\\live_thinklog.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from config import THINKLOG_MATCH_FORWARD_DAYS
from domain.thinklog_override import get_override
from infrastructure.thinklog_reader import build_multi_entry_lookup, read_thinklog_csv

logger = logging.getLogger(__name__)


def load_live_thinklog_lookup(thinklog_path: Optional[Union[str, Path]]) -> Dict:
    """Load a live-account ThinkLog CSV into a per-line-dated lookup.

    Returns an empty dict (not None) when no path is given or the file is
    missing -- callers can look up against it unconditionally, no
    None-check needed.

    Args:
        thinklog_path: Path to a TOS ThinkLog CSV export, or None.

    Returns:
        {(symbol, date): ParsedThinkLog} from
        infrastructure.thinklog_reader.build_multi_entry_lookup().
    """
    if not thinklog_path:
        return {}
    path = Path(thinklog_path)
    if not path.exists():
        logger.warning(f"ThinkLog path given but not found: {path}")
        return {}
    records = read_thinklog_csv(path)
    return build_multi_entry_lookup(records)


def apply_thinklog_overrides(
    trades: List[Dict], thinklog_lookup: Dict, audit: List[str]
) -> int:
    """Apply ThinkLog tag overrides to a batch of trade dicts, in place.

    Tag always wins over vault/tracker/default (Tony directive, 2026-08-16)
    -- see domain/thinklog_override.py docstring for the full reasoning.
    Only touches trades where a tag was actually found within the forward
    window; every other trade is left exactly as the caller's prior
    resolution set it.

    Args:
        trades: Trade dicts -- need 'underlying_symbol', 'open_date',
                'system'. Mutated in place.
        thinklog_lookup: Lookup from load_live_thinklog_lookup(). Empty
                dict is a safe no-op.
        audit: Audit log line list -- one line appended per override.

    Returns:
        Number of trades overridden.
    """
    if not thinklog_lookup:
        return 0
    overridden = 0
    for trade in trades:
        override = get_override(
            trade.get("underlying_symbol", ""),
            trade.get("open_date"),
            thinklog_lookup,
            trade.get("system", ""),
            forward_days=THINKLOG_MATCH_FORWARD_DAYS,
        )
        if override is None:
            continue
        trade["system"] = override.system
        trade["reason"] = override.reason
        trade["signal_strength"] = override.signal_strength
        overridden += 1
        gap_note = f" (tag dated {override.tag_date}, {override.gap_days}d earlier)" if override.gap_days else ""
        audit.append(
            f"TAG OVERRIDE: {trade.get('underlying_symbol')} {trade.get('open_date')} "
            f"system {override.previous_system} -> {override.system}{gap_note}"
        )
    return overridden
