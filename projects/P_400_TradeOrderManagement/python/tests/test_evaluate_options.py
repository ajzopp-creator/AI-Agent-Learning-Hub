"""test_evaluate_options.py -- Unit tests for application/evaluate_options.py.

Pure orchestration test -- infrastructure readers monkeypatched so no real
filesystem state (P_010, P_000, chain file) is required.
"""

import sys
from pathlib import Path

import pytest


from schemas import AccountParams, OptionChainInput, PostureSnapshot
from application import evaluate_options as eo_module
from application.evaluate_options import evaluate_options


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
# WO-P400-E8.003: evaluate_options() no longer takes a packet -- symbol/
# stock_stop/stock_target passed directly below (values match what
# make_packet() used to supply: symbol="TEST", stop=95.0, target=115.0).

def make_chain(**kwargs) -> OptionChainInput:
    defaults = dict(
        symbol="TEST", underlying_price=100.0, expiration="2026-07-17",
        strike=100.0, option_type="call",
        bid=4.80, ask=5.20, mid=5.00,
        delta=0.50, iv=0.30,
        open_interest=300, spread_pct_of_mid=8.0,
        data_source="tos", chain_timestamp="2026-06-30T10:00:00Z",
    )
    defaults.update(kwargs)
    return OptionChainInput(**defaults)


def make_snapshot(**kwargs) -> dict:
    defaults = dict(
        symbol="TEST", price=100.0, bid=99.95, ask=100.05,
        price_timestamp="2026-06-30T10:00:00Z", price_delay_seconds=5,
        atr_14=2.5, avg_volume_20d=1000000, data_source="web",
    )
    defaults.update(kwargs)
    return defaults


def _patch_readers(monkeypatch, chain, oi=300, spread_pct=8.0):
    monkeypatch.setattr(eo_module, "load_chain", lambda path: chain)
    monkeypatch.setattr(eo_module, "read_posture", lambda: PostureSnapshot(
        risk_mode="OFF", avg_posture=-5.99, timestamp="2026-06-30T10:00:00Z",
    ))
    monkeypatch.setattr(eo_module, "read_params", lambda: AccountParams(
        account_balance=32669.72, risk_per_trade=490.04, max_position=1633.47,
    ))


# ---------------------------------------------------------------------------
# Council PASS -> spec rendered
# ---------------------------------------------------------------------------

def test_council_pass_renders_spec(monkeypatch):
    chain = make_chain()
    _patch_readers(monkeypatch, chain)
    result = evaluate_options(
        symbol="TEST", stock_stop=95.0, stock_target=115.0,
        snapshot_raw=make_snapshot(),
        chain_path="chain_TEST.json", cash_available=6000.0, stock_rr=2.5,
    )
    assert result.verdict in ("PASS", "CAUTION")
    assert result.spec_text is not None
    assert "PATTERN B" in result.spec_text


# ---------------------------------------------------------------------------
# Council BLOCK -> no spec
# ---------------------------------------------------------------------------

def test_council_block_no_spec(monkeypatch):
    chain = make_chain(open_interest=50)  # < 150 minimum -> OI_TOO_LOW block
    _patch_readers(monkeypatch, chain)
    result = evaluate_options(
        symbol="TEST", stock_stop=95.0, stock_target=115.0,
        snapshot_raw=make_snapshot(),
        chain_path="chain_TEST.json", cash_available=6000.0, stock_rr=2.5,
    )
    assert result.verdict == "BLOCK"
    assert result.spec_text is None
    assert any("OI_TOO_LOW" in b for b in result.council.blocks)


# ---------------------------------------------------------------------------
# Chain file missing -> raises cleanly
# ---------------------------------------------------------------------------

def test_missing_chain_file_raises(monkeypatch):
    def _raise(path):
        raise FileNotFoundError(f"Chain file not found: {path}")
    monkeypatch.setattr(eo_module, "load_chain", _raise)
    monkeypatch.setattr(eo_module, "read_posture", lambda: PostureSnapshot(
        risk_mode="OFF", avg_posture=-5.99, timestamp="2026-06-30T10:00:00Z",
    ))
    monkeypatch.setattr(eo_module, "read_params", lambda: AccountParams(
        account_balance=32669.72, risk_per_trade=490.04, max_position=1633.47,
    ))
    with pytest.raises(FileNotFoundError):
        evaluate_options(
            symbol="TEST", stock_stop=95.0, stock_target=115.0,
            snapshot_raw=make_snapshot(),
            chain_path="chain_MISSING.json", cash_available=6000.0, stock_rr=2.5,
        )