"""
test_p010_known_bugs.py -- Regression guard for the P_010 Error
Corrections Log (docs/P_010_Error_Corrections_Log.md), mirrored in
.claude/skills/p010-project-context/SKILL.md Bugs Already Fixed table.

One test per error. Run after any edit to P_010_intraday_vp_check_v4.py
or shared_resources/hub_mcp_launcher.ps1, before calling a fix "done."

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_010_Current_Market_Posture\\python\\tests\\
           test_p010_known_bugs.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe test_p010_known_bugs.py
"""
import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture")
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")

if str(PROJECT_ROOT / "python") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "python"))

RESULTS = []


def check(name, kind, passed, detail=""):
    RESULTS.append((name, kind, passed, detail))


def _load_intraday_module():
    """Load P_010_intraday_vp_check_v4.py by path (filename starts with
    a digit-adjacent segment, so import by spec rather than plain import)."""
    path = PROJECT_ROOT / "python" / "P_010_intraday_vp_check_v4.py"
    spec = importlib.util.spec_from_file_location("p010_intraday_v4", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_error001_upgrade_off_to_half():
    """BEHAVIOR -- determine_final_risk_mode() UPGRADE signal (both above
    band) must move OFF -> HALF, not FULL and not stay OFF."""
    mod = _load_intraday_module()
    final_mode, signal, _ = mod.determine_final_risk_mode(
        "OFF",
        {"band_status": "above_band"},
        {"band_status": "above_band"},
    )
    ok = signal == "UPGRADE" and final_mode == "HALF"
    check("error001_upgrade_off_to_half", "BEHAVIOR", ok,
          f"got signal={signal!r} final_mode={final_mode!r}")


def test_error001_downgrade_full_to_half():
    """BEHAVIOR -- DOWNGRADE signal (both below band) must move
    FULL -> HALF, not OFF and not stay FULL."""
    mod = _load_intraday_module()
    final_mode, signal, _ = mod.determine_final_risk_mode(
        "FULL",
        {"band_status": "below_band"},
        {"band_status": "below_band"},
    )
    ok = signal == "DOWNGRADE" and final_mode == "HALF"
    check("error001_downgrade_full_to_half", "BEHAVIOR", ok,
          f"got signal={signal!r} final_mode={final_mode!r}")


def test_error001_confirm_preserves_morning_baseline():
    """BEHAVIOR -- CONFIRM signal (both in band) must return the morning
    baseline unchanged -- this is the exact value the cascade bug used to
    corrupt on a second same-day run."""
    mod = _load_intraday_module()
    final_mode, signal, _ = mod.determine_final_risk_mode(
        "HALF",
        {"band_status": "in_band"},
        {"band_status": "in_band"},
    )
    ok = signal == "CONFIRM" and final_mode == "HALF"
    check("error001_confirm_preserves_morning_baseline", "BEHAVIOR", ok,
          f"got signal={signal!r} final_mode={final_mode!r}")


def test_error001_source_reads_morning_risk_mode_not_risk_mode():
    """SOURCE -- the capture-once-per-day pattern must still be present:
    morning_risk_mode captured from risk_mode only if absent, and every
    subsequent read pulls from morning_risk_mode, never risk_mode directly
    (ERROR 001)."""
    src = (PROJECT_ROOT / "python" / "P_010_intraday_vp_check_v4.py").read_text(encoding="utf-8")
    ok = (
        "'morning_risk_mode' not in risk_config" in src
        and "risk_config['morning_risk_mode'] = risk_config['risk_mode']" in src
        and "morning_baseline = risk_config['morning_risk_mode']" in src
    )
    check("error001_source_reads_morning_risk_mode_not_risk_mode", "SOURCE", ok)


def test_error002_no_start_process_nonewwindow():
    """SOURCE -- the shared Hub launcher must never use
    'Start-Process -NoNewWindow', which inherits MCP's stdio pipes and
    hangs the MCP server until the child exits (ERROR 002). The
    production fix uses a detached Start-Process (-WindowStyle Hidden)
    instead."""
    launcher = HUB_ROOT / "shared_resources" / "hub_mcp_launcher.ps1"
    src = launcher.read_text(encoding="utf-8")
    ok = "-NoNewWindow" not in src and "Start-Process" in src
    check("error002_no_start_process_nonewwindow", "SOURCE", ok)


def _load_freshness_module():
    """Load grid_freshness_check.py by path -- keeps this test file
    consistent with the intraday-module loader above (import by spec,
    not plain import, in case sys.path ever differs at runtime)."""
    path = PROJECT_ROOT / "python" / "grid_freshness_check.py"
    spec = importlib.util.spec_from_file_location("p010_grid_freshness", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_e1004_expected_day_tuesday_to_friday_is_yesterday():
    """BEHAVIOR -- Tue-Fri mornings expect yesterday's grid_date, not
    today's (WO-P010-E1.004)."""
    from datetime import date
    mod = _load_freshness_module()
    # 2026-08-27 is a Thursday
    got = mod.expected_trading_day(date(2026, 8, 27))
    ok = got == date(2026, 8, 26)
    check("e1004_expected_day_tuesday_to_friday_is_yesterday", "BEHAVIOR", ok,
          f"got {got!r}")


def test_e1004_expected_day_monday_is_last_friday():
    """BEHAVIOR -- a Monday morning expects last Friday's grid_date,
    not Sunday's (grid_date legitimately lags 3 calendar days on
    Mondays -- the exact false-positive class this WO must avoid)."""
    from datetime import date
    mod = _load_freshness_module()
    # 2026-08-31 is a Monday
    got = mod.expected_trading_day(date(2026, 8, 31))
    ok = got == date(2026, 8, 28)
    check("e1004_expected_day_monday_is_last_friday", "BEHAVIOR", ok,
          f"got {got!r}")


def test_e1004_fresh_grids_do_not_false_positive():
    """BEHAVIOR -- grid_dates exactly matching expected_trading_day must
    NOT be flagged stale (the E1.004 fix must not become a new source
    of false halts on an ordinary morning)."""
    from datetime import date
    mod = _load_freshness_module()
    today = date(2026, 8, 27)  # Thursday -> expects 2026-08-26
    grid_dates = {"SPY": date(2026, 8, 26), "QQQ": date(2026, 8, 26),
                  "VXX": date(2026, 8, 26)}
    stale, detail = mod.check_grid_freshness(grid_dates, today)
    check("e1004_fresh_grids_do_not_false_positive", "BEHAVIOR", not stale,
          f"stale={stale} detail={detail!r}")


def test_e1004_stale_grid_detected_and_named():
    """BEHAVIOR -- a grid_date older than expected must be flagged
    stale, and the offending symbol named in the detail string (this is
    the exact miss from 2026-08-28: script ran clean on 3-day-old
    QQQ/SPY/VXX data with nothing catching it)."""
    from datetime import date
    mod = _load_freshness_module()
    today = date(2026, 8, 28)  # Friday -> expects 2026-08-27
    grid_dates = {"SPY": date(2026, 8, 25), "QQQ": date(2026, 8, 25),
                  "VXX": date(2026, 8, 25)}
    stale, detail = mod.check_grid_freshness(grid_dates, today)
    ok = stale and "SPY" in detail and "QQQ" in detail and "VXX" in detail
    check("e1004_stale_grid_detected_and_named", "BEHAVIOR", ok,
          f"stale={stale} detail={detail!r}")


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
