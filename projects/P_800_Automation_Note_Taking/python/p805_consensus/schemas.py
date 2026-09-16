"""schemas.py -- Pydantic models for the P_805 Consensus Dashboard."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RankedCandidate(BaseModel):
    """One row from a P_805 daily ranked.csv file."""

    ticker: str
    source_count: int
    sector_count: int
    sources: list[str]
    direction: str
    first_seen: datetime
    last_seen: datetime


class TrackerRow(BaseModel):
    """One row read from the Tracker Log worksheet."""

    date: datetime
    symbol: str
    step1_verdict: str = Field(default="")


class ConsensusRow(BaseModel):
    """One aggregated row for the Dashboard consensus table."""

    email_source: str
    today_symbols: list[str] = Field(default_factory=list)
    mtd_candidates: int = 0
    ytd_candidates: int = 0
    mtd_buy_asym: int = 0
    ytd_buy_asym: int = 0