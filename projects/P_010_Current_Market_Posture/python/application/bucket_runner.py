"""
P_010 Market Health -- application/bucket_runner.py

Orchestrates Workstream D: reads trades, looks up phases,
buckets by phase, computes win-rate delta, returns results.
"""
import logging
from dataclasses import dataclass
from typing import Optional

from domain.trade_bucket import bucket_trades, compute_delta, go_no_go
from infrastructure.snapshot_reader import lookup_phases
from infrastructure.trade_reader import read_closed_trades
from market_health.schemas import BucketResult, TradeRecord

log = logging.getLogger(__name__)


@dataclass
class BucketRunResult:
    """Full output of one bucket analysis run."""
    trades: list[TradeRecord]
    buckets: list[BucketResult]
    delta: Optional[float]
    decision: str
    unknown_count: int   # trades with no snapshot match


def run_bucket_analysis() -> BucketRunResult:
    """
    Full Workstream D pipeline.

    Steps:
      1. Read P_115/P_118 closed trades from P_020
      2. Look up market_phase for each trade's open_date
      3. Bucket by phase, compute win-rate + R stats
      4. Compute delta, apply go/no-go gate

    Returns BucketRunResult with all intermediate data.
    """
    log.info('Workstream D: loading trades from P_020...')
    trades = read_closed_trades()
    log.info('Loaded %d trades', len(trades))

    log.info('Looking up market phases from snapshot archive...')
    trades = lookup_phases(trades)
    unknown_count = sum(1 for t in trades if t.market_phase == 'UNKNOWN')
    if unknown_count:
        log.warning('%d trades have UNKNOWN phase -- excluded from bucketing', unknown_count)

    matched = [t for t in trades if t.market_phase != 'UNKNOWN']
    log.info('%d trades matched to a phase', len(matched))

    buckets = bucket_trades(matched)
    delta = compute_delta(buckets)
    decision = go_no_go(delta)

    log.info('Delta: %s pp  Decision: %s', delta, decision)
    return BucketRunResult(
        trades=trades,
        buckets=buckets,
        delta=delta,
        decision=decision,
        unknown_count=unknown_count,
    )