"""Tests for infrastructure.p000_params_writer -- write_balance_to_p000_params()
pulled-timestamp guarantee. Ref WO-P020-E1.014.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import infrastructure.p000_params_writer as writer

SAMPLE_MD = """# P_000 Account Parameters

## Active Parameters

| Parameter | Value |
|---|---|
| Buying Power | $1,000.00 |
| Cash Available for Trading | N/A |

### Cash Balance (Separate Concept)

Some other text.
"""


def _write_sample(tmp_path: Path) -> Path:
    p = tmp_path / "P_000_Account_Parameters_Current.md"
    p.write_text(SAMPLE_MD, encoding="utf-8")
    return p


def test_pulled_timestamp_present_in_both_fields(tmp_path, monkeypatch):
    """A successful write tags both Buying Power and Cash Available with
    a '(pulled ...)' suffix, not just the raw dollar value."""
    target = _write_sample(tmp_path)
    monkeypatch.setattr(writer, "P000_PARAMS_FILE", target)

    ok = writer.write_balance_to_p000_params(36911.08, None)

    assert ok is True
    text = target.read_text(encoding="utf-8")
    assert "$36,911.08 (pulled " in text
    assert "N/A (pulled " in text


def test_none_field_still_tagged_na_with_timestamp(tmp_path, monkeypatch):
    """cash_available=None still writes 'N/A (pulled ...)', not a bare
    'N/A' -- the None case must not skip the timestamp."""
    target = _write_sample(tmp_path)
    monkeypatch.setattr(writer, "P000_PARAMS_FILE", target)

    writer.write_balance_to_p000_params(None, None)

    text = target.read_text(encoding="utf-8")
    na_lines = [
        line for line in text.split("\n")
        if line.startswith("| Buying Power")
        or line.startswith("| Cash Available for Trading")
    ]
    assert all("(pulled " in line for line in na_lines)


def test_rerun_overwrites_not_duplicates(tmp_path, monkeypatch):
    """Running the write twice updates the same row in place -- no
    duplicate 'Buying Power' rows accumulate in the table."""
    target = _write_sample(tmp_path)
    monkeypatch.setattr(writer, "P000_PARAMS_FILE", target)

    writer.write_balance_to_p000_params(36911.08, None)
    writer.write_balance_to_p000_params(39296.76, None)

    text = target.read_text(encoding="utf-8")
    assert text.count("| Buying Power |") == 1
    assert "$39,296.76 (pulled " in text
    assert "$36,911.08" not in text


def test_format_pulled_timestamp_uses_no_leading_zero_day():
    """_format_pulled_timestamp() builds the day/hour from ints, not
    %-d/%-I strftime flags -- those are Unix-only and break on Windows."""
    from datetime import datetime

    ts = writer._format_pulled_timestamp(datetime(2026, 8, 19, 16, 47))
    assert ts == "Aug 19, 2026 4:47 PM"

    ts_midnight = writer._format_pulled_timestamp(datetime(2026, 8, 19, 0, 5))
    assert ts_midnight == "Aug 19, 2026 12:05 AM"
