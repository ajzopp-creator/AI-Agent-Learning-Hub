"""row_mapper.py — maps a raw Excel row dict to P_115 schema fields.

Pure logic — no I/O. Returns a clean dict ready for write_to_vault(),
or None if required fields are absent.
"""

from __future__ import annotations

import logging
import re
from typing import Any

log = logging.getLogger(__name__)

# Fields P_800 always sets — never pulled from Excel.
# Applied AFTER the column map loop so they cannot be overwritten.
_STATIC_FIELDS: dict[str, str] = {
    "source": "P_115",
    "signal_source": "P_115",
}

# schema: Optional[float]
_FLOAT_FIELDS = frozenset({
    "breakout_volume_multiple",
    "rs_vs_spy",
    "entry_price",
    "tp_level",
    "sl_level",
    "stop_level",
    "risk_pct",
    "account_balance",
})

# schema: Optional[int] — V110 decimal tiers (3.5) are rounded to nearest int
_INT_FIELDS = frozenset({
    "distribution_day_count",
    "fundamentals_tier",
    "analysis_tier",
    "candle_tier",
    "setup_score",
    "liquidity_tier",
})

# schema: Optional[str] — any non-string, non-None value is coerced to str
_STRING_FIELDS = frozenset({
    "traded",
    "outcome",
    "follow_through_day",
    "market_direction",
    "step1_verdict",
    "pattern_type",
    "breakout_verdict",
    "recheck_status",
    "simulation_notes",
    "comments",
    "why_code",
    "sig_code",
})

# Windows filename invalid characters — rows with these in symbol are skipped
_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\[\]]')


def _to_float(value: Any) -> float | None:
    """Convert to float or return None."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _to_int(value: Any) -> int | None:
    """Convert to int (via round) or return None."""
    if value is None:
        return None
    try:
        return int(round(float(value)))
    except (ValueError, TypeError):
        return None


def _to_str(value: Any) -> str | None:
    """Coerce non-string cell values to str. Booleans → 'Y'/'N'."""
    if value is None:
        return None
    if isinstance(value, bool):
        return "Y" if value else "N"
    if isinstance(value, str):
        return value
    return str(value)


def _symbol_is_valid(symbol: Any) -> bool:
    """Return False if symbol is None, empty, or contains invalid filename chars."""
    if not symbol or not isinstance(symbol, str):
        return False
    return not _INVALID_FILENAME_CHARS.search(symbol)


def map_row(
    excel_row: dict[str, Any],
    column_map: dict[str, str],
    required_fields: list[str],
) -> dict[str, Any] | None:
    """Map one Excel row to P_115 schema fields.

    Args:
        excel_row: Raw dict keyed by Excel column header names.
        column_map: Maps Excel header → schema field name (from config).
        required_fields: Schema fields that must be non-null to proceed.

    Returns:
        Clean schema dict, or None if any required field is missing.
    """
    mapped: dict[str, Any] = {}

    for excel_col, schema_field in column_map.items():
        mapped[schema_field] = excel_row.get(excel_col)

    # Static fields applied AFTER loop — cannot be overwritten by Excel data
    mapped.update(_STATIC_FIELDS)

    for field in required_fields:
        if not mapped.get(field):
            log.debug("Skipping row — '%s' is empty. Row: %s", field, excel_row)
            return None

    if not _symbol_is_valid(mapped.get("symbol")):
        log.warning("Skipping row — invalid symbol: %s", mapped.get("symbol"))
        return None

    for field in _FLOAT_FIELDS:
        if field in mapped:
            mapped[field] = _to_float(mapped[field])

    for field in _INT_FIELDS:
        if field in mapped:
            mapped[field] = _to_int(mapped[field])

    for field in _STRING_FIELDS:
        if field in mapped:
            mapped[field] = _to_str(mapped[field])

    return mapped
