"""P_400 domain: behavioral history inputs for council.behavioral_vote().

Pure logic only -- no I/O, no network, no print.
Takes the same List[BookRecord] that portfolio.py consumes; computes the
three data-backed inputs behavioral_vote() has never received in production
(WO-P000-E10.001 Phase 2, item 2.1).

Definitional note (approximation, stated plainly): BookRecord carries no
exit-reason field, only realized_pnl sign on CLOSED records. "Stopped out"
here means "closed at a loss" -- not specifically "exited via a stop order"
as distinct from any other losing exit. This is the only signal available;
Tony confirmed this approximation 2026-08-04.

daily_order_norm and win_streak_threshold are NOT computed here -- they are
policy thresholds, correctly left at behavioral_vote()'s own coded defaults
(3 each), not caller-propagation gaps (same reasoning as P_020's
multiplier default, WO-P000-E10.001 item 1.2).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional

from schemas import BookRecord

RECENT_STOPOUT_WINDOW_DAYS = 5


@dataclass
class BehavioralInputs:
    """Computed inputs for council.behavioral_vote(), minus the two
    threshold params that stay at their coded defaults."""

    recently_stopped_out_symbols: List[str]
    orders_today: int
    consecutive_wins: int


def compute_behavioral_inputs(
    records: List[BookRecord],
    today: Optional[date] = None,
) -> BehavioralInputs:
    """Compute behavioral_vote() inputs from the same book records
    portfolio.py already reads -- no extra I/O.

    Args:
        records: All records from book_loader.load_book().
        today: Reference date; defaults to date.today().

    Returns:
        BehavioralInputs ready to unpack into behavioral_vote().
    """
    if today is None:
        today = date.today()

    orders_today = _count_orders_today(records, today)
    closed_sorted = _closed_records_by_close_date_desc(records)
    stopped_out = _recently_stopped_out(closed_sorted, today)
    wins = _consecutive_wins(closed_sorted)

    return BehavioralInputs(
        recently_stopped_out_symbols=stopped_out,
        orders_today=orders_today,
        consecutive_wins=wins,
    )


def _count_orders_today(records: List[BookRecord], today: date) -> int:
    """Count records whose order_date (filename-derived) is today."""
    today_str = today.isoformat()
    return sum(1 for r in records if r.order_date == today_str)


def _closed_records_by_close_date_desc(records: List[BookRecord]) -> List[BookRecord]:
    """CLOSED records with a close_date, most recent first."""
    closed = [
        r for r in records
        if r.status.upper() == "CLOSED" and r.close_date and r.realized_pnl is not None
    ]
    return sorted(closed, key=lambda r: r.close_date, reverse=True)


def _recently_stopped_out(closed_sorted: List[BookRecord], today: date) -> List[str]:
    """Symbols closed at a loss within RECENT_STOPOUT_WINDOW_DAYS.

    Approximation: "stopped out" = "closed at a loss" -- no exit-reason
    field exists to distinguish a stop-loss exit from any other losing exit.
    """
    cutoff = today - timedelta(days=RECENT_STOPOUT_WINDOW_DAYS)
    result = []
    for r in closed_sorted:
        close_date = date.fromisoformat(r.close_date)
        if close_date < cutoff:
            break  # sorted desc -- everything after this is even older
        if r.realized_pnl is not None and r.realized_pnl < 0:
            result.append(r.symbol)
    return result


def _consecutive_wins(closed_sorted: List[BookRecord]) -> int:
    """Count consecutive winning closes from most recent, stop at first
    non-win (loss or breakeven)."""
    count = 0
    for r in closed_sorted:
        if r.realized_pnl is not None and r.realized_pnl > 0:
            count += 1
        else:
            break
    return count