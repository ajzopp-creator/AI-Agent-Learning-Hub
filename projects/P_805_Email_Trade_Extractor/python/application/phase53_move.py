"""Application: Phase 5.3 — move successfully-extracted messages via IMAP.

Workflow:
  1. Configure logging.
  2. Load today's signals CSV and the moved-message audit log.
  3. Resolve unique (account, message_id) candidates via domain.message_selector
     (skips signals with no message_id and anything already status='moved').
  4. For each account with at least one candidate, call
     infrastructure.imap_mover.move_message() per message.
  5. Append every attempt (moved/dry_run/not_found/failed) to the audit log.
  6. Log a summary.

This module owns orchestration only — no IMAP calls, no CSV parsing logic
live here directly; those stay in infrastructure/.
"""

import logging
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import config
from domain.message_selector import select_candidates
from infrastructure.daily_csv_reader import load_signals_csv
from infrastructure.imap_mover import move_message
from infrastructure.logging_setup import configure_logging
from infrastructure.moved_log import append_moved_log, load_moved_log
from schemas import MovedMessage

logger = logging.getLogger("p805")


def run(signals_path: Path | None = None) -> None:
    """Phase 5.3 entry point. Called from cli.py."""
    configure_logging()

    if signals_path is None:
        filename = config.DAILY_OUTPUT_CSV.format(date=date.today().isoformat())
        signals_path = config.DATA_DAILY_DIR / filename

    mode = "DRY RUN" if config.MOVE_DRY_RUN else "LIVE"
    logger.info(f"Phase 5.3 ({mode}): moving extracted messages from {signals_path.name}")
    if config.MOVE_SKIP_ACCOUNTS:
        logger.info(f"Skipping accounts (see config.MOVE_SKIP_ACCOUNTS): {sorted(config.MOVE_SKIP_ACCOUNTS)}")

    signals = load_signals_csv(signals_path)
    if not signals:
        logger.error("No signals loaded — aborting Phase 5.3.")
        sys.exit(1)

    moved_log = load_moved_log(config.MOVED_LOG_PATH)
    candidates = select_candidates(signals, moved_log, skip_accounts=frozenset(config.MOVE_SKIP_ACCOUNTS))
    logger.info(f"Candidates eligible for move: {len(candidates)}")

    if not candidates:
        logger.info("Nothing to move.")
        return

    results: dict[str, int] = {"moved": 0, "dry_run": 0, "not_found": 0, "failed": 0}
    new_entries: list[MovedMessage] = []

    logger.info("-" * 72)
    for cand in candidates:
        status = move_message(cand.account, cand.message_id)
        results[status] = results.get(status, 0) + 1
        new_entries.append(MovedMessage(
            message_id=cand.message_id,
            account=cand.account,
            ticker_count=cand.ticker_count,
            moved_at=datetime.now(timezone.utc),
            status=status,
            dry_run=config.MOVE_DRY_RUN,
        ))
    logger.info("-" * 72)

    append_moved_log(new_entries, config.MOVED_LOG_PATH)
    logger.info(
        f"Moved={results['moved']}  DryRun={results['dry_run']}  "
        f"NotFound={results['not_found']}  Failed={results['failed']}"
    )
