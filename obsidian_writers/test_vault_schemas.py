"""test_vault_schemas.py — P400Record options-field coverage (WO-P400-E3.004 scope item 5).

Confirms the schema fix: options fields no longer silently dropped (Pydantic
default `extra` behavior was "ignore" before this fix -- now "forbid" on
P400Record specifically), and that the 10 options fields + order_id-adjacent
fields record_writer.py passes are all accepted.
"""
import pytest
from pydantic import ValidationError

from domain.vault_schemas import P400Record


def _base_fields() -> dict:
    return {
        "signal_date": "2026-06-29",
        "run_date": "2026-06-29",
        "run_ts": "2026-06-29T14:00:00",
        "written_by": "test",
        "ticker": "TEST",
    }


def test_p400record_accepts_options_fields():
    """All 10 options fields record_writer.py passes are accepted, not dropped."""
    data = _base_fields()
    data.update({
        "option_method": "chart_based",
        "option_structure": "single_leg",
        "option_contract": "ADBE260717C215",
        "option_entry_premium": 4.00,
        "option_stop_premium": 0.01,
        "option_target_premium": 27.38,
        "option_contracts": 1,
        "option_override": True,
        "option_override_justification": "OVERRIDE BLOCK ON ADBE -- I ACCEPT RESPONSIBILITY",
        "iv_rank": 40.7,
    })
    record = P400Record(**data)
    assert record.option_contract == "ADBE260717C215"
    assert record.option_contracts == 1
    assert record.option_override is True
    assert record.iv_rank == 40.7


def test_p400record_options_fields_default_none_for_stock():
    """Stock-only records (no options kwargs passed) still construct cleanly,
    all options fields default None -- matches record_writer.py stock-path calls."""
    record = P400Record(**_base_fields())
    assert record.option_method is None
    assert record.option_contracts is None
    assert record.option_override is None


def test_p400record_rejects_truly_unknown_field():
    """extra='forbid' on P400Record: a genuinely unrecognized field now raises
    loudly instead of silently vanishing (the original bug this WO fixes)."""
    data = _base_fields()
    data["totally_made_up_field_xyz"] = "should not be allowed"
    with pytest.raises(ValidationError):
        P400Record(**data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])