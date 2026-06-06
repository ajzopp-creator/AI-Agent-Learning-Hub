"""Application: Phase 1 scan with sender filtering and structured logging.

Workflow:
  1. Configure logging (main + reject loggers).
  2. Load the enabled-senders set from sender_sheet.csv.
  3. For each account in IMAP_ACCOUNT_ORDER (or just one if requested):
       - Open the mbox.
       - For every message inside SCAN_DAYS:
           · Approved sender → log row at DEBUG (file only).
           · Rejected sender → log to rejects file (file only).
       - Emit a per-account summary at INFO (console + main log).
  4. Emit a grand-total summary at INFO.

No I/O or parsing happens here directly — this module composes the
domain and infrastructure layers.
"""

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import config
from domain.headers import decode_header_safe
from domain.sender_filter import extract_email_address, is_approved
from infrastructure.logging_setup import configure_logging
from infrastructure.mbox_reader import iter_mbox_messages, parse_message_date
from infrastructure.sender_sheet import load_enabled_senders

logger = logging.getLogger("p805")
reject_logger = logging.getLogger("p805.rejects")


def summarize_mbox(
    mbox_path: Path,
    scan_days: int,
    enabled: set[str],
    account: str,
) -> tuple[int, int, int, int]:
    """Scan one mbox; classify approved vs rejected; log at appropriate levels.

    Returns (total_in_file, in_window, approved, rejected).
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=scan_days)
    total = 0
    in_window = 0
    approved = 0
    rejected = 0
    logger.debug(f"--- Reading {account}: {mbox_path} ---")
    for msg in iter_mbox_messages(mbox_path):
        total += 1
        msg_date = parse_message_date(msg.get("Date"))
        if msg_date is None or msg_date < cutoff:
            continue
        in_window += 1
        sender_addr = extract_email_address(msg.get("From"))
        subject = decode_header_safe(msg.get("Subject"))[:60]
        stamp = msg_date.strftime("%Y-%m-%d %H:%M")
        if is_approved(sender_addr, enabled):
            approved += 1
            logger.debug(
                f"[KEEP] {account:7s} | {stamp} | {sender_addr:<40} | {subject}"
            )
        else:
            rejected += 1
            reject_logger.info(
                f"account={account} address={sender_addr} subject={subject!r}"
            )
    return total, in_window, approved, rejected


def scan_account(account_name: str, enabled: set[str]) -> tuple[int, int, int, int]:
    """Resolve mbox path for one account, scan it, log per-account summary."""
    relative = config.MBOX_FILES.get(account_name)
    if relative is None:
        logger.warning(f"Unknown account '{account_name}'.")
        return 0, 0, 0, 0
    mbox_path = config.PROFILE_ROOT / relative
    if not mbox_path.exists():
        logger.warning(f"[{account_name}] mbox not found: {mbox_path}")
        return 0, 0, 0, 0
    total, in_window, approved, rejected = summarize_mbox(
        mbox_path, config.SCAN_DAYS, enabled, account_name
    )
    logger.info(
        f"[{account_name:7s}] file={total:5d}  window={in_window:5d}  "
        f"approved={approved:4d}  rejected={rejected:5d}"
    )
    return total, in_window, approved, rejected


def run(account: str | None = None) -> None:
    """Phase 1 entry point. Called from cli.py."""
    configure_logging()
    enabled = load_enabled_senders()
    if not enabled:
        logger.error("No enabled senders loaded — aborting scan.")
        return
    targets = [account] if account else list(config.IMAP_ACCOUNT_ORDER)
    logger.info(f"Scanning {len(targets)} account(s): {', '.join(targets)}")
    logger.info(
        f"Lookback: {config.SCAN_DAYS} days  |  Enabled senders: {len(enabled)}"
    )
    logger.info("-" * 72)
    grand = [0, 0, 0, 0]
    for name in targets:
        result = scan_account(name, enabled)
        for i, val in enumerate(result):
            grand[i] += val
    if len(targets) > 1:
        logger.info("-" * 72)
        logger.info(
            f"GRAND TOTAL  file={grand[0]}  window={grand[1]}  "
            f"approved={grand[2]}  rejected={grand[3]}"
        )
