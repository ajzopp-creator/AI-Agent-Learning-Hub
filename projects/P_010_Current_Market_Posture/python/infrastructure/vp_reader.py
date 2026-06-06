"""
P_010 Market Health -- infrastructure/vp_reader.py

Reads VP grid Excel files for SPY/QQQ, parses into VPDailyRow lists.
Pure IO layer -- no domain logic.

Spec reference: docs/P_010_MarketHealth_Spec_v1_1.md Section 10
                (schema verified 2026-04-25; row 0 is a garbage label row)
"""

from datetime import date
from pathlib import Path

import pandas as pd

from market_health.config import (
    COL_CLOSE,
    COL_DATE,
    COL_HIGH,
    COL_LOW,
    COL_OPEN,
    COL_VOLUME,
    LOOKBACK_DAYS,
    VP_FILES,
)
from market_health.schemas import Ticker, VPDailyRow


REQUIRED_COLUMNS = (COL_DATE, COL_OPEN, COL_HIGH, COL_LOW, COL_CLOSE, COL_VOLUME)


def read_vp_history(
    ticker: Ticker,
    lookback_days: int = LOOKBACK_DAYS,
) -> list[VPDailyRow]:
    """
    Load the trailing `lookback_days` of VP rows for the given ticker.

    Returns rows sorted ascending by trade_date with pct_change and
    volume_up computed against the prior row (first row has both as None).
    """
    path = VP_FILES.get(ticker)
    if path is None:
        raise ValueError(f"Unknown ticker: {ticker}")
    if not path.exists():
        raise FileNotFoundError(f"VP file not found: {path}")

    df = _load_dataframe(path)
    df = _drop_garbage_row(df)
    df = _validate_columns(df, path)
    df = df.sort_values(COL_DATE).reset_index(drop=True)
    df = df.tail(lookback_days).reset_index(drop=True)

    return _to_rows(df)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_dataframe(path: Path) -> pd.DataFrame:
    """Read the Excel file. Pandas handles datetime64 parsing natively."""
    return pd.read_excel(path)


def _drop_garbage_row(df: pd.DataFrame) -> pd.DataFrame:
    """Row 0 of these VP exports is a label row -- NaT date, mostly NaN."""
    if df.empty:
        return df
    if pd.isna(df.iloc[0][COL_DATE]):
        return df.iloc[1:].reset_index(drop=True)
    return df


def _validate_columns(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"VP file {path.name} missing required columns: {missing}"
        )
    return df


def _to_rows(df: pd.DataFrame) -> list[VPDailyRow]:
    rows: list[VPDailyRow] = []
    prior_close: float | None = None
    prior_volume: float | None = None

    for _, r in df.iterrows():
        row_date = _coerce_date(r[COL_DATE])
        close = float(r[COL_CLOSE])
        volume = float(r[COL_VOLUME])

        pct_change = None
        volume_up = None
        if prior_close is not None and prior_close != 0:
            pct_change = ((close - prior_close) / prior_close) * 100.0
        if prior_volume is not None:
            volume_up = volume > prior_volume

        rows.append(
            VPDailyRow(
                trade_date=row_date,
                open=float(r[COL_OPEN]),
                high=float(r[COL_HIGH]),
                low=float(r[COL_LOW]),
                close=close,
                volume=volume,
                pct_change=pct_change,
                volume_up=volume_up,
            )
        )
        prior_close = close
        prior_volume = volume

    return rows


def _coerce_date(value: object) -> date:
    """VP Date column is datetime64[us]; pandas yields Timestamp."""
    if isinstance(value, pd.Timestamp):
        return value.date()
    if isinstance(value, date):
        return value
    return pd.Timestamp(value).date()
