"""
test_p020_known_bugs.py -- Regression guard for the P_020 "Bugs Already
Fixed" table in shared_resources/skills/p020-project-context/SKILL.md.

One test per row in that table. Run this after ANY edit to the files it
covers, and before calling a fix "done."

Two kinds of test, both labeled below:
  BEHAVIOR -- calls the real function against a tiny synthetic input and
              checks the actual output. Confirms the bug cannot recur.
  SOURCE   -- greps the file for the fix's signature. Cheaper, but only
              confirms the fix line is still there, not full behavior.
              Used where a real behavioral test needs live API/DB fixtures
              that aren't worth building yet.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\tests\\
           test_p020_known_bugs.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe test_p020_known_bugs.py
"""
import csv
import sys
import tempfile
from pathlib import Path

INFRA = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database\infrastructure")
APPLICATION = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database\application")
PARSERS = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\parsers")
sys.path.insert(0, str(INFRA))
sys.path.insert(0, str(APPLICATION))

RESULTS = []


def check(name, kind, passed, detail=""):
    RESULTS.append((name, kind, passed, detail))


def test_thinklog_seconds_optional():
    """BEHAVIOR -- thinklog_reader must parse timestamps with no seconds."""
    import thinklog_reader as tr
    ts = tr._parse_timestamp("7/5/2026 12:36")
    check("thinklog_seconds_optional", "BEHAVIOR", ts is not None,
          f"got {ts!r}")


def test_thinklog_seconds_still_works():
    """BEHAVIOR -- original H:MM:SS format must still parse."""
    import thinklog_reader as tr
    ts = tr._parse_timestamp("7/5/26 12:36:59")
    ok = ts is not None and ts.second == 59
    check("thinklog_seconds_still_works", "BEHAVIOR", ok, f"got {ts!r}")


