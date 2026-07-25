"""
FILE: archive_scanner_file.py
VERSION: 1.0
DATE: 2026-07-12
AUTHOR: Anthony Zoppi + Claude
LAYER: utilities
DESCRIPTION:
    Post-scan archive utility for the Scanner Loop (WO-P300-E3.001).
    After scanner_loop.py finishes detection on one nightly-export
    file -- STRICT hit or not -- this utility:
      1. Verifies the XLSX is inside DATA_BULK_NIGHTLY_SCAN.
      2. Appends the XLSX to the current month's zip in
         SCANNER_ARCHIVE_DIR (E:\\ external backup drive), prefixed
         with today's date to prevent filename collisions.
      3. Deletes the original XLSX from DATA_BULK_NIGHTLY_SCAN.

    Mirrors utilities/archive_pattern_file.py's proven safety pattern
    (Pipeline A's archiver) -- append -> verify entry landed -> only
    then delete source. Two differences from that file: filename
    convention (bulk shape, not Pipeline A's Pattern_YYYYMMDD_YYYYMMDD_
    SYMBOL.xlsx) and archive target (E:\\ external drive with a
    month-suffixed zip name, not DATA_PROCESSED's YYYY-MM.zip).

    Called from application/scanner_loop.py once per processed file,
    unconditionally (every file archives regardless of detection
    outcome -- Tony's explicit correction to the original "no
    archiving" draft, 2026-07-12).

    Safety rules:
      - Will not run if the XLSX is not inside DATA_BULK_NIGHTLY_SCAN.
      - Verifies the zip entry landed before deleting the source file.
      - If the zip write fails, the source file is NOT deleted.

CHANGELOG:
    - 2026-07-12 v1.0: Initial delivery. WO-P300-E3.001 file #1 of 5.
"""
from __future__ import annotations

import logging
import re
import sys
import zipfile
from datetime import date
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import (  # noqa: E402
    DATA_BULK_NIGHTLY_SCAN,
    SCANNER_ARCHIVE_BASENAME,
    SCANNER_ARCHIVE_DIR,
)

log = logging.getLogger(__name__)

# Matches: "<years>[I]_Pattern_<SYMBOL>.xlsx" (case-insensitive ext).
# Same convention as bulk_grid_reader.py's _parse_filename -- SYMBOL
# group captures everything after "_Pattern_" so tickers with
# underscores (e.g. BRK_A) still parse correctly.
_BULK_FILENAME_RE = re.compile(
    r"^\d+I?_Pattern_(.+)\.xlsx$", re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_symbol(xlsx_path: Path) -> str:
    """Extract ticker from <years>[I]_Pattern_<SYMBOL>.xlsx.

    Raises ValueError if filename does not match the convention.
    """
    m = _BULK_FILENAME_RE.match(xlsx_path.name)
    if not m:
        raise ValueError(
            f"Filename does not match <years>[I]_Pattern_<SYMBOL>.xlsx: "
            f"{xlsx_path.name}"
        )
    return m.group(1).upper()


def _monthly_zip(today: date) -> Path:
    """Return SCANNER_ARCHIVE_DIR/<basename><MMMYY>.zip for the given
    date, e.g. 10_Pattern_BulkCreateJul26.zip."""
    return SCANNER_ARCHIVE_DIR / f"{SCANNER_ARCHIVE_BASENAME}{today.strftime('%b%y')}.zip"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_archive(xlsx_path: Path) -> int:
    """Archive one scanner XLSX after processing (hit or not).

    Returns 0 on success, 1 on any failure. Source file is NOT deleted
    unless the zip write and verification both pass.
    """
    xlsx_path = xlsx_path.resolve()

    if not xlsx_path.exists():
        log.error("XLSX not found: %s", xlsx_path)
        return 1

    # Must live inside DATA_BULK_NIGHTLY_SCAN
    try:
        xlsx_path.relative_to(DATA_BULK_NIGHTLY_SCAN.resolve())
    except ValueError:
        log.error(
            "XLSX is not inside DATA_BULK_NIGHTLY_SCAN (%s): %s",
            DATA_BULK_NIGHTLY_SCAN, xlsx_path,
        )
        return 1

    # Extract symbol from filename
    try:
        symbol = _parse_symbol(xlsx_path)
    except ValueError as exc:
        log.error("%s", exc)
        return 1

    # Build zip path and entry name
    today = date.today()
    zip_path = _monthly_zip(today)
    entry_name = f"{today.strftime('%Y%m%d')}_{xlsx_path.name}"
    SCANNER_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Append to (or create) monthly zip
    try:
        with zipfile.ZipFile(
            zip_path, mode="a", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            if entry_name in zf.namelist():
                log.warning(
                    "Entry already in zip: %s -- skipping write", entry_name
                )
            else:
                zf.write(xlsx_path, arcname=entry_name)
                log.info("Added to zip: %s", entry_name)
    except Exception as exc:
        log.error("Zip write failed (%s): %s", zip_path, exc)
        return 1

    # Verify entry landed before touching source
    try:
        with zipfile.ZipFile(zip_path, mode="r") as zf:
            if entry_name not in zf.namelist():
                log.error(
                    "Zip verification failed -- entry not found: %s", entry_name
                )
                return 1
    except Exception as exc:
        log.error("Zip verification error: %s", exc)
        return 1

    # Safe to delete source
    try:
        xlsx_path.unlink()
        log.info("Deleted from nightly_scan: %s", xlsx_path.name)
    except Exception as exc:
        log.error(
            "Zip written but delete failed: %s -- remove manually", exc
        )
        return 1

    print(f"ARCHIVE OK  -- {xlsx_path.name}")
    print(f"  zip  : {zip_path}")
    print(f"  entry: {entry_name}")
    print(f"  symbol: {symbol}")
    return 0
