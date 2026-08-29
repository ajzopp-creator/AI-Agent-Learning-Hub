"""
FILE: domain/zone_finder.py
VERSION: 1.0
DATE: 2026-08-26
AUTHOR: Tony + Claude
LAYER: domain
DESCRIPTION:
    State 0 (ZONE_SCAN) of the Break-and-Retest FSM. Pure logic, no I/O --
    computes ATR, finds swing highs, and clusters them into resistance
    zones with an ATR-based tolerance band.

    Resistance zones only -- Tony trades long-only across every strategy
    in the Hub, no short-side infrastructure exists anywhere (per the
    P_115 evaluation of this same strategy).

CHANGELOG:
    - 2026-08-26 v1.0: Initial build.
"""
from __future__ import annotations

from typing import NamedTuple

from schemas import BulkBarRaw


class Zone(NamedTuple):
    """One clustered resistance zone -- a candidate ceiling to break above."""
    zone_low: float
    zone_high: float
    level: float
    touch_count: int
    formed_idx: int  # bar index where the zone reached touch_min


def compute_atr(bars: list[BulkBarRaw], period: int) -> list[float | None]:
    """True Range rolling average. First `period` bars are None (warmup)."""
    true_ranges: list[float] = []
    for i, bar in enumerate(bars):
        if i == 0:
            true_ranges.append(bar.high - bar.low)
            continue
        prev_close = bars[i - 1].close
        tr = max(
            bar.high - bar.low,
            abs(bar.high - prev_close),
            abs(bar.low - prev_close),
        )
        true_ranges.append(tr)

    atr: list[float | None] = [None] * len(bars)
    for i in range(period - 1, len(bars)):
        window = true_ranges[i - period + 1: i + 1]
        atr[i] = sum(window) / period
    return atr


def find_swing_highs(bars: list[BulkBarRaw], order: int) -> list[int]:
    """Indices where high[i] is the max within [i-order, i+order]."""
    swing_idxs: list[int] = []
    for i in range(order, len(bars) - order):
        window = bars[i - order: i + order + 1]
        if bars[i].high == max(b.high for b in window):
            swing_idxs.append(i)
    return swing_idxs


def cluster_zones(
    bars: list[BulkBarRaw],
    atr: list[float | None],
    swing_high_idxs: list[int],
    touch_min: int,
    atr_mult: float,
) -> list[Zone]:
    """Groups swing-high prices within an ATR tolerance band into zones.

    A zone confirms the moment its touch count reaches touch_min --
    formed_idx marks that bar so the strategy engine never evaluates a
    breakout before the zone actually existed.
    """
    zones: list[Zone] = []
    used = [False] * len(swing_high_idxs)

    for a, idx_a in enumerate(swing_high_idxs):
        if used[a]:
            continue
        level = bars[idx_a].high
        tolerance = (atr[idx_a] or 0.0) * atr_mult
        if tolerance == 0.0:
            continue  # no ATR yet (warmup period) -- skip as anchor

        touches = [idx_a]
        for b in range(a + 1, len(swing_high_idxs)):
            idx_b = swing_high_idxs[b]
            if used[b]:
                continue
            if abs(bars[idx_b].high - level) <= tolerance:
                touches.append(idx_b)
                used[b] = True

        if len(touches) >= touch_min:
            used[a] = True
            touches.sort()
            formed_idx = touches[touch_min - 1]
            zone_prices = [bars[t].high for t in touches]
            zones.append(
                Zone(
                    zone_low=level - tolerance,
                    zone_high=level + tolerance,
                    level=sum(zone_prices) / len(zone_prices),
                    touch_count=len(touches),
                    formed_idx=formed_idx,
                )
            )
    return zones
