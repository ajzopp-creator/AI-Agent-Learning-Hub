"""
run_this_P115_20260902_104300.py
P_118 STEP1 batch (9/2/26) -- STEP 2 emission for DNOW and HNGE.
Both are P_118-sourced (Eddie Z Breakout scan), P_115 recheck engine
determined DNOW=ASYM, HNGE=BUY. Fund Verification clean for both (no
tier drop vs submitted chart values), no post-earnings flag for either.
This calls emit_signal() directly (same call cli.py's main() makes) so
it can run unattended without an interactive --help/argparse round trip,
since the python.exe process for this session stalled past the 4-min
MCP ceiling on a plain --help invocation.

Success criteria: two SIGNAL_V2 packets written to
trading_journal\\TradeOrderManagement\\signals\\ :
  2026-09-02_DNOW_v2.0.json
  2026-09-02_HNGE_v2.0.json
Both files should exist after this script runs and each should contain
signal_source: "P_115" (NOT "P_118" -- packet field is always P_115 per
architecture doc 8.2 step 3, even though tracker SignalSource=P_118 for
these two tickers; see lessons.md 2026-08-24 entry, do not conflate).

What to fix on failure: read the printed exception. Common causes are an
import path issue (config.py / application/emit_signal.py not found --
check sys.path insert below matches the actual project python\\ folder)
or a schema validation error in signal_schemas.py (check the printed
field name against SIGNAL_V2's required fields). Do not change the
emission parameter *values* below (entry/stop/target/etc.) without
Tony's say-so -- those came from live chart reads and stockanalysis.com
verification this session, not placeholders. If a value genuinely looks
wrong, flag it in the output and stop rather than silently adjusting it.
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

    signals = [
        dict(
            symbol="DNOW",
            session_date="2026-09-02",
            signal_timestamp="2026-09-02T14:43:00Z",
            strategy="breakout",
            guideline_entry=16.52,
            guideline_stop=15.32,
            guideline_target=22.24,
            signal_horizon="10-15 trading days",
            confidence_level="MEDIUM",
            close_at_signal=15.98,
            trailing_volume_30d=2542317,
            signal_rationale=(
                "P_118 High Handle candidate; P_115 recheck ASYM "
                "(Fund 2, Anal 3, Candle 2, Setup 3, STR 0). Fund "
                "Verification (stockanalysis.com): ROE -5.23% fails, "
                "Debt/Cap ~21% passes, FCF +$134M passes -- consistent "
                "with submitted Fund=2, no tier drop. 200-MA 17.2% "
                "NORMAL, zero penalty. No earnings until Nov 2026. "
                "BreakoutVerdict (TrueBounce confirmation)=PASS, "
                "Setup/Confirm not yet live-confirmed on chart."
            ),
            chart_timeframe="1D",
            signal_source_link="P_118_STEP1/DNOW_2026-09-02",
            atm_at_signal=None,
            intelliscan_support_1=None,
            intelliscan_support_2=None,
            signal_source="P_115",
        ),
        dict(
            symbol="HNGE",
            session_date="2026-09-02",
            signal_timestamp="2026-09-02T14:43:30Z",
            strategy="breakout",
            guideline_entry=94.20,
            guideline_stop=83.77,
            guideline_target=98.69,
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
                "Setup/Confirm not yet live-confirmed on chart."
            ),
            chart_timeframe="1D",
            signal_source_link="P_118_STEP1/HNGE_2026-09-02",
            atm_at_signal=None,
            intelliscan_support_1=None,
            intelliscan_support_2=None,
            signal_source="P_115",
        ),
    ]

    results = []
    for sig in signals:
        symbol = sig["symbol"]
        try:
            path = emit_signal(
                symbol=sig["symbol"],
                session_date=sig["session_date"],
                signal_timestamp=sig["signal_timestamp"],
                strategy=sig["strategy"],
                guideline_entry=sig["guideline_entry"],
                guideline_stop=sig["guideline_stop"],
                guideline_target=sig["guideline_target"],
                signal_horizon=sig["signal_horizon"],
                confidence_level=sig["confidence_level"],
                close_at_signal=sig["close_at_signal"],
                trailing_volume_30d=sig["trailing_volume_30d"],
                signal_rationale=sig["signal_rationale"],
                chart_timeframe=sig["chart_timeframe"],
                signal_source_link=sig["signal_source_link"],
                atm_at_signal=sig["atm_at_signal"],
                intelliscan_support_1=sig["intelliscan_support_1"],
                intelliscan_support_2=sig["intelliscan_support_2"],
                signal_source=sig["signal_source"],
            )
            print(f"{symbol}: Signal written: {path}")
            results.append((symbol, True, str(path)))
        except Exception as exc:  # noqa: BLE001
            print(f"{symbol}: FAILED -- {exc}")
            traceback.print_exc()
            results.append((symbol, False, str(exc)))

    all_ok = all(ok for _, ok, _ in results)
    if all_ok:
        print("PASS")
        write_done("PASS", 0)
    else:
        print("FAIL:", [s for s, ok, _ in results if not ok])
        write_done("FAIL", 1)
        sys.exit(1)


if __name__ == "__main__":
    main()
