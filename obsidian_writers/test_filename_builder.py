"""test_filename_builder.py — P020 filename collision fix (WO-P800-E3.002).

Covers the fix: P020 filenames now include trade_id when the payload
carries one, so two systems closing the same symbol on the same date no
longer silently overwrite each other. Also guards that P115/P300/P400/KB
identifier logic is untouched by the P020-only branch added in
filename_builder.py v2.2.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\obsidian_writers\\
           test_filename_builder.py
"""
from domain.filename_builder import build_filepath


def test_p020_different_trade_id_gives_different_paths():
    """Same date+symbol, different trade_id -- the collision this WO fixes."""
    data_a = {"signal_date": "2026-03-11", "symbol": "POWL", "trade_id": "101"}
    data_b = {"signal_date": "2026-03-11", "symbol": "POWL", "trade_id": "102"}

    path_a = build_filepath("P020", data_a)
    path_b = build_filepath("P020", data_b)

    assert path_a != path_b
    assert path_a.name == "2026-03-11_POWL_101.md"
    assert path_b.name == "2026-03-11_POWL_102.md"


def test_p020_same_trade_id_gives_same_path():
    """Re-running the same trade must still resolve to one canonical file
    (overwrite/versioning depends on this staying stable)."""
    data = {"signal_date": "2026-03-11", "symbol": "POWL", "trade_id": "101"}

    path_first = build_filepath("P020", dict(data))
    path_second = build_filepath("P020", dict(data))

    assert path_first == path_second


def test_p020_missing_trade_id_falls_back_to_symbol_only():
    """No trade_id in the payload -- old symbol-only behavior, unchanged.
    Keeps legacy callers and pre-fix notes resolving to the same filename."""
    data = {"signal_date": "2026-01-28", "symbol": "VSAT"}

    path = build_filepath("P020", data)

    assert path.name == "2026-01-28_VSAT.md"


def test_p115_identifier_unchanged_even_with_trade_id_present():
    """P115 must never branch into the P020 trade_id logic, even if a
    trade_id key happens to be present in the payload."""
    data = {"signal_date": "2026-03-11", "symbol": "AAPL", "trade_id": "999"}

    path = build_filepath("P115", data)

    assert path.name == "2026-03-11_AAPL.md"


def test_p300_and_p400_identifier_unchanged():
    """Regression guard: P300/P400 still key off ticker, no trade_id logic."""
    data = {"signal_date": "2026-03-11", "ticker": "MSFT", "trade_id": "999"}

    path_p300 = build_filepath("P300", dict(data))
    path_p400 = build_filepath("P400", dict(data))

    assert path_p300.name == "2026-03-11_MSFT.md"
    assert path_p400.name == "2026-03-11_MSFT.md"
