"""Application: Phase 3 — extract tickers from approved emails into a daily CSV.

Workflow:
  1. Configure logging.
  2. Load the enabled-senders set from sender_sheet.csv.
  3. For each account in IMAP_ACCOUNT_ORDER (or one if --account given):
       - Open the mbox.
       - For every approved, non-excluded message inside SCAN_DAYS:
           · Pull plain-text body (subject + body combined).
           · Run config.TICKER_PATTERNS over the text.
           · For each unique ticker found in the message, keep the
             highest-confidence match; infer direction from context;
             build a TickerSignal.
  4. Validate every signal through the Pydantic schema, then write
     them to data/daily/{today}_signals.csv.
"""

import csv
import logging
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import config
from domain.headers import decode_header_safe
from domain.sender_filter import extract_email_address, is_approved
from domain.ticker_extractor import find_tickers, infer_direction, TickerMatch
from infrastructure.logging_setup import configure_logging
from infrastructure.mbox_body import extract_body
from infrastructure.mbox_reader import iter_mbox_messages, parse_message_date
from infrastructure.sender_sheet import load_enabled_senders
from schemas import TickerSignal

logger = logging.getLogger("p805")

_CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1}


def _is_excluded(raw_from: str | None) -> bool:
    """Substring-match the From header against EXCLUDED_SENDER_SUBSTRINGS."""
    if not raw_from:
        return False
    haystack = raw_from.lower()
    return any(sub in haystack for sub in config.EXCLUDED_SENDER_SUBSTRINGS)


def _best_per_ticker(matches: list[TickerMatch]) -> dict[str, TickerMatch]:
    """Reduce many matches to one per ticker, keeping highest confidence."""
    best: dict[str, TickerMatch] = {}
    for m in matches:
        rank = _CONFIDENCE_RANK.get(m.confidence, 0)
        existing = best.get(m.ticker)
        if existing is None or rank > _CONFIDENCE_RANK.get(existing.confidence, 0):
            best[m.ticker] = m
    return best


def _build_signal(
    match: TickerMatch,
    msg_date: datetime,
    sender_addr: str,
    raw_from: str,
    subject: str,
    account: str,
    message_id: str,
) -> TickerSignal:
    """Wrap one TickerMatch into a validated TickerSignal."""
    direction = infer_direction(match.context, config.DIRECTION_KEYWORDS)
    sender_name = decode_header_safe(raw_from).split("<")[0].strip().strip('"')
    return TickerSignal(
        ticker=match.ticker,
        direction=direction,
        confidence=match.confidence,
        pattern=match.pattern_name,
        source_address=sender_addr,
        source_name=sender_name or None,
        timestamp=msg_date,
        subject=subject[:200],
        raw_context=match.context[:config.RAW_CONTEXT_CHARS],
        account=account,
        message_id=message_id,
    )


def scan_account(account: str, enabled: set[str]) -> list[TickerSignal]:
    """Scan one account; return all TickerSignals extracted from approved mail."""
    relative = config.MBOX_FILES.get(account)
    if not relative:
        logger.warning(f"Unknown account '{account}'.")
        return []
    mbox_path = config.PROFILE_ROOT / relative
    if not mbox_path.exists():
        logger.warning(f"[{account}] mbox not found: {mbox_path}")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=config.SCAN_DAYS)
    signals: list[TickerSignal] = []
    approved_count = 0
    extracted_count = 0
    for msg in iter_mbox_messages(mbox_path):
        msg_date = parse_message_date(msg.get("Date"))
        if msg_date is None or msg_date < cutoff:
            continue
        raw_from = msg.get("From") or ""
        sender_addr = extract_email_address(raw_from)
        if not is_approved(sender_addr, enabled) or _is_excluded(raw_from):
            continue
        approved_count += 1
        subject = decode_header_safe(msg.get("Subject"))
        message_id = (msg.get("Message-ID") or "").strip()
        body = extract_body(msg)
        text = f"{subject}\n\n{body}"
        matches = find_tickers(
            text, config.TICKER_PATTERNS, config.BARE_PAREN_BLOCKLIST,
        )
        if not matches:
            continue
        best = list(_best_per_ticker(matches).values())
        cap = config.SENDER_MAX_TICKERS.get(sender_addr.lower())
        if cap is not None and len(best) > cap:
            logger.debug(
                f"[{account}] {sender_addr}: capped {len(best)} → {cap} tickers"
            )
            best = best[:cap]
        for match in best:
            signals.append(_build_signal(
                match, msg_date, sender_addr, raw_from, subject, account, message_id,
            ))
            extracted_count += 1
    logger.info(
        f"[{account:7s}] approved={approved_count:4d}  "
        f"signals={len(signals):4d}  extractions={extracted_count}"
    )
    return signals


def write_csv(signals: list[TickerSignal], output_path: Path) -> None:
    """Write one TickerSignal per row to a CSV; create parent dir if needed."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(TickerSignal.model_fields.keys())
    with open(output_path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for sig in signals:
            row = sig.model_dump()
            row["timestamp"] = sig.timestamp.isoformat()
            writer.writerow(row)


def run(account: str | None = None) -> None:
    """Phase 3 entry point. Called from cli.py."""
    configure_logging()
    enabled = load_enabled_senders()
    if not enabled:
        logger.error("No enabled senders loaded — aborting Phase 3.")
        sys.exit(1)
    targets = [account] if account else list(config.IMAP_ACCOUNT_ORDER)
    logger.info(f"Phase 3: extracting from {len(targets)} account(s)")
    logger.info(f"Patterns: {[p['name'] for p in config.TICKER_PATTERNS]}")
    logger.info("-" * 72)
    all_signals: list[TickerSignal] = []
    for name in targets:
        all_signals.extend(scan_account(name, enabled))
    logger.info("-" * 72)
    output_path = config.DATA_DAILY_DIR / config.DAILY_OUTPUT_CSV.format(
        date=date.today().isoformat()
    )
    write_csv(all_signals, output_path)
    logger.info(f"GRAND TOTAL signals: {len(all_signals)}")
    logger.info(f"Wrote: {output_path}")
