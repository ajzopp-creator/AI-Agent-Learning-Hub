"""test_p020_live_thinklog_override.py -- Regression tests for the live
ThinkLog tag override feature (Tony directive, 2026-08-16 session).

Covers: domain/thinklog_parser.parse_thinklog_entries() (multi-entry
per-line parsing -- live notes accumulate several dated [WHY][SIG]
lines in one running note per symbol, unlike paper's single-tag
assumption), infrastructure/thinklog_reader.build_multi_entry_lookup()
(per-line date resolution, OCC symbol normalization, and collision-safe
lookup building), domain/thinklog_override.get_override() (tag-wins-
always resolution), and application/live_thinklog.
apply_thinklog_overrides() (the live ingest hook's caller). No real DB
or file I/O -- lookups are built in-memory from synthetic records.
"""
import sys
from datetime import date
from pathlib import Path

DB_DIR = Path(__file__).resolve().parents[1] / "python" / "database"
sys.path.insert(0, str(DB_DIR))

from domain.thinklog_parser import parse_thinklog_entries
from infrastructure.thinklog_reader import build_multi_entry_lookup, _normalize_symbol
from domain.thinklog_override import get_override
from application.live_thinklog import apply_thinklog_overrides


def _rec(symbol, record_date_iso, body):
    """Build a read_thinklog_csv()-shaped record dict for testing."""
    return {"symbol": symbol, "date": date.fromisoformat(record_date_iso), "body": body}


# ---------------------------------------------------------------------------
# parse_thinklog_entries() -- multi-entry parsing (the bug Tony caught)
# ---------------------------------------------------------------------------

def test_two_dated_lines_produce_two_entries():
    body = "0201: [SNT][A] STOP target etc.\n0712: [OIL][A] SL: CA:VB etc."
    entries = parse_thinklog_entries(body)
    assert len(entries) == 2
    assert entries[0]["date_token"] == "0201"
    assert entries[0]["reason"] == "SNT"
    assert entries[1]["date_token"] == "0712"
    assert entries[1]["reason"] == "OIL"
    # This is exactly what the old parse_thinklog_note() lost -- confirm
    # the second tag is NOT silently dropped.


def test_continuation_line_attaches_to_prior_entry():
    body = "0201: [SNT][A] STOP target\nfollow-up thought, no date here"
    entries = parse_thinklog_entries(body)
    assert len(entries) == 1
    assert "follow-up thought" in entries[0]["notes"]


def test_single_entry_still_works():
    entries = parse_thinklog_entries("0810: [P_116] [B] options income")
    assert len(entries) == 1
    assert entries[0]["reason"] == "P_116"


def test_no_dated_line_returns_empty():
    assert parse_thinklog_entries("just a note, no date or tags") == []


def test_empty_body_returns_empty():
    assert parse_thinklog_entries("") == []


def test_no_space_before_bracket_still_parses():
    # Tony's second example had no space: "0712:[OIL][A]"
    entries = parse_thinklog_entries("0712:[OIL][A] SL: CA:VB etc.")
    assert len(entries) == 1
    assert entries[0]["reason"] == "OIL"


# ---------------------------------------------------------------------------
# _normalize_symbol() -- OCC option symbol stripping (real bug, 2026-08-16
# export: TOS's "Symbol:" field carries the full option symbol)
# ---------------------------------------------------------------------------

def test_occ_option_symbol_strips_to_underlying():
    assert _normalize_symbol(".DINO260918C92.5") == "DINO"


def test_plain_stock_symbol_unchanged():
    assert _normalize_symbol("IWM") == "IWM"


def test_mutual_fund_symbol_unchanged():
    # No trailing digits -- must not be mistaken for an OCC symbol.
    assert _normalize_symbol("SWPPX") == "SWPPX"


# ---------------------------------------------------------------------------
# build_multi_entry_lookup() -- per-line date resolution
# ---------------------------------------------------------------------------

