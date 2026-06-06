"""Phase 1 diagnostic — scans all live IMAP inbox mbox files under the profile
and reports each one's message count + oldest/newest date.

Purpose: find which inbox caches are actually current vs. stale, so we can
point MBOX_FILE at a useful one.

Run:
    python check_all_inboxes.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from infrastructure.mbox_reader import iter_mbox_messages, parse_message_date


# Candidate inbox paths, relative to PROFILE_ROOT.
CANDIDATES = [
    r"ImapMail\imap.gmail-1.com\INBOX",
    r"ImapMail\imap.mail.yahoo.com\INBOX",
    r"ImapMail\imap.mail.me-1.com\INBOX-1",
    r"ImapMail\imap.mail.me.com\INBOX-1",
]


def report(rel_path: str) -> None:
    """Print summary stats for one mbox file."""
    mbox_path = config.PROFILE_ROOT / rel_path
    print(f"\n{rel_path}")
    if not mbox_path.exists():
        print("  (file does not exist)")
        return
    size_mb = mbox_path.stat().st_size / (1024 * 1024)
    print(f"  size: {size_mb:.2f} MB")
    total = 0
    parsed = []
    for msg in iter_mbox_messages(mbox_path):
        total += 1
        dt = parse_message_date(msg.get("Date"))
        if dt is not None:
            parsed.append(dt)
    print(f"  messages: {total}")
    if parsed:
        parsed.sort()
        print(f"  oldest:   {parsed[0].isoformat()}")
        print(f"  newest:   {parsed[-1].isoformat()}")


def main() -> None:
    print(f"Profile: {config.PROFILE_ROOT}")
    for rel in CANDIDATES:
        report(rel)

    # Also list anything else that looks like an inbox we haven't thought of
    imap_root = config.IMAP_ROOT
    print(f"\n--- All non-empty files directly under ImapMail\\<server>\\ ---")
    if imap_root.exists():
        for server_dir in sorted(imap_root.iterdir()):
            if not server_dir.is_dir():
                continue
            for child in sorted(server_dir.iterdir()):
                if child.is_file() and child.suffix == "" and child.stat().st_size > 0:
                    size_kb = child.stat().st_size / 1024
                    print(f"  {size_kb:>10.1f} KB   {child.relative_to(imap_root)}")


if __name__ == "__main__":
    main()
