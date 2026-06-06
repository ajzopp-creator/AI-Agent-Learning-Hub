"""
P_010 Market Health -- infrastructure/snapshot_reader.py

Looks up market_phase from the dated snapshot archive for a given date.
Falls back to nearest prior date if exact date missing.
"""
import json
import logging
from datetime import date, timedelta

from market_health.config import SNAPSHOT_DIR

log = logging.getLogger(__name__)


def lookup_phase(trade_date: date, lookback: int = 5) -> str:
    """
    Return market_phase for the given date from the snapshot archive.

    Tries exact date first, then walks back up to lookback calendar
    days to find the nearest prior snapshot (handles weekends/holidays).
    Returns 'UNKNOWN' if no snapshot found within the lookback window.
    """
    for offset in range(lookback + 1):
        check_date = trade_date - timedelta(days=offset)
        snap = SNAPSHOT_DIR / f'{check_date:%Y%m%d}.json'
        if snap.exists():
            phase = _read_phase(snap)
            if offset > 0:
                log.debug('Phase for %s: used %s (offset %d)', trade_date, check_date, offset)
            return phase

    log.warning('No snapshot found for %s within %d days', trade_date, lookback)
    return 'UNKNOWN'


def lookup_phases(trades: list) -> list:
    """
    Bulk phase lookup. Mutates each TradeRecord in-place by setting
    the market_phase field. Returns the same list for convenience.
    """
    missing = 0
    for trade in trades:
        phase = lookup_phase(trade.open_date)
        trade.market_phase = phase
        if phase == 'UNKNOWN':
            missing += 1

    if missing:
        log.warning('%d trades could not be matched to a snapshot', missing)
    return trades


def _read_phase(snap_path) -> str:
    """Read market_phase from a snapshot JSON file."""
    try:
        data = json.loads(snap_path.read_text(encoding='utf-8'))
        return data.get('market_phase', 'UNKNOWN')
    except Exception as exc:
        log.error('Failed to read snapshot %s: %s', snap_path, exc)
        return 'UNKNOWN'