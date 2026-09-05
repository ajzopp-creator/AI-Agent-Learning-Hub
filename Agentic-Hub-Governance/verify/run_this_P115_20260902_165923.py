"""
run_this_P115_20260902_165923.py
HNGE re-emission with CORRECTED target field.

Original emission this morning (run_this_P115_20260902_104300.py) used
guideline_target=98.69 (T1 Exit). P_400's cli_evaluate ran ~3:28pm and
DROPPED HNGE: council_verdict=REVIEWED_NO_TRADE, drop_reason=RR_BELOW_MIN.
With entry 94.20 / stop 83.77, T1=98.69 gives R:R ~0.43 -- clearly why it
was dropped. Per 2026-09-01 session tool notes (found via conversation
search), the established default is T2 (higher target), not T1. This
script re-emits HNGE with target=105.55 (T2 Exit from the chart) instead.

emit_signal() has overwrite=True hardcoded, so re-running with the same
symbol+session_date safely replaces the existing SIGNAL_V2 vault note --
this is not a duplicate.

Everything else (entry, stop, confidence, rationale substance, volume,
strategy) is unchanged from this morning's emission -- only guideline_target
changes from 98.69 to 105.55, and the rationale gets one added sentence
documenting the correction.

Success criteria: the call completes without exception and prints PASS.
Since emit_signal() writes via P_800's write_to_vault() (an Obsidian note
under TradeOrderManagement\\P400\\, NOT a JSON file under
TradeOrderManagement\\signals\\), do not check for a signals\\ JSON file
as proof -- that path is not where this schema writes. P_400's own
cli_evaluate process picks up the vault note on its own schedule (this
morning it took until ~3:28pm), so this script's own success only confirms
the vault write, not P_400's downstream evaluation. Confirm the vault
write itself by checking
C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\P_800_Automation_Note_Taking
for a freshly modified note, or just re-check
trading_journal\\TradeOrderManagement\\P400\\2026-09-02_HNGE.md later for an
updated run_ts / target_1 value once P_400 re-evaluates.

What to fix on failure: read the printed exception/traceback. Likely
causes: import path wrong, or a SIGNAL_V2 schema validation error --
check the field name in the error against signal_schemas.py. Do not
change the entry/stop/target/volume VALUES beyond the single target
correction described above without Tony's say-so.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from datetime import datetime

PROJECT_PYTHON = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python"
)
sys.path.insert(0, str(PROJECT_PYTHON))

DONE_PATH = Path(__file__).with_suffix(".py.done")


def write_done(status: str, exit_code: int) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    DONE_PATH.write_text(
        f"timestamp: {ts}\nstatus: {status}\nexit_code: {exit_code}\n",
        encoding="utf-8",
    )


def main() -> None:
    from application.emit_signal import emit_signal  # noqa: E402

    symbol = "HNGE"
    try:
        result = emit_signal(
            symbol=symbol,
            session_date="2026-09-02",
            signal_timestamp="2026-09-02T20:59:30Z",
            strategy="breakout",
            guideline_entry=94.20,
            guideline_stop=83.77,
            guideline_target=105.55,  # CORRECTED: was 98.69 (T1), now T2
            signal_horizon="10-15 trading days",
            confidence_level="HIGH",
            close_at_signal=91.84,
            trailing_volume_30d=1666307,
            signal_rationale=(
                "P_118 High Handle candidate; P_115 recheck BUY "
                "(Fund 4, Anal 3, Candle 2, Setup 3, STR 0, HybridTier 7). "
                "Fund Verification (stockanalysis.com): ROE 30.38% "
                "passes, Debt/Equity 0.02 (Debt/Cap ~2%) passes, "
                "FCF +~$290M passes -- exceeds submitted Fund=4, no "
                "tier drop. 200-MA 63.2% NORMAL, zero penalty. Last "
                "earnings Aug 4 2026 (4 weeks ago), no post-earnings "
                "flag. BreakoutVerdict (TrueBounce confirmation)=PASS, "
                "Setup/Confirm not yet live-confirmed on chart. "
                "RE-EMIT 2026-09-02 16:59 ET: original emission used "
                "T1=98.69 as target, giving R:R~0.43 vs stop 83.77 -- "
                "P_400 dropped it (RR_BELOW_MIN). Corrected to T2=105.55 "
                "per established target convention."
            ),
            chart_timeframe="1D",
            signal_source_link="P_118_STEP1/HNGE_2026-09-02_reemit",
            atm_at_signal=None,
            intelliscan_support_1=None,
            intelliscan_support_2=None,
            signal_source="P_115",
        )
        print(f"{symbol}: emit_signal returned: {result}")
        print("PASS")
        write_done("PASS", 0)
    except Exception as exc:  # noqa: BLE001
        print(f"{symbol}: FAILED -- {exc}")
        traceback.print_exc()
        write_done("FAIL", 1)
        sys.exit(1)


if __name__ == "__main__":
    main()
