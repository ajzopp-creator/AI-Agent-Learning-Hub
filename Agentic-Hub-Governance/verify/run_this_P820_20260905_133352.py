"""
PEH verify script -- P820 override record write (EVERPURE)
WO ref: WO-P820-E1.001 (override/exception capture path)
Date: 2026-09-05

Tests that write_to_vault("P820", payload) accepts a full P820Record
payload for a P_400 Gate-1 sizing override and writes a note to
TradeOrderManagement\\P820\\ without raising.

Success: PASS printed to stdout, .done marker written next to this file.
Do not change test assertions.
"""
import sys
from pathlib import Path
from datetime import datetime

HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
sys.path.insert(0, str(HUB_ROOT))

from shared_resources.python_utils.vault_interface import write_to_vault

PAYLOAD = {
    "signal_date": "2026-09-05",
    "run_date": "2026-09-05",
    "run_ts": "2026-09-05T13:33:52",
    "written_by": "P_820/chat_dictation",
    "symbol": "EVERPURE",
    "why_code": "P_116",
    "entry_price": 1.80,
    "target_price": 119.10,
    "notes": (
        "qty=3 (approved=2, FULL mode Gate1 cap $410.34/$1.80=2), "
        "trade_mode=PAPER, override_reason=Gate 1 sizing overshoot "
        "(decay-adj +31.6%/$540 vs $410.34; worst-case +82.8%/$750), "
        "Gates 2/3 clear, R:R 2.0:1 TP $112.10/3.3:1 Primary $119.10 PASS, "
        "risk_mode=FULL (P_010_RiskConfig 2026-09-05T06:48:09), "
        "VXX neutral avg_posture 1.65, manual override by Tony in P_400 "
        "session, deliberate not reactive per Behavioral Judge"
    ),
}


def write_done_marker(status: str, exit_code: int) -> None:
    done_path = Path(__file__).with_name(Path(__file__).name + ".done")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    done_path.write_text(
        f"timestamp: {ts}\nstatus: {status}\nexit_code: {exit_code}\n",
        encoding="utf-8",
    )


def main() -> int:
    try:
        result = write_to_vault("P820", PAYLOAD)
        print("WRITE RESULT:", result)
        print("PASS")
        write_done_marker("PASS", 0)
        return 0
    except Exception as exc:
        print("FAIL:", exc)
        write_done_marker("FAIL", 1)
        return 1


if __name__ == "__main__":
    sys.exit(main())
