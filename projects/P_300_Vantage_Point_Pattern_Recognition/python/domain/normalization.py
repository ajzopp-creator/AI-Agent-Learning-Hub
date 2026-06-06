"""
FILE: domain/normalization.py
VERSION: 1.0
DATE: 2026-05-14
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Pure-Python implementation of architecture §9.3 normalization formulas.
    Takes raw VP bars in, returns normalized values out. No I/O, no DB,
    no print, no logging — strictly testable in isolation.

    Normalization makes cross-symbol matching valid by construction:
    a 5% range on SPY at $550 and a 5% range on OII at $23 produce
    identical range_pct values. SPY-vs-OII shape comparison becomes
    apples-to-apples instead of apples-to-oranges.

    All ten normalized columns computed per bar:
        close_pct_from_anchor  range_pct        body_pct
        volume_zscore          stdiff_pct       mtdiff_pct
        ltdiff_pct             pred_high_pct    pred_low_pct
        pred_range_pct

    LAUNCH framing: anchor defaults to bars[-1] (the chronologically
    latest bar = offset 0 = the launch day per architecture §1.5).
    Caller may override for testing or alternative framings.

CHANGELOG:
    - 2026-05-14 v1.0: Initial Stage 4 POC release. Implements all
      ten §9.3 formulas. Handles std=0 edge case (constant volume
      across window) by returning volume_zscore=0.0.
"""
from __future__ import annotations

import sys
import statistics
from dataclasses import dataclass
from pathlib import Path

# Bootstrap sys.path so this module can import schemas/config when invoked
# standalone for testing. Stage 4 entry points via cli.py set PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from schemas import VPBarRaw  # noqa: E402


@dataclass(frozen=True)
class NormalizedValues:
    """
    In-memory intermediate. Holds the 10 normalized columns computed for one bar.
    Not a Pydantic model because this never crosses a persistence boundary —
    values flow directly into PatternBarRecord assembly in catalog_writer.py.
    """
    close_pct_from_anchor: float
    range_pct: float
    body_pct: float
    volume_zscore: float
    stdiff_pct: float
    mtdiff_pct: float
    ltdiff_pct: float
    pred_high_pct: float
    pred_low_pct: float
    pred_range_pct: float


def compute_volume_stats(bars: list[VPBarRaw]) -> tuple[float, float]:
    """
    Return (mean, sample_stdev) of the bars' volume column. Sample stdev
    uses n-1 denominator (statistics.stdev). With fewer than 2 bars or
    when all volumes are equal, stdev is 0.0 and downstream z-scores
    fall back to 0.0 instead of dividing by zero.
    """
    vols = [b.volume for b in bars]
    if len(vols) < 2:
        return (vols[0] if vols else 0.0, 0.0)
    mean = statistics.mean(vols)
    try:
        std = statistics.stdev(vols)
    except statistics.StatisticsError:
        std = 0.0
    return (mean, std)


def normalize_bar(
    bar: VPBarRaw,
    anchor: VPBarRaw,
    vol_mean: float,
    vol_std: float,
) -> NormalizedValues:
    """
    Compute the 10 normalized columns for one bar relative to an anchor.
    Architecture §9.3 formulas. Prices guaranteed > 0 by VPBarRaw validators,
    so no zero-divisor branches needed on close/open/anchor.close.
    """
    return NormalizedValues(
        close_pct_from_anchor=(bar.close - anchor.close) / anchor.close,
        range_pct=(bar.high - bar.low) / bar.close,
        body_pct=(bar.close - bar.open) / bar.open,
        volume_zscore=((bar.volume - vol_mean) / vol_std) if vol_std > 0 else 0.0,
        stdiff_pct=bar.stdiff / bar.close,
        mtdiff_pct=bar.mtdiff / bar.close,
        ltdiff_pct=bar.ltdiff / bar.close,
        pred_high_pct=(bar.pred_high - bar.close) / bar.close,
        pred_low_pct=(bar.pred_low - bar.close) / bar.close,
        pred_range_pct=bar.pred_range / bar.close,
    )


def normalize_window(
    bars: list[VPBarRaw],
    anchor: VPBarRaw | None = None,
) -> list[NormalizedValues]:
    """
    Normalize an entire ordered window. Bars must be sorted ascending by date
    (caller's responsibility — PatternFileParse validator enforces this on
    persistence input).

    Under LAUNCH-anchor framing, anchor defaults to bars[-1] (the latest bar,
    offset 0, the launch day). Override the anchor argument for PEAK framing
    or other experiments.

    Returns a list of NormalizedValues in the same order as the input bars.
    """
    if not bars:
        raise ValueError("normalize_window requires at least one bar")
    if anchor is None:
        anchor = bars[-1]
    vol_mean, vol_std = compute_volume_stats(bars)
    return [normalize_bar(b, anchor, vol_mean, vol_std) for b in bars]
