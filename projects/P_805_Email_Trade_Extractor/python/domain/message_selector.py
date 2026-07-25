"""Domain: select messages eligible for the Phase 5.3 IMAP move.

Pure logic, no I/O. Given today's TickerSignals and the moved-message
audit log, return the unique (account, message_id) pairs that should be
moved this run.

Eligibility rule (confirmed with Tony 2026-07-14): a message qualifies
only if it produced at least one TickerSignal (a ticker was found).
Approved-sender messages that produced zero tickers are never moved.
"""

from collections import Counter

from schemas import MovedMessage, TickerSignal


class MoveCandidate:
    """One message eligible for the mover, with a citation count."""

    def __init__(self, account: str, message_id: str, ticker_count: int):
        self.account = account
        self.message_id = message_id
        self.ticker_count = ticker_count

    def __repr__(self) -> str:
        return (
            f"MoveCandidate(account={self.account!r}, "
            f"message_id={self.message_id!r}, "
            f"ticker_count={self.ticker_count})"
        )


def _already_moved(moved_log: list[MovedMessage]) -> set[tuple[str, str]]:
    """Return the set of (account, message_id) pairs with status='moved'.

    Dry-run entries do NOT count as already-moved — they should not block
    a later real attempt.
    """
    return {
        (m.account, m.message_id)
        for m in moved_log
        if m.status == "moved"
    }


def select_candidates(
    signals: list[TickerSignal],
    moved_log: list[MovedMessage],
    skip_accounts: frozenset[str] = frozenset(),
) -> list[MoveCandidate]:
    """Return unique, not-yet-moved messages that have at least one ticker.

    Args:
        signals: All TickerSignals from today's (or a given) signals CSV.
        moved_log: All rows from the moved-message audit log.
        skip_accounts: Accounts to exclude entirely (e.g. an account whose
            IMAP server rejects the auth method this mover uses — see
            config.MOVE_SKIP_ACCOUNTS). Caller passes this in; domain layer
            does not read config directly.

    Returns:
        One MoveCandidate per unique (account, message_id), skipping any
        signal with an empty message_id (older CSVs predate this field),
        any account in skip_accounts, and any pair already marked 'moved'
        in the log.
    """
    skip = _already_moved(moved_log)
    counts: Counter[tuple[str, str]] = Counter()

    for sig in signals:
        if not sig.message_id:
            continue
        if sig.account in skip_accounts:
            continue
        key = (sig.account, sig.message_id)
        if key in skip:
            continue
        counts[key] += 1

    return [
        MoveCandidate(account=account, message_id=message_id, ticker_count=count)
        for (account, message_id), count in counts.items()
    ]
