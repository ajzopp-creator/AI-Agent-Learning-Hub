"""run_this_P115_20260914_104500.py -- write P115 vault audit notes for NFLX + ADP.

Task: close the --source-link placeholder gap on both already-emitted SIGNAL_V2
packets by writing the real P_115 audit-trail markdown note via write_to_vault
("P115", ...), then patch each packet's signal_metadata.signal_source_link to
the real relative path.

Verification: list trading_journal\\TradeOrderManagement\\P115\\ before and after each
write and confirm a new/updated file matching the symbol appears -- never trust
write_to_vault's boolean return alone (Content integrity / Durable signal, peh-handoff).

CORRECTED 2026-09-14: first run used TradeManagement\\P115\\ (per the skill file's
Critical Paths table) and got a false FAIL -- the real write landed under
TradeOrderManagement\\P115\\ instead. Skill file corrected separately; this script
uses the verified-correct path.
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
SIGNALS_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\signals")

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

TICKERS = [
    {
        "symbol": "NFLX",
        "signal_packet": SIGNALS_DIR / "2026-09-14_NFLX_v2.0.json",
        "data": {
            "signal_date": "2026-09-14",
            "run_date": "2026-09-14",
            "run_ts": NOW,
            "written_by": "Claude/P_115_session",
            "symbol": "NFLX",
            "signal_source": "P_116",
            "step1_verdict": "BUY",
            "pattern_type": "Bounce",
            "breakout_verdict": "Bounce",
            "breakout_volume_multiple": None,
            "distribution_day_count": None,
            "follow_through_day": None,
            "market_direction": "OFF",
            "rs_vs_spy": None,
            "fundamentals_tier": 3,
            "analysis_tier": 3,
            "candle_tier": 2,
            "setup_score": 3,
            "liquidity_tier": None,
            "traded": "N",
            "entry_price": 79.90,
            "tp_level": 123.77,
            "sl_level": 74.81,
            "stop_level": 74.81,
            "risk_pct": 0.75,
            "account_balance": 29458.74,
            "outcome": None,
            "recheck_status": None,
            "simulation_notes": "",
            "comments": "RVOL 0.31 (low)",
        },
    },
    {
        "symbol": "ADP",
        "signal_packet": SIGNALS_DIR / "2026-09-14_ADP_v2.0.json",
        "data": {
            "signal_date": "2026-09-14",
            "run_date": "2026-09-14",
            "run_ts": NOW,
            "written_by": "Claude/P_115_session",
            "symbol": "ADP",
            "signal_source": "P_116",
            "step1_verdict": "BUY",
            "pattern_type": "Bounce",
            "breakout_verdict": "Bounce",
            "breakout_volume_multiple": None,
            "distribution_day_count": None,
            "follow_through_day": None,
            "market_direction": "OFF",
            "rs_vs_spy": None,
            "fundamentals_tier": 4,
            "analysis_tier": 3,
            "candle_tier": 2,
            "setup_score": 3,
            "liquidity_tier": None,
            "traded": "N",
            "entry_price": 273.76,
            "tp_level": 372.74,
            "sl_level": 264.26,
            "stop_level": 264.26,
            "risk_pct": 0.75,
            "account_balance": 29458.74,
            "outcome": None,
            "recheck_status": None,
            "simulation_notes": "",
            "comments": "RVOL 0.17 (low); T1=T2=372.74 on chart, flagged not normalized",
        },
    },
]


def write_done(status: str, exit_code: int, note: str = "") -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = f"{status}\n{exit_code}\n{ts}\n"
    if note:
        body += f"{note}\n"
    DONE_PATH.write_text(body, encoding="utf-8")


def main() -> None:
    results = []
    for entry in TICKERS:
        symbol = entry["symbol"]
        before = {f.name: f.stat().st_mtime for f in VAULT_DIR.glob("*") if symbol in f.name}

        ok = write_to_vault("P115", entry["data"])
        if not ok:
            print(f"FAIL: write_to_vault returned False for {symbol}")
            write_done("FAIL", 1, f"write_to_vault False for {symbol}")
            sys.exit(1)

        after = {f.name: f.stat().st_mtime for f in VAULT_DIR.glob("*") if symbol in f.name}
        new_or_changed = [
            name for name, mtime in after.items()
            if name not in before or before[name] != mtime
        ]
        if not new_or_changed:
            print(f"FAIL: write_to_vault returned True for {symbol} but no file changed on disk")
            write_done("FAIL", 1, f"no disk change for {symbol}")
            sys.exit(1)

        note_path = VAULT_DIR / new_or_changed[0]
        size = note_path.stat().st_size
        print(f"{symbol}: wrote {note_path} ({size} bytes)")

        packet_path = entry["signal_packet"]
        if not packet_path.exists():
            print(f"FAIL: expected signal packet missing: {packet_path}")
            write_done("FAIL", 1, f"missing packet {packet_path}")
            sys.exit(1)
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        rel_link = f"TradeOrderManagement/P115/{note_path.name}"
        packet["signal_metadata"]["signal_source_link"] = rel_link
        packet_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
        print(f"{symbol}: patched signal_source_link -> {rel_link}")

        results.append((symbol, note_path, size))

    for symbol, note_path, size in results:
        if not note_path.exists() or note_path.stat().st_size < 50:
            print(f"FAIL: post-write verification failed for {symbol}")
            write_done("FAIL", 1, f"post-write check failed {symbol}")
            sys.exit(1)

    print("PASS")
    write_done("PASS", 0, "; ".join(f"{s}={p}" for s, p, _ in results))


if __name__ == "__main__":
    main()
