"""Domain: consensus ranking logic for Phase 4.

Pure functions only — no I/O, no logging, no external calls.
Receives a list of TickerSignal objects, returns a list of RankedSignal
objects sorted by source_count descending, then last_seen descending.
"""

from collections import Counter, defaultdict
from typing import Optional

from schemas import RankedSignal, TickerSignal


def _majority_direction(directions: list[str]) -> str:
    """Return the most common non-unknown direction, or 'unknown'."""
    known = [d for d in directions if d != "unknown"]
    if not known:
        return "unknown"
    return Counter(known).most_common(1)[0][0]


def build_ranked_signals(
    signals: list[TickerSignal],
    consensus_threshold: int = 2,
    sector_map: Optional[dict[str, str]] = None,
) -> list[RankedSignal]:
    """Deduplicate signals by ticker, compute consensus, return ranked list.

    Args:
        signals: All TickerSignal rows from today's CSV.
        consensus_threshold: Minimum distinct sources for inclusion.
        sector_map: lowercased source_address -> sector, from
            infrastructure.sender_sheet.load_sender_sectors(). Addresses
            absent from the map are treated as sector 'unknown'. Pass
            None (default) to skip sector weighting entirely — every
            ticker then gets sector_count=1.

    Returns:
        List of RankedSignal sorted by source_count desc, last_seen desc.
        Only tickers meeting the threshold are included.
    """
    sector_map = sector_map or {}

    # Group signals by ticker (case-normalised)
    by_ticker: dict[str, list[TickerSignal]] = defaultdict(list)
    for sig in signals:
        by_ticker[sig.ticker.upper()].append(sig)

    ranked: list[RankedSignal] = []

    for ticker, sigs in by_ticker.items():
        unique_sources = list({s.source_address for s in sigs})
        source_count = len(unique_sources)

        if source_count < consensus_threshold:
            continue

        directions = [s.direction for s in sigs]
        timestamps = [s.timestamp for s in sigs]

        sectors = {
            sector_map.get(addr.lower(), "unknown") for addr in unique_sources
        }
        sector_count = len(sectors)

        ranked.append(
            RankedSignal(
                ticker=ticker,
                source_count=source_count,
                sector_count=sector_count,
                sources="|".join(sorted(unique_sources)),
                direction=_majority_direction(directions),
                first_seen=min(timestamps),
                last_seen=max(timestamps),
            )
        )

    ranked.sort(key=lambda r: (r.source_count, r.last_seen), reverse=True)
    return ranked


def filter_by_direction(
    ranked: list[RankedSignal],
    direction: Optional[str],
) -> list[RankedSignal]:
    """Optionally filter ranked list to a single direction.

    Args:
        ranked: Full ranked list from build_ranked_signals.
        direction: 'long', 'short', 'watch', 'unknown', or None (no filter).

    Returns:
        Filtered list preserving original sort order.
    """
    if direction is None:
        return ranked
    return [r for r in ranked if r.direction == direction]
