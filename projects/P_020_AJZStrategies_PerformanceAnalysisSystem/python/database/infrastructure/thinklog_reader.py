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

# Matches "M/D/YY HH:MM:SS" or "MM/DD/YYYY HH:MM:SS"
_TIMESTAMP_RE = re.compile(
    r"^\s*(\d{1,2})/(\d{1,2})/(\d{2,4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*$"
)
_SYMBOL_LINE_RE = re.compile(r"^\s*Symbol:\s*(\S+)\s*$", re.IGNORECASE)


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
            symbol = m.group(1).upper()
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
    Build {(symbol, date): concatenated_body} from records.
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
