"""
P_010 Market Health -- application/backtest_runner.py

Iterate over a range of historical VP trading dates and compute the
MarketHealthOutput as if each day were "today". Used to generate the
Workstream D dataset for trade-bucketed phase analysis.

Spec reference: Phase 2 Plan v1.1 -- Workstream C (backtest harness)
"""

from datetime import date
from pathlib import Path
from typing import Optional

from market_health.config import DISTRIBUTION_WINDOW_DAYS
from market_health.schemas import MarketHealthOutput
from infrastructure.backtest_writer import write_backtest_csv
from infrastructure.vp_reader import read_vp_history
from application.health_runner import run_market_health


# Default backtest lookback -- enough history for any reasonable backtest range
# given current VP file size (~124 rows). Bump higher only if VP files grow.
DEFAULT_BACKTEST_LOOKBACK = 1000

# Minimum days of warmup before producing a backtest row. Distribution window
# is 25 days; we add a buffer so the rally state machine has time to settle.
DEFAULT_WARMUP_DAYS = max(DISTRIBUTION_WINDOW_DAYS + 5, 30)


def run_backtest(
    output_csv: Path,
    start: Optional[date] = None,
    end: Optional[date] = None,
    warmup_days: int = DEFAULT_WARMUP_DAYS,
) -> tuple[Path, int]:
    """
    Run the P_010 phase derivation across each historical trading day in
    the available VP grid, write results to CSV.

    Args:
      output_csv: target CSV file path.
      start:      first as_of date to emit (inclusive). If None, uses
                  earliest VP date + warmup_days.
      end:        last as_of date to emit (inclusive). If None, uses the
                  latest VP date.
      warmup_days: minimum trailing rows required before emitting a row.

    Returns:
      (output_path, rows_written)
    """
    trading_dates = _intersect_trading_dates(DEFAULT_BACKTEST_LOOKBACK)
    if not trading_dates:
        raise ValueError("No overlapping trading dates between SPY and QQQ VP files")

    backtest_dates = _select_dates(trading_dates, start, end, warmup_days)
    if not backtest_dates:
        raise ValueError(
            f"Date range produced zero backtest dates "
            f"(start={start}, end={end}, warmup_days={warmup_days})"
        )

    outputs: list[MarketHealthOutput] = []
    for as_of in backtest_dates:
        out = run_market_health(
            as_of=as_of,
            dry_run=True,
            lookback_days=DEFAULT_BACKTEST_LOOKBACK,
        )
        outputs.append(out)

    write_backtest_csv(outputs, output_csv)
    return output_csv, len(outputs)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _intersect_trading_dates(lookback: int) -> list[date]:
    """Sorted list of trading dates present in BOTH SPY and QQQ VP files."""
    spy_dates = {r.trade_date for r in read_vp_history("SPY", lookback_days=lookback)}
    qqq_dates = {r.trade_date for r in read_vp_history("QQQ", lookback_days=lookback)}
    return sorted(spy_dates & qqq_dates)


def _select_dates(
    trading_dates: list[date],
    start: Optional[date],
    end: Optional[date],
    warmup_days: int,
) -> list[date]:
    """Filter the trading-date universe to the requested backtest window."""
    if warmup_days >= len(trading_dates):
        return []

    earliest_allowed = trading_dates[warmup_days]
    effective_start = max(start, earliest_allowed) if start else earliest_allowed
    effective_end = min(end, trading_dates[-1]) if end else trading_dates[-1]

    return [d for d in trading_dates if effective_start <= d <= effective_end]
