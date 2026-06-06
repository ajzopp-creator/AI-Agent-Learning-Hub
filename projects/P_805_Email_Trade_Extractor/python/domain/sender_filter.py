"""Domain: pure-logic functions for sender filtering.

No I/O happens here — these functions take strings or sets and return
strings or booleans. Safely callable from any layer.
"""

from email.utils import parseaddr

from domain.headers import decode_header_safe


def extract_email_address(from_header: str | None) -> str | None:
    """Pull the bare email address out of a From: header.

    Decodes RFC 2047 encoding (e.g., =?utf-8?q?=20...?=), parses the
    'Display Name <addr@example.com>' pattern, and returns the address
    portion stripped and lowercased. Returns None if the header is empty
    or no address is parseable.
    """
    if not from_header:
        return None
    decoded = decode_header_safe(from_header)
    _, addr = parseaddr(decoded)
    if not addr:
        return None
    return addr.strip().lower()


def is_approved(address: str | None, enabled: set[str]) -> bool:
    """Return True if address is in the enabled-senders set.

    The enabled set is expected to contain lowercased addresses; callers
    should normalize on load (see infrastructure.sender_sheet).
    """
    if address is None:
        return False
    return address in enabled
