"""
thinklog_reader.py - Infrastructure layer.

Parses the TOS ThinkLog CSV export. The export is record-based, not row-based:
each entry is a 4-line block separated by blank lines:

    HEADER LINE       (usually symbol, sometimes a full order string)
    M/D/YY HH:MM:SS   (timestamp)
    BODY              (free text, may be quoted with embedded newlines)
    Symbol: XXX       (the reliable symbol field)

The first non-empty line at the top of the file is "thinkLog" (a section
header); the reader skips the file preamble until it finds the first record.

Multiple entries for the same (symbol, date) are concatenated with " | "
in chronological order.

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   infrastructure
"""
from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from domain.thinklog_parser import ParsedThinkLog, parse_thinklog_entries

# Matches "M/D/YY HH:MM:SS" or "MM/DD/YYYY HH:MM:SS"
_TIMESTAMP_RE = re.compile(
    r"^\s*(\d{1,2})/(\d{1,2})/(\d{2,4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*$"
)
_SYMBOL_LINE_RE = re.compile(r"^\s*Symbol:\s*(\S+)\s*$", re.IGNORECASE)

# TOS's "Symbol:" field carries the full OCC option symbol on option
# entries, e.g. ".DINO260918C92.5" -- underlying + expiry + C/P + strike.
# Real trades.underlying_symbol is always the bare ticker ("DINO"), so
# this must be stripped at read time or every option ThinkLog entry
# silently fails to match (found 2026-08-16, real export, Tony's DINO
# entry). Matches an optional leading '.', captures leading letters,
# requires the OCC date digits to follow -- plain tickers with no
# trailing digits (SWPPX, QQQ) are untouched.
_OCC_SYMBOL_RE = re.compile(r"^\.?([A-Z]+)\d")


def _normalize_symbol(raw: str) -> str:
    """Strip OCC option-symbol suffix down to the bare underlying ticker.

    '.DINO260918C92.5' -> 'DINO'. Plain tickers (no trailing digits,
    e.g. 'IWM', 'SWPPX') pass through unchanged aside from case/dot.
    """
    s = raw.strip().upper()
    m = _OCC_SYMBOL_RE.match(s)
    return m.group(1) if m else s.lstrip(".")


def _parse_timestamp(s: str) -> Optional[datetime]:
    m = _TIMESTAMP_RE.match(s)
    if not m:
        return None
    mo, d, y, hh, mm, ss = m.groups()
    mo, d, y, hh, mm = int(mo), int(d), int(y), int(hh), int(mm)
    ss = int(ss) if ss else 0
    if y < 100:
        y += 2000
    try:
        return datetime(y, mo, d, hh, mm, ss)
    except ValueError:
        return None


def _split_records(text: str) -> List[List[str]]:
    """Split file content into records on blank lines."""
    lines = text.splitlines()
    if lines and lines[0].startswith("\ufeff"):
        lines[0] = lines[0].lstrip("\ufeff")

    records: List[List[str]] = []
    current: List[str] = []
    for ln in lines:
        if ln.strip() == "":
            if current:
                records.append(current)
                current = []
        else:
            current.append(ln)
    if current:
        records.append(current)
    return records


def _parse_record(block: List[str]) -> Optional[Dict]:
    """
    Parse one record block into {symbol, date, datetime, body}.
    Returns None if the block doesn't look like a ThinkLog entry.
    """
    if len(block) < 3:
        return None

    ts_idx = None
    for i, ln in enumerate(block):
        if _TIMESTAMP_RE.match(ln):
            ts_idx = i
            break
    if ts_idx is None:
        return None

    ts = _parse_timestamp(block[ts_idx])
    if ts is None:
        return None

    symbol = None
    for ln in block:
        m = _SYMBOL_LINE_RE.match(ln)
        if m:
            symbol = _normalize_symbol(m.group(1))
            break
    if not symbol:
        return None

    body_lines: List[str] = []
    for ln in block[ts_idx + 1:]:
        if _SYMBOL_LINE_RE.match(ln):
            break
        body_lines.append(ln)
    body = "\n".join(body_lines).strip()
    if body.startswith('"') and body.endswith('"') and len(body) >= 2:
        body = body[1:-1].strip()

    return {
        "symbol": symbol,
        "date": ts.date(),
        "datetime": ts,
        "body": body,
    }


def read_thinklog_csv(path: Path) -> List[Dict]:
    """
    Read a TOS ThinkLog CSV export. Returns a list of records:
        [{symbol, date, datetime, body}, ...]
    Never raises on malformed entries — bad blocks are silently skipped.
    """
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return []

    records = []
    for block in _split_records(text):
        rec = _parse_record(block)
        if rec is not None:
            records.append(rec)
    return records


