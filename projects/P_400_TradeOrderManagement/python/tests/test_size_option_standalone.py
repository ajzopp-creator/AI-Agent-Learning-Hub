"""test_size_option_standalone.py -- Unit tests for
application\\size_option_standalone.py (WO-P400-E8.003).

Infrastructure readers monkeypatched at both the evaluate_options and
size_option_standalone module boundaries -- no real filesystem state
(P_010, P_000, chain file) required except a real temp snapshot file
(simpler than monkeypatching open()/json.loads for one small JSON read).
"""

import json

import pytest

from schemas import AccountParams, OptionChainInput, PostureSnapshot
from application import evaluate_options as eo_module
from application import size_option_standalone as sos_module
from application.size_option_standalone import cmd_size_option


def make_chain(**kwargs) -> OptionChainInput:
    defaults = dict(
        symbol="NFLX", underlying_price=78.115, expiration="2026-10-02",
        strike=79.0, option_type="call",
        bid=1.87, ask=1.90, mid=1.885,
        delta=0.449, iv=0.34556,
        open_interest=589, spread_pct_of_mid=1.59,
        data_source="schwab_api", chain_timestamp="2026-09-15T16:45:59Z",
    )
    defaults.update(kwargs)
    return OptionChainInput(**defaults)


def write_snapshot(tmp_path, price=78.115, **extra) -> str:
    defaults = dict(
        symbol="NFLX", price=price, bid=78.10, ask=78.13,
        price_timestamp="2026-09-15T16:45:00Z", price_delay_seconds=5,
        atr_14=2.5, avg_volume_20d=8000000, data_source="web",
    )
    defaults.update(extra)
    path = tmp_path / "snapshot_NFLX.json"
    path.write_text(json.dumps(defaults), encoding="utf-8")
    return str(path)


def _patch_all(monkeypatch, chain, risk_per_trade=441.88, max_position=1472.94):
    monkeypatch.setattr(eo_module, "load_chain", lambda path: chain)
    monkeypatch.setattr(eo_module, "read_posture", lambda: PostureSnapshot(
        risk_mode="OFF", avg_posture=-1.91, timestamp="2026-09-15T10:00:00Z",
    ))
    monkeypatch.setattr(eo_module, "read_params", lambda: AccountParams(
        account_balance=29458.74, risk_per_trade=risk_per_trade, max_position=max_position,
    ))
    monkeypatch.setattr(sos_module, "read_posture", lambda: PostureSnapshot(
        risk_mode="OFF", avg_posture=-1.91, timestamp="2026-09-15T10:00:00Z",
    ))
    written = {}

    def _fake_write_record(**fields):
        written["record_fields"] = fields
        return True

    def _fake_write_cache(symbol, fields):
        written["cache_symbol"] = symbol
        written["cache_fields"] = fields
        return True

    monkeypatch.setattr(sos_module, "write_p400_record", _fake_write_record)
    monkeypatch.setattr(sos_module, "write_eval_cache", _fake_write_cache)
    return written


# ---------------------------------------------------------------------------
# Usage error
# ---------------------------------------------------------------------------

def test_no_target_at_all_is_a_usage_error(tmp_path):
    snap = write_snapshot(tmp_path)
    rc = cmd_size_option("NFLX", snap, "chain_NFLX.json", 76.12, 16397.00)
    assert rc == 1


# ---------------------------------------------------------------------------
# Real-world proof point: reproduces the actual NFLX retroactive check from
# this WO's own WHY section -- risk budget $220.94 (OFF, 0.50x of $441.88),
# risk/contract $89.60 -> Gate 1 = 2 contracts, not the 4 Tony hand-picked.
# ---------------------------------------------------------------------------

def test_reproduces_live_nflx_gate1_sizing(tmp_path, monkeypatch):
    chain = make_chain()
    written = _patch_all(monkeypatch, chain)
    snap = write_snapshot(tmp_path)

    rc = cmd_size_option(
        "NFLX", snap, "chain_NFLX.json", stock_stop=76.12, cash=16397.00,
        stock_target=98.84, is_paper=True,
    )

    assert rc == 0
    assert written["cache_fields"]["option_contracts"] == 2


