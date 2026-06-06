"""Domain: ticker extraction from email text.

Pure-logic functions only — no I/O, no logging.

Design: patterns and direction keywords come in as parameters from the
caller (which reads them from config.py). This means new patterns or
keyword buckets can be added by editing config.py alone — no changes
needed in this module.

Each pattern is a dict with at least:
  - "name":       short identifier carried into output (e.g., "cashtag")
  - "regex":      a compiled-or-string pattern with EXACTLY ONE capture group
  - "confidence": label string ("high"/"medium"/"low") for downstream sorting

The blocklist applies only to patterns whose name contains 'paren' (the
extension hook for parenthesized patterns where false positives are
common). Cashtags and exchange-prefixed matches bypass the blocklist
because they're already high-precision.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TickerMatch:
    """One ticker hit produced by find_tickers()."""
    ticker: str
    pattern_name: str
    confidence: str
    context: str


def _grab_context(text: str, start: int, end: int, window: int) -> str:
    """Extract ~window chars centered on [start:end], with ellipses if trimmed."""
    lo = max(0, start - window // 2)
    hi = min(len(text), end + window // 2)
    snippet = text[lo:hi].strip()
    if lo > 0:
        snippet = "…" + snippet
    if hi < len(text):
        snippet = snippet + "…"
    return snippet


def find_tickers(
    text: str,
    patterns: list[dict],
    blocklist: set[str],
    context_chars: int = 80,
) -> list[TickerMatch]:
    """Run every pattern over text. Return one match per (ticker, pattern).

    Within a single pattern the same ticker may appear many times in the
    text; we keep only the first occurrence per pattern. Across patterns
    a ticker may match multiple times (e.g., once as exchange_paren and
    once as bare_paren) — those are returned separately so the caller
    can decide which one to keep.
    """
    if not text:
        return []
    results: list[TickerMatch] = []
    for pattern in patterns:
        seen_in_pattern: set[str] = set()
        for match in re.finditer(pattern["regex"], text):
            ticker = match.group(1).upper()
            if "paren" in pattern["name"] and ticker in blocklist:
                continue
            if ticker in seen_in_pattern:
                continue
            seen_in_pattern.add(ticker)
            results.append(TickerMatch(
                ticker=ticker,
                pattern_name=pattern["name"],
                confidence=pattern["confidence"],
                context=_grab_context(text, match.start(), match.end(), context_chars),
            ))
    return results


def infer_direction(
    context: str,
    keywords: dict[str, list[str]],
) -> str:
    """Return 'long', 'short', 'watch', or 'unknown' based on keyword scan.

    Iterates the keywords dict in order; first bucket with any hit wins.
    Case-insensitive; uses word-boundary-free contains check (a typical
    newsletter writes 'bullish' inside a sentence, not as a standalone
    token, so substring is what we want).
    """
    if not context:
        return "unknown"
    haystack = context.lower()
    for direction, words in keywords.items():
        for word in words:
            if word.lower() in haystack:
                return direction
    return "unknown"
