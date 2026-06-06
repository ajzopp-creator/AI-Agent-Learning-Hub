"""Domain: RFC 2047 mail header decoding.

Pure functions — no I/O, no dependencies on other project modules.
Testable in isolation.
"""

from email.header import decode_header, make_header
from typing import Optional


def decode_header_safe(raw_value: Optional[str]) -> str:
    """Decode an RFC 2047 encoded mail header into a plain unicode string.

    Mail subjects and sender names often arrive encoded as tokens like
    =?UTF-8?B?...?= or =?ISO-8859-1?Q?...?=. This function converts them
    to their unicode form. If decoding fails for any reason, the raw
    value is returned unchanged so downstream code always receives a
    string rather than an exception.

    Args:
        raw_value: The raw header string from an email message, or None
            if the header is missing.

    Returns:
        The decoded header as a plain unicode string. Empty string if
        raw_value is None.
    """
    if raw_value is None:
        return ""
    try:
        return str(make_header(decode_header(raw_value)))
    except Exception:
        return str(raw_value)
