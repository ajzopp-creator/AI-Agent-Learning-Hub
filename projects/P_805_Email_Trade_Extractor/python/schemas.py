"""P_805 Pydantic schemas for all non-temporary file I/O.

Per the Hub-wide python-project-architecture standard: any file read or
written on a non-temporary basis must have a Pydantic schema defined here
before the read/write code is written.

Currently modeled:
  - ApprovedSender — one row of data/sender_sheet.csv
  - TickerSignal   — one row of data/daily/YYYY-MM-DD_signals.csv
  - RankedSignal   — one row of data/daily/YYYY-MM-DD_ranked.csv
  - MovedMessage   — one row of data/moved_messages.csv (Phase 5.3 IMAP move log)
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ApprovedSender(BaseModel):
    """One row of data/sender_sheet.csv (Section 5.2 of SYSTEM_DOCUMENTATION).

    The 'sector' column is currently unpopulated for most rows; it is
    optional and tolerates missing/empty values from the CSV.

    date_added accepts ISO (2026-04-26) or US (4/26/2026) format on input
    (Entry 016, 2026-08-23) — the CSV was opened in Excel on 2026-07-22,
    which silently reformatted every date to US style and, because the
    field is a strict `date` type, made every row fail validation
    identically for a month with no visible error (Phase 3 logged it but
    exited 0 either way — see Entry 016's second fix in phase3_extract.py
    and siblings). Tolerating both formats here is the permanent fix for
    this exact failure mode recurring after a future Excel re-save.
    """

    email_address: str
    sender_name: str
    date_added: date
    sector: str | None = Field(default=None)
    enabled: bool

    @field_validator("date_added", mode="before")
    @classmethod
    def _parse_flexible_date(cls, value):
        """Accept ISO (YYYY-MM-DD) or US (M/D/YYYY) date strings.

        Passes non-str values (already a date/datetime) through untouched
        so Pydantic's normal coercion still applies to those.
        """
        if not isinstance(value, str):
            return value
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
        try:
            return datetime.strptime(value, "%m/%d/%Y").date()
        except ValueError:
            raise ValueError(
                f"date_added {value!r} matches neither ISO (YYYY-MM-DD) "
                "nor US (M/D/YYYY) format"
            )


class TickerSignal(BaseModel):
    """One extracted ticker mention from one approved email.

    Multiple TickerSignals can come from a single email (one per distinct
    ticker found). The (ticker, source_address, timestamp) triple should
    be unique within a single daily output file. message_id ties a signal
    back to its source email for Phase 5.3 IMAP move eligibility — every
    signal from the same email carries the same message_id.
    """

    ticker: str
    direction: str = Field(default="unknown")  # long / short / watch / unknown
    confidence: str = Field(default="medium")  # high / medium / low
    pattern: str                               # which TICKER_PATTERN matched
    source_address: str                        # bare email like adam@elite...
    source_name: str | None = Field(default=None)
    timestamp: datetime
    subject: str
    raw_context: str                           # ~500 chars around the match
    account: str                               # icloud / gmail / outlook / yahoo
    message_id: str = Field(default="")        # raw Message-ID header, empty if absent


class RankedSignal(BaseModel):
    """One consensus-ranked ticker for a single trading day.

    Produced by Phase 4 from the daily signals CSV. Only tickers that
    appear in >= CONSENSUS_THRESHOLD distinct sources are included.

    sector_count is the number of distinct sender sectors among the
    contributing sources (per data/sender_sheet.csv 'sector' column).
    Sources with no sector tag are bucketed together as 'unknown' and
    do not inflate this count — an untagged sender adds a source but
    not independent-sector evidence. sector_count == 1 means either a
    single sector or all-unknown sources; treat it as weaker consensus
    than sector_count >= 2.
    """

    ticker: str
    source_count: int                          # number of distinct senders
    sector_count: int = Field(default=1)       # distinct sectors among sources (see above)
    sources: str                               # pipe-separated sender addresses
    direction: str = Field(default="unknown")  # majority direction across signals
    first_seen: datetime
    last_seen: datetime


class MovedMessage(BaseModel):
    """One row of data/moved_messages.csv (Phase 5.3 IMAP move audit log).

    Written for every message the mover attempts, whether dry-run or real,
    whether it succeeds or fails. Read back before every move run so an
    already-moved (status='moved') message is never retried; a dry-run
    entry (status='dry_run') does not block a later real attempt.
    """

    message_id: str
    account: str                               # icloud / gmail / outlook / yahoo
    ticker_count: int                          # how many TickerSignals cited this email
    moved_at: datetime
    status: str                                # moved / dry_run / failed
    dry_run: bool
