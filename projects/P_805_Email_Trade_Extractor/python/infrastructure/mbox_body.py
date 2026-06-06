"""Infrastructure: extract a plain-text body from an email.message.Message.

Handles the messy reality of email bodies:
  - Multipart messages: prefer text/plain part; fall back to text/html
  - Encoding: trust Content-Charset, fall back to utf-8 with errors='ignore'
  - Some senders put HTML markup inside text/plain parts — strip_html runs
    unconditionally at the end to clean those up too

Returns a single whitespace-collapsed string suitable for regex matching.
Returns "" on any failure rather than raising, so callers don't need
try/except for every message.
"""

from email.message import Message

from domain.html_strip import strip_html


def _decode_part(part: Message) -> str:
    """Decode one MIME part's payload to a string. '' on failure."""
    try:
        raw = part.get_payload(decode=True)
        if raw is None:
            return ""
        charset = part.get_content_charset() or "utf-8"
        return raw.decode(charset, errors="ignore")
    except Exception:
        return ""


def extract_body(msg: Message) -> str:
    """Return the best available plain-text body for an email message.

    Prefers text/plain, falls back to text/html, runs HTML strip on
    whatever is selected (defensive — some plain parts contain markup).
    """
    if msg.is_multipart():
        plain = ""
        html = ""
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain" and not plain:
                plain = _decode_part(part)
            elif ctype == "text/html" and not html:
                html = _decode_part(part)
        raw = plain or html
    else:
        raw = _decode_part(msg)
        if not raw:
            # get_payload(decode=False) returns the unencoded payload, which
            # for some malformed messages is the only thing available.
            try:
                raw = msg.get_payload() or ""
            except Exception:
                raw = ""
    return strip_html(raw)
