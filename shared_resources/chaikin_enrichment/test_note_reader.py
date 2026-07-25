"""test_note_reader.py -- Frontmatter + section parsing against real notes
(WO-P800-E4.001).

Reads real vault notes rather than fixtures, per the WO's VERIFY
requirement to test against real data.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\shared_resources\\
           chaikin_enrichment\\test_note_reader.py
"""
from pathlib import Path

from shared_resources.chaikin_enrichment.infrastructure.note_reader import read_note

_P300 = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeManagement\P300"
)
_P115 = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeManagement\P115"
)


def test_note_with_existing_chaikin_section_is_detected():
    """Real fixture: 2026-07-23_CLF.md already has a clean
    '## Chaikin Power Gauge' section (independently verified 2026-07-24)."""
    scanned = read_note(_P300 / "2026-07-23_CLF.md", "CLF")
    assert scanned is not None
    assert scanned.write_route == "WATCH"
    assert scanned.has_chaikin_section is True


def test_second_note_with_existing_section_is_also_detected():
    """Real fixture: 2026-07-21_CIFR.md -- the WO's own idempotency
    example."""
    scanned = read_note(_P300 / "2026-07-21_CIFR.md", "CIFR")
    assert scanned is not None
    assert scanned.write_route == "BUY"
    assert scanned.has_chaikin_section is True


def test_note_without_chaikin_section_is_a_clean_candidate():
    """Real fixture: 2026-07-23_DNN.md -- WATCH, no section yet."""
    scanned = read_note(_P300 / "2026-07-23_DNN.md", "DNN")
    assert scanned is not None
    assert scanned.write_route == "WATCH"
    assert scanned.has_chaikin_section is False


def test_p115_note_without_chaikin_section():
    """Real fixture: 2026-07-24_PH.md -- BUY, no section yet, P_115 schema
    (confirms note_reader is schema-agnostic)."""
    scanned = read_note(_P115 / "2026-07-24_PH.md", "PH")
    assert scanned is not None
    assert scanned.write_route == "BUY"
    assert scanned.has_chaikin_section is False


def test_missing_file_returns_none():
    scanned = read_note(_P300 / "1999-01-01_NOPE.md", "NOPE")
    assert scanned is None
