"""
P_010 Market Health -- infrastructure/backtest_writer.py

Flatten MarketHealthOutput rows to CSV for backtest analysis.

Pure IO layer -- consumed by application/backtest_runner.py.

Spec reference: Phase 2 Plan v1.1 -- Workstream C (backtest harness)
"""

import csv
from pathlib import Path
from typing import Iterable

from market_health.schemas import MarketHealthOutput


CSV_COLUMNS = (
    "trade_date",
    "phase",
    "phase_reason",
    "max_dist",
    "spy_dist",
    "spy_rally",
    "spy_attempt_day",
    "spy_ftd_date",
    "spy_ftd_age",
    "qqq_dist",
    "qqq_rally",
    "qqq_attempt_day",
    "qqq_ftd_date",
    "qqq_ftd_age",
)


def write_backtest_csv(outputs: Iterable[MarketHealthOutput], target: Path) -> Path:
    """
    Write one CSV row per MarketHealthOutput. Overwrites any existing file.
    Caller is responsible for ensuring outputs are sorted chronologically.

    Returns the final path written.
    """
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for out in outputs:
            writer.writerow(_flatten(out))

    return target


def _flatten(out: MarketHealthOutput) -> dict:
    """Flatten one MarketHealthOutput into a single CSV row dict."""
    return {
        "trade_date": out.as_of_date.isoformat(),
        "phase": out.market_phase,
        "phase_reason": out.phase_reason,
        "max_dist": out.max_dist_count,
        "spy_dist": out.spy.dist_count,
        "spy_rally": out.spy.rally_state,
        "spy_attempt_day": _opt(out.spy.rally_attempt_day),
        "spy_ftd_date": _opt_date(out.spy.follow_through_day),
        "spy_ftd_age": _opt(out.spy.ftd_age_days),
        "qqq_dist": out.qqq.dist_count,
        "qqq_rally": out.qqq.rally_state,
        "qqq_attempt_day": _opt(out.qqq.rally_attempt_day),
        "qqq_ftd_date": _opt_date(out.qqq.follow_through_day),
        "qqq_ftd_age": _opt(out.qqq.ftd_age_days),
    }


def _opt(value) -> str:
    return "" if value is None else str(value)


def _opt_date(value) -> str:
    return "" if value is None else value.isoformat()
