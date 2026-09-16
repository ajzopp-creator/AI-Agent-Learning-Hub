"""run_this_P115_20260911_112040.py -- PEH verify: emit PATH signal packet.

Emits the P_115 -> P_400 signal for PATH (P_910 scan-sourced, P_115-scored
BUY, Fund-verified, no existing position confirmed by Tony) via the same
emit_signal() call cli.py uses. Never modifies production files -- calls
the existing emit path once and confirms the output landed.
"""
from __future__ import annotations

import sys
import os
from pathlib import Path
from datetime import datetime

PROJECT_PY = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python")
sys.path.insert(0, str(PROJECT_PY))

DONE_PATH = Path(__file__).with_suffix(".py.done")


def write_done(status, exit_code):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    DONE_PATH.write_text("timestamp: " + ts + "\nstatus: " + status + "\nexit_code: " + str(exit_code) + "\n")


def main():
    try:
        import config  # noqa: F401
        from application.emit_signal import emit_signal

        path = emit_signal(
            symbol="PATH",
            session_date="2026-09-11",
            signal_timestamp="2026-09-11T15:20:40Z",
            strategy="dip_buy",
            guideline_entry=13.93,
            guideline_stop=13.15,
            guideline_target=15.40,
            signal_horizon="10-15 trading days",
            confidence_level="HIGH",
            close_at_signal=13.93,
            trailing_volume_30d=8008719,
            signal_rationale=(
                "P_910 scan candidate; P_115 HybridTier 7 (Fund 4 verified: "
                "ROE approx 18pct, D-C approx 3-4pct, FCF positive; Anal 3); "
                "STR:-2 but Fund not 0 so no Cause A auto-reject; price "
                "above rising 200-SMA (+8pct) despite downtrend flag on a "
                "separate overlay study; no existing position confirmed"
            ),
            chart_timeframe="1D",
            signal_source_link="docs/project_notes/2026-09-11_PATH_signal_audit.md",
            atm_at_signal=0.98,
            intelliscan_support_1=None,
            intelliscan_support_2=None,
            signal_source="P_115",
        )
    except Exception as exc:
        print("FAIL:", exc)
        write_done("FAIL", 1)
        sys.exit(1)

    if not os.path.exists(path):
        print("FAIL: emit_signal returned a path that does not exist on disk:", path)
        write_done("FAIL", 1)
        sys.exit(1)

    print("Signal written:", path)
    print("PASS")
    write_done("PASS", 0)


if __name__ == "__main__":
    main()