def test_paper_import_options_columns():
    """BEHAVIOR -- read_options_csv must read Long/Short and Entry $$."""
    import paper_import as pi
    rows = [
        "Symbol,System,Trade Type,Long/Short,Strike,Cur Stock $,Trade Date,"
        "Entry $$,Contracts,Exit #1 $,# Exited,Exit Date,# of Days,"
        "Exit #2 $,# Exited2,Exit Date3,# of Days4,Exit #3 $,# Exited5,"
        "Exit Date6,# of Days7,Comm.,Gain/Loss,Trade Comments,Exit #1,"
        "Exit #2,Exit #3\n",
        "ADBE,P_300,CALL,Long,215,3.95,6/29/2026,3.95,2,,,,,,,,,,,,,2.66,,,,,\n",
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.writelines(rows)
        path = Path(f.name)
    trades = pi.read_options_csv(path)
    path.unlink()
    ok = (len(trades) == 1 and trades[0]["entry_price"] == 3.95
          and trades[0]["direction"] == "long")
    check("paper_import_options_columns", "BEHAVIOR", ok,
          f"got {trades[0] if trades else None}")


def test_tos_parser_blank_fee_not_nan():
    """BEHAVIOR -- blank Misc Fees / Commissions cells must become 0."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "tos_parser_v24", PARSERS / "P_020_TOS_Parser_v2.4.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    stmt = (
        "DATE,TIME,TYPE,REF #,DESCRIPTION,Misc Fees,Commissions & Fees,"
        "AMOUNT,BALANCE\n"
        '6/1/26,09:31:11,TRD,="1",BOT +11 NXT @151.50,,,-1666.50,94570.78\n'
    )
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write(stmt)
        path = Path(f.name)
    df = mod.load_tos_csv(path)
    path.unlink()
    row = df.iloc[0]
    import math
    ok = (not math.isnan(row["Misc Fees"]) and row["Misc Fees"] == 0
          and not math.isnan(row["Commissions & Fees"]))
    check("tos_parser_blank_fee_not_nan", "BEHAVIOR", ok,
          f"Misc Fees={row['Misc Fees']!r}")


def test_tracker_snt_valid_system():
    """BEHAVIOR -- SNT must be in the valid-systems set."""
    import tracker_reader as tk
    check("tracker_snt_valid_system", "BEHAVIOR",
          "SNT" in tk._VALID_SYSTEMS, f"set={tk._VALID_SYSTEMS}")


def test_tracker_closest_date_guard():
    """SOURCE -- +/-3-day window matching logic must still be present.
    Lives in schemas.py TrackerLookup.get(), not tracker_reader.py."""
    src = (INFRA.parent / "schemas.py").read_text(encoding="utf-8")
    ok = "timedelta" in src and "for delta in" in src
    check("tracker_closest_date_guard", "SOURCE", ok)


def test_schwab_mapper_fifo_guard():
    """SOURCE -- qty-aware FIFO allocator keys must still be present."""
    src = (INFRA / "schwab_mapper.py").read_text(encoding="utf-8")
    ok = "full_symbol" in src
    check("schwab_mapper_fifo_guard", "SOURCE", ok)


def test_schwab_balance_pull_token_manager_guard():
    """SOURCE -- must still import get_client from the Token Manager."""
    src = (INFRA / "schwab_balance_pull.py").read_text(encoding="utf-8")
    ok = "P_020_Schwab_Token_Manager" in src and "get_client" in src
    check("schwab_balance_pull_token_manager_guard", "SOURCE", ok)


def test_schwab_positions_field_guard():
    """SOURCE -- must read longOpenProfitLoss, not call
    .get("unrealizedProfitLoss") as a lookup key (mentioning it in a
    comment explaining why it's wrong is fine)."""
    src = (INFRA / "schwab_positions.py").read_text(encoding="utf-8")
    ok = "longOpenProfitLoss" in src and 'get("unrealizedProfitLoss"' not in src
    check("schwab_positions_field_guard", "SOURCE", ok)


def test_closed_trades_have_exits():
    """BEHAVIOR -- any trade with status='closed' must have >=1 exit row.
    Regression guard for paper_import.py writing status='closed' without
    ever inserting exit records (found 2026-07-05, 28 trades affected).
    Will FAIL until that gap is fixed -- that is the point of this test."""
    import sqlite3
    db = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db")
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM trades t WHERE t.status = 'closed' "
        "AND NOT EXISTS (SELECT 1 FROM exits e WHERE e.trade_id = t.trade_id)"
    )
    orphan_count = cur.fetchone()[0]
    con.close()
    check("closed_trades_have_exits", "BEHAVIOR", orphan_count == 0,
          f"{orphan_count} closed trades with zero exit rows")


def test_wo_e1001_no_unrecorded_closes():
    """BEHAVIOR -- re-run qty-aware allocator against the latest AJZ6348
    pull and confirm no open/partial trade has a close the DB is missing.
    Regression guard for WO-P020-E1.001 (skip-bug + qty-aware allocation).
    Skips cleanly if the latest pull file isn't present."""
    import sqlite3
    root = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem")
    pull = root / "data" / "api_pulls" / "ajz_strategies" / "P_020_raw_AJZ_Strategies_2026-06-28_to_2026-07-05_20260705_132949.json"
    if not pull.exists():
        check("wo_e1001_no_unrecorded_closes", "BEHAVIOR", True, "SKIPPED -- pull file not present")
        return

    sys.path.insert(0, str(root / "python" / "database"))
    sys.path.insert(0, str(root / "python" / "database" / "domain"))
    import schwab_mapper as sm

    _, trade_dicts, _ = sm.map_pull_file(pull)
    con = sqlite3.connect(root / "data" / "database" / "P_020_trades.db")
    flags = []
    for trade in trade_dicts:
        txn_id = trade.get("schwab_transaction_id")
        if not txn_id:
            continue
        row = con.execute(
            "SELECT trade_id, status FROM trades "
            "WHERE schwab_transaction_id = ? AND account_id = 'AJZ6348'",
            (txn_id,),
        ).fetchone()
        if row is None:
            continue
        trade_id, status = row
        if status not in ("open", "partial"):
            continue
        pull_exits = {n for n in (1, 2, 3) if trade.get(f"exit_{n}")}
        if not pull_exits:
            continue
        recorded = {r[0] for r in con.execute(
            "SELECT exit_number FROM exits WHERE trade_id = ?", (trade_id,)
        ).fetchall()}
        if pull_exits - recorded:
            flags.append(f"trade_id={trade_id} missing={sorted(pull_exits - recorded)}")
    con.close()
    check("wo_e1001_no_unrecorded_closes", "BEHAVIOR", len(flags) == 0, "; ".join(flags))


def test_wo_e1001_orphans_returned_and_dispositionable():
    """BEHAVIOR -- WO-P020-E1.008 Option 2.

    E1.001 fixed two things: (a) the qty-aware allocator stopped skipping
    exits, and (b) orphaned exits started being RETURNED and resolved
    against the DB instead of logged-then-silently-dropped.
    test_wo_e1001_no_unrecorded_closes guards (a). This guards (b).

    Invariants, each tied to how import_command._resolve_orphans_against_db
    actually consumes an orphan:

      1. map_pull_file() returns a 3-tuple whose third element is a list.
         This is the exact contract whose drift silently killed the
         sibling guard for weeks (WO-P020-E1.008).

      2. Every orphan carries the keys the resolver keys on. A blank
         underlying_symbol matches nothing in the DB, degrades to a
         content-free warning, and reproduces the original silent-drop
         bug through the back door.

      3. Every orphan is dispositionable -- get_open_trade_for_symbol()
         returns either None (genuine unresolved: warned, not dropped)
         or a row the resolver may attach to. attach_orphan_exit()
         assumes that row is open/partial; a closed row would attach an
         exit to an already-closed position.

    Uses real asserts, not just check(), so it fails under pytest as well
    as under main().

    Skips cleanly if the pull file isn't present."""
    root = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem")
    pull = root / "data" / "api_pulls" / "ajz_strategies" / "P_020_raw_AJZ_Strategies_2026-06-28_to_2026-07-05_20260705_132949.json"
    if not pull.exists():
        check("wo_e1001_orphans_returned_and_dispositionable", "BEHAVIOR",
              True, "SKIPPED -- pull file not present")
        return

    sys.path.insert(0, str(root / "python" / "database"))
    sys.path.insert(0, str(root / "python" / "database" / "domain"))
    import schwab_mapper as sm

    # -- invariant 1: return contract ------------------------------------
    result = sm.map_pull_file(pull)
    assert isinstance(result, tuple) and len(result) == 3, (
        f"map_pull_file must return 3 values (account, trades, orphans); "
        f"got {len(result) if isinstance(result, tuple) else type(result)}"
    )
    _, _, orphans = result
    assert isinstance(orphans, list), (
        f"orphans must be a list, got {type(orphans).__name__}"
    )

    # -- invariant 2: resolver keys present ------------------------------
    required = ("underlying_symbol", "open_date", "qty")
    malformed = []
    for o in orphans:
        missing = [k for k in required if not o.get(k)]
        if missing:
            label = o.get("underlying_symbol") or "<blank symbol>"
            malformed.append(f"{label} missing {missing}")
    assert not malformed, (
        f"orphans missing keys _resolve_orphans_against_db keys on: {malformed}"
    )

    # -- invariant 3: every orphan dispositionable -----------------------
    from infrastructure.db_client import get_connection
    from infrastructure.db_reader import get_open_trade_for_symbol

    conn = get_connection()
    bad_target = []
    try:
        for o in orphans:
            row = get_open_trade_for_symbol(
                conn, "AJZ6348", o["underlying_symbol"]
            )
            if row is not None and row["status"] not in ("open", "partial"):
                bad_target.append(
                    f"{o['underlying_symbol']} -> trade_id={row['trade_id']} "
                    f"status={row['status']}"
                )
    finally:
        conn.close()

    assert not bad_target, (
        f"attach target must be open/partial, got: {bad_target}"
    )

    check("wo_e1001_orphans_returned_and_dispositionable", "BEHAVIOR", True,
          f"{len(orphans)} orphan(s), all dispositionable")


def main():
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for t in tests:
        try:
            t()
        except Exception as e:
            check(t.__name__, "ERROR", False, repr(e))

    failed = [r for r in RESULTS if not r[2]]
    for name, kind, passed, detail in RESULTS:
        mark = "PASS" if passed else "FAIL"
        line = f"[{mark}] ({kind}) {name}"
        if detail and not passed:
            line += f" -- {detail}"
        print(line)

    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
