"""run_this_P110_20260914_121500.py -- write P115 vault audit note for SELF.

Closes the --source-link placeholder gap, same pattern as NFLX/ADP/EHC/GCT.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub")

from shared_resources.python_utils.vault_interface import write_to_vault  # noqa: E402

DONE_PATH = Path(__file__).with_suffix(".py.done")
VAULT_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\P115")
SIGNAL_PACKET = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement"
    r"\signals\2026-09-14_SELF_v2.0.json"
)

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

DATA = {
    "signal_date": "2026-09-14",
    "run_date": "2026-09-14",
    "run_ts": NOW,
    "written_by": "Claude/P_115_session",
    "symbol": "SELF",
    "signal_source": "P_110",
    "step1_verdict": "ASYM",
    "pattern_type": None,
    "breakout_verdict": "ASYM",
    "breakout_volume_multiple": None,
    "distribution_day_count": None,
    "follow_through_day": None,
    "market_direction": "OFF",
    "rs_vs_spy": None,
    "fundamentals_tier": 2,
    "analysis_tier": 3,
    "candle_tier": 3,
    "setup_score": 3,
    "liquidity_tier": None,
    "traded": "N",
    "entry_price": 5.15,
    "tp_level": 5.92,
    "sl_level": 5.01,
    "stop_level": 5.01,
    "risk_pct": 0.75,
    "account_balance": 29458.74,
    "outcome": None,
    "recheck_status": None,
    "simulation_notes": "",
    "comments": "RVOL 0.12 (low); PA1(BOSS); Fund Verification clean (ROE ~4-6pct, Debt/Cap ~25-26pct, FCF+); chart T1=T2=5.92 flagged not normalized",
}


def write_done(status: str, exit_code: int, note: str = "") -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = f"{status}\n{exit_code}\n{ts}\n"
    if note:
        body += f"{note}\n"
    DONE_PATH.write_text(body, encoding="utf-8")


def main() -> None:
    before = {f.name: f.stat().st_mtime for f in VAULT_DIR.glob("*") if "SELF" in f.name}

    ok = write_to_vault("P115", DATA)
    if not ok:
        print("FAIL: write_to_vault returned False for SELF")
        write_done("FAIL", 1, "write_to_vault False for SELF")
        sys.exit(1)

    after = {f.name: f.stat().st_mtime for f in VAULT_DIR.glob("*") if "SELF" in f.name}
    new_or_changed = [
        name for name, mtime in after.items()
        if name not in before or before[name] != mtime
    ]
    if not new_or_changed:
        print("FAIL: write_to_vault returned True for SELF but no file changed on disk")
        write_done("FAIL", 1, "no disk change for SELF")
        sys.exit(1)

    note_path = VAULT_DIR / new_or_changed[0]
    size = note_path.stat().st_size
    print(f"SELF: wrote {note_path} ({size} bytes)")

    if not SIGNAL_PACKET.exists():
        print(f"FAIL: expected signal packet missing: {SIGNAL_PACKET}")
        write_done("FAIL", 1, f"missing packet {SIGNAL_PACKET}")
        sys.exit(1)
    packet = json.loads(SIGNAL_PACKET.read_text(encoding="utf-8"))
    rel_link = f"TradeOrderManagement/P115/{note_path.name}"
    packet["signal_metadata"]["signal_source_link"] = rel_link
    SIGNAL_PACKET.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(f"SELF: patched signal_source_link -> {rel_link}")

    if not note_path.exists() or note_path.stat().st_size < 50:
        print("FAIL: post-write verification failed for SELF")
        write_done("FAIL", 1, "post-write check failed SELF")
        sys.exit(1)

    print("PASS")
    write_done("PASS", 0, f"SELF={note_path}")


if __name__ == "__main__":
    main()
