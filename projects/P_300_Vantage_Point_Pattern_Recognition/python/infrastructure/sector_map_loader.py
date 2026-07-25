"""
FILE: infrastructure/sector_map_loader.py
VERSION: 1.0
DATE: 2026-07-10
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Reads + validates data/reference/sector_map.csv for WO-P300-E2.002.
    Pure I/O + translation -- no stats logic (that's domain/
    sector_stats_calc.py).

    The CSV encodes an ETF's non-applicable sector as the literal
    string "N/A" (human-readable placeholder for the operator, not a
    real sector name) -- translated to sector=None here, before
    constructing SectorMapRow, since the schema's own validator
    (Decision 5) requires ETF rows to carry sector=None, never a
    placeholder string masquerading as a value. Verified against the
    real file (2026-07-10, 127 rows: 126 STOCK, 1 ETF/SPY).

    verify_full_coverage() is the code-level enforcement of Decision 2's
    zero-tolerance rule (every catalog symbol must have a real sector,
    no "Unclassified" resting state) -- fails loudly, does not silently
    skip, per the WO's Acceptance Criteria.

CHANGELOG:
    - 2026-07-10 v1.0: Initial release (WO-P300-E2.002 file #5 of 11).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import ASSET_CLASS_ETF, SECTOR_MAP_CSV  # noqa: E402
from schemas_sector_analysis import SectorMapRow  # noqa: E402

# Literal placeholder the CSV uses for an ETF's non-applicable sector
# (human-readable in the file; never a real GICS sector name).
_ETF_SECTOR_PLACEHOLDER = "N/A"


def load_sector_map(csv_path: Path = SECTOR_MAP_CSV) -> dict[str, SectorMapRow]:
    """
    Parse sector_map.csv into {symbol: SectorMapRow}. Raises
    FileNotFoundError if csv_path doesn't exist, ValueError on any row
    that fails SectorMapRow validation (Decision 2/5 enforced at the
    schema level, this function just surfaces which line/symbol failed)
    or on a duplicate symbol.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"sector_map.csv not found: {csv_path}")

    rows: dict[str, SectorMapRow] = {}
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line_num, raw in enumerate(reader, start=2):  # header is line 1
            symbol = raw["symbol"].strip()
            asset_class = raw["asset_class"].strip()
            sector_raw = raw["sector"].strip()
            is_etf = asset_class == ASSET_CLASS_ETF
            sector = None if (is_etf or sector_raw == _ETF_SECTOR_PLACEHOLDER) else sector_raw
            source_note = raw.get("source_note", "").strip()

            if symbol in rows:
                raise ValueError(
                    f"sector_map.csv line {line_num}: duplicate symbol {symbol!r}"
                )
            try:
                rows[symbol] = SectorMapRow(
                    symbol=symbol,
                    sector=sector,
                    asset_class=asset_class,
                    source_note=source_note,
                )
            except Exception as exc:
                raise ValueError(
                    f"sector_map.csv line {line_num} ({symbol}): {exc}"
                ) from exc

    return rows


def verify_full_coverage(
    catalog_tickers: list[str], sector_map: dict[str, SectorMapRow]
) -> None:
    """
    Fails loudly (Decision 2 zero-tolerance) if any catalog symbol has
    no sector_map.csv entry -- the code-level backstop the WO's
    Acceptance Criteria requires. Does NOT check the reverse direction:
    sector_map.csv may legitimately contain more symbols than are in a
    given catalog snapshot (e.g. after a symbol is added to the map
    ahead of its export being run).
    """
    missing = sorted(set(catalog_tickers) - set(sector_map.keys()))
    if missing:
        raise ValueError(
            f"{len(missing)} catalog symbol(s) missing from sector_map.csv "
            f"(Decision 2 zero-tolerance violation): {missing}"
        )
