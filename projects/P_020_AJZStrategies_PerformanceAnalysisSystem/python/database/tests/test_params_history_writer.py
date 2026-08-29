"""Tests for domain.params_history_writer -- pure markdown edits for
Growth Projections / Parameter History / Next Review (WO-P020-E1.011).
No file I/O in this module.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from domain.params_history_writer import (
    append_history_row,
    update_next_review,
    upsert_growth_current_row,
)

SAMPLE_MD = """# P_000 Account Parameters

**Next Review:** August 2026 (monthly) or when balance hits $35,000

---

## Growth Projections

| Balance | Risk (1.5%) | Max Position (5%) |
|---------|-------------|-------------------|
| $31,348.39 (current) | $470.23 | $1,567.42 |
| $35,000 | $525.00 | $1,750.00 |
| $40,000 | $600.00 | $2,000.00 |

---

## Parameter History

| Date | Balance | Risk (1.5%) | Max (5%) | Notes |
|------|---------|-------------|----------|-------|
| Jan 23, 2026 | $30,000 | $450.00 | $1,500.00 | System initialization |
| Aug 4, 2026 | $31,348.39 | $470.23 | $1,567.42 | Monthly review |

---

## Change Log
"""


# ---------------------------------------------------------------------
# upsert_growth_current_row
# ---------------------------------------------------------------------

def test_upsert_growth_current_row_replaces_only_current_row():
    new_row = "| $36,000.00 (current) | $540.00 | $1,800.00 |"
    result = upsert_growth_current_row(SAMPLE_MD, new_row)
    assert new_row in result
    assert "$31,348.39 (current)" not in result
    # Static milestone rows untouched
    assert "| $35,000 | $525.00 | $1,750.00 |" in result
    assert "| $40,000 | $600.00 | $2,000.00 |" in result


def test_upsert_growth_current_row_missing_section_raises():
    try:
        upsert_growth_current_row("no growth section here", "| x |")
        assert False, "expected ValueError"
    except ValueError:
        pass


# ---------------------------------------------------------------------
# append_history_row
# ---------------------------------------------------------------------

def test_append_history_row_adds_one_row_at_end():
    new_row = "| Aug 22, 2026 | $36,000.00 | $540.00 | $1,800.00 | Threshold-triggered sync |"
    result = append_history_row(SAMPLE_MD, new_row)
    assert new_row in result
    lines = result.split("\n")
    history_rows = [
        l for l in lines
        if l.startswith("|") and ("2026" in l or "Notes" in l or "---" in l)
    ]
    # Original 2 data rows + header + separator + new row = 5 pipe lines
    assert result.count("| Jan 23, 2026") == 1
    assert result.count("| Aug 4, 2026") == 1
    assert result.count("| Aug 22, 2026") == 1


def test_append_history_row_never_edits_prior_rows():
    """Explicit acceptance criterion: existing rows are untouched, never
    removed or rewritten."""
    new_row = "| Aug 22, 2026 | $36,000.00 | $540.00 | $1,800.00 | Note |"
    result = append_history_row(SAMPLE_MD, new_row)
    assert "| Jan 23, 2026 | $30,000 | $450.00 | $1,500.00 | System initialization |" in result
    assert "| Aug 4, 2026 | $31,348.39 | $470.23 | $1,567.42 | Monthly review |" in result


def test_append_history_row_twice_produces_two_new_rows_not_duplicates():
    row1 = "| Aug 22, 2026 | $36,000.00 | $540.00 | $1,800.00 | First |"
    row2 = "| Sep 1, 2026 | $37,000.00 | $555.00 | $1,850.00 | Second |"
    result = append_history_row(SAMPLE_MD, row1)
    result = append_history_row(result, row2)
    assert result.count("| Aug 22, 2026") == 1
    assert result.count("| Sep 1, 2026") == 1
    assert result.count("| Jan 23, 2026") == 1


def test_append_history_row_missing_section_raises():
    try:
        append_history_row("no history section here", "| x |")
        assert False, "expected ValueError"
    except ValueError:
        pass


# ---------------------------------------------------------------------
# update_next_review
# ---------------------------------------------------------------------

def test_update_next_review_replaces_value():
    result = update_next_review(SAMPLE_MD, "September 2026 (monthly) or when balance hits $35,000")
    assert "**Next Review:** September 2026 (monthly) or when balance hits $35,000" in result
    assert "**Next Review:** August 2026" not in result


def test_update_next_review_missing_line_is_noop():
    """No guessing a new location -- returns markdown unchanged."""
    md = "# no next review line here"
    result = update_next_review(md, "September 2026")
    assert result == md
