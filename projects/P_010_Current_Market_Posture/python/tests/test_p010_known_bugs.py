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