def build_lookup(records: List[Dict]) -> Dict[Tuple[str, date], str]:
    """
    Build {(symbol, date): concatenated_body} from records. PAPER-ONLY --
    keys on the record's own timestamp date, whole body as one string.
    Live notes need per-line dated entries; see build_multi_entry_lookup().

    Multiple entries for same key are joined with ' | ' chronologically.
    """
    grouped: Dict[Tuple[str, date], List[Tuple[datetime, str]]] = {}
    for rec in records:
        key = (rec["symbol"], rec["date"])
        grouped.setdefault(key, []).append((rec["datetime"], rec["body"]))

    lookup: Dict[Tuple[str, date], str] = {}
    for key, entries in grouped.items():
        entries.sort(key=lambda x: x[0])
        bodies = [b for _, b in entries if b]
        lookup[key] = " | ".join(bodies) if bodies else ""
    return lookup


def get_body_for_trade(
    lookup: Dict[Tuple[str, date], str],
    symbol: str,
    trade_date,
) -> Optional[str]:
    """Look up concatenated ThinkLog body for (symbol, date). None if no match."""
    if not symbol or trade_date is None:
        return None

    if isinstance(trade_date, str):
        try:
            d = date.fromisoformat(trade_date[:10])
        except ValueError:
            return None
    elif isinstance(trade_date, datetime):
        d = trade_date.date()
    elif isinstance(trade_date, date):
        d = trade_date
    else:
        return None

    return lookup.get((symbol.upper(), d))


def _mmdd_to_month_day(token: str) -> Optional[Tuple[int, int]]:
    """Parse a 3- or 4-digit MMDD/MDD token into (month, day). None if invalid."""
    if len(token) == 4:
        mm, dd = int(token[:2]), int(token[2:])
    elif len(token) == 3:
        mm, dd = int(token[0]), int(token[1:])
    else:
        return None
    if not (1 <= mm <= 12 and 1 <= dd <= 31):
        return None
    return mm, dd


def _resolve_entry_date(mmdd_token: str, record_date: date) -> Optional[date]:
    """Resolve an embedded MMDD token to a real date, anchored to the
    record's own timestamp date.

    Tries the record's own year first. A resolved date more than 60 days
    AFTER the record's own date is implausible (an entry can't post-date
    the note it's written in by that much) -- falls back to year - 1,
    which handles a January record still referencing a prior December
    entry in the same running note.
    """
    parsed = _mmdd_to_month_day(mmdd_token)
    if parsed is None:
        return None
    mm, dd = parsed
    try:
        candidate = date(record_date.year, mm, dd)
    except ValueError:
        return None
    if (candidate - record_date).days > 60:
        try:
            candidate = date(record_date.year - 1, mm, dd)
        except ValueError:
            pass
    return candidate


def build_multi_entry_lookup(
    records: List[Dict],
) -> Dict[Tuple[str, date], ParsedThinkLog]:
    """
    Build a per-line-dated lookup for LIVE ThinkLog notes.

    Unlike build_lookup() (record-level date, whole body as one opaque
    string -- paper only), this explodes each record's body into one
    entry per embedded MMDD-prefixed line via
    domain.thinklog_parser.parse_thinklog_entries(), keyed by that
    line's own resolved date -- not the record's outer timestamp date.

    Entries with no extracted reason (a dated line whose [WHY] tag
    failed to parse -- malformed brackets, stray whitespace, etc.) are
    skipped entirely rather than written to the lookup. Real case found
    2026-08-16: TOS export had two DINO entries for the same date, one
    with a valid tag and one with a typo'd '{P_116]' that failed to
    parse -- without this guard, the broken entry (processed second)
    silently overwrote the valid one for the same (symbol, date) key.

    Args:
        records: Output of read_thinklog_csv().

    Returns:
        {(symbol, resolved_date): ParsedThinkLog} -- values are already
        fully parsed (reason, signal_strength, notes), no second parse
        pass needed by the caller. Only entries with a non-empty reason
        are included.
    """
    lookup: Dict[Tuple[str, date], ParsedThinkLog] = {}
    for rec in records:
        for entry in parse_thinklog_entries(rec["body"]):
            if not entry["reason"]:
                continue
            resolved = _resolve_entry_date(entry["date_token"], rec["date"])
            if resolved is None:
                continue
            lookup[(rec["symbol"], resolved)] = entry
    return lookup
