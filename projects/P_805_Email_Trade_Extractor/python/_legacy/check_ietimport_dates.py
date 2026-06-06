"""
P_805 diagnostic — find the newest message date in each INBOX mbox
under the IETimport profile. Confirms whether IETimport is the live
profile (newest dates from this week) or another archive.

Save location:
  C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\P_805_Email_Trade_Extractor\\python\\_legacy\\check_ietimport_dates.py
"""
import mailbox
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

PROFILE_ROOT = Path(
    r"C:\Users\Trader\AppData\Roaming\Thunderbird\Profiles"
    r"\m306ztzh.IETimport\ImapMail"
)

INBOXES = {
    "Yahoo":   PROFILE_ROOT / "imap.mail.yahoo.com"   / "INBOX",
    "Gmail":   PROFILE_ROOT / "imap.gmail-1.com"      / "INBOX",
    "iCloud":  PROFILE_ROOT / "imap.mail.me-1.com"    / "INBOX",
    "Outlook": PROFILE_ROOT / "outlook.office365.com" / "INBOX",
}


def parse_date(raw: str):
    """Parse an RFC 2822 Date header into a tz-aware datetime, or None."""
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def scan_mbox(label: str, path: Path) -> None:
    """Print message count plus oldest and newest message dates for one mbox."""
    if not path.exists():
        print(f"{label:8s}  MISSING  {path}")
        return
    box = mailbox.mbox(str(path))
    count = 0
    newest = None
    oldest = None
    for msg in box:
        count += 1
        dt = parse_date(msg.get("Date", ""))
        if dt is None:
            continue
        if newest is None or dt > newest:
            newest = dt
        if oldest is None or dt < oldest:
            oldest = dt
    box.close()
    print(f"{label:8s}  msgs={count:6d}  oldest={oldest}  newest={newest}")


def main() -> None:
    print(f"Scanning IETimport INBOX files at:\n  {PROFILE_ROOT}\n")
    for label, path in INBOXES.items():
        scan_mbox(label, path)


if __name__ == "__main__":
    main()
