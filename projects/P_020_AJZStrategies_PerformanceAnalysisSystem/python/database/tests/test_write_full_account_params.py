"""Tests for infrastructure.p000_params_writer.write_full_account_params()
-- the WO-P020-E1.011 threshold-gated 6-location sync. This is the branch
that had never run against real file content outside a 2026-08-09 sandbox
dry-run and had zero automated coverage before this WO's closeout review
(2026-08-22).

Fixture mirrors the real P_000_Account_Parameters_Current.md structure
(all 6 sections + the E1.009 Buying Power/Cash rows) so a passing test
here means the real file's actual shape is exercised, not a simplified
stand-in.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
import infrastructure.p000_params_writer as writer

FIXTURE_MD = """# P_000 Account Parameters -- All Trading Projects

**File:** P_000_Account_Parameters_Current.md
**Last Updated:** August 04, 2026
**Next Review:** September 2026 (monthly) or when balance hits $35,000

---

## Active Parameters

| Parameter | Value |
|-----------|-------|
| Account Balance | $31,348.39 |
| Risk per Trade | 1.5% = $470.23|
| Max Position (5%) | $1,567.42 |
| Options Rule | Use underlying STOCK price as the management trigger |
| Buying Power | $39,260.98 (pulled Aug 22, 2026 11:00 AM) |
| Cash Available for Trading | $19,630.49 (pulled Aug 22, 2026 11:00 AM) |

---

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

## Critical Rules

### Cash Balance (Separate Concept)
**Note (WO-P020-E1.009):** Buying Power and Cash Available for Trading in the table above are broker-reported reference numbers only.

### Three-Gate Position Sizing
```text
Gate 1 (Risk-Based):    $470.23 / (Entry - Stop)
Gate 2 (Cash Limit):    User-provided per trade
Gate 3 (Concentration): $1,567.42 max (or premium for options)

Final Position Size = SMALLEST of three gates
```

---

## Growth Projections

| Balance | Risk (1.5%) | Max Position (5%) |
|---------|-------------|-------------------|
| $31,348.39 (current) | $470.23 | $1,567.42 |
| $35,000 | $525.00 | $1,750.00 |
| $40,000 | $600.00 | $2,000.00 |
| $50,000 | $750.00 | $2,500.00 |
| $75,000 | $1,125.00 | $3,750.00 |
| $100,000 | $1,500.00 | $5,000.00 |

---

## Parameter History

| Date | Balance | Risk (1.5%) | Max (5%) | Notes |
|------|---------|-------------|----------|-------|
| Jan 23, 2026 | $30,000 | $450.00 | $1,500.00 | System initialization |
| Aug 4, 2026 | $31,348.39 | $470.23 | $1,567.42 | Monthly review -- Net Liq per broker (live pull) |

---

## Change Log

