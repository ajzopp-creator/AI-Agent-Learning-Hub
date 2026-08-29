"""Tests for the WO-P020-E1.002 wiring fix in application.paper_import --
spread detection only runs when --raw-csv is given, and the commit flag
propagates to it correctly. Does not touch a real DB -- run_spread_import
and import_spreads are monkeypatched.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "application"))

import paper_import


def test_run_spread_import_missing_file_returns_zero_stats(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.csv"
    result = paper_import.run_spread_import(missing, commit=True)
    assert result == {"found": 0, "imported": 0}
    assert "not found" in capsys.readouterr().out


def test_run_spread_import_calls_import_spreads_with_commit_flag(tmp_path, monkeypatch):
    """Confirms the actual wiring: run_spread_import opens a connection
    and calls import_spreads() with the same commit value it was given."""
    raw_csv = tmp_path / "AccountStatement.csv"
    raw_csv.write_text("dummy", encoding="utf-8")

    calls = []

    class FakeConn:
        def close(self):
            calls.append("closed")

    def fake_get_connection():
        calls.append("connected")
        return FakeConn()

    def fake_import_spreads(conn, csv_path, commit, verbose):
        calls.append(("import_spreads", csv_path, commit, verbose))
        return {"found": 1, "imported": 1 if commit else 0}

    import infrastructure.db_client as db_client
    import paper_spread_import as psi
    monkeypatch.setattr(db_client, "get_connection", fake_get_connection)
    monkeypatch.setattr(psi, "import_spreads", fake_import_spreads)

    result = paper_import.run_spread_import(raw_csv, commit=True)

    assert result == {"found": 1, "imported": 1}
    assert "connected" in calls
    assert "closed" in calls
    assert any(c[0] == "import_spreads" and c[2] is True for c in calls if isinstance(c, tuple))


def test_run_spread_import_dry_run_does_not_write(tmp_path, monkeypatch):
    raw_csv = tmp_path / "AccountStatement.csv"
    raw_csv.write_text("dummy", encoding="utf-8")

    class FakeConn:
        def close(self):
            pass

    def fake_get_connection():
        return FakeConn()

    def fake_import_spreads(conn, csv_path, commit, verbose):
        return {"found": 1, "imported": 1 if commit else 0}

    import infrastructure.db_client as db_client
    import paper_spread_import as psi
    monkeypatch.setattr(db_client, "get_connection", fake_get_connection)
    monkeypatch.setattr(psi, "import_spreads", fake_import_spreads)

    result = paper_import.run_spread_import(raw_csv, commit=False)

    assert result == {"found": 1, "imported": 0}


def test_main_without_raw_csv_skips_spread_detection(tmp_path, monkeypatch, capsys):
    """No --raw-csv given -- behavior identical to before this option
    existed, no spread detection attempted."""
    options_csv = tmp_path / "opts.csv"
    options_csv.write_text("Symbol,System\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["paper_import.py", "--options", str(options_csv)])
    monkeypatch.setattr(paper_import, "read_options_csv", lambda p: [])
    monkeypatch.setattr(paper_import, "write_trades", lambda trades: {
        "inserted": 0, "skipped_dup": 0, "errors": 0, "exits_inserted": 0
    })

    called = {"spread": False}
    def fail_if_called(*a, **k):
        called["spread"] = True
        return {"found": 0, "imported": 0}
    monkeypatch.setattr(paper_import, "run_spread_import", fail_if_called)

    paper_import.main()

    assert called["spread"] is False
    assert "Spread detection" not in capsys.readouterr().out
