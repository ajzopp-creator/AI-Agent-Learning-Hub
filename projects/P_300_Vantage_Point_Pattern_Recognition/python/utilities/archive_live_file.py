"""
FILE: archive_live_file.py
VERSION: 1.1
DATE: 2026-05-20
AUTHOR: Anthony Zoppi + Claude
LAYER: utilities
DESCRIPTION:
    Post-eval archive utility for Pipeline B. After daily-evaluate writes
    a report, this utility:
      1. Verifies a matching report exists in REPORTS_DIR for the symbol.
      2. Appends the XLSX to the current month's zip in DATA_PROCESSED,
         prefixed with today's date to prevent same-symbol collisions
         within a month.
      3. Deletes the original XLSX from DATA_LIVE.

    Called via cli.py archive-eval --xlsx PATH.

    Safety rules:
      - Will not run if the XLSX is not inside DATA_LIVE.
      - Will not run if no report exists for the symbol in REPORTS_DIR.
      - Verifies the zip entry landed before deleting the source file.
      - If the zip write fails, the source file is NOT deleted.

CHANGELOG:
    - 2026-05-20 v1.1: Fixed _find_report glob. Actual report filename
      format is report_<SYMBOL>_<date>_<timestamp>.txt; v1.0 glob
      "*_SYMBOL.txt" expected symbol at the end and matched nothing.
      Corrected to "report_<SYMBOL>_*.txt". Caught on first live run
      (OLED 2026-05-20).
    - 2026-05-20 v1.0: Initial delivery. Per plan approved 2026-05-20.
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

from config import DATA_LIVE, DATA_PROCESSED, REPORTS_DIR  # noqa: E402

log = logging.getLogger(__name__)

# Matches: "History Grid (SYMBOL).xlsx" (case-insensitive extension)
_LIVE_FILENAME_RE = re.compile(r"^History Grid \((.+)\)\.xlsx$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_symbol(xlsx_path: Path) -> str:
    """Extract ticker from 'History Grid (SYMBOL).xlsx'. Raises ValueError."""
    m = _LIVE_FILENAME_RE.match(xlsx_path.name)
    if not m:
        raise ValueError(
            f"Filename does not match 'History Grid (SYMBOL).xlsx': {xlsx_path.name}"
        )
    return m.group(1).upper()


def _find_report(symbol: str) -> Path | None:
    """Return the most recent report_<SYMBOL>_*.txt in REPORTS_DIR, or None."""
    if not REPORTS_DIR.exists():
        return None
    matches = sorted(REPORTS_DIR.glob(f"report_{symbol}_*.txt"))
    return matches[-1] if matches else None


def _monthly_zip(today: date) -> Path:
    """Return DATA_PROCESSED/YYYY-MM.zip for the given date."""
    return DATA_PROCESSED / f"{today.strftime('%Y-%m')}.zip"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_archive(xlsx_path: Path) -> int:
    """
    Archive one live eval XLSX after a successful daily-evaluate run.

    Returns 0 on success, 1 on any failure. Source file is NOT deleted
    unless the zip write and verification both pass.
    """
    xlsx_path = xlsx_path.resolve()

    if not xlsx_path.exists():
        log.error("XLSX not found: %s", xlsx_path)
        return 1

    # Must live inside DATA_LIVE
    try:
        xlsx_path.relative_to(DATA_LIVE.resolve())
    except ValueError:
        log.error(
            "XLSX is not inside DATA_LIVE (%s): %s", DATA_LIVE, xlsx_path
        )
        return 1

    # Extract symbol from filename
    try:
        symbol = _parse_symbol(xlsx_path)
    except ValueError as exc:
        log.error("%s", exc)
        return 1

    # Require a report to exist before archiving
    report = _find_report(symbol)
    if report is None:
        log.error(
            "No report found for %s in %s -- run daily-evaluate first",
            symbol, REPORTS_DIR,
        )
        return 1
    log.info("Report verified: %s", report.name)

    # Build zip path and entry name
    today = date.today()
    zip_path = _monthly_zip(today)
    entry_name = f"{today.strftime('%Y%m%d')}_{xlsx_path.name}"
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    # Append to (or create) monthly zip
    try:
        with zipfile.ZipFile(zip_path, mode="a", compression=zipfile.ZIP_DEFLATED) as zf:
            if entry_name in zf.namelist():
                log.warning("Entry already in zip: %s -- skipping write", entry_name)
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
                log.error("Zip verification failed -- entry not found: %s", entry_name)
                return 1
    except Exception as exc:
        log.error("Zip verification error: %s", exc)
        return 1

    # Safe to delete source
    try:
        xlsx_path.unlink()
        log.info("Deleted from live: %s", xlsx_path.name)
    except Exception as exc:
        log.error("Zip written but delete failed: %s -- remove manually", exc)
        return 1

    print(f"ARCHIVE OK  -- {xlsx_path.name}")
    print(f"  zip  : {zip_path}")
    print(f"  entry: {entry_name}")
    print(f"  report verified: {report.name}")
    return 0
