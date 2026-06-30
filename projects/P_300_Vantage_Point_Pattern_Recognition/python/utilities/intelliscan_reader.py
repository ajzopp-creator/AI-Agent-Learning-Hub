"""
FILE: intelliscan_reader.py
VERSION: 1.0
DATE: 2026-06-16
AUTHOR: Anthony Zoppi + Claude
LAYER: utility
DESCRIPTION:
    Reads the daily IntelliScan eval-parameters grid
    (P_300_HistoryGrid_IntelliscanEvalParameters.xlsx) and exposes
    per-symbol VP support levels for use in stop calculation.

    Expected file location (operator drops before running daily eval bat):
        <project_root>/data/live/P_300_HistoryGrid_IntelliscanEvalParameters.xlsx

    The IntelliScan grid contains two Verified Support Zone columns per symbol:
        - support_1: nearer structural level (primary stop anchor)
        - support_2: wider structural level (P_400 fallback if support_1
                     creates a position that exceeds risk parameters)

    P_300 emits both levels in the signal packet. P_400 decides which to
    use based on its three-gate position-sizing logic (M-050).

    Column mapping (0-indexed, Tab 1):
        Col 0:  Company name
        Col 1:  Symbol (uppercase ticker)
        Col 16: Support Level 1 (price)
        Col 17: Support Level 1 -- Days in Place
        Col 18: Support Level 2 (price)  [labeled "Resistance" header but is
                second support tier in VP output -- confirmed from live data]
        Col 19: Support Level 2 -- Days in Place

    Behavior:
        - Returns None for both levels if the file is missing (non-blocking;
          pipeline continues without IntelliScan data -- M-043).
        - Returns None for a symbol not present in the grid.
        - Logs at WARNING when file is missing; INFO on successful load.

CHANGELOG:
    - 2026-06-16 v1.0: Initial. WO-P300-E1.001 -- IntelliScan stop integration.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── CONFIG ─────────────────────────────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTELLISCAN_PATH = (
    _PROJECT_ROOT / "data" / "live" /
    "P_300_HistoryGrid_IntelliscanEvalParameters.xlsx"
)

# Column indices in the IntelliScan Tab 1 sheet (0-based, after header rows).
_COL_SYMBOL      = 1
_COL_SUPPORT_1   = 16
_COL_SUPPORT_2   = 18


# ── DATA CONTRACT ──────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class IntelliScanLevels:
    """Support levels extracted for one symbol."""
    symbol: str
    support_1: Optional[float]   # nearer structural support (primary stop anchor)
    support_2: Optional[float]   # wider structural support (P_400 fallback)


# ── LOADER ─────────────────────────────────────────────────────────────────────
def load_intelliscan(path: Path = INTELLISCAN_PATH) -> dict[str, IntelliScanLevels]:
    """Parse the IntelliScan XLSX and return a symbol -> IntelliScanLevels map.

    Args:
        path: Override path for testing. Defaults to INTELLISCAN_PATH.

    Returns:
        Dict keyed by uppercase symbol. Empty dict if file is missing or
        unreadable (non-blocking).
    """
    if not path.exists():
        logger.warning(
            "IntelliScan file not found -- stop levels will use ATR floor only. "
            "Expected: %s", path
        )
        return {}

    try:
        import openpyxl  # deferred: keeps startup clean if openpyxl absent
    except ImportError:
        logger.warning(
            "openpyxl not available -- IntelliScan stop levels skipped."
        )
        return {}

    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        wb.close()
    except Exception as exc:
        logger.warning("IntelliScan read error (%s): %s", path.name, exc)
        return {}

    # First two rows are the merged header / sub-header -- skip them.
    result: dict[str, IntelliScanLevels] = {}
    for row in rows[2:]:
        if not row or row[_COL_SYMBOL] is None:
            continue
        symbol = str(row[_COL_SYMBOL]).strip().upper()
        if not symbol:
            continue

        def _to_float(val) -> Optional[float]:
            try:
                return float(val) if val is not None else None
            except (TypeError, ValueError):
                return None

        result[symbol] = IntelliScanLevels(
            symbol=symbol,
            support_1=_to_float(row[_COL_SUPPORT_1]),
            support_2=_to_float(row[_COL_SUPPORT_2]),
        )

    logger.info(
        "IntelliScan loaded: %d symbols from %s", len(result), path.name
    )
    return result


def get_support_levels(
    symbol: str,
    intelliscan: dict[str, IntelliScanLevels],
) -> tuple[Optional[float], Optional[float]]:
    """Return (support_1, support_2) for a symbol, or (None, None) if absent.

    Args:
        symbol:       Uppercase ticker.
        intelliscan:  Dict returned by load_intelliscan().

    Returns:
        (support_1, support_2) — either or both may be None.
    """
    entry = intelliscan.get(symbol.upper())
    if entry is None:
        return None, None
    return entry.support_1, entry.support_2


# ── SMOKE TEST ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format="%(levelname)s %(message)s")

    grid = load_intelliscan()
    if not grid:
        print("No IntelliScan data loaded.")
        sys.exit(1)

    print(f"\nLoaded {len(grid)} symbols:\n")
    print(f"{'Symbol':<8}  {'Support 1':>12}  {'Support 2':>12}")
    print("-" * 38)
    for sym, lvl in sorted(grid.items()):
        s1 = f"{lvl.support_1:.4f}" if lvl.support_1 is not None else "None"
        s2 = f"{lvl.support_2:.4f}" if lvl.support_2 is not None else "None"
        print(f"{sym:<8}  {s1:>12}  {s2:>12}")
