"""tracker_writer.py -- P_115 vault export.

Reads every data row from the Excel tracker, normalizes each row to
P115Record field names, and calls write_to_vault() for each row.

Usage:
    python tracker_writer.py

Rows missing signal_date or symbol are skipped and logged.
All other rows are written with overwrite=True per work-order spec.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Any

import openpyxl

# Hub interface -- the ONLY import path for cross-project vault writes (M-038).
# Resolves via the hub_shared editable install (WO-P000-E2.002); no sys.path
# side-channel required (WO-P000-E2.003).
from shared_resources.python_utils.vault_interface import write_to_vault

# Local config
sys.path.insert(0, str(Path(__file__).parent))
from config import TRACKER_PATH, VAULT_SCHEMA, WRITTEN_BY, REQUIRED_FIELDS, COLUMN_MAP  # noqa: E402

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Verdict normalization: tracker has mixed-case variants; vault expects exact
# ---------------------------------------------------------------------------
_VERDICT_NORM: dict[str, str] = {
    "buy":        "BUY",
    "asym":       "ASYM",
    "pass":       "PASS",
    "no signal":  "PASS",
    "no":         "PASS",
}

def _normalize_verdict(raw: Any) -> str | None:
    """Uppercase-normalize step1_verdict to BUY | ASYM | PASS."""
    if raw is None:
        return None
    return _VERDICT_NORM.get(str(raw).strip().lower(), str(raw).strip().upper())


# ---------------------------------------------------------------------------
# Infrastructure: read tracker rows
# ---------------------------------------------------------------------------

# Sentinel strings that mean "no value" in the tracker
_NULL_STRINGS = frozenset({"--", "-", "n/a", "na", "none", ""})


def _normalize_value(value: Any) -> Any:
    """Convert Excel cell types to vault-friendly Python types.

    - datetime/date   -> ISO string
    - dash/empty/null -> None  (handles em-dash, en-dash, regular dash variants)
    - everything else -> unchanged
    """
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if value is None:
        return None
    # Strip whitespace and check against null sentinel set
    # Also catch Unicode dash variants: em-dash U+2014, en-dash U+2013
    cleaned = str(value).strip().replace("\u2014", "--").replace("\u2013", "--")
    if cleaned.lower() in _NULL_STRINGS:
        return None
    return value


def load_tracker_rows() -> list[dict[str, Any]]:
    """Read all data rows from the Excel tracker.

    Returns:
        List of dicts keyed by snake_case P115Record field names.
    """
    log.info("Opening tracker: %s", TRACKER_PATH)
    wb = openpyxl.load_workbook(TRACKER_PATH, read_only=True, data_only=True)
    ws = wb.active

    rows_iter = ws.iter_rows(values_only=True)
    raw_headers = next(rows_iter, None)
    if raw_headers is None:
        log.error("Tracker sheet is empty -- no headers found.")
        wb.close()
        return []

    # Build index: col position --> snake_case field name (skip unmapped cols)
    col_index: dict[int, str] = {}
    for i, h in enumerate(raw_headers):
        field = COLUMN_MAP.get(str(h).strip() if h else "")
        if field:
            col_index[i] = field

    log.info("Mapped %d of %d header columns.", len(col_index), len(raw_headers))

    records: list[dict[str, Any]] = []
    for row in rows_iter:
        record: dict[str, Any] = {}
        for i, field in col_index.items():
            raw = row[i] if i < len(row) else None
            record[field] = _normalize_value(raw)
        # Normalize verdict after all fields are set
        if "step1_verdict" in record:
            record["step1_verdict"] = _normalize_verdict(record["step1_verdict"])
        records.append(record)

    wb.close()
    log.info("Loaded %d data rows from tracker.", len(records))
    return records


# ---------------------------------------------------------------------------
# Domain: validate row
# ---------------------------------------------------------------------------

def is_valid_row(record: dict[str, Any]) -> bool:
    """Return True if row has all required fields populated."""
    for field in REQUIRED_FIELDS:
        if not record.get(field):
            return False
    return True


# ---------------------------------------------------------------------------
# Application: orchestrate
# ---------------------------------------------------------------------------

def run() -> None:
    """Main entry point: load rows, validate, write to vault."""
    records = load_tracker_rows()
    if not records:
        log.warning("No rows loaded -- nothing to write.")
        return

    written = 0
    skipped = 0

    for record in records:
        if not is_valid_row(record):
            symbol = record.get("symbol") or "(no symbol)"
            date_val = record.get("signal_date") or "(no date)"
            log.warning("Skipped row -- missing required field: symbol=%s date=%s", symbol, date_val)
            skipped += 1
            continue

        # Inject provenance fields required by Note Standard v1.1
        record["written_by"] = WRITTEN_BY

        try:
            write_to_vault(
                schema_name=VAULT_SCHEMA,
                data=record,
                overwrite=True,
            )
            written += 1
        except (ValueError, OSError) as exc:
            log.error(
                "Vault write failed: symbol=%s date=%s error=%s",
                record.get("symbol"),
                record.get("signal_date"),
                exc,
            )
            skipped += 1

    log.info("Done. Written: %d  Skipped: %d  Total: %d", written, skipped, len(records))


if __name__ == "__main__":
    run()