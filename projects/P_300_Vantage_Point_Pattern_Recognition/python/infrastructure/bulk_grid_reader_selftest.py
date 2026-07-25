"""
FILE: infrastructure/bulk_grid_reader_selftest.py
VERSION: 1.0
DATE: 2026-07-08
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Standalone CLI smoke test for bulk_grid_reader.parse_bulk_file().
    Split out of bulk_grid_reader.py v1.1 to keep that file under the
    300-line hard limit after the infinity-value fix. Not part of the
    reader's public API -- operator-run diagnostic only, same role as
    vp_xlsx_reader.py's inline _selftest but as its own file since the
    bulk reader plus this test together would exceed the limit combined.

CHANGELOG:
    - 2026-07-08 v1.0: Initial release, extracted from
      bulk_grid_reader.py v1.0's inline _selftest/argparse block.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import LOG_FORMAT, LOG_LEVEL  # noqa: E402
from infrastructure.bulk_grid_reader import parse_bulk_file  # noqa: E402


def selftest(xlsx_path_str: str) -> int:
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, stream=sys.stdout)
    xlsx_path = Path(xlsx_path_str)
    try:
        parse = parse_bulk_file(xlsx_path)
    except Exception as e:
        print(f"\nPARSE FAILED: {type(e).__name__}: {e}")
        return 1

    md = parse.metadata
    print(f"\nFile:     {md.filename}")
    print(f"Symbol:   {md.symbol}")
    print(f"Window:   {md.window_years}yr  IntelliScan: {md.is_intelliscan_export}")
    print(
        f"Bars:     {len(parse.bars)} "
        f"(file range {parse.bars[0].bar_date} -> {parse.bars[-1].bar_date})"
    )
    print("\nFirst 3 bars:")
    for b in parse.bars[:3]:
        print(
            f"  {b.bar_date}  C={b.close:7.2f}  neural={b.neural_index:>7}  "
            f"tc_short={b.tc_short:7.2f}  tc_medium={b.tc_medium:7.2f}"
        )
    print("\nLast 3 bars:")
    for b in parse.bars[-3:]:
        print(
            f"  {b.bar_date}  C={b.close:7.2f}  neural={b.neural_index:>7}  "
            f"tc_short={b.tc_short:7.2f}  tc_medium={b.tc_medium:7.2f}"
        )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse one bulk Pattern XLSX as a self-test."
    )
    parser.add_argument("--xlsx", required=True)
    args = parser.parse_args()
    sys.exit(selftest(args.xlsx))
