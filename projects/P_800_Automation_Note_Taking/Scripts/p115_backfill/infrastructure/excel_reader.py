"""excel_reader.py — reads P_115 tracker rows from the xlsx file.

Yields one dict per data row, keyed by Excel column header names.
Completely empty rows are skipped automatically.

Uses pandas instead of openpyxl directly — handles stale worksheet
dimension metadata that causes openpyxl to stop early.

NOTE: File must be closed in Excel before running.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

import pandas as pd

log = logging.getLogger(__name__)

_EMPTY_STRINGS = {"", "--", "n/a", "null", "none"}

_DATE_FORMATS = (
    "%Y-%m-%d %H:%M:%S",   # pandas Timestamp str: 2026-04-15 00:00:00
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%m-%d-%Y",
    "%Y/%m/%d",
)


def _normalize_date(value: Any) -> str | None:
    """Convert a pandas date/timestamp/string to ISO string YYYY-MM-DD."""
    if value is None:
        return None
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    raw = str(value).strip()
    if not raw or raw.lower() in _EMPTY_STRINGS or raw == "nan":
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    log.warning("Unrecognized date format — keeping raw: %s", raw)
    return raw


def _normalize_cell(value: Any) -> Any:
    """Normalize a cell value — strip strings, convert blanks to None.

    Booleans are coerced to 'Y'/'N'. pandas NaN/NaT become None.
    """
    if value is None:
        return None
    if isinstance(value, float) and str(value) == "nan":
        return None
    if isinstance(value, bool):
        return "Y" if value else "N"
    if isinstance(value, str):
        stripped = value.strip()
        return None if stripped.lower() in _EMPTY_STRINGS else stripped
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return value


def read_rows(
    path: Path,
    sheet_name: str | None,
    header_row: int,
) -> Generator[dict[str, Any], None, None]:
    """Yield one dict per data row from the Excel tracker.

    Args:
        path: Full path to the .xlsx file.
        sheet_name: Sheet tab name, or None for first sheet.
        header_row: 1-indexed row number containing column headers.

    Yields:
        Dict mapping Excel column header → cell value (normalized).
    """
    log.info("Opening tracker: %s", path)

    sheet = 0 if sheet_name is None else sheet_name

    df = pd.read_excel(
        path,
        sheet_name=sheet,
        header=header_row - 1,
        dtype=str,
        engine="openpyxl",
        keep_default_na=False,
        na_values=list(_EMPTY_STRINGS),
    )

    log.info(
        "pandas loaded %d rows x %d columns from sheet '%s'",
        len(df), len(df.columns), sheet,
    )

    row_count = 0
    for _, pandas_row in df.iterrows():
        row_dict: dict[str, Any] = {}

        for col in df.columns:
            raw = pandas_row[col]
            if isinstance(raw, float) and str(raw) == "nan":
                row_dict[col] = None
            else:
                row_dict[col] = _normalize_cell(raw)

        if all(v is None for v in row_dict.values()):
            continue

        if "Date" in row_dict:
            row_dict["Date"] = _normalize_date(row_dict["Date"])

        row_count += 1
        yield row_dict

    log.info("Finished reading — %d data rows yielded", row_count)
