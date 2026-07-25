"""test_vault_scanner.py -- Vault folder scan against real P_300/P_115 data
(WO-P800-E4.001).

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\shared_resources\\
           chaikin_enrichment\\test_vault_scanner.py
"""
from datetime import date

import pytest

import shared_resources.chaikin_enrichment.infrastructure.vault_scanner as vault_scanner


def test_p300_scan_finds_notes_within_default_lookback():
    """2026-07-23_CLF.md's signal_date lags its run_date by one session --
    the exact pattern the old prompt's fallback-day caveat existed for.
    Default LOOKBACK_DAYS against today=2026-07-24 must still find it by
    filename date alone, with no date-guessing."""
    results = vault_scanner.scan_schema("P300", today=date(2026, 7, 24))
    symbols = {n.symbol for n in results}
    assert "CLF" in symbols
    assert "DNN" in symbols


def test_p300_scan_excludes_notes_outside_lookback_window():
    """2026-07-21_CIFR.md is 3 days back from 2026-07-24 -- outside the
    default 1-day lookback window."""
    results = vault_scanner.scan_schema("P300", today=date(2026, 7, 24))
    symbols = {n.symbol for n in results}
    assert "CIFR" not in symbols


def test_wider_lookback_window_includes_cifr(monkeypatch):
    """Confirms the window is driven by config, not hardcoded -- widening
    it must reach CIFR without touching scan_schema's own code."""
    monkeypatch.setattr(vault_scanner, "LOOKBACK_DAYS", 5)
    results = vault_scanner.scan_schema("P300", today=date(2026, 7, 24))
    symbols = {n.symbol for n in results}
    assert "CIFR" in symbols


def test_p115_scan_finds_real_ph_note():
    results = vault_scanner.scan_schema("P115", today=date(2026, 7, 24))
    symbols = {n.symbol for n in results}
    assert "PH" in symbols


def test_unknown_schema_raises():
    with pytest.raises(ValueError):
        vault_scanner.scan_schema("NOT_A_SCHEMA")
