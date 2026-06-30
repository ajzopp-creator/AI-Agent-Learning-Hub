"""P_805 Pydantic schemas for all non-temporary file I/O.

Per the Hub-wide python-project-architecture standard: any file read or
written on a non-temporary basis must have a Pydantic schema defined here
before the read/write code is written.

Currently modeled:
  - ApprovedSender — one row of data/sender_sheet.csv
  - TickerSignal   — one row of data/daily/YYYY-MM-DD_signals.csv
  - RankedSignal   — one row of data/daily/YYYY-MM-DD_ranked.csv
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class ApprovedSender(BaseModel):
    """One row of data/sender_sheet.csv (Section 5.2 of SYSTEM_DOCUMENTATION).

    The 'sector' column is currently unpopulated for most rows; it is
    optional and tolerates missing/empty values from the CSV.
    """

    email_address: str
    sender_name: str
    date_added: date
    sector: str | None = Field(default=None)
    enabled: bool


class TickerSignal(BaseModel):
    """One extracted ticker mention from one approved email.

    Multiple TickerSignals can come from a single email (one per distinct
    ticker found). The (ticker, source_address, timestamp) triple should
    be unique within a single daily output file.
    """

    ticker: str
    direction: str = Field(default="unknown")  # long / short / watch / unknown
    confidence: str = Field(default="medium")  # high / medium / low
    pattern: str                               # which TICKER_PATTERN matched
    source_address: str                        # bare email like adam@elite...
    source_name: str | None = Field(default=None)
    timestamp: datetime
    subject: str
    raw_context: str                           # ~80 chars around the match
    account: str                               # icloud / gmail / outlook / yahoo


class RankedSignal(BaseModel):
    """One consensus-ranked ticker for a single trading day.

    Produced by Phase 4 from the daily signals CSV. Only tickers that
    appear in >= CONSENSUS_THRESHOLD distinct sources are included.
    """

    ticker: str
    source_count: int                          # number of distinct senders
    sources: str                               # pipe-separated sender addresses
    direction: str = Field(default="unknown")  # majority direction across signals
    first_seen: datetime
    last_seen: datetime
