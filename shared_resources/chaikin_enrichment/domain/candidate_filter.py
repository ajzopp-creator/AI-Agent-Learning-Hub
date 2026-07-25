"""candidate_filter.py -- Pure filtering logic for Chaikin enrichment.

No I/O. Given each scanned note's write_route and whether it already
carries a Chaikin section, decides which notes qualify for enrichment.
Built against WO-P800-E4.001.

CHANGELOG:
  v1.0  2026-07-24  Initial version.
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


def is_candidate(note: ScannedNote) -> bool:
    """Decides whether a single scanned note qualifies for enrichment.

    A note qualifies when its write_route is BUY or WATCH
    (CANDIDATE_WRITE_ROUTES) and it does not already carry a Chaikin
    Power Gauge section -- the idempotency check from WO-P800-E4.001
    (real examples: 2026-07-21_CIFR.md and 2026-07-23_CLF.md must both
    be excluded on a re-run).

    Args:
        note: A ScannedNote produced by vault_scanner.py.

    Returns:
        True if the note should be enriched, False otherwise.
    """
    if note.has_chaikin_section:
        return False
    return note.write_route in CANDIDATE_WRITE_ROUTES


def filter_candidates(notes: list[ScannedNote]) -> list[NoteCandidate]:
    """Filters a batch of scanned notes down to enrichment candidates.

    Args:
        notes: All notes vault_scanner.py found in the lookback window,
            for one schema.

    Returns:
        NoteCandidate list, same order as the input, containing only
        notes that passed is_candidate().
    """
    return [
        NoteCandidate(symbol=note.symbol, note_path=note.note_path)
        for note in notes
        if is_candidate(note)
    ]
