"""Tests for the WO-P020-E1.011 additions to domain.params_md_writer --
upsert_risk_mode_table() and upsert_gate_block(). The E1.009 functions
(upsert_active_parameter_rows, ensure_cash_note, parse_last_written_balance)
are already covered by tests/test_p000_params_writer.py; not duplicated
here.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from domain.params_md_writer import upsert_gate_block, upsert_risk_mode_table

SAMPLE_MD = """# P_000 Account Parameters

## Risk Mode Adjustments (from P_010_RiskConfig.json)

**Authority rule:** JSON governs.

| Risk Mode | Risk/Trade | Max Position | Notes |
|-----------|------------|--------------|-------|
| OFF / CORRECTION | $235.12 (50%) | $783.71 (50%) | avg_posture < -1.0 |
| HALF | $352.67 (75%) | $1,175.57 (75%) | 25% reduction |
| STANDARD | $470.23 | $1,567.42 | Base risk |
| FULL | $470.23 | $1,567.42 | Same as STANDARD |
| HOT | Tiered up to 5% | Up to $1,567.42 | avg_posture > 1.08 |

---

### Three-Gate Position Sizing
```text
Gate 1 (Risk-Based):    $470.23 / (Entry - Stop)
Gate 2 (Cash Limit):    User-provided per trade
Gate 3 (Concentration): $1,567.42 max (or premium for options)

Final Position Size = SMALLEST of three gates
```

### Options Management Rule
Some unrelated later section.
"""


# ---------------------------------------------------------------------
# upsert_risk_mode_table
# ---------------------------------------------------------------------

def test_upsert_risk_mode_table_updates_dollar_cells():
    mode_pairs = {
        "OFF / CORRECTION": ("$270.00 (50%)", "$900.00 (50%)"),
        "HALF": ("$405.00 (75%)", "$1,350.00 (75%)"),
        "STANDARD": ("$540.00", "$1,800.00"),
        "FULL": ("$540.00", "$1,800.00"),
        "HOT": ("Tiered up to 5%", "Up to $1,800.00"),
    }
    result = upsert_risk_mode_table(SAMPLE_MD, mode_pairs)
    assert "| OFF / CORRECTION | $270.00 (50%) | $900.00 (50%) | avg_posture < -1.0 |" in result
    assert "| STANDARD | $540.00 | $1,800.00 | Base risk |" in result
    assert "| HOT | Tiered up to 5% | Up to $1,800.00 | avg_posture > 1.08 |" in result


def test_upsert_risk_mode_table_never_touches_notes_column():
    """Notes column (avg_posture ranges) is explicitly out of scope --
    mode-selection thresholds stay untouched."""
    mode_pairs = {"STANDARD": ("$1.00", "$2.00")}
    result = upsert_risk_mode_table(SAMPLE_MD, mode_pairs)
    assert "avg_posture < -1.0" in result
    assert "avg_posture > 1.08" in result
    assert "25% reduction" in result


def test_upsert_risk_mode_table_missing_section_raises():
    try:
        upsert_risk_mode_table("no risk mode section", {"STANDARD": ("$1", "$2")})
        assert False, "expected ValueError"
    except ValueError:
        pass


# ---------------------------------------------------------------------
# upsert_gate_block
# ---------------------------------------------------------------------

def test_upsert_gate_block_replaces_gate1_and_gate3_only():
    result = upsert_gate_block(
        SAMPLE_MD,
        "Gate 1 (Risk-Based):    $540.00 / (Entry - Stop)",
        "Gate 3 (Concentration): $1,800.00 max (or premium for options)",
    )
    assert "Gate 1 (Risk-Based):    $540.00 / (Entry - Stop)" in result
    assert "Gate 3 (Concentration): $1,800.00 max (or premium for options)" in result
    # Gate 2 is static prose, must survive unchanged
    assert "Gate 2 (Cash Limit):    User-provided per trade" in result
    assert "Final Position Size = SMALLEST of three gates" in result


def test_upsert_gate_block_stops_at_closing_fence():
    """Must not wander past the code block into later sections."""
    result = upsert_gate_block(SAMPLE_MD, "Gate 1 (Risk-Based):    $1.00", "Gate 3 (Concentration): $2.00")
    assert "Some unrelated later section." in result


def test_upsert_gate_block_missing_section_raises():
    try:
        upsert_gate_block("no gate section here", "Gate 1: $1", "Gate 3: $2")
        assert False, "expected ValueError"
    except ValueError:
        pass
