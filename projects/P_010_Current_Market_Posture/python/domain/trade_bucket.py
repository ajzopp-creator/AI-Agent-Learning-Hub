"""
P_010 Market Health -- domain/trade_bucket.py

Pure domain logic for bucketing trades by market_phase and computing
win-rate, avg PnL, and avg R per bucket. No I/O.
"""
from typing import Optional

from market_health.config import BUCKET_MIN_TRADES, BUCKET_DELTA_THRESHOLD
from market_health.schemas import BucketResult, TradeRecord


def bucket_trades(trades: list[TradeRecord]) -> list[BucketResult]:
    """Group trades by market_phase; compute stats per bucket."""
    grouped: dict[str, list[TradeRecord]] = {}
    for t in trades:
        phase = t.market_phase or 'UNKNOWN'
        grouped.setdefault(phase, []).append(t)

    results = []
    for phase, group in sorted(grouped.items()):
        results.append(_compute_bucket(phase, group))
    return results


def compute_delta(buckets: list[BucketResult]) -> Optional[float]:
    """
    Return best_win_rate - worst_win_rate across all buckets.
    Returns None if fewer than 2 buckets have sufficient sample size.
    """
    valid = [b for b in buckets if not b.low_sample]
    if len(valid) < 2:
        return None
    rates = [b.win_rate for b in valid]
    return (max(rates) - min(rates)) * 100.0  # as percentage points


def go_no_go(delta: Optional[float]) -> str:
    """
    Binary Phase 3 decision.
    Returns 'GO', 'NO_GO', or 'INSUFFICIENT_DATA'.
    """
    if delta is None:
        return 'INSUFFICIENT_DATA'
    return 'GO' if delta >= BUCKET_DELTA_THRESHOLD else 'NO_GO'


def _compute_bucket(phase: str, trades: list[TradeRecord]) -> BucketResult:
    """Compute stats for a single phase bucket."""
    wins = [t for t in trades if t.exit_pnl is not None and t.exit_pnl > 0]
    win_rate = len(wins) / len(trades) if trades else 0.0
    avg_pnl = (_safe_mean([t.exit_pnl for t in trades if t.exit_pnl is not None]))

    r_values = _compute_r_values(trades)
    avg_r = _safe_mean(r_values) if r_values is not None else None

    return BucketResult(
        phase=phase,
        trade_count=len(trades),
        win_count=len(wins),
        win_rate=win_rate,
        avg_pnl=avg_pnl,
        avg_r=avg_r,
        low_sample=len(trades) < BUCKET_MIN_TRADES,
    )


def _compute_r_values(trades: list[TradeRecord]) -> Optional[list[float]]:
    """Return list of R-multiples if all trades have risk_amount, else None."""
    if not all(t.risk_amount and t.risk_amount > 0 and t.exit_pnl is not None
               for t in trades):
        return None
    return [t.exit_pnl / t.risk_amount for t in trades]


def _safe_mean(values: list[float]) -> float:
    """Mean of a list; returns 0.0 for empty list."""
    return sum(values) / len(values) if values else 0.0