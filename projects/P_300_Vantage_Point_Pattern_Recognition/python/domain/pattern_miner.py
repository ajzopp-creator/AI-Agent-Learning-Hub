"""
FILE: domain/pattern_miner.py
VERSION: 2.1
DATE: 2026-07-13
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Crossover-gated pattern mining (WO-P300-E3.002). Given a full bar
    history for one symbol, finds candidate anchors -- bars sitting at
    or near a Medium-Term crossover in an eventually->=15% direction --
    matching how Tony's actual process works: IntelliScan surfaces a
    symbol on a trend/crossover event (his .isc: `Cross(PMAMedium,0,
    AMAMedium,0)`, TripleCrossCriteria=True), he picks an entry within
    that trend, outcome confirms the pick was worth cataloging.

    v1.0-v1.6 screened PURE OUTCOME instead ("does a >=15% move
    eventually happen from this bar?") -- true of nearly every bar
    inside a real sustained trend, so no amount of jump-cap tuning
    (M-082), cross-class interruption (v1.5), or same-class re-arm
    (v1.6, confirmed 2026-07-13 to reintroduce M-083's per-bar bleed)
    could converge. Tony diagnosed the real gap: mining pure outcomes
    can't reproduce a process that starts from a sparse, structurally-
    gated population (crossover events), not "screen every bar."

    ELIGIBILITY (v2.0): a bar is eligible for class C only if it sits
    within MINE_XOVER_MAX_BARS of its own most recent same-direction MT
    crossover (mtdiff sign flip). bars_since_crossover <=
    MINE_IGNITION_MAX_BARS tags entry_tier="ignition", else
    "continuation". Both constants measured from 66 real ground-truth
    picks (2026-07-13: 50% within 3 bars, 86% within 11, 95% within 20).

    SCANNING (v1.4 mechanics, v1.6 same-class re-arm REMOVED in v2.0):
    sequential cursor scan per class -- on a match, jump the cursor past
    the consumption window, capped at _MAX_STANDARD_HORIZON regardless
    of search length (M-082). Cross-class interruption (v1.5) kept.

    WINDOW-STRIDE BUG, found + fixed (v2.1, 2026-07-13): the real
    84-anchor ground-truth run found 6 real misses (BURL/GOOGL/GS/HAL/
    INTC/NVDA), ALL traced to the SAME mechanism, 6/6 -- an earlier
    same-class match's capped jump can land INSIDE or PAST the very
    next crossover's own eligibility window, so those bars are never
    evaluated (eligibility tiering was correct, the cursor just never
    revisited them). Fix: `_find_fresh_crossover()` scans the capped
    window for a bar that IS ITSELF a fresh same-direction crossover
    (bars_since_crossover == 0) -- structurally rare, NOT v1.6's
    mistake of re-arming on outcome requalification. Whichever
    truncation fires first -- opposite-class (v1.5) or fresh same-class
    crossover (v2.1) -- ends the window there.

    OUTCOME CHECK unchanged since v1.1: HIGH/LOW range per horizon
    window, standard then extended search (M-081) -- SEARCH and
    ELIGIBILITY are independent axes (M-082's distinction).

    GROUND-TRUTH MATCHING: a hit shares the pick's crossover event, not
    bar-proximity -- see run_this.py / tests/mine_ground_truth.py.

    Class labels: "uptrend"/"breakdown" are FORWARD moves; do not
    conflate with M-033's "pullback" (a TRAILING decline). No I/O, no DB, no print -- strictly testable in isolation.

CHANGELOG:
    - 2026-07-13 v2.1: `_find_fresh_crossover()` added -- window
      truncation now also fires on a fresh same-direction crossover
      inside the capped window (see docstring), fixing the jump-
      strides-over-next-crossover bug confirmed 6/6 on the real,
      corrected 84-anchor ground truth (tests/mine_ground_truth.py,
      also new this session). tests/test_pattern_miner.py gains a
      corresponding test.
    - 2026-07-13 v2.0: Outcome-only screening replaced with crossover-
      gated eligibility; same-class re-arm (v1.6) removed. See prior
      version's changelog (git/lessons.md) for the full v1.0-v1.6
      history -- condensed here to keep this file under 300 lines.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import (  # noqa: E402
    FORWARD_HORIZONS,
    MINE_IGNITION_MAX_BARS,
    MINE_MAX_SCREEN_DAYS,
    MINE_MIN_ANCHOR_DATE,
    MINE_MOVE_THRESHOLD,
    MINE_XOVER_MAX_BARS,
)
from schemas_bulk import BulkBarRaw  # noqa: E402

UPTREND = "uptrend"
BREAKDOWN = "breakdown"
IGNITION = "ignition"
CONTINUATION = "continuation"

_MIN_BARS_BACK = 20  # setup-window eligibility, same as bulk pipeline
_MAX_STANDARD_HORIZON = max(FORWARD_HORIZONS)


@dataclass(frozen=True)
class MinedCandidate:
    """One qualifying launch anchor, pre-symbol-attachment (the caller
    -- mine_patterns_pipeline.py -- knows the symbol from the filename;
    this module never needs it)."""
    anchor_date: date
    pattern_class: str        # UPTREND | BREAKDOWN
    horizon_days: int         # trading-day count whose hi/lo range qualified
    move_pct: float           # signed hi/lo extreme move, decimal fraction (M-020)
    standard_horizon: bool    # True if horizon_days is in FORWARD_HORIZONS
    bars_since_crossover: int  # v2.0 -- distance to the trend's own MT crossover
    entry_tier: str            # v2.0 -- IGNITION | CONTINUATION


def _bars_since_crossover(bars: list[BulkBarRaw], idx: int):
    """v2.0 -- walks backward from idx to the start of the current
    same-sign mtdiff run (the most recent Medium-Term crossover in the
    bar's own direction). Returns (bars_since, direction) where
    direction is UPTREND/BREAKDOWN/None (mtdiff exactly 0), or
    (None, direction) if the run reaches the start of available data."""
    mt = bars[idx].mtdiff
    if mt > 0:
        direction = UPTREND
    elif mt < 0:
        direction = BREAKDOWN
    else:
        return (None, None)

    same_sign = (lambda v: v > 0) if mt > 0 else (lambda v: v < 0)
    i = idx
    while i > 0 and same_sign(bars[i - 1].mtdiff):
        i -= 1
    if i == 0:
        return (None, direction)
    return (idx - i, direction)


def _qualifies_for_class(
    bars: list[BulkBarRaw],
    idx: int,
    want_class: str,
    allow_extended: bool = True,
):
    """Outcome check ONLY, independent of eligibility (M-081/M-082's
    search-vs-jump distinction still applies). Checks whether bar idx's
    high/low range clears MINE_MOVE_THRESHOLD in want_class's direction
    -- standard horizons first, then, if allow_extended, the extended
    search out to MINE_MAX_SCREEN_DAYS. Returns (horizon_days,
    move_pct, standard_horizon) at the first qualifying window, or None."""
    anchor_close = bars[idx].close

    def _check(window) -> float | None:
        if want_class == UPTREND:
            extreme = max(b.high for b in window)
            pct = (extreme - anchor_close) / anchor_close
        else:
            extreme = min(b.low for b in window)
            pct = (anchor_close - extreme) / anchor_close
        if pct >= MINE_MOVE_THRESHOLD:
            return pct if want_class == UPTREND else -pct
        return None

    for h in FORWARD_HORIZONS:
        window = bars[idx + 1: idx + 1 + h]
        if not window:
            continue
        pct = _check(window)
        if pct is not None:
            return (h, pct, True)

    if not allow_extended:
        return None

    for h in range(_MAX_STANDARD_HORIZON + 1, MINE_MAX_SCREEN_DAYS + 1):
        window = bars[idx + 1: idx + 1 + h]
        if not window:
            break
        pct = _check(window)
        if pct is not None:
            return (h, pct, False)
    return None


def _find_interruption(
    bars: list[BulkBarRaw], start_idx: int, end_idx: int, check_class: str
):
    """v1.5, kept in v2.x -- scans bars[start_idx:end_idx] (interior of
    an already-capped consumption window) for the first bar where
    check_class independently qualifies (outcome only) at a STANDARD
    horizon. Returns that interior bar index, or None. Used for cross-
    class interruption only -- v1.6's same-class use is removed."""
    for p in range(start_idx, end_idx):
        result = _qualifies_for_class(bars, p, check_class, allow_extended=False)
        if result is not None:
            return p
    return None


def _find_fresh_crossover(
    bars: list[BulkBarRaw], start_idx: int, end_idx: int, want_class: str
):
    """v2.1 -- scans bars[start_idx:end_idx] for the first bar that is
    ITSELF a fresh same-direction crossover (bars_since_crossover == 0
    for want_class) -- a genuine new ignition inside an already-capped
    consumption window. Structurally rare, NOT v1.6's mistake of
    re-arming on outcome requalification. Returns that index, or None."""
    for p in range(start_idx, end_idx):
        bs, direction = _bars_since_crossover(bars, p)
        if bs == 0 and direction == want_class:
            return p
    return None


def _is_eligible(bars: list[BulkBarRaw], idx: int, want_class: str):
    """v2.0 -- setup window, forward window, post-backfill boundary
    (MINE_MIN_ANCHOR_DATE), AND the crossover gate: idx must sit within
    MINE_XOVER_MAX_BARS of its own most recent same-direction crossover,
    direction matching want_class. Returns (eligible,
    bars_since_crossover, entry_tier)."""
    if idx < _MIN_BARS_BACK:
        return (False, None, None)
    if bars[idx].bar_date < MINE_MIN_ANCHOR_DATE:
        return (False, None, None)
    bars_after = len(bars) - 1 - idx
    if bars_after < _MAX_STANDARD_HORIZON:
        return (False, None, None)

    bars_since, direction = _bars_since_crossover(bars, idx)
    if bars_since is None or direction != want_class:
        return (False, None, None)
    if bars_since > MINE_XOVER_MAX_BARS:
        return (False, None, None)

    tier = IGNITION if bars_since <= MINE_IGNITION_MAX_BARS else CONTINUATION
    return (True, bars_since, tier)


def _scan_class(
    bars: list[BulkBarRaw], want_class: str, opposite_class: str
) -> list[MinedCandidate]:
    """Sequential cursor scan for one class: a bar is a candidate only
    if crossover-eligible AND its outcome clears MINE_MOVE_THRESHOLD.
    On a match, consume the window that proved the outcome -- capped at
    _MAX_STANDARD_HORIZON regardless of search length (M-082) -- unless
    a truncation event fires first: the OPPOSITE class interrupting
    (v1.5) or a fresh SAME-class crossover inside the window (v2.1).
    Whichever comes first ends the window there."""
    found: list[MinedCandidate] = []
    cursor = 0
    n = len(bars)
    while cursor < n:
        eligible, bars_since, tier = _is_eligible(bars, cursor, want_class)
        if not eligible:
            cursor += 1
            continue
        result = _qualifies_for_class(bars, cursor, want_class)
        if result is None:
            cursor += 1
            continue
        horizon_days, move_pct, standard_horizon = result
        found.append(MinedCandidate(
            anchor_date=bars[cursor].bar_date,
            pattern_class=want_class,
            horizon_days=horizon_days,
            move_pct=move_pct,
            standard_horizon=standard_horizon,
            bars_since_crossover=bars_since,
            entry_tier=tier,
        ))

        # M-082: consumption capped regardless of search length.
        jump = min(horizon_days, _MAX_STANDARD_HORIZON)

        # v1.5 opposite-class interruption + v2.1 fresh same-class
        # crossover -- whichever fires first truncates the window.
        opposite_interrupt = _find_interruption(
            bars, cursor + 1, cursor + 1 + jump, opposite_class
        )
        fresh_xover = _find_fresh_crossover(
            bars, cursor + 1, cursor + 1 + jump, want_class
        )
        truncation_points = [p for p in (opposite_interrupt, fresh_xover) if p is not None]
        cursor = min(truncation_points) if truncation_points else cursor + jump + 1
    return found


def mine_bars(bars: list[BulkBarRaw]) -> list[MinedCandidate]:
    """Full pipeline for one symbol's bar history: independent
    sequential cursor scan per class (see module docstring), merged
    and sorted by anchor_date. bars must be sorted ascending
    (bulk_grid_reader.py's contract)."""
    if not bars:
        return []
    uptrend = _scan_class(bars, UPTREND, BREAKDOWN)
    breakdown = _scan_class(bars, BREAKDOWN, UPTREND)
    return sorted(uptrend + breakdown, key=lambda c: c.anchor_date)
