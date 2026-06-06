"""
FILE: domain/labeler.py
VERSION: 1.0
DATE: 2026-05-14
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Pure-Python computation of forward labels for pattern outcomes.
    Takes a sorted bar list and an anchor date; returns one ForwardLabel
    per horizon defined in config.FORWARD_HORIZONS (5/7/10/15/20 trading
    days). No I/O, no DB, no print — strictly testable in isolation.

    Convention:
      - return_pct stored as fractional RATIO, not percentage.
        Example: 0.0436 means +4.36%. Multiply by 100 for display.
        Matches architecture §9.3 normalization columns which also use
        ratios despite the "_pct" suffix.
      - is_profitable = (return_pct > 0). Zero-return bars (rare, exact
        ties) are NOT profitable. Threshold can be raised later if a
        minimum profitable return is needed.
      - future_date is taken from the actual bar at +horizon trading days.
        Trading days, not calendar days — the bar list IS the trading
        calendar.

    LAUNCH framing: anchor_date = trend launch date. Forward labels
    measure the move itself plus what comes after.
    PEAK framing: anchor_date = trend completion date. Forward labels
    measure the post-completion drift.
    Either works; same function, different anchor_date.

CHANGELOG:
    - 2026-05-14 v1.0: Initial Stage 4 POC release. Closes the labeler
      slot in the file plan. Verified against the OII Pattern #1 hand
      computation (+4.36% / +5.95% / +15.23% / +11.42% / +0.98% at
      LAUNCH anchor 11/20/2025).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

# Bootstrap sys.path for standalone testing; cli.py entry points
# set PYTHONPATH instead.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import FORWARD_HORIZONS  # noqa: E402
from schemas import VPBarRaw  # noqa: E402


@dataclass(frozen=True)
class ForwardLabel:
    """
    In-memory intermediate. Mirrors ForwardLabelRecord without the PK.
    catalog_writer.py converts these into ForwardLabelRecord at persistence.
    """
    horizon_days: int
    future_date: date
    return_pct: float       # stored as ratio (0.0436 == +4.36%)
    is_profitable: bool


def find_anchor_index(bars: list[VPBarRaw], anchor_date: date) -> int:
    """
    Locate anchor_date in an ascending-sorted bar list. Raises ValueError
    if not present — anchor must be a real trading bar, not interpolated.
    """
    for i, b in enumerate(bars):
        if b.bar_date == anchor_date:
            return i
    raise ValueError(
        f"anchor_date {anchor_date} not found in bars "
        f"(range: {bars[0].bar_date} to {bars[-1].bar_date}, count: {len(bars)})"
    )


def compute_forward_labels(
    bars: list[VPBarRaw],
    anchor_date: date,
    horizons: tuple[int, ...] = FORWARD_HORIZONS,
) -> list[ForwardLabel]:
    """
    Compute forward labels at every horizon in `horizons` (default: the
    architecture-defined 5/7/10/15/20).

    bars must be sorted ascending by date and contain at least max(horizons)
    trading bars AFTER anchor_date. Raises ValueError on either condition.

    Returns one ForwardLabel per horizon, in the order of `horizons`.
    """
    if not bars:
        raise ValueError("compute_forward_labels requires at least one bar")
    if not horizons:
        raise ValueError("horizons tuple is empty")

    anchor_idx = find_anchor_index(bars, anchor_date)
    anchor_close = bars[anchor_idx].close

    max_horizon = max(horizons)
    bars_after_anchor = len(bars) - 1 - anchor_idx
    if bars_after_anchor < max_horizon:
        raise ValueError(
            f"insufficient forward data after anchor {anchor_date}: "
            f"need {max_horizon} bars, have {bars_after_anchor}"
        )

    labels: list[ForwardLabel] = []
    for h in horizons:
        future_bar = bars[anchor_idx + h]
        return_pct = (future_bar.close - anchor_close) / anchor_close
        labels.append(ForwardLabel(
            horizon_days=h,
            future_date=future_bar.bar_date,
            return_pct=return_pct,
            is_profitable=(return_pct > 0),
        ))
    return labels
