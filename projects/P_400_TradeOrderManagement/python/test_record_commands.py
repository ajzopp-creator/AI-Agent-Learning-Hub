"""test_record_commands.py -- WO-P400-E3.006: cmd_record_submit / cmd_record_decline.

Both eval_cache and record_writer are monkeypatched -- no real filesystem
or Obsidian I/O. Verifies the packet/archiver is never touched (the whole
point of this WO: no second archive_packet call on a `record` invocation).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import application.record_commands as rc_module


APPROVED_CACHE = {
    "symbol": "MSTR", "verdict": "APPROVED", "risk_mode": "OFF",
    "entry_price": 101.96, "stop_price": 90.81, "target_1": 136.25,
    "position_size": 7, "signal_source": "P_300",
    "trade_mode_value": "REAL", "drop_reason": None,
    "signal_date": "2026-07-02",
}


def _patch_cache(monkeypatch, cached):
    monkeypatch.setattr(rc_module, "read_eval_cache", lambda symbol: cached)


def _patch_writer(monkeypatch):
    captured = {}
    def fake_write(**kwargs):
        captured.update(kwargs)
        return True
    monkeypatch.setattr(rc_module, "write_p400_record", fake_write)
    return captured


def test_submit_no_cache_errors(monkeypatch, capsys):
    _patch_cache(monkeypatch, None)
    result = rc_module.cmd_record_submit("MSTR", "5365031365")
    assert result == 1
    assert "No cached" in capsys.readouterr().out


def test_submit_wrong_verdict_errors(monkeypatch, capsys):
    _patch_cache(monkeypatch, {**APPROVED_CACHE, "verdict": "BLOCKED"})
    result = rc_module.cmd_record_submit("MSTR", "5365031365")
    assert result == 1
    assert "only APPROVED" in capsys.readouterr().out


def test_submit_writes_order_id(monkeypatch):
    _patch_cache(monkeypatch, APPROVED_CACHE)
    captured = _patch_writer(monkeypatch)
    result = rc_module.cmd_record_submit("MSTR", "5365031365")
    assert result == 0
    assert captured["order_id"] == "5365031365"
    assert captured["symbol"] == "MSTR"
    assert captured["position_size"] == 7


def test_submit_paper_override_sets_trade_mode_paper(monkeypatch):
    _patch_cache(monkeypatch, APPROVED_CACHE)
    captured = _patch_writer(monkeypatch)
    result = rc_module.cmd_record_submit("MSTR", "5365031365", paper=True)
    assert result == 0
    assert captured["trade_mode_value"] == "PAPER"


def test_submit_without_paper_flag_keeps_cached_mode(monkeypatch):
    _patch_cache(monkeypatch, APPROVED_CACHE)
    captured = _patch_writer(monkeypatch)
    result = rc_module.cmd_record_submit("MSTR", "5365031365")
    assert result == 0
    assert captured["trade_mode_value"] == "REAL"


def test_submit_paper_override_does_not_mutate_eval_cache(monkeypatch):
    cached = dict(APPROVED_CACHE)
    _patch_cache(monkeypatch, cached)
    _patch_writer(monkeypatch)
    rc_module.cmd_record_submit("MSTR", "5365031365", paper=True)
    assert cached["trade_mode_value"] == "REAL"


def test_decline_no_cache_errors(monkeypatch, capsys):
    _patch_cache(monkeypatch, None)
    result = rc_module.cmd_record_decline("MSTR")
    assert result == 1
    assert "No cached" in capsys.readouterr().out


def test_decline_wrong_verdict_errors(monkeypatch, capsys):
    _patch_cache(monkeypatch, {**APPROVED_CACHE, "verdict": "BLOCKED"})
    result = rc_module.cmd_record_decline("MSTR")
    assert result == 1
    assert "decline only applies" in capsys.readouterr().out


def test_decline_writes_manual_decline(monkeypatch):
    _patch_cache(monkeypatch, APPROVED_CACHE)
    captured = _patch_writer(monkeypatch)
    result = rc_module.cmd_record_decline("MSTR")
    assert result == 0
    assert captured["drop_reason"] == "MANUAL_DECLINE"
    assert "order_id" not in captured

# ---------------------------------------------------------------------------
# Regression: cache_written_at/spec_text (WO-P400-E3.009 spec cache)
# must never reach write_p400_record() -- live WMT failure 2026-07-14,
# TypeError: unexpected keyword argument 'spec_text'
# ---------------------------------------------------------------------------

CACHE_WITH_SPEC_TEXT = {
    **APPROVED_CACHE,
    "spec_text": "BUY 10 WMT @ 114.22 LIMIT, DAY",
    "cache_written_at": "2026-07-14",
}


def test_submit_strips_spec_text_before_writer(monkeypatch):
    _patch_cache(monkeypatch, CACHE_WITH_SPEC_TEXT)
    captured = _patch_writer(monkeypatch)
    result = rc_module.cmd_record_submit("MSTR", "5365031365")
    assert result == 0
    assert "spec_text" not in captured
    assert "cache_written_at" not in captured
    assert captured["order_id"] == "5365031365"


def test_decline_strips_spec_text_before_writer(monkeypatch):
    _patch_cache(monkeypatch, CACHE_WITH_SPEC_TEXT)
    captured = _patch_writer(monkeypatch)
    result = rc_module.cmd_record_decline("MSTR")
    assert result == 0
    assert "spec_text" not in captured
    assert "cache_written_at" not in captured
    assert captured["drop_reason"] == "MANUAL_DECLINE"
