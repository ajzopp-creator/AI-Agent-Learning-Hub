"""Tests for application.reconcile_command -- the datetime-parsing fix
behind WO-P400-E6.001's live-API reconcile leg (found live 2026-09-17:
schwab-py requires datetime objects for from/to_entered_datetime, not
plain ISO strings; the pull silently threw and got swallowed before
this fix).
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from application.reconcile_command import _parse_pull_datetime


def test_parse_pull_datetime_accepts_date_only():
    """CLI's --start/--end are commonly passed as plain dates
    ('2026-09-14'), the exact form that broke the 2026-09-17 live run."""
    result = _parse_pull_datetime("2026-09-14")
    assert result == datetime(2026, 9, 14)


def test_parse_pull_datetime_accepts_full_iso_datetime():
    result = _parse_pull_datetime("2026-09-14T16:06:40")
    assert result == datetime(2026, 9, 14, 16, 6, 40)


def test_parse_pull_datetime_returns_datetime_not_str():
    """The whole point of the fix: schwab-py rejects a plain str."""
    result = _parse_pull_datetime("2026-09-14")
    assert isinstance(result, datetime)
    assert not isinstance(result, str)
