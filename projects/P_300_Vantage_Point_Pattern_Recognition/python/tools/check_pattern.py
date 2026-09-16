"""
FILE: check_pattern.py
VERSION: 1.0
DATE: 2026-07-25
AUTHOR: Anthony Zoppi + Claude
LAYER: utilities
DESCRIPTION:
    Read-only pre-export duplicate check (WO-P300-E5.003). Answers one
    question before Tony spends a manual VP export + bulk-ingest cycle
    on a symbol: is this already in the catalog?

    Two modes:
        1. Default (no --symbol): scans config.DATA_LIVE (data\\live\\)
           for "History Grid (SYMBOL).xlsx" files -- the files Tony's
           manual process already drops there -- extracts each ticker,
           dedupes, and reports catalog status per symbol. Files that
           don't match the naming pattern (e.g. the IntelliScan eval-
           parameters grid, Excel lock files) are counted and named
           once, not silently dropped.
        2. --symbol override: explicit comma-separated ticker list,
           bypasses the directory scan entirely -- for an ad-hoc check
           with nothing exported yet.

    Reuses, does not re-derive (M-082):
        - infrastructure.vp_xlsx_reader._parse_live_filename() for the
          "History Grid (SYMBOL).xlsx" regex -- same parser Pipeline B
          already trusts for the real live-file read.
        - infrastructure.catalog_writer.get_anchor_dates_for_ticker()
          for the catalog lookup -- same exact-match join as
          pattern_exists_for_ticker_anchor(), no new query logic.

    Read-only against the active catalog (resolved via
    utilities.db_utils.get_latest_catalog). No writes, no migrations.

    Usage:
        python cli.py check-pattern
        python cli.py check-pattern --symbol AAPL
        python cli.py check-pattern --symbol AAPL,MSFT,TSLA
        python cli.py check-pattern --catalog PATH

CHANGELOG:
    - 2026-07-25 v1.0: WO-P300-E5.003 build. Directory-scan default
      mode chosen over a required --symbol flag per Tony's explicit
      description of his manual workflow (export to data/live/ first,
      then check before deciding whether to bulk-export a pattern).
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import DATA_LIVE, LOG_FORMAT  # noqa: E402
from infrastructure.vp_xlsx_reader import _parse_live_filename  # noqa: E402
from infrastructure.catalog_writer import get_anchor_dates_for_ticker  # noqa: E402
from utilities.db_connect import connection_context  # noqa: E402
from utilities.db_utils import get_latest_catalog  # noqa: E402

logger = logging.getLogger(__name__)

_BAR = "=" * 76


# ─────────────────────────────────────────────────────────────────────────────
# Symbol resolution
# ─────────────────────────────────────────────────────────────────────────────

def _symbols_from_arg(raw: str) -> list[str]:
    """Parse a comma-separated --symbol value into a deduped, uppercased
    ticker list, order preserved."""
    seen: dict[str, None] = {}
    for piece in raw.split(","):
        ticker = piece.strip().upper()
        if ticker:
            seen[ticker] = None
    return list(seen.keys())


def _symbols_from_live_dir(live_dir: Path) -> tuple[list[str], int]:
    """Scan live_dir for 'History Grid (SYMBOL).xlsx' files. Returns
    (deduped ticker list order-preserved, count of files that didn't
    match the pattern -- reported, not silently dropped)."""
    if not live_dir.exists():
        return [], 0
    seen: dict[str, None] = {}
    skipped = 0
    for f in sorted(live_dir.iterdir()):
        if not f.is_file():
            continue
        try:
            ticker = _parse_live_filename(f.name)
        except ValueError:
            skipped += 1
            continue
        seen[ticker] = None
    return list(seen.keys()), skipped


# ─────────────────────────────────────────────────────────────────────────────
# Public entrypoint
# ─────────────────────────────────────────────────────────────────────────────

def run_check(
    symbol_arg: str | None = None,
    catalog_path: Path | None = None,
    live_dir: Path | None = None,
) -> int:
    """Report catalog status per symbol. Returns 0 always (informational
    tool, not a gate) -- 1 only if the catalog itself can't be opened.
    """
    live_dir = live_dir if live_dir is not None else DATA_LIVE
    skipped = 0
    if symbol_arg:
        tickers = _symbols_from_arg(symbol_arg)
        source_note = f"--symbol ({len(tickers)} given)"
    else:
        tickers, skipped = _symbols_from_live_dir(live_dir)
        source_note = f"scanned {live_dir}"

    if catalog_path is None:
        catalog_path = Path(get_latest_catalog())
    if not catalog_path.exists():
        print(f"FATAL: catalog not found: {catalog_path}")
        return 1

    print()
    print(_BAR)
    print(f"P_300 Pre-Export Pattern Check — {source_note}")
    print(f"Catalog: {catalog_path.name}")
    print(_BAR)

    if not tickers:
        print("No symbols to check.")
        if skipped:
            print(
                f"({skipped} file(s) in {live_dir} did not match "
                f"'History Grid (SYMBOL).xlsx' — skipped)"
            )
        print(_BAR)
        print()
        return 0

    with connection_context(catalog_path=str(catalog_path)) as conn:
        for ticker in tickers:
            dates = get_anchor_dates_for_ticker(conn, ticker)
            if dates:
                print(f"{ticker}: {len(dates)} pattern(s) already captured")
                print(f"  {', '.join(dates)}")
            else:
                print(f"{ticker}: not in catalog — clear to export")

    if skipped:
        print(_BAR)
        print(
            f"{skipped} file(s) in {live_dir} did not match "
            f"'History Grid (SYMBOL).xlsx' — skipped"
        )
    print(_BAR)
    print()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pre-export duplicate check against the live catalog."
    )
    parser.add_argument(
        "--symbol", default=None,
        help="Comma-separated ticker(s), e.g. AAPL or AAPL,MSFT. "
             "Omit to scan data/live/ instead.",
    )
    parser.add_argument(
        "--catalog", default=None,
        help="Catalog path override; defaults to db_utils.get_latest_catalog().",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT, stream=sys.stdout)
    catalog = Path(args.catalog) if args.catalog else None
    sys.exit(run_check(args.symbol, catalog))
