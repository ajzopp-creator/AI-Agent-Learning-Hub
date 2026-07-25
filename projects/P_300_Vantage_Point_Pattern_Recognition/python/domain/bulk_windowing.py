"""
FILE: domain/bulk_windowing.py
VERSION: 1.1
DATE: 2026-07-08
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Pure-Python window sweep logic for WO-P300-E2.001 Bulk Pattern
    Extraction. No I/O, no DB, no print -- strictly testable in isolation.
    Operates on BulkBarRaw (bulk export shape) and
    domain.bulk_pattern_detector (bulk-specific 9-condition evaluator).

    Three responsibilities:
      1. find_predictive_boundary_index -- VP backfills predictive columns
         (ST/MT/LT Diff, Predicted High/Low, Triple Cross) exactly 5 years
         before export date; verified against real SPY and BP 10-year
         exports that these fields are zero-filled before that boundary,
         ragged across fields (stdiff can go live 1-2 bars before
         mtdiff/ltdiff/Triple Cross at the same transition). neural_index
         is TEXT and is populated throughout, backfill or not -- it is
         deliberately NOT part of the zero-fill check (a text field is
         never "zero"; checking it would be a silent no-op). Detection
         must never run on the pre-boundary segment (guaranteed-false
         conditions on the numeric fields, wasted work) -- this function
         finds where real data starts, per file, rather than assuming a
         fixed calendar date.
      2. run_detection_sweep -- slides bulk_pattern_detector.
         detect_bulk_pattern across every eligible bar from the boundary
         forward, collecting every raw hit (STRICT or RELAXED) before
         spacing is applied.
      3. apply_spacing_rule -- enforces BULK_MIN_DETECTION_SPACING_BARS
         per tier (WO scope: "no second detection within N bars of a
         prior detection on the same symbol+tier"). This module handles
         one symbol's bar list, so spacing here is tier-only; the symbol
         dimension is inherently satisfied since each call is scoped to
         one symbol's bars.

CHANGELOG:
    - 2026-07-08 v1.1: Corrected from VPBarRaw/pattern_detector to
      BulkBarRaw/bulk_pattern_detector (schemas_bulk.py v1.1 introduced
      the real bulk bar shape after live-file verification). Fixed a
      latent bug in the pre-correction version: the predictive-data
      zero-check referenced triple_cross_short/medium/long (VPBarRaw
      field names, don't exist on BulkBarRaw) and neural_index as if
      numeric (BulkBarRaw.neural_index is text -- a string is never
      "== 0", so including it would have silently no-op'd that part of
      the check rather than raising or gating correctly). Zero-check now
      covers exactly the 9 numeric predictive fields VP actually
      backfills: stdiff, mtdiff, ltdiff, pred_high, pred_low,
      neural_x_max, tc_short, tc_medium, tc_long.
    - 2026-07-08 v1.0: Initial release (superseded same-day).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import BULK_MIN_DETECTION_SPACING_BARS  # noqa: E402
from domain.bulk_pattern_detector import (  # noqa: E402
    BulkDetectionResult,
    detect_bulk_pattern,
)
from schemas_bulk import BulkBarRaw, DetectionTier  # noqa: E402

# Consecutive bars required to confirm the predictive-column boundary --
# guards against a single stray nonzero value false-triggering the
# boundary before VP's real backfill actually starts.
_BOUNDARY_CONFIRM_RUN: int = 5


@dataclass(frozen=True)
class BulkDetectionHit:
    """One surviving detection after the spacing rule -- ready for the
    catalog-row builder (infrastructure/application layer, out of scope
    here)."""
    bar_index: int
    anchor_date: date
    tier: DetectionTier
    resistance_level: float


def _bar_has_predictive_data(bar: BulkBarRaw) -> bool:
    """
    True if every NUMERIC predictive field on `bar` is nonzero. VP
    zero-fills (not nulls) the pre-backfill segment -- verified on real
    SPY and BP 10-year exports. neural_index is deliberately excluded:
    it is TEXT ('up'/'down'/'unknown'), populated even pre-backfill,
    and a string is never meaningfully "zero" -- including it here
    would silently no-op that part of the check rather than gate
    anything.
    """
    predictive_fields = (
        bar.stdiff,
        bar.mtdiff,
        bar.ltdiff,
        bar.pred_high,
        bar.pred_low,
        bar.neural_x_max,
        bar.tc_short,
        bar.tc_medium,
        bar.tc_long,
    )
    return all(v != 0 for v in predictive_fields)


def find_predictive_boundary_index(bars: list[BulkBarRaw]) -> int | None:
    """
    Scans `bars` (ascending) for the first index that begins a run of
    at least _BOUNDARY_CONFIRM_RUN consecutive bars with fully nonzero
    predictive fields. Returns that index, or None if no such run
    exists (file has no usable predictive window at all -- e.g. a
    short export that never reaches back to the backfill boundary is
    NOT this case; such a file is entirely inside the predictive era
    and returns index 0, verified against a real 6-month BP export).
    """
    if len(bars) < _BOUNDARY_CONFIRM_RUN:
        return None

    for i in range(len(bars) - _BOUNDARY_CONFIRM_RUN + 1):
        window = bars[i: i + _BOUNDARY_CONFIRM_RUN]
        if all(_bar_has_predictive_data(b) for b in window):
            return i
    return None


def run_detection_sweep(
    bars: list[BulkBarRaw],
    start_idx: int,
) -> list[tuple[int, BulkDetectionResult]]:
    """
    Slides detect_bulk_pattern across every bar from start_idx to the
    end of `bars`. Returns raw (bar_index, BulkDetectionResult) pairs
    for every hit -- unfiltered by spacing. Caller applies
    apply_spacing_rule next.
    """
    hits: list[tuple[int, BulkDetectionResult]] = []
    for idx in range(start_idx, len(bars)):
        result = detect_bulk_pattern(bars, idx)
        if result is not None:
            hits.append((idx, result))
    return hits


def apply_spacing_rule(
    bars: list[BulkBarRaw],
    raw_hits: list[tuple[int, BulkDetectionResult]],
    min_spacing_bars: int = BULK_MIN_DETECTION_SPACING_BARS,
) -> list[BulkDetectionHit]:
    """
    Suppresses a detection if it falls within `min_spacing_bars` of the
    last KEPT detection of the SAME tier. Processes raw_hits in index
    order (ascending); the first hit of a tier always survives, later
    hits of that tier survive only once the spacing gap has elapsed.
    STRICT and RELAXED are tracked independently -- a RELAXED hit does
    not block a nearby STRICT hit or vice versa.
    """
    last_kept_idx: dict[DetectionTier, int] = {}
    survivors: list[BulkDetectionHit] = []

    for idx, result in raw_hits:
        prior = last_kept_idx.get(result.tier)
        if prior is not None and (idx - prior) < min_spacing_bars:
            continue
        last_kept_idx[result.tier] = idx
        survivors.append(BulkDetectionHit(
            bar_index=idx,
            anchor_date=bars[idx].bar_date,
            tier=result.tier,
            resistance_level=result.resistance_level,
        ))

    return survivors
