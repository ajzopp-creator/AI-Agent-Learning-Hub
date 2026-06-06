"""
P_010 Market Health -- market_health/bucket_cli.py

CLI entry point for Workstream D trade-bucket analysis.
Writes outputs/trade_bucket_report.md.
Run from python/ directory: python -m market_health.bucket_cli
"""
import logging
import sys
from datetime import datetime

from application.bucket_runner import run_bucket_analysis
from market_health.config import BUCKET_DELTA_THRESHOLD, BUCKET_REPORT_PATH
from market_health.schemas import BucketResult

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)


def main() -> int:
    """Run analysis and write report. Returns 0 on success."""
    log.info('Workstream D -- Trade Bucket Analysis')
    result = run_bucket_analysis()

    BUCKET_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = _build_report(result)
    BUCKET_REPORT_PATH.write_text(report, encoding='utf-8')
    log.info('Report written to %s', BUCKET_REPORT_PATH)

    print(report)
    return 0


def _build_report(result) -> str:
    """Format BucketRunResult as a Markdown report."""
    lines = [
        '# P_010 Workstream D — Trade Bucket Analysis',
        f'Generated: {datetime.now():%Y-%m-%d %H:%M}',
        '',
        '## Summary',
        f'- Total trades analyzed: {len(result.trades)}',
        f'- Trades matched to phase: {len(result.trades) - result.unknown_count}',
        f'- Trades unmatched (UNKNOWN): {result.unknown_count}',
        f'- Win-rate delta (best vs worst): {_fmt_delta(result.delta)}',
        f'- Phase 3 decision: **{result.decision}**',
        f'- Delta threshold: {BUCKET_DELTA_THRESHOLD}pp',
        '',
        '## Bucket Results',
        '',
        '| Phase | Trades | Wins | Win Rate | Avg PnL | Avg R | Note |',
        '|-------|--------|------|----------|---------|-------|------|',
    ]
    for b in result.buckets:
        lines.append(_bucket_row(b))

    lines += [
        '',
        '## Trade Detail',
        '',
        '| Date | System | Symbol | Phase | PnL |',
        '|------|--------|--------|-------|-----|',
    ]
    for t in result.trades:
        pnl = ('$' + f'{t.exit_pnl:+.2f}') if t.exit_pnl is not None else 'n/a'
        lines.append(f'| {t.open_date} | {t.system} | {t.underlying_symbol} | {t.market_phase} | {pnl} |')

    return nl.join(lines)


def _fmt_delta(delta) -> str:
    if delta is None:
        return 'n/a (insufficient data)'
    return f'{delta:.1f}pp'


def _bucket_row(b: BucketResult) -> str:
    note = 'LOW SAMPLE' if b.low_sample else ''
    avg_r = f'{b.avg_r:.2f}R' if b.avg_r is not None else 'n/a'
    pnl_str = ('$' + f'{b.avg_pnl:+.0f}')
    return f'| {b.phase} | {b.trade_count} | {b.win_count} | {b.win_rate:.0%} | {pnl_str} | {avg_r} | {note} |'


nl = chr(10)


if __name__ == '__main__':
    sys.exit(main())
