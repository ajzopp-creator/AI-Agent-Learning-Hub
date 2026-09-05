"""
run_this_P115_20260811_151546.py
PEH verification script: emits SIGNAL_V2 packet for AA BUY signal.
Session: 2026-08-11 P_115 session. Ticker: AA.
Calls application.emit_signal.emit_signal() directly with STEP1-confirmed values.
Fixed from prior run (WSM 144857): emit_signal returns a bool, not a path --
verify success by checking the expected output file directly instead of
wrapping the return value in Path().
"""
import sys
import traceback
import datetime
from pathlib import Path

PROJECT_PYTHON = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python"
sys.path.insert(0, PROJECT_PYTHON)

SIGNALS_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\signals")
EXPECTED_FILE = SIGNALS_DIR / "2026-08-11_AA_v2.0.json"

DONE_PATH = Path(__file__).resolve().parent / (Path(__file__).name + ".done")


def write_done(status, exit_code, detail=""):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    DONE_PATH.write_text(f"{status}\n{exit_code}\n{ts}\n{detail}\n", encoding="utf-8")


try:
    from application.emit_signal import emit_signal

    result = emit_signal(
        symbol="AA",
        session_date="2026-08-11",
        signal_timestamp="2026-08-11T15:15:46Z",
        strategy="dip_buy",
        guideline_entry=53.65,
        guideline_stop=42.26,
        guideline_target=56.94,
        signal_horizon="5-10 days",
        confidence_level="MEDIUM",
        close_at_signal=53.65,
        trailing_volume_30d=2603558,
        signal_rationale=(
            "HybridTier 6 (Anal3+Fund3, bare minimum BUY). Fund Verification clean: "
            "ROE ~19.2%, Debt/Cap ~23%, FCF $519M positive. 200-MA -5.1% (PULLBACK), "
            "-1 penalty applied (raw Fund 4->3). PA Stop 42.26 (Structure). Caveat: "
            "D_102 BigTrendsSNT overlay shows an independent BEAR ACTIVE signal "
            "(entry 53.5, trailing DC/4% exit) concurrently on this chart -- separate "
            "system, not P_115 verdict, flagged not resolved."
        ),
        chart_timeframe="1D",
        signal_source_link="TOS_Chart/P_115_BuytheDipChart_V16/AA_2026-08-11",
        atm_at_signal=None,
        intelliscan_support_1=None,
        intelliscan_support_2=None,
        signal_source="P_115",
    )

    print(f"emit_signal returned: {result!r}")

    if EXPECTED_FILE.exists():
        print("PASS")
        write_done("PASS", 0, f"signal_written={EXPECTED_FILE}")
    else:
        print(f"FAIL: expected signal file not found: {EXPECTED_FILE}")
        write_done("FAIL", 1, f"missing_file={EXPECTED_FILE}")
        sys.exit(1)

except Exception as e:
    print(f"FAIL: {e}")
    traceback.print_exc()
    write_done("FAIL", 1, str(e))
    sys.exit(1)