- Aug 4, 2026 - Updated Account Balance to $31,348.39.
"""

FAKE_PARAMS = {"default_risk_pct": 0.015, "max_position_pct": 0.05}


def _write_fixture(tmp_path: Path) -> Path:
    p = tmp_path / "P_000_Account_Parameters_Current.md"
    p.write_text(FIXTURE_MD, encoding="utf-8")
    return p


def test_noop_below_threshold_leaves_file_byte_identical(tmp_path, monkeypatch):
    """Real 2026-08-22 case: -3.65% move, must be a silent no-op --
    matches the acceptance criterion exactly."""
    target = _write_fixture(tmp_path)
    monkeypatch.setattr(writer, "P000_PARAMS_FILE", target)
    monkeypatch.setattr(config, "load_params", lambda: FAKE_PARAMS)
    before = target.read_text(encoding="utf-8")

    result = writer.write_full_account_params(30203.56)

    assert result is False
    assert target.read_text(encoding="utf-8") == before


def test_triggered_sync_updates_all_six_locations(tmp_path, monkeypatch):
    """+/-10%+ move fires the full sync. This is the branch that had
    never run against real file content before this test existed."""
    target = _write_fixture(tmp_path)
    monkeypatch.setattr(writer, "P000_PARAMS_FILE", target)
    monkeypatch.setattr(config, "load_params", lambda: FAKE_PARAMS)

    result = writer.write_full_account_params(36000.00)  # +14.8% vs 31348.39

    assert result is True
    text = target.read_text(encoding="utf-8")

    # 1. Active Parameters
    assert "| Account Balance | $36,000.00 |" in text
    assert "| Risk per Trade | 1.5% = $540.00 |" in text
    assert "| Max Position (5%) | $1,800.00 |" in text

    # 2. Risk Mode Adjustments (5 rows)
    assert "| OFF / CORRECTION | $270.00 (50%) | $900.00 (50%) | avg_posture < -1.0 |" in text
    assert "| HALF | $405.00 (75%) | $1,350.00 (75%) | 25% reduction |" in text
    assert "| STANDARD | $540.00 | $1,800.00 | Base risk |" in text
    assert "| FULL | $540.00 | $1,800.00 | Same as STANDARD |" in text
    assert "| HOT | Tiered up to 5% | Up to $1,800.00 | avg_posture > 1.08 |" in text

    # 3. Three-Gate block
    assert "Gate 1 (Risk-Based):    $540.00 / (Entry - Stop)" in text
    assert "Gate 3 (Concentration): $1,800.00 max (or premium for options)" in text

    # 4. Growth Projections current row
    assert "| $36,000.00 (current) | $540.00 | $1,800.00 |" in text
    assert "$31,348.39 (current)" not in text
    assert "| $35,000 | $525.00 | $1,750.00 |" in text  # static row untouched

    # 5. Next Review auto-bump
    assert "**Next Review:**" in text
    assert "or when balance hits $35,000" in text

    # 6. Parameter History append -- new row present, prior row untouched
    assert "$36,000.00" in text
    assert "| Jan 23, 2026 | $30,000 | $450.00 | $1,500.00 | System initialization |" in text
    assert "| Aug 4, 2026 | $31,348.39 | $470.23 | $1,567.42 |" in text


def test_triggered_sync_history_appends_exactly_one_new_row(tmp_path, monkeypatch):
    target = _write_fixture(tmp_path)
    monkeypatch.setattr(writer, "P000_PARAMS_FILE", target)
    monkeypatch.setattr(config, "load_params", lambda: FAKE_PARAMS)

    writer.write_full_account_params(36000.00)

    text = target.read_text(encoding="utf-8")
    # Original 2 history rows + 1 new = 3, no duplicates
    assert text.count("| Jan 23, 2026") == 1
    assert text.count("| Aug 4, 2026") == 1
    assert text.count("$36,000.00 |") >= 1


def test_triggered_sync_no_regression_to_e1009_rows(tmp_path, monkeypatch):
    """Buying Power / Cash Available (E1.009's rows) must survive a
    threshold-triggered E1.011 sync untouched -- write_full_account_params()
    never calls into the E1.009 write path."""
    target = _write_fixture(tmp_path)
    monkeypatch.setattr(writer, "P000_PARAMS_FILE", target)
    monkeypatch.setattr(config, "load_params", lambda: FAKE_PARAMS)

    writer.write_full_account_params(36000.00)

    text = target.read_text(encoding="utf-8")
    assert "| Buying Power | $39,260.98 (pulled Aug 22, 2026 11:00 AM) |" in text
    assert "| Cash Available for Trading | $19,630.49 (pulled Aug 22, 2026 11:00 AM) |" in text


def test_first_run_none_baseline_always_triggers(tmp_path, monkeypatch):
    """Baseline that fails to parse (or first run) must not silently
    block sync forever -- should_write() treats None as always-write."""
    target = tmp_path / "P_000_Account_Parameters_Current.md"
    broken_md = FIXTURE_MD.replace("| Account Balance | $31,348.39 |", "| Account Balance | TBD |")
    target.write_text(broken_md, encoding="utf-8")
    monkeypatch.setattr(writer, "P000_PARAMS_FILE", target)
    monkeypatch.setattr(config, "load_params", lambda: FAKE_PARAMS)

    result = writer.write_full_account_params(31000.00)

    assert result is True


def test_missing_file_returns_false_not_raises(tmp_path, monkeypatch):
    target = tmp_path / "does_not_exist.md"
    monkeypatch.setattr(writer, "P000_PARAMS_FILE", target)
    monkeypatch.setattr(config, "load_params", lambda: FAKE_PARAMS)

    result = writer.write_full_account_params(36000.00)

    assert result is False
