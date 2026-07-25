r"""Tests for application/dispose_failed.py -- WO-P400-E2.018 verify.

Run: C:\Users\Trader\.conda\envs\p140\python.exe -m pytest test_dispose_failed.py -v

Covers: FAIL triggers drop_signal with correct reason code, PASS/WARN
untouched, mixed batch only disposes FAILs, missing packet is skipped.
drop_signal itself is mocked -- no real archive/vault I/O in these tests.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.dirname(__file__))

from types import SimpleNamespace
from unittest.mock import patch

from config import TradeMode
from domain.screen import ScreenResult, SCREEN_PASS, SCREEN_FAIL, SCREEN_WARN
from application.dispose_failed import dispose_failed


def _result(symbol, outcome, reason_codes=None):
    return ScreenResult(
        symbol=symbol,
        signal_file=f"{symbol}_test_v2.0.json",
        outcome=outcome,
        reason_codes=reason_codes or [],
        packet_rr=1.0,
        posture_gate_shares=10,
    )


def _packet(symbol):
    return SimpleNamespace(symbol=symbol)


# ---------------------------------------------------------------------------
# FAIL triggers drop_signal with correct reason code
# ---------------------------------------------------------------------------

def test_fail_disposes_with_reason_code():
    results = [_result("ZM", SCREEN_FAIL, ["RR_BELOW_MIN"])]
    packets = [_packet("ZM")]

    with patch("application.drop_signal.drop_signal", return_value=True) as mock_drop:
        outcomes = dispose_failed(results, packets, TradeMode.REAL)

    mock_drop.assert_called_once_with(packets[0], "RR_BELOW_MIN", TradeMode.REAL)
    assert len(outcomes) == 1
    assert outcomes[0].symbol == "ZM"
    assert outcomes[0].drop_reason == "RR_BELOW_MIN"
    assert outcomes[0].archived is True
    assert outcomes[0].written is True


def test_fail_joins_multiple_reason_codes():
    results = [_result("KR", SCREEN_FAIL, ["RR_BELOW_MIN", "DUPLICATE_OPEN"])]
    packets = [_packet("KR")]

    with patch("application.drop_signal.drop_signal", return_value=True) as mock_drop:
        dispose_failed(results, packets, TradeMode.REAL)

    mock_drop.assert_called_once_with(packets[0], "RR_BELOW_MIN+DUPLICATE_OPEN", TradeMode.REAL)


# ---------------------------------------------------------------------------
# PASS and WARN untouched
# ---------------------------------------------------------------------------

def test_pass_never_disposed():
    results = [_result("MSTR", SCREEN_PASS, [])]
    packets = [_packet("MSTR")]

    with patch("application.drop_signal.drop_signal", return_value=True) as mock_drop:
        outcomes = dispose_failed(results, packets, TradeMode.REAL)

    mock_drop.assert_not_called()
    assert outcomes == []


def test_warn_never_disposed():
    results = [_result("VTR", SCREEN_WARN, ["SIGNAL_STALE"])]
    packets = [_packet("VTR")]

    with patch("application.drop_signal.drop_signal", return_value=True) as mock_drop:
        outcomes = dispose_failed(results, packets, TradeMode.REAL)

    mock_drop.assert_not_called()
    assert outcomes == []


# ---------------------------------------------------------------------------
# Mixed batch only disposes FAILs
# ---------------------------------------------------------------------------

def test_mixed_batch_disposes_only_fails():
    results = [
        _result("MSTR", SCREEN_PASS, []),
        _result("ZM", SCREEN_FAIL, ["RR_BELOW_MIN"]),
        _result("VTR", SCREEN_WARN, ["SIGNAL_STALE"]),
        _result("GOOGL", SCREEN_FAIL, ["RR_BELOW_MIN"]),
    ]
    packets = [_packet("MSTR"), _packet("ZM"), _packet("VTR"), _packet("GOOGL")]

    with patch("application.drop_signal.drop_signal", return_value=True) as mock_drop:
        outcomes = dispose_failed(results, packets, TradeMode.REAL)

    assert mock_drop.call_count == 2
    disposed_symbols = {o.symbol for o in outcomes}
    assert disposed_symbols == {"ZM", "GOOGL"}


# ---------------------------------------------------------------------------
# Missing packet is skipped, not crashed
# ---------------------------------------------------------------------------

def test_fail_with_no_matching_packet_is_skipped():
    results = [_result("NOPKT", SCREEN_FAIL, ["RR_BELOW_MIN"])]
    packets = []

    with patch("application.drop_signal.drop_signal", return_value=True) as mock_drop:
        outcomes = dispose_failed(results, packets, TradeMode.REAL)

    mock_drop.assert_not_called()
    assert outcomes == []


# ---------------------------------------------------------------------------
# Partial failure (drop_signal returns False) reflected in outcome
# ---------------------------------------------------------------------------

def test_drop_signal_failure_reflected():
    results = [_result("GDYN", SCREEN_FAIL, ["RR_BELOW_MIN"])]
    packets = [_packet("GDYN")]

    with patch("application.drop_signal.drop_signal", return_value=False):
        outcomes = dispose_failed(results, packets, TradeMode.REAL)

    assert outcomes[0].archived is False
    assert outcomes[0].written is False