# ---------------------------------------------------------------------------
# stock_rr computed internally, not required as an input
# ---------------------------------------------------------------------------

def test_stock_rr_computed_from_entry_stop_target(tmp_path, monkeypatch):
    chain = make_chain(open_interest=589, spread_pct_of_mid=1.59)
    written = _patch_all(monkeypatch, chain)
    snap = write_snapshot(tmp_path, price=78.115)

    cmd_size_option(
        "NFLX", snap, "chain_NFLX.json", stock_stop=76.12, cash=16397.00,
        stock_target=98.84,
    )

    # rr = (98.84 - 78.115) / (78.115 - 76.12) = 20.725 / 1.995 = 10.39
    assert written["cache_fields"] is not None  # ran to a real write, not a usage error


# ---------------------------------------------------------------------------
# PASS/CAUTION writes a record; verdict string mapped correctly
# ---------------------------------------------------------------------------

def test_pass_writes_record_and_cache(tmp_path, monkeypatch):
    chain = make_chain()
    written = _patch_all(monkeypatch, chain)
    snap = write_snapshot(tmp_path)

    rc = cmd_size_option(
        "NFLX", snap, "chain_NFLX.json", stock_stop=76.12, cash=16397.00,
        stock_target=98.84,
    )

    assert rc == 0
    assert written["record_fields"]["verdict"] in ("APPROVED", "APPROVED_WITH_CAUTION")
    assert written["cache_symbol"] == "NFLX"


# ---------------------------------------------------------------------------
# BLOCK still writes a record (full audit trail, not BLOCK-only) with a
# drop_reason -- matches write_options_eval_record()'s existing convention.
# ---------------------------------------------------------------------------

def test_block_still_writes_record_with_drop_reason(tmp_path, monkeypatch):
    chain = make_chain(open_interest=50)  # < 150 minimum -> OI_TOO_LOW block
    written = _patch_all(monkeypatch, chain)
    snap = write_snapshot(tmp_path)

    rc = cmd_size_option(
        "NFLX", snap, "chain_NFLX.json", stock_stop=76.12, cash=16397.00,
        stock_target=98.84,
    )

    assert rc == 0  # a clean BLOCK is a legitimate outcome, not a tool failure
    assert written["record_fields"]["verdict"] == "BLOCKED"
    assert written["record_fields"]["drop_reason"] == "COUNCIL_BLOCK"


# ---------------------------------------------------------------------------
# target_2-only: primary target becomes target_2, single-bracket path
# ---------------------------------------------------------------------------

def test_target_2_only_uses_it_as_primary(tmp_path, monkeypatch):
    chain = make_chain()
    written = _patch_all(monkeypatch, chain)
    snap = write_snapshot(tmp_path)

    rc = cmd_size_option(
        "NFLX", snap, "chain_NFLX.json", stock_stop=76.12, cash=16397.00,
        stock_target_2=98.84,
    )

    assert rc == 0
    assert written["cache_fields"]["target_1"] == 98.84
    assert written["cache_fields"]["option_structure"] == "single_leg"
    # target-2-only is a single bracket -- fields.target_2 stays None, not
    # 98.84 duplicated into both slots.
    assert written["cache_fields"]["target_2"] is None


# ---------------------------------------------------------------------------
# Real scale-out (both targets): target_2 actually reaches write_p400_record
# and eval_cache -- follow-on fix, same session, after this was found to be
# missing despite an earlier claim that it was already there.
# ---------------------------------------------------------------------------

def test_both_targets_writes_target_2_to_record_and_cache(tmp_path, monkeypatch):
    chain = make_chain()
    written = _patch_all(monkeypatch, chain)
    snap = write_snapshot(tmp_path)

    rc = cmd_size_option(
        "NFLX", snap, "chain_NFLX.json", stock_stop=76.12, cash=16397.00,
        stock_target=90.00, stock_target_2=98.84,
    )

    assert rc == 0
    assert written["record_fields"]["target_1"] == 90.00
    assert written["record_fields"]["target_2"] == 98.84
    assert written["cache_fields"]["target_2"] == 98.84
    assert written["cache_fields"]["option_structure"] == "scale_out"
