"""P_400 domain: portfolio state and governance inputs.

Pure logic only -- no I/O, no network, no print.
Takes a list of BookRecord objects; returns PortfolioState.
PortfolioState fields feed directly into council.risk_vote().

Architecture v2.0 Section 4.3.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Set

from schemas import BookRecord

logger = logging.getLogger("p400.portfolio")

OPEN_STATUSES: frozenset = frozenset(
    {"PENDING", "SUBMITTED", "FILLED", "T1_HIT", "TRAILING"}
)


@dataclass
class PortfolioState:
    """Aggregated view of the open book; feeds council.risk_vote() inputs."""

    heat_dollars: float
    open_position_count: int
    open_sector_counts: Dict[str, int]
    open_symbols: Set[str]
    realized_day_loss_dollars: float

    def has_duplicate(self, symbol: str) -> bool:
        """Return True if symbol already has an open position."""
        return symbol.upper() in self.open_symbols


def build_portfolio_state(
    records: List[BookRecord],
    today: Optional[date] = None,
) -> PortfolioState:
    """Compute portfolio state from open-position book records.

    OPEN_STATUSES records contribute to heat, count, sectors, and symbols --
    except source_label-tagged external records (WO-P400-E6.003), which
    contribute to symbols only (duplicate detection) and are excluded from
    heat/count/sector math since P_400 never sized them.
    CLOSED records with today's close_date and negative realized_pnl contribute
    to realized_day_loss_dollars (circuit-breaker input).

    Args:
        records: All records from book_loader (CLOSED included for day-loss calc).
        today: Reference date for daily-loss filter; defaults to date.today().

    Returns:
        PortfolioState ready to pass into council.risk_vote().
    """
    if today is None:
        today = date.today()
    today_str = today.isoformat()

    heat = 0.0
    count = 0
    sectors: Dict[str, int] = {}
    symbols: Set[str] = set()
    day_loss = 0.0

    for rec in records:
        upper_status = rec.status.upper()

        if upper_status in OPEN_STATUSES:
            symbols.add(rec.symbol.upper())
            if rec.source_label:
                # External position (WO-P400-E6.003): counts for duplicate
                # detection only -- never sized by P_400, must not inflate
                # RISK's heat/position-count/sector caps.
                continue
            heat += rec.open_risk_dollars
            count += 1
            if rec.sector:
                sectors[rec.sector] = sectors.get(rec.sector, 0) + 1

        elif upper_status == "CLOSED":
            if (
                rec.realized_pnl is not None
                and rec.realized_pnl < 0
                and rec.close_date == today_str
            ):
                day_loss += abs(rec.realized_pnl)

    logger.debug(
        "Portfolio state: heat=$%.2f pos=%d sectors=%s day_loss=$%.2f",
        heat, count, sectors, day_loss,
    )
    return PortfolioState(
        heat_dollars=heat,
        open_position_count=count,
        open_sector_counts=sectors,
        open_symbols=symbols,
        realized_day_loss_dollars=day_loss,
    )