def test_lookup_keys_on_embedded_date_not_record_date():
    # Record's own timestamp is 2026-07-15, but the body's dated lines are
    # 0201 and 0712 -- the lookup must key on THOSE dates, not 07-15.
    records = [_rec("AAPL", "2026-07-15",
                     "0201: [SNT][A] STOP target\n0712: [OIL][A] SL etc.")]
    lookup = build_multi_entry_lookup(records)
    assert ("AAPL", date(2026, 2, 1)) in lookup
    assert ("AAPL", date(2026, 7, 12)) in lookup
    assert ("AAPL", date(2026, 7, 15)) not in lookup
    assert lookup[("AAPL", date(2026, 2, 1))]["reason"] == "SNT"
    assert lookup[("AAPL", date(2026, 7, 12))]["reason"] == "OIL"


def test_implausible_future_date_falls_back_a_year():
    # Record dated Jan 2026 referencing "1215" (Dec 15) -- must resolve
    # to 2025-12-15, not 2026-12-15 (350 days in the future).
    records = [_rec("GM", "2026-01-05", "1215: [SNT][A] year-end pick")]
    lookup = build_multi_entry_lookup(records)
    assert ("GM", date(2025, 12, 15)) in lookup
    assert ("GM", date(2026, 12, 15)) not in lookup


def test_unparseable_tag_never_clobbers_a_valid_one_for_same_key():
    # Real case, 2026-08-16 export: two DINO entries, same date. One has
    # a valid [P_116] tag, one has a typo'd '{P_116]' that fails to
    # parse. The broken one (processed second) must NOT overwrite the
    # valid one for the same (symbol, date) key.
    records = [
        _rec("DINO", "2026-08-16", "0812:[P_116][A] valid entry"),
        _rec("DINO", "2026-08-16", "0812:{P_116][A] typo'd entry, curly brace"),
    ]
    lookup = build_multi_entry_lookup(records)
    assert lookup[("DINO", date(2026, 8, 12))]["reason"] == "P_116"


def test_entry_with_no_reason_excluded_from_lookup():
    # A dated line whose tag failed to parse must not appear at all --
    # not even with reason=None -- so it can never mask a real one.
    records = [_rec("FSLR", "2026-08-06", "0806: P_115 BUY no brackets at all")]
    lookup = build_multi_entry_lookup(records)
    assert ("FSLR", date(2026, 8, 6)) not in lookup


# ---------------------------------------------------------------------------
# get_override() -- core resolution logic
# ---------------------------------------------------------------------------

def test_no_tag_returns_none():
    assert get_override("AAPL", "2026-08-10", {}, "TOS_Import") is None


def test_tag_present_overrides_resolved_system():
    records = [_rec("ASX", "2026-08-10", "0810: [P_116] [B] OIL subscription")]
    lookup = build_multi_entry_lookup(records)
    result = get_override("ASX", "2026-08-10", lookup, "P_300")
    assert result.system == "P_116"
    assert result.previous_system == "P_300"


def test_tag_sets_system_when_nothing_resolved():
    records = [_rec("GM", "2026-08-11", "0811: [SNT] [A] Wall Street Zen pick")]
    lookup = build_multi_entry_lookup(records)
    result = get_override("GM", "2026-08-11", lookup, "TOS_Import")
    assert result.system == "SNT"
    assert result.previous_system == "TOS_Import"


def test_open_vocabulary_new_code_flows_through():
    # WSZ isn't in any locked list -- must still work, no schema change.
    records = [_rec("XYZ", "2026-08-10", "0810: [WSZ] [B] new subscription source")]
    lookup = build_multi_entry_lookup(records)
    assert get_override("XYZ", "2026-08-10", lookup, "TOS_Import").system == "WSZ"


def test_tag_captures_signal_strength():
    records = [_rec("DINO", "2026-08-12", "0812: [P_116] [C] marginal setup")]
    lookup = build_multi_entry_lookup(records)
    assert get_override("DINO", "2026-08-12", lookup, "TOS_Import").signal_strength == "C"


