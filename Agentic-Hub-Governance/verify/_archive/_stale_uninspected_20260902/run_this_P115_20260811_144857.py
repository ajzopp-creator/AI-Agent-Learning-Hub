"""
run_this_P115_20260811_144857.py
PEH verification script: emits SIGNAL_V2 packet for WSM BUY signal.
Session: 2026-08-11 P_115 session. Ticker: WSM.
Calls application.emit_signal.emit_signal() directly with STEP1-confirmed values.
"""
import sys
import traceback
import datetime
from pathlib import Path

PROJECT_PYTHON = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python"
sys.path.insert(0, PROJECT_PYTHON)

DONE_PATH = Path(__file__).resolve().parent / (Path(__file__).name + ".done")


def write_done(status, exit_code, detail=""):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    DONE_PATH.write_text(f"{status}\n{exit_code}\n{ts}\n{detail}\n", encoding="utf-8")


try:
    from application.emit_signal import emit_signal

    path = emit_signal(
        symbol="WSM",
        session_date="2026-08-11",
        signal_timestamp="2026-08-11T14:48:57Z",
        strategy="dip_buy",
        guideline_entry=253.10,
        guideline_stop=227.82,
        guideline_target=341.64,
        signal_horizon="5-10 days",
        confidence_level="HIGH",
        close_at_signal=252.26,
        trailing_volume_30d=82115.6,
        signal_rationale=(
            "HybridTier 7 (Anal3+Fund4) BUY. RSI 68.6, Daily/4H Uptrend, ADX 28.4 "
            "Strong. Fund Verification clean: ROE ~51.5%, Debt/Cap ~41.2%, FCF "
            "$1.06B positive. PA Stop 227.82 (Structure). 200-MA +25.8% NORMAL, "
            "no penalty."
        ),
        chart_timeframe="1D",
        signal_source_link="TOS_Chart/P_115_BuytheDipChart_V16/WSM_2026-08-11",
        atm_at_signal=None,
        intelliscan_support_1=None,
        intelliscan_support_2=None,
        signal_source="P_115",
    )

    p = Path(path)
    if p.exists():
        print("PASS")
        write_done("PASS", 0, f"signal_written={path}")
    else:
        print(f"FAIL: emit_signal returned path but file does not exist: {path}")
        write_done("FAIL", 1, f"missing_file={path}")
        sys.exit(1)

except Exception as e:
    print(f"FAIL: {e}")
    traceback.print_exc()
    write_done("FAIL", 1, str(e))
    sys.exit(1)
