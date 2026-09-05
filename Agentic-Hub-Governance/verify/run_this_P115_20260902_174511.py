"""
run_this_P115_20260902_174511.py
CEG emission -- P_117 (outside rec, info@lockandloadfinance.com), P_115
recheck BUY (Fund 4, Anal 3, Candle 2, Setup 3, STR 0, HybridTier 7).

Tony explicitly overrode a hold: CEG has an active BEAR option position
already open (Days:0, Strike 247.3, P&L 3.6%) shown on the same chart --
same-ticker opposing-direction conflict, FSLR/SATL precedent. Override
confirmed by Tony ("override"), documented in the rationale field below.

Fund Verification (stockanalysis.com) done this session: ROE 15.05% (barely
clears the 15% bar), Debt/Capital ~43% (passes), FCF TTM positive but
negative in several recent fiscal years (capital-intensive nuclear
buildout / Calpine integration) -- soft spots, not a fail, consistent
with submitted Fund=4, no tier drop. Earnings reported 8/6/26, well
outside the 3-session post-earnings window -- clear.

Confidence set MEDIUM rather than HIGH: HybridTier=7 is comfortably above
the BUY threshold, but the opposing-position override plus the
borderline ROE / FCF-volatility caveats both argue against HIGH. Same
reasoning pattern as the AA precedent (bare-threshold BUY + concurrent
bearish signal -> MEDIUM, not HIGH).

Target uses T2 (393.83), not T1 (352.22), per the established convention
(confirmed again today after the HNGE T1/T2 correction).

Success criteria: prints PASS. Confirm the written JSON at
trading_journal\\TradeOrderManagement\\signals\\2026-09-02_CEG_v2.0.json
has signal_source: "P_115" (not "P_117" -- packet field is always P_115,
tracker SignalSource=P_117 is provenance only, do not conflate). Note
from this session: the vault write can take a while to surface elsewhere
(P_400's own note/evaluation runs on a separate schedule, not
immediately) -- the JSON packet itself is what confirms this script's
own success, don't wait on a P400 note to appear before calling this
done.

What to fix on failure: read the printed exception/traceback. Likely
causes: import path wrong, or a SIGNAL_V2 schema validation error --
check the field name in the error against signal_schemas.py. Do not
change entry/stop/target/volume values without Tony's say-so.
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

    symbol = "CEG"
    try:
        result = emit_signal(
            symbol=symbol,
            session_date="2026-09-02",
            signal_timestamp="2026-09-02T21:45:15Z",
            strategy="dip_buy",
            guideline_entry=290.04,
            guideline_stop=267.07,
            guideline_target=393.83,
            signal_horizon="10-15 trading days",
            confidence_level="MEDIUM",
            close_at_signal=290.04,
            trailing_volume_30d=2522443,
            signal_rationale=(
                "P_117 outside rec (info@lockandloadfinance.com); P_115 "
                "recheck BUY (Fund 4, Anal 3, Candle 2, Setup 3, STR 0, "
                "HybridTier 7). Fund Verification (stockanalysis.com): "
                "ROE 15.05% passes but right at the 15% bar, Debt/Capital "
                "~43% passes, FCF TTM positive but negative in several "
                "recent fiscal years (capital-intensive nuclear buildout / "
                "Calpine integration) -- soft spots, consistent with "
                "submitted Fund=4, no tier drop. 200-MA -2.3% NORMAL, "
                "zero penalty despite chart's Trend:BEAR badge (separate "
                "label, doesn't override NORMAL zone). Earnings reported "
                "8/6/26, well outside 3-session window, clear. OVERRIDE: "
                "active BEAR option position already open on CEG (Days:0, "
                "Strike 247.3, P&L 3.6%) -- same-ticker opposing-direction "
                "conflict, FSLR/SATL precedent. Tony explicitly overrode "
                "and confirmed emission. Confidence set MEDIUM (not HIGH) "
                "given the override plus ROE/FCF caveats, despite "
                "HybridTier=7 comfortably clearing BUY threshold."
            ),
            chart_timeframe="1D",
            signal_source_link="P_117/CEG_2026-09-02",
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
