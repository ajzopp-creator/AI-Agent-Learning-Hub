"""One-off diagnostic: scan P_805's INBOX + spam/junk mbox exports across all
four accounts for sender addresses not yet on the approved-sender whitelist,
and write a candidate-senders report for Tony to review.

Read-only. Never touches sender_sheet.csv, never moves/deletes mail, no IMAP
connection, no keyring, no LLM calls -- pure local mbox parsing via P_805's
existing infrastructure.mbox_reader (mailbox.mbox() per Entry 001; never a
regex split on mbox content).

Staged per peh-handoff SKILL.md at Tony's explicit request, 2026-08-24 --
execution handed to Claude Code rather than run live through this chat's
Windows-MCP relay.
"""

import csv
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor")
sys.path.insert(0, str(PROJECT_ROOT / "python"))

import config  # noqa: E402
from infrastructure.mbox_reader import iter_mbox_messages, parse_message_date  # noqa: E402
from domain.sender_filter import extract_email_address  # noqa: E402
from domain.headers import decode_header_safe  # noqa: E402

# Spam/junk mbox paths per account -- not in config.py yet (P_805 has never
# scanned these); confirmed present on disk 2026-08-24, real content in all four.
SPAM_MBOX_FILES: dict[str, str] = {
    "icloud":  r"ImapMail\imap.mail.me-1.com\Junk",
    "gmail":   r"ImapMail\imap.gmail-1.com\[Gmail].sbd\Spam",
    "outlook": r"ImapMail\outlook.office365.com\Junk",
    "yahoo":   r"ImapMail\imap.mail.yahoo.com\Bulk",
}

OUTPUT_DIR = config.DATA_DIR / "candidate_senders"
TODAY = datetime.now(timezone.utc).date()
OUTPUT_PATH = OUTPUT_DIR / f"{TODAY.isoformat()}_candidate_senders.csv"
DONE_PATH = Path(__file__).with_name(Path(__file__).name + ".done")


def load_all_whitelist_addresses() -> set[str]:
    """Return every email_address in sender_sheet.csv, enabled or not.

    Broader than infrastructure.sender_sheet.load_enabled_senders() on
    purpose -- a sender Tony already disabled shouldn't resurface as a
    'candidate' just because it's still landing in spam.
    """
    addresses: set[str] = set()
    if not config.SENDER_SHEET.exists():
        return addresses
    with open(config.SENDER_SHEET, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            addr = (row.get("email_address") or "").strip().lower()
            if addr:
                addresses.add(addr)
    return addresses


def scan_mailbox(mbox_path, account, mailbox_type, cutoff, whitelist, excluded):
    """Yield (address, subject, date, account, mailbox_type) for one mbox file.

    Skips: unparseable/missing From, whitelisted addresses (enabled or
    disabled), excluded-substring matches, and anything older than cutoff
    (messages with no parseable Date header are kept -- better a false
    positive Tony can ignore than a silent gap).
    """
    if not mbox_path.exists():
        print(f"  [skip] {mbox_path} not found")
        return
    count = 0
    for msg in iter_mbox_messages(mbox_path):
        from_header = msg.get("From")
        address = extract_email_address(from_header)
        if not address or address in whitelist:
            continue
        if any(sub in (from_header or "").lower() for sub in excluded):
            continue
        date = parse_message_date(msg.get("Date"))
        if date is not None and date < cutoff:
            continue
        subject = decode_header_safe(msg.get("Subject"))
        count += 1
        yield (address, subject, date, account, mailbox_type)
    print(f"  [{account}/{mailbox_type}] {count} candidate messages")


def aggregate_candidates(records):
    """Collapse per-message records into one row per unique sender address."""
    agg = {}
    for address, subject, date, account, mailbox_type in records:
        row = agg.setdefault(address, {
            "count": 0, "accounts": set(), "mailbox_types": set(),
            "first_seen": date, "last_seen": date, "example_subject": subject,
        })
        row["count"] += 1
        row["accounts"].add(account)
        row["mailbox_types"].add(mailbox_type)
        if date is not None:
            if row["first_seen"] is None or date < row["first_seen"]:
                row["first_seen"] = date
            if row["last_seen"] is None or date > row["last_seen"]:
                row["last_seen"] = date
    return agg


def write_report(agg, output_path):
    """Write one CSV row per unique candidate sender, busiest first."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(agg.items(), key=lambda kv: kv[1]["count"], reverse=True)
    with open(output_path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "email_address", "occurrence_count", "accounts_seen",
            "mailbox_types", "first_seen", "last_seen", "example_subject",
        ])
        for address, row in rows:
            writer.writerow([
                address,
                row["count"],
                "|".join(sorted(row["accounts"])),
                "|".join(sorted(row["mailbox_types"])),
                row["first_seen"].date().isoformat() if row["first_seen"] else "",
                row["last_seen"].date().isoformat() if row["last_seen"] else "",
                row["example_subject"][:150],
            ])
    return len(rows)


def write_done_marker(status, exit_code):
    """peh-handoff completion signal -- written inline, not via a helper."""
    DONE_PATH.write_text(
        f"status={status}\nexit_code={exit_code}\n"
        f"timestamp={datetime.now(timezone.utc).isoformat()}\n",
        encoding="utf-8",
    )


def main():
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.SCAN_DAYS)
    whitelist = load_all_whitelist_addresses()
    if not whitelist:
        print("FAIL: sender_sheet.csv empty or unreadable -- aborting.")
        write_done_marker("FAIL", 1)
        sys.exit(1)
    print(f"Whitelist loaded: {len(whitelist)} addresses (enabled + disabled)")
    print(f"Lookback: {config.SCAN_DAYS} days (cutoff {cutoff.date().isoformat()})")

    records = []
    for account in config.IMAP_ACCOUNT_ORDER:
        # MBOX_FILES (and SPAM_MBOX_FILES) already start with ImapMail\;
        # join to PROFILE_ROOT, matching application.phase1_scan.
        inbox_path = config.PROFILE_ROOT / config.MBOX_FILES[account]
        spam_path = config.PROFILE_ROOT / SPAM_MBOX_FILES[account]
        records.extend(scan_mailbox(
            inbox_path, account, "regular", cutoff, whitelist, config.EXCLUDED_SENDER_SUBSTRINGS,
        ))
        records.extend(scan_mailbox(
            spam_path, account, "spam", cutoff, whitelist, config.EXCLUDED_SENDER_SUBSTRINGS,
        ))

    agg = aggregate_candidates(records)
    row_count = write_report(agg, OUTPUT_PATH)
    print(f"Candidates written: {row_count} unique senders -> {OUTPUT_PATH}")
    print("PASS")
    write_done_marker("PASS", 0)


if __name__ == "__main__":
    main()
