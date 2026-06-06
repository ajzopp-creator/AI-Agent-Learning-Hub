"""
FILE: archive_pattern_file.py
VERSION: 1.0
DATE: 2026-05-21
AUTHOR: Anthony Zoppi + Claude
LAYER: utilities
DESCRIPTION:
    Post-ingest archive utility for Pipeline A. After add-pattern
    successfully promotes a pattern to the catalog, this utility:
      1. Verifies the XLSX is inside DATA_HISTORICAL_PATTERNS.
      2. Appends the XLSX to the current month's zip in DATA_PROCESSED,
         prefixed with today's date to prevent filename collisions.
      3. Deletes the original XLSX from DATA_HISTORICAL_PATTERNS.

    Called via cli.py archive-pattern --xlsx PATH.

    Safety rules:
      - Will not run if the XLSX is not inside DATA_HISTORICAL_PATTERNS.
      - Verifies the zip entry landed before deleting the source file.
      - If the zip write fails, the source file is NOT deleted.

CHANGELOG:
    - 2026-05-21 v1.0: Initial delivery. Pipeline A equivalent of
      archive_live_file.py. No report-verification step (Pipeline A
      produces no per-pattern reports).
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

from config import DATA_HISTORICAL_PATTERNS, DATA_PROCESSED  # noqa: E402

log = logging.getLogger(__name__)

# Matches: "Pattern_YYYYMMDD_YYYYMMDD_SYMBOL.xlsx" (case-insensitive ext)
# SYMBOL group captures everything after the second date -- covers tickers
# with underscores (e.g. BRK_A).
_PATTERN_FILENAME_RE = re.compile(
    r"^Pattern_\d{8}_\d{8}_(.+)\.xlsx$", re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_symbol(xlsx_path: Path) -> str:
    """Extract ticker from Pattern_YYYYMMDD_YYYYMMDD_SYMBOL.xlsx.

    Raises ValueError if filename does not match the convention.
    """
    m = _PATTERN_FILENAME_RE.match(xlsx_path.name)
    if not m:
        raise ValueError(
            f"Filename does not match Pattern_YYYYMMDD_YYYYMMDD_SYMBOL.xlsx: "
            f"{xlsx_path.name}"
        )
    return m.group(1).upper()


def _monthly_zip(today: date) -> Path:
    """Return DATA_PROCESSED/YYYY-MM.zip for the given date."""
    return DATA_PROCESSED / f"{today.strftime('%Y-%m')}.zip"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_archive(xlsx_path: Path) -> int:
    """Archive one Pattern XLSX after a successful add-pattern run.

    Returns 0 on success, 1 on any failure. Source file is NOT deleted
    unless the zip write and verification both pass.
    """
    xlsx_path = xlsx_path.resolve()

    if not xlsx_path.exists():
        log.error("XLSX not found: %s", xlsx_path)
        return 1

    # Must live inside DATA_HISTORICAL_PATTERNS
    try:
        xlsx_path.relative_to(DATA_HISTORICAL_PATTERNS.resolve())
    except ValueError:
        log.error(
            "XLSX is not inside DATA_HISTORICAL_PATTERNS (%s): %s",
            DATA_HISTORICAL_PATTERNS, xlsx_path,
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
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

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
        log.info("Deleted from historical_patterns: %s", xlsx_path.name)
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
