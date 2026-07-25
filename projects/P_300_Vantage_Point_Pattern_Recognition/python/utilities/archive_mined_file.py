"""
FILE: archive_mined_file.py
VERSION: 1.0
DATE: 2026-07-14
AUTHOR: Anthony Zoppi + Claude
LAYER: utilities
DESCRIPTION:
    Post-ingest archive utility for the Outcome-First Pattern Miner
    (WO-P300-E3.002) / "BulkAddPattern" process. After ingest-mined
    successfully processes a symbol's bulk file (audit gate + staging
    insert + M-079 eval, all already complete by the time this runs),
    this utility:
      1. Verifies the XLSX is inside DATA_BULK_MINE.
      2. Appends the XLSX to the current month's zip in MINE_ARCHIVE_DIR
         (E:\\ external backup drive) -- NO rename/date-prefix on the
         entry itself (Tony's explicit call, 2026-07-14: unlike
         archive_scanner_file.py's date-prefixed entries, these files
         don't need per-entry disambiguation).
      3. Deletes the original XLSX from DATA_BULK_MINE.

    Mirrors utilities/archive_scanner_file.py's proven safety pattern
    (append -> verify entry landed -> only then delete source) almost
    exactly. Two deliberate differences from that file:
      - No entry rename (arcname = xlsx_path.name, not date-prefixed).
      - Zip naming is DATE-FIRST: <MMMYY>BULKPattern.zip (e.g.
        Jul26BULKPattern.zip), not basename-first like Scanner Loop's
        10_Pattern_BulkCreate<MMMYY>.zip -- Tony's explicit convention
        for this stream, same E:\\ drive, separate named constant
        (MINE_ARCHIVE_DIR) so the two archives stay independently
        configurable even though they point at the same physical drive
        today.

    Called from P_300_RunBulkAddPattern.ps1 once per file remaining in
    DATA_BULK_MINE after a successful ingest-mined run -- unconditional,
    same posture as Scanner Loop's archiver (every file that was part of
    the batch archives, not just ones with successful inserts; a file
    with 0 inserts this run may still produce candidates on a future
    re-mine once its symbol trades more bars, but the ARCHIVE step here
    only runs after the whole batch's ingest-mined call has already
    succeeded, so "was in the batch" and "is safe to archive" are the
    same condition for this WO -- unlike Pipeline A, mined files are
    NOT single-shot: re-mining an archived-and-deleted symbol later
    requires re-exporting from VP, a known, accepted tradeoff (Tony's
    call, 2026-07-14) rather than keeping every file on local disk
    forever.

    Safety rules:
      - Will not run if the XLSX is not inside DATA_BULK_MINE.
      - Verifies the zip entry landed before deleting the source file.
      - If the zip write fails, the source file is NOT deleted.

CHANGELOG:
    - 2026-07-14 v1.0: Initial delivery. "BulkAddPattern" process, file #1 of 4.
"""
from __future__ import annotations

import logging
import sys
import zipfile
from datetime import date
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import DATA_BULK_MINE, MINE_ARCHIVE_DIR, MINE_ARCHIVE_SUFFIX  # noqa: E402

log = logging.getLogger(__name__)


def _monthly_zip(today: date) -> Path:
    """Return MINE_ARCHIVE_DIR/<MMMYY><suffix>.zip for the given date,
    e.g. Jul26BULKPattern.zip -- date-first, unlike Scanner Loop's
    basename-first convention."""
    return MINE_ARCHIVE_DIR / f"{today.strftime('%b%y')}{MINE_ARCHIVE_SUFFIX}.zip"


def run_archive(xlsx_path: Path) -> int:
    """Archive one mined-corpus XLSX after a successful ingest-mined run.

    Returns 0 on success, 1 on any failure. Source file is NOT deleted
    unless the zip write and verification both pass.
    """
    xlsx_path = xlsx_path.resolve()

    if not xlsx_path.exists():
        log.error("XLSX not found: %s", xlsx_path)
        return 1

    # Must live inside DATA_BULK_MINE
    try:
        xlsx_path.relative_to(DATA_BULK_MINE.resolve())
    except ValueError:
        log.error(
            "XLSX is not inside DATA_BULK_MINE (%s): %s",
            DATA_BULK_MINE, xlsx_path,
        )
        return 1

    today = date.today()
    zip_path = _monthly_zip(today)
    entry_name = xlsx_path.name  # no rename -- Tony's explicit call
    MINE_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

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
        log.info("Deleted from data/bulk/mine: %s", xlsx_path.name)
    except Exception as exc:
        log.error(
            "Zip written but delete failed: %s -- remove manually", exc
        )
        return 1

    print(f"ARCHIVE OK  -- {xlsx_path.name}")
    print(f"  zip  : {zip_path}")
    print(f"  entry: {entry_name}")
    return 0
