"""
thinklog_parser.py — Domain layer.

Parses ThinkLog tag format: MMDD: [WHY] [SIG] free text

Pure functions only. No I/O, no DB, no file access.
Vocabulary is OPEN — parser does not validate WHY or SIG against any list.

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   domain
"""
from __future__ import annotations

import re
from typing import Optional, TypedDict

# Pattern: MMDD: [TAG1] [TAG2] rest
# - Groups 1-4 all optional to survive malformed or legacy entries
# - Tags are \w+ (alphanumeric + underscore), normalized to uppercase
_TAG_LINE_PATTERN = re.compile(
    r"^\s*"
    r"(?P<date>\d{3,4})?"             # MMDD or MDD
    r"\s*:?\s*"
    r"(?:\[(?P<tag1>\w+)\])?"         # [WHY]
    r"\s*"
    r"(?:\[(?P<tag2>\w+)\])?"         # [SIG]
    r"\s*"
    r"(?P<rest>.*?)"                  # free text
    r"\s*$"
)


class ParsedThinkLog(TypedDict):
    date_token: Optional[str]
    reason: Optional[str]
    signal_strength: Optional[str]
    notes: Optional[str]
    raw: str


def parse_thinklog_line(line: str) -> ParsedThinkLog:
    """
    Parse a single ThinkLog tag line.

    Returns a ParsedThinkLog dict with all four fields.
    Missing fields are None. Never raises.
    """
    raw = line if line is not None else ""
    stripped = raw.strip()

    if not stripped:
        return ParsedThinkLog(
            date_token=None, reason=None, signal_strength=None,
            notes=None, raw=raw,
        )

    m = _TAG_LINE_PATTERN.match(stripped)
    if not m:
        return ParsedThinkLog(
            date_token=None, reason=None, signal_strength=None,
            notes=stripped or None, raw=raw,
        )

    date_token = m.group("date")
    tag1 = m.group("tag1")
    tag2 = m.group("tag2")
    rest = m.group("rest") or None

    # If no date prefix and no tags, treat entire line as notes
    if date_token is None and tag1 is None and tag2 is None:
        return ParsedThinkLog(
            date_token=None, reason=None, signal_strength=None,
            notes=stripped, raw=raw,
        )

    return ParsedThinkLog(
        date_token=date_token,
        reason=tag1.upper() if tag1 else None,
        signal_strength=tag2.upper() if tag2 else None,
        notes=rest,
        raw=raw,
    )


def parse_thinklog_note(text: str) -> ParsedThinkLog:
    """
    Parse a full ThinkLog note. Takes the first non-empty line as the tag line.

    Additional lines below the tag line are appended to notes with a pipe separator.
    """
    if not text:
        return ParsedThinkLog(
            date_token=None, reason=None, signal_strength=None,
            notes=None, raw=text or "",
        )

    lines = text.splitlines()
    first_idx = next((i for i, ln in enumerate(lines) if ln.strip()), None)
    if first_idx is None:
        return ParsedThinkLog(
            date_token=None, reason=None, signal_strength=None,
            notes=None, raw=text,
        )

    parsed = parse_thinklog_line(lines[first_idx])
    extra = [ln.strip() for ln in lines[first_idx + 1:] if ln.strip()]

    if extra:
        combined = parsed["notes"] or ""
        tail = " | ".join(extra)
        parsed["notes"] = (combined + " | " + tail).strip(" |") if combined else tail

    parsed["raw"] = text
    return parsed
