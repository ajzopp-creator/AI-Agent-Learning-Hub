"""Infrastructure: mbox file I/O using Python stdlib mailbox module.

Per Section 3.4 MUST rule: uses `mailbox.mbox()` exclusively. Never
splits raw mbox on ^From with regex, and never uses
`email.message_from_binary_file` with manual seek() — both approaches
fail on MIME boundaries containing "From " prefixes (Error Entry 001,
2026-04-17).

All I/O lives here. No business logic.
"""

import mailbox
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterator, List, Optional


# Thunderbird stores mail in two sibling subdirs of a profile. Live IMAP
# inboxes land in ImapMail/; POP mail and user-created archives land in Mail/.
_MAIL_SUBDIRS = ("Mail", "ImapMail")


def list_candidate_mbox_files(profile_root: Path) -> List[Path]:
    """Find mbox-like files under Mail/ and ImapMail/ of a Thunderbird profile.

    Thunderbird stores one mbox file per folder, with no file extension.
    Dirs ending in `.mozmsgs` hold attachment indexes and are skipped.

    Args:
        profile_root: The Thunderbird profile directory,
            e.g. `...\\Profiles\\2slie5gz.default-release`.

    Returns:
        Sorted list of candidate mbox file paths across Mail/ and ImapMail/.
        Empty list if neither subdir exists.
    """
    candidates: List[Path] = []
    for sub in _MAIL_SUBDIRS:
        base = profile_root / sub
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if any(part.endswith(".mozmsgs") for part in path.parts):
                continue
            if path.is_file() and path.suffix == "" and path.stat().st_size > 0:
                candidates.append(path)
    return sorted(candidates)


def parse_message_date(raw_date: Optional[str]) -> Optional[datetime]:
    """Parse an RFC 2822 Date header into a UTC-aware datetime.

    Args:
        raw_date: The raw Date header string from an email, or None.

    Returns:
        UTC-aware datetime, or None if raw_date is missing or unparseable.
    """
    if not raw_date:
        return None
    try:
        parsed = parsedate_to_datetime(raw_date)
    except (TypeError, ValueError):
        return None
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iter_mbox_messages(mbox_path: Path) -> Iterator:
    """Yield parsed messages from an mbox file one at a time.

    Uses a generator so large mbox files (hundreds of MB) don't need
    to load entirely into memory. The underlying file is closed when
    iteration completes or the generator is garbage-collected.

    Args:
        mbox_path: Absolute path to the mbox file.

    Yields:
        `email.message.Message` objects parsed by `mailbox.mbox()`.
    """
    mbox = mailbox.mbox(str(mbox_path))
    try:
        for msg in mbox:
            yield msg
    finally:
        mbox.close()
