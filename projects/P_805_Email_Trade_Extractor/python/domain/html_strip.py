"""Domain: HTML-to-text utility.

Pure-logic helper. Strips HTML tags and collapses whitespace. Safe to
run on plain text (no-op when there are no tags). Handles HTML entities
via convert_charrefs=True (so &amp; becomes &, etc.).

No I/O. No business logic specific to this project.
"""

import re
from html.parser import HTMLParser


class _HTMLStripper(HTMLParser):
    """Internal helper that collects text data while ignoring tags."""

    def __init__(self) -> None:
        super().__init__()
        self.convert_charrefs = True
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        self._chunks.append(data)

    def text(self) -> str:
        return " ".join(self._chunks)


def strip_html(text: str) -> str:
    """Strip HTML tags from text and collapse internal whitespace.

    Returns the input unchanged on parse error, then still collapses
    whitespace so downstream regex matching works consistently.
    """
    if not text:
        return ""
    try:
        stripper = _HTMLStripper()
        stripper.feed(text)
        out = stripper.text()
    except Exception:
        out = text
    return re.sub(r"\s+", " ", out).strip()
