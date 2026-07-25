"""test_candidate_filter.py -- Domain filter logic (WO-P800-E4.001).

Pure logic tests, no I/O. Covers the BUY/WATCH threshold and the
idempotency check (a note with an existing Chaikin section must never be
re-selected), using the same write_route vocabulary real notes carry.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\shared_resources\\
           chaikin_enrichment\\test_candidate_filter.py
"""
from shared_resources.chaikin_enrichment.domain.candidate_filter import (
    ScannedNote,
    filter_candidates,
    is_candidate,
)


def test_buy_note_without_section_is_candidate():
    note = ScannedNote("PH", "P115/2026-07-24_PH.md", "BUY", False)
    assert is_candidate(note) is True


def test_watch_note_without_section_is_candidate():
    note = ScannedNote("DNN", "P300/2026-07-23_DNN.md", "WATCH", False)
    assert is_candidate(note) is True


def test_pass_note_is_never_a_candidate():
    note = ScannedNote("SKIP", "P300/2026-01-01_SKIP.md", "PASS", False)
    assert is_candidate(note) is False


def test_note_with_existing_section_is_excluded_even_if_buy_or_watch():
    """Idempotency -- real examples: 2026-07-21_CIFR.md (BUY) and
    2026-07-23_CLF.md (WATCH) both already carry a Chaikin section and
    must be excluded on a re-run."""
    cifr = ScannedNote("CIFR", "P300/2026-07-21_CIFR.md", "BUY", True)
    clf = ScannedNote("CLF", "P300/2026-07-23_CLF.md", "WATCH", True)
    assert is_candidate(cifr) is False
    assert is_candidate(clf) is False


def test_filter_candidates_keeps_order_and_drops_non_candidates():
    notes = [
        ScannedNote("DNN", "d.md", "WATCH", False),  # keep
        ScannedNote("CLF", "c.md", "WATCH", True),    # drop -- has section
        ScannedNote("SKIP", "s.md", "PASS", False),   # drop -- PASS
        ScannedNote("PH", "p.md", "BUY", False),      # keep
    ]

    result = filter_candidates(notes)

    assert [c.symbol for c in result] == ["DNN", "PH"]
