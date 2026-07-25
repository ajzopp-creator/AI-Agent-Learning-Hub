"""test_write_route.py — write_route rename coverage (WO-P400-E2.020).

The gate test (test_signal_v2_e2e.py) only exercises the JSON signal path,
which skips write_route normalization entirely — it gives zero coverage for
this change. This file confirms: (1) _inject_write_route sets the normalized
write_route field correctly via VERDICT_MAP, with council_verdict untouched;
(2) vault_writer's read-existing-note logic falls back to the legacy
verdict/verdict_history keys for notes written before the 2026-07-10 rename,
so their provenance trail isn't lost on next overwrite.
"""
import pytest

from application.write_handler import _inject_write_route
from infrastructure.vault_writer import _read_existing_frontmatter, _parse_history


def test_inject_write_route_p300_buy():
    """P_300's native 'signal' field maps straight through via VERDICT_MAP."""
    data = {"signal": "BUY"}
    _inject_write_route("P300", data)
    assert data["write_route"] == "BUY"


def test_inject_write_route_p400_blocked_maps_to_pass():
    """P_400 BLOCKED maps to PASS; council_verdict (true disposition) untouched."""
    data = {"council_verdict": "BLOCKED"}
    _inject_write_route("P400", data)
    assert data["write_route"] == "PASS"
    assert data["council_verdict"] == "BLOCKED"


def test_read_existing_frontmatter_legacy_verdict_fallback(tmp_path):
    """A pre-rename note (verdict:, verdict_history:) still yields write_route
    on read, so its history isn't silently reset on next overwrite."""
    note = tmp_path / "legacy_note.md"
    note.write_text(
        "---\n"
        "verdict: BUY\n"
        "note_version: 2\n"
        "run_date: 2026-07-01\n"
        "verdict_history:\n"
        "  - {verdict: PASS, run_date: 2026-06-01, note_version: 1}\n"
        "---\n",
        encoding="utf-8",
    )
    result = _read_existing_frontmatter(note)
    assert result["write_route"] == "BUY"
    assert result["note_version"] == 2
    assert result["write_route_history"] == [
        "{verdict: PASS, run_date: 2026-06-01, note_version: 1}"
    ]


def test_read_existing_frontmatter_current_write_route(tmp_path):
    """A post-rename note (write_route:) reads straight through, no fallback needed."""
    note = tmp_path / "current_note.md"
    note.write_text(
        "---\n"
        "write_route: WATCH\n"
        "note_version: 1\n"
        "run_date: 2026-07-10\n"
        "write_route_history: []\n"
        "---\n",
        encoding="utf-8",
    )
    result = _read_existing_frontmatter(note)
    assert result["write_route"] == "WATCH"
    assert result["write_route_history"] == []


def test_parse_history_normalizes_legacy_key():
    """Inline legacy history entries get their 'verdict' key renamed to
    'write_route' so frontmatter_builder can read them under the new name."""
    history = ["{verdict: PASS, run_date: 2026-06-01, note_version: 1}"]
    parsed = _parse_history(history)
    assert parsed[0]["write_route"] == "PASS"
    assert "verdict" not in parsed[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
