"""run_this_P115_20260910_150000.py -- PEH staged emission wrapper (retry
after v1 FAIL: P115 vault schema needs signal_date/run_date/run_ts/written_by,
not a bare 'date' key).
Emits TWLO SIGNAL_V2 via the P_115 application layer (STEP 2, emission-only,
architecture v1.3). Writes the P_115 vault audit note first, then the
SIGNAL_V2 packet. AVAH/INCY withheld from this batch -- their Eddie Z
breakout entry price sits above the chart's T1/T2 exit levels, which would
fail SignalV2's guideline_target > guideline_entry validator; need a
resistance level above the breakout price before those can emit.
"""
import sys
from datetime import datetime, timezone

sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python")

DONE_PATH = r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_P115_20260910_150000.py.done"


def write_done(status, detail):
    with open(DONE_PATH, "w", encoding="utf-8") as f:
        f.write("status=" + status + "\n")
        f.write("detail=" + str(detail) + "\n")
        f.write("timestamp=" + datetime.now(timezone.utc).isoformat() + "\n")


try:
    from shared_resources.python_utils.vault_interface import write_to_vault
    from application.emit_signal import emit_signal

    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. P_115 vault audit note (Note Standard v1.1) -- gives emit_signal a
    #    real signal_source_link to point to, per established convention.
    vault_data = {
        "signal_date": "2026-09-10",
        "run_date": "2026-09-10",
        "run_ts": now_iso,
        "written_by": "P_115/claude_session",
        "symbol": "TWLO",
        "signal_source": "P_118",
        "step1_verdict": "ASYM",
        "pattern_type": "High Handle",
        "fundamentals_tier": 2,
        "analysis_tier": 3,
        "candle_tier": 2,
        "setup_score": 3,
        "traded": "N",
        "entry_price": 241.11,
        "comments": (
            "High Handle: breakout to $258 high (6mo daily), ~4wk "
            "consolidation, renewed bull signal (2x Bull Signal Rise marks). "
            "Entry = Eddie Z standard breakout point (pending trigger, "
            "current price 230.525 below it). Fund Verified 2->2, no tier "
            "drop. HybridTier 5 (AsymmetricSetup path)."
        ),
    }
    vault_written = write_to_vault("P115", vault_data, overwrite=True)
    print("Vault note written:", vault_written)

    # 2. SIGNAL_V2 emission
    path = emit_signal(
        symbol="TWLO",
        session_date="2026-09-10",
        signal_timestamp="2026-09-10T18:35:00Z",
        strategy="dip_buy",
        guideline_entry=241.11,
        guideline_stop=220.78,
        guideline_target=246.73,
        signal_horizon="10-15 trading days",
        confidence_level="MEDIUM",
        close_at_signal=230.525,
        trailing_volume_30d=728265,
        signal_rationale=(
            "High Handle: breakout to $258 high (6mo daily), ~4wk "
            "consolidation, renewed bull signal. P_115 recheck ASYM "
            "Fund2/Anal3/Candle2/Setup3, HybridTier5 (AsymmetricSetup path: "
            "Anal>=3, Fund>=2). Fund Verified 2->2, no tier drop. RVOL thin "
            "0.46 at signal. Entry = Eddie Z standard breakout point, "
            "pending trigger (current 230.525 below it)."
        ),
        chart_timeframe="1D",
        signal_source_link="P_115_TrackerDashboard_V3.xlsx#2026-09-10_TWLO",
        atm_at_signal=10.8,
        intelliscan_support_1=220.78,
        signal_source="P_115",
    )
    print("Signal written:", path)
    print("PASS")
    write_done("PASS", path)
except Exception as exc:
    print("FAIL:", exc)
    write_done("FAIL", exc)
    sys.exit(1)
