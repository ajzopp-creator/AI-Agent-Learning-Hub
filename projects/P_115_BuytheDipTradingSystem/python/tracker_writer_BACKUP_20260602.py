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

# ---------------------------------------------------------------------------
# Resolve shared_resources on sys.path so vault_interface is importable
# ---------------------------------------------------------------------------
_HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
_SHARED = _HUB_ROOT / "shared_resources" / "python_utils"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from vault_interface import write_to_vault  # noqa: E402

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
# Infrastructure: read tracker rows
# ---------------------------------------------------------------------------

def _normalize_value(value: Any) -> Any:
    """Convert Excel cell types to vault-friendly Python types."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if value == "--" or value == "":
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