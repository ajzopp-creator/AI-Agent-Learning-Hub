"""candidate_filter.py -- Pure filtering logic for Chaikin enrichment.

No I/O. Given each scanned note's write_route and whether it already
carries a Chaikin section, decides which notes qualify for enrichment.
Built against WO-P800-E4.001.

CHANGELOG:
  v1.0  2026-07-24  Initial version.
  v1.1  2026-08-12  Added optional skip_symbols param to is_candidate() /
                    filter_candidates() -- a schema's skip list (e.g.
                    P_300's WO-P300-E5.007) now excludes symbols the same
                    way an existing Chaikin section does. Defaults to an
                    empty frozenset so both signatures stay backward
                    compatible -- existing callers (tests, P_115) see no
                    behavior change.
"""

from dataclasses import dataclass

from shared_resources.chaikin_enrichment.config import CANDIDATE_WRITE_ROUTES


@dataclass(frozen=True)
class ScannedNote:
    """One note as read off disk by vault_scanner.py + note_reader.py.

    Attributes:
        symbol: Ticker symbol parsed from the note's filename.
        note_path: Absolute path to the note file.
        write_route: Normalized write_route value from frontmatter
            (e.g. "BUY", "WATCH", "PASS").
        has_chaikin_section: True if note_reader.py found an existing
            Chaikin Power Gauge section in this note.
    """

    symbol: str
    note_path: str
    write_route: str
    has_chaikin_section: bool


@dataclass(frozen=True)
class NoteCandidate:
    """One note confirmed as a Chaikin enrichment candidate.

    Attributes:
        symbol: Ticker symbol.
        note_path: Absolute path to the note file.
    """

    symbol: str
    note_path: str


def is_candidate(note: ScannedNote, skip_symbols: frozenset[str] = frozenset()) -> bool:
    """Decides whether a single scanned note qualifies for enrichment.

    A note qualifies when its write_route is BUY or WATCH
    (CANDIDATE_WRITE_ROUTES), it does not already carry a Chaikin
    Power Gauge section -- the idempotency check from WO-P800-E4.001
    (real examples: 2026-07-21_CIFR.md and 2026-07-23_CLF.md must both
    be excluded on a re-run) -- and its symbol is not in the caller's
    skip_symbols (a schema's own permanent skip list, e.g. WO-P300-E5.007
    -- symbols Chaikin structurally cannot rate).

    Args:
        note: A ScannedNote produced by vault_scanner.py.
        skip_symbols: Symbols to exclude regardless of write_route/section
            state. Empty by default -- callers with no skip list (or none
            configured for their schema) see unchanged behavior.

    Returns:
        True if the note should be enriched, False otherwise.
    """
    if note.has_chaikin_section:
        return False
    if note.symbol in skip_symbols:
        return False
    return note.write_route in CANDIDATE_WRITE_ROUTES


def filter_candidates(
    notes: list[ScannedNote], skip_symbols: frozenset[str] = frozenset()
) -> list[NoteCandidate]:
    """Filters a batch of scanned notes down to enrichment candidates.

    Args:
        notes: All notes vault_scanner.py found in the lookback window,
            for one schema.
        skip_symbols: Passed through to is_candidate() -- see there.

    Returns:
        NoteCandidate list, same order as the input, containing only
        notes that passed is_candidate().
    """
    return [
        NoteCandidate(symbol=note.symbol, note_path=note.note_path)
        for note in notes
        if is_candidate(note, skip_symbols)
    ]
