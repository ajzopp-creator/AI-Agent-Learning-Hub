"""
FILE: domain/bulk_labeler.py
VERSION: 1.0
DATE: 2026-07-08
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Forward-label computation for WO-P300-E2.001 bulk detections. Separate
    module from domain/labeler.py, not a patched version of it -- labeler.py
    is hard-typed to VPBarRaw (imports it directly in its signature), so
    reusing it for BulkBarRaw would mean either a runtime duck-typing
    assumption or a signature change to a shared live-pipeline file for a
    research-only caller. Same rationale as bulk_pattern_detector.py being
    separate from pattern_detector.py (see that module's docstring).

    The underlying math is identical to labeler.py: return_pct is a
    fractional ratio (M-020, not percent), is_profitable = return_pct > 0,
    future_date comes from the actual bar at +horizon trading days (bars
    ARE the trading calendar, no calendar-day math). significant_move_15
    is the one addition -- derived here, once, at the same boundary the
    ratio is computed, per schemas_bulk.py's BulkForwardLabelRecord
    docstring ("the conversion happens once, at this boundary").

    No I/O, no DB, no print -- strictly testable in isolation.

CHANGELOG:
    - 2026-07-08 v1.0: Initial release. compute_bulk_forward_labels,
      BulkForwardLabel (in-memory intermediate, mirrors labeler.py's
      ForwardLabel dataclass pattern).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import BULK_SIGNIFICANT_MOVE_PCT, FORWARD_HORIZONS  # noqa: E402
from schemas_bulk import BulkBarRaw  # noqa: E402


@dataclass(frozen=True)
class BulkForwardLabel:
    """In-memory intermediate. research_catalog_io.py callers convert
    these into BulkForwardLabelRecord at persistence (adds pattern_
    instance_id, which isn't known until the row exists)."""
    horizon_days: int
    future_date: date
    return_pct: float          # fractional ratio (M-020): 0.0436 == +4.36%
    is_profitable: bool
    significant_move_15: bool


def find_anchor_index(bars: list[BulkBarRaw], anchor_date: date) -> int:
    """Locate anchor_date in an ascending-sorted bar list. Raises
    ValueError if not present -- same contract as labeler.py's version,
    duplicated rather than imported since the two operate on different
    bar types and importing across would create a cross-schema coupling
    for a four-line function."""
    for i, b in enumerate(bars):
        if b.bar_date == anchor_date:
            return i
    raise ValueError(
        f"anchor_date {anchor_date} not found in bars "
        f"(range: {bars[0].bar_date} to {bars[-1].bar_date}, count: {len(bars)})"
    )


def compute_bulk_forward_labels(
    bars: list[BulkBarRaw],
    anchor_date: date,
    horizons: tuple[int, ...] = FORWARD_HORIZONS,
) -> list[BulkForwardLabel]:
    """
    Compute forward labels at every horizon in `horizons` (default:
    5/7/10/15/20, same as the live catalog). bars must be sorted
    ascending and contain at least max(horizons) trading bars AFTER
    anchor_date -- raises ValueError otherwise (a detection near the
    end of a bulk export simply can't be labeled at longer horizons
    yet; caller decides whether to skip or defer, not this function).

    significant_move_15 compares abs(return_pct) * 100 (converting to
    percent space at this single boundary, per M-020 + schemas_bulk.py's
    BulkForwardLabelRecord docstring) against BULK_SIGNIFICANT_MOVE_PCT.
    """
    if not bars:
        raise ValueError("compute_bulk_forward_labels requires at least one bar")
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

    labels: list[BulkForwardLabel] = []
    for h in horizons:
        future_bar = bars[anchor_idx + h]
        return_pct = (future_bar.close - anchor_close) / anchor_close
        labels.append(BulkForwardLabel(
            horizon_days=h,
            future_date=future_bar.bar_date,
            return_pct=return_pct,
            is_profitable=(return_pct > 0),
            significant_move_15=(abs(return_pct) * 100 >= BULK_SIGNIFICANT_MOVE_PCT),
        ))
    return labels
