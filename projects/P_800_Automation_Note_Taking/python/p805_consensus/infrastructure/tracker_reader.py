"""tracker_reader.py -- reads the live P_115/P_118 Tracker Log worksheet."""

from __future__ import annotations

import logging

import pandas as pd

from p805_consensus.config import (
    TRACKER_DATE_COL,
    TRACKER_PATH,
    TRACKER_SHEET_NAME,
    TRACKER_SYMBOL_COL,
    TRACKER_VERDICT_COL,
)
from p805_consensus.schemas import TrackerRow

logger = logging.getLogger(__name__)


def read_tracker_rows() -> list[TrackerRow]:
    """Read Date/Symbol/Step1Verdict from the live Tracker Log sheet."""
    if not TRACKER_PATH.exists():
        raise FileNotFoundError(f"Tracker workbook not found: {TRACKER_PATH}")

    logger.info("Reading Tracker Log from %s", TRACKER_PATH)
    frame = pd.read_excel(TRACKER_PATH, sheet_name=TRACKER_SHEET_NAME)

    rows: list[TrackerRow] = []
    for _, record in frame.iterrows():
        raw_date = record.get(TRACKER_DATE_COL)
        raw_symbol = record.get(TRACKER_SYMBOL_COL)
        if pd.isna(raw_date) or pd.isna(raw_symbol):
            continue
        raw_verdict = record.get(TRACKER_VERDICT_COL)
        verdict = "" if pd.isna(raw_verdict) else str(raw_verdict)
        try:
            rows.append(
                TrackerRow(
                    date=raw_date, symbol=str(raw_symbol), step1_verdict=verdict
                )
            )
        except ValueError as exc:
            logger.warning(
                "Skipping bad Tracker row (%s, %s): %s", raw_date, raw_symbol, exc
            )
    return rows