def test_no_symbol_match_returns_none():
    records = [_rec("AAPL", "2026-08-10", "0810: [P_115] [A] dip buy")]
    lookup = build_multi_entry_lookup(records)
    assert get_override("MSFT", "2026-08-10", lookup, "TOS_Import") is None


def test_beyond_window_returns_none():
    # Default window is 3 days -- a tag 5 days before the fill is too old.
    records = [_rec("AAPL", "2026-08-05", "0805: [P_115] [A] dip buy")]
    lookup = build_multi_entry_lookup(records)
    assert get_override("AAPL", "2026-08-10", lookup, "TOS_Import") is None


def test_one_day_earlier_matches_within_default_window():
    # Real case, 2026-08-16 export: SHEL tagged 07-07, filled 07-08.
    records = [_rec("SHEL", "2026-07-07", "0707: [P_920] [A] STEP 3 options")]
    lookup = build_multi_entry_lookup(records)
    result = get_override("SHEL", "2026-07-08", lookup, "TOS_Import")
    assert result is not None
    assert result.system == "P_920"
    assert result.gap_days == 1


def test_exact_date_wins_over_earlier_date_when_both_present():
    records = [
        _rec("AAPL", "2026-08-09", "0809: [P_300] [B] earlier idea"),
        _rec("AAPL", "2026-08-10", "0810: [P_115] [A] same-day tag"),
    ]
    lookup = build_multi_entry_lookup(records)
    result = get_override("AAPL", "2026-08-10", lookup, "TOS_Import")
    assert result.system == "P_115"
    assert result.gap_days == 0


def test_custom_forward_days_narrows_window():
    records = [_rec("AAPL", "2026-08-08", "0808: [P_115] [A] dip buy")]
    lookup = build_multi_entry_lookup(records)
    # 2 days back with forward_days=1 -- outside a tightened window.
    assert get_override("AAPL", "2026-08-10", lookup, "TOS_Import", forward_days=1) is None
    # Same gap, default window (3) -- inside it.
    assert get_override("AAPL", "2026-08-10", lookup, "TOS_Import") is not None


def test_multiple_dates_same_symbol_resolve_independently():
    # The exact scenario Tony described: one symbol, two unrelated
    # trades months apart, each must resolve to its own system.
    records = [_rec("AAPL", "2026-07-15",
                     "0201: [SNT][A] STOP target\n0712: [OIL][A] SL etc.")]
    lookup = build_multi_entry_lookup(records)
    feb = get_override("AAPL", "2026-02-01", lookup, "TOS_Import")
    jul = get_override("AAPL", "2026-07-12", lookup, "TOS_Import")
    assert feb.system == "SNT"
    assert jul.system == "OIL"


# ---------------------------------------------------------------------------
# apply_thinklog_overrides() -- live ingest hook caller
# ---------------------------------------------------------------------------

def test_apply_overrides_mutates_trades_in_place():
    trades = [
        {"underlying_symbol": "GM", "open_date": "2026-08-11", "system": "TOS_Import"},
        {"underlying_symbol": "DAL", "open_date": "2026-08-13", "system": "P_116"},
    ]
    records = [_rec("GM", "2026-08-11", "0811: [P_116] [B] options income")]
    lookup = build_multi_entry_lookup(records)
    audit = []
    count = apply_thinklog_overrides(trades, lookup, audit)
    assert count == 1
    assert trades[0]["system"] == "P_116"
    assert trades[0]["reason"] == "P_116"
    assert trades[1]["system"] == "P_116"  # untouched, no tag for DAL
    assert "reason" not in trades[1]
    assert len(audit) == 1
    assert "GM" in audit[0]


def test_apply_overrides_empty_lookup_is_noop():
    trades = [{"underlying_symbol": "GM", "open_date": "2026-08-11", "system": "TOS_Import"}]
    audit = []
    count = apply_thinklog_overrides(trades, {}, audit)
    assert count == 0
    assert trades[0]["system"] == "TOS_Import"
    assert audit == []
