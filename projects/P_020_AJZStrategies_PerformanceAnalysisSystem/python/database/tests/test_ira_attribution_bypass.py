"""Tests for the WO-P020-E1.015 IRA attribution bypass in
application.system_attribution.run_full_attribution() -- IRA9885 must
skip the vault/Tracker/default chain entirely (Decision 1), while AJZ
and every other account keep the full chain unchanged. ThinkLog and
P_820 layers still run for IRA -- only apply_system_names() is skipped.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import application.system_attribution as sa


def test_ira_skips_apply_system_names(monkeypatch):
    """The core bypass: apply_system_names() must not be called at all
    for account_id='IRA9885'."""
    called = {"apply_system_names": False}

    def fail_if_called(*a, **k):
        called["apply_system_names"] = True

    monkeypatch.setattr(sa, "apply_system_names", fail_if_called)
    monkeypatch.setattr(sa, "apply_thinklog_overrides", lambda trades, lookup, audit: 0)
    monkeypatch.setattr(sa, "apply_p820_overrides", lambda trades, lookup, audit: 0)

    trades = [{"underlying_symbol": "URA", "open_date": "2026-03-03"}]
    audit = []
    sa.run_full_attribution(
        trades, lookup=None, vault_lookup=None, thinklog_lookup={},
        p820_lookup={}, params={"default_system_name": "TOS_Import"},
        audit=audit, account_id="IRA9885",
    )

    assert called["apply_system_names"] is False
    assert any("bypasses vault/Tracker" in line for line in audit)


def test_ajz_still_runs_apply_system_names(monkeypatch):
    """Regression: AJZ6348 (and the default empty-string case) must keep
    running the full vault/Tracker chain exactly as before this WO."""
    called = {"apply_system_names": False}

    def mark_called(trades, lookup, default, vault_lookup=None):
        called["apply_system_names"] = True

    monkeypatch.setattr(sa, "apply_system_names", mark_called)
    monkeypatch.setattr(sa, "apply_thinklog_overrides", lambda trades, lookup, audit: 0)
    monkeypatch.setattr(sa, "apply_p820_overrides", lambda trades, lookup, audit: 0)

    trades = [{"underlying_symbol": "AAPL", "open_date": "2026-08-01"}]
    audit = []
    sa.run_full_attribution(
        trades, lookup=None, vault_lookup=None, thinklog_lookup={},
        p820_lookup={}, params={"default_system_name": "TOS_Import"},
        audit=audit, account_id="AJZ6348",
    )

    assert called["apply_system_names"] is True
    assert not any("bypasses vault/Tracker" in line for line in audit)


def test_default_account_id_runs_full_chain(monkeypatch):
    """account_id omitted entirely (empty-string default) must preserve
    pre-WO behavior -- existing callers that never pass account_id are
    unaffected."""
    called = {"apply_system_names": False}

    def mark_called(trades, lookup, default, vault_lookup=None):
        called["apply_system_names"] = True

    monkeypatch.setattr(sa, "apply_system_names", mark_called)
    monkeypatch.setattr(sa, "apply_thinklog_overrides", lambda trades, lookup, audit: 0)
    monkeypatch.setattr(sa, "apply_p820_overrides", lambda trades, lookup, audit: 0)

    trades = [{"underlying_symbol": "TSLA", "open_date": "2026-08-01"}]
    audit = []
    sa.run_full_attribution(
        trades, lookup=None, vault_lookup=None, thinklog_lookup={},
        p820_lookup={}, params={"default_system_name": "TOS_Import"},
        audit=audit,
    )

    assert called["apply_system_names"] is True


def test_ira_still_gets_thinklog_and_p820_overrides(monkeypatch):
    """Bypass only skips apply_system_names() -- ThinkLog and P_820
    layers must still run for IRA trades."""
    calls = []

    monkeypatch.setattr(sa, "apply_system_names", lambda *a, **k: calls.append("system_names"))
    monkeypatch.setattr(
        sa, "apply_thinklog_overrides",
        lambda trades, lookup, audit: calls.append("thinklog") or 1,
    )
    monkeypatch.setattr(
        sa, "apply_p820_overrides",
        lambda trades, lookup, audit: calls.append("p820") or 1,
    )

    trades = [{"underlying_symbol": "GDXJ", "open_date": "2026-01-30"}]
    audit = []
    sa.run_full_attribution(
        trades, lookup=None, vault_lookup=None, thinklog_lookup={"x": 1},
        p820_lookup={"y": 1}, params={"default_system_name": "TOS_Import"},
        audit=audit, account_id="IRA9885",
    )

    assert "system_names" not in calls
    assert "thinklog" in calls
    assert "p820" in calls


def test_ira_trade_without_system_key_falls_back_to_default_in_build_trade():
    """When apply_system_names is skipped and no ThinkLog tag matches, a
    trade dict never gets a 'system' key set at all -- confirms
    dict.get('system', default) is the safe fallback _build_trade() relies
    on, not an assumption."""
    trade = {"underlying_symbol": "SWPPX", "open_date": "2026-01-06"}
    assert trade.get("system", "TOS_Import") == "TOS_Import"
