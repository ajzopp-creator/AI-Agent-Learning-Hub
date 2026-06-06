"""P_805 diagnostic — pull a sample of approved-sender bodies across all
four accounts so we can see how tickers actually appear in Tony's
newsletters before designing the regex extractor.

Writes the output to a file under python\\logs\\ (NOT to console) so
the Claude session can read it directly via the filesystem.

Strategy: up to 2 messages per approved sender, across all four
accounts, with full headers + plain-text body up to 2000 chars.
"""

import sys
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from html.parser import HTMLParser

# Make python/ directory importable so we can reuse existing modules.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from domain.headers import decode_header_safe
from domain.sender_filter import extract_email_address, is_approved
from infrastructure.mbox_reader import iter_mbox_messages, parse_message_date
from infrastructure.sender_sheet import load_enabled_senders


PER_SENDER_LIMIT = 2
BODY_PREVIEW_CHARS = 2000
OUTPUT_FILE = config.LOGS_DIR / "approved_bodies_sample.txt"


class _HTMLStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.convert_charrefs = True
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        self._chunks.append(data)

    def text(self) -> str:
        return " ".join(self._chunks)


def strip_html(text: str) -> str:
    """Strip HTML tags; collapse whitespace. Safe to run on plain text too."""
    try:
        stripper = _HTMLStripper()
        stripper.feed(text)
        out = stripper.text()
    except Exception:
        out = text
    return re.sub(r"\s+", " ", out).strip()


def extract_body(msg) -> str:
    """Pull the best available text body from a possibly-multipart message.

    Always runs strip_html at the end — some senders put HTML markup
    inside text/plain parts, so stripping unconditionally is safer.
    """
    if msg.is_multipart():
        plain = ""
        html = ""
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain" and not plain:
                try:
                    plain = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="ignore"
                    )
                except Exception:
                    pass
            elif ctype == "text/html" and not html:
                try:
                    html = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="ignore"
                    )
                except Exception:
                    pass
        raw = plain or html
    else:
        try:
            raw = msg.get_payload(decode=True).decode(
                msg.get_content_charset() or "utf-8", errors="ignore"
            )
        except Exception:
            raw = msg.get_payload() or ""
    return strip_html(raw)


def collect_samples(account: str, enabled: set[str]) -> list[dict]:
    """Walk one account's mbox; return up to PER_SENDER_LIMIT samples per sender."""
    relative = config.MBOX_FILES.get(account)
    if not relative:
        return []
    mbox_path = config.PROFILE_ROOT / relative
    if not mbox_path.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.SCAN_DAYS)
    seen: dict[str, int] = defaultdict(int)
    samples: list[dict] = []
    for msg in iter_mbox_messages(mbox_path):
        msg_date = parse_message_date(msg.get("Date"))
        if msg_date is None or msg_date < cutoff:
            continue
        sender = extract_email_address(msg.get("From"))
        if not is_approved(sender, enabled):
            continue
        if seen[sender] >= PER_SENDER_LIMIT:
            continue
        seen[sender] += 1
        samples.append({
            "account": account,
            "sender": sender,
            "subject": decode_header_safe(msg.get("Subject")),
            "date": str(msg_date),
            "body": extract_body(msg)[:BODY_PREVIEW_CHARS],
        })
    return samples


def main() -> None:
    enabled = load_enabled_senders()
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    all_samples: list[dict] = []
    for account in config.IMAP_ACCOUNT_ORDER:
        all_samples.extend(collect_samples(account, enabled))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(f"# P_805 approved-body sample dump\n")
        fh.write(f"# Generated: {datetime.now().isoformat()}\n")
        fh.write(f"# Total samples: {len(all_samples)}\n")
        fh.write(f"# Per-sender limit: {PER_SENDER_LIMIT}\n")
        fh.write(f"# Body preview: {BODY_PREVIEW_CHARS} chars\n\n")
        for sample in all_samples:
            fh.write("=" * 100 + "\n")
            fh.write(f"ACCOUNT: {sample['account']}\n")
            fh.write(f"FROM:    {sample['sender']}\n")
            fh.write(f"SUBJECT: {sample['subject']}\n")
            fh.write(f"DATE:    {sample['date']}\n")
            fh.write("-" * 100 + "\n")
            fh.write(sample["body"])
            fh.write("\n\n")
    print(f"Wrote {len(all_samples)} samples to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
