"""run_this_P115_20260914_102558.py -- verify NFLX P_116 signal emission via P_115 cli.py.

Task: emit SIGNAL_V2 packet for NFLX (P_115 STEPS 1-2, SignalSource=P_116) to P_400.
Tests: cli.py --symbol NFLX ... runs cleanly, exits 0, and the printed file path
actually exists on disk (not just a clean process return -- Durable signal, peh-handoff).
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DONE_PATH = Path(__file__).with_suffix(".py.done")


def write_done(status: str, exit_code: int) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    DONE_PATH.write_text(f"{status}\n{exit_code}\n{ts}\n", encoding="utf-8")


def main() -> None:
    cli = Path(
        r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem"
        r"\python\cli.py"
    )
    python_exe = r"C:\Users\Trader\.conda\envs\p140\python.exe"

    args = [
        python_exe, str(cli),
        "--symbol", "NFLX",
        "--session-date", "2026-09-14",
        "--timestamp", "2026-09-14T10:25:58Z",
        "--strategy", "bounce_income",
        "--entry", "79.90",
        "--stop", "74.81",
        "--target", "123.77",
        "--horizon", "10-15 trading days",
        "--confidence", "MEDIUM",
        "--close", "79.90",
        "--volume", "2358641",
        "--rationale",
        "P_115 dip engine BUY, HybridTier 6 (Fund 3 adj PULLBACK -7.2pct, Anal 3, "
        "Candle 2, Setup 3, STR 0); PA Stop structure 74.81; T2 123.77; "
        "SignalSource=P_116 bounce/premium",
        "--timeframe", "1D",
        "--source-link", "TradeManagement/P115/2026-09-14_NFLX.md",
        "--atm", "2.22",
        "--source", "P_115",
    ]

    try:
        result = subprocess.run(
            args,
            cwd=str(cli.parent),
            capture_output=True,
            text=True,
            timeout=180,
        )
    except Exception as exc:  # noqa: BLE001
        print("FAIL:", f"subprocess error: {exc}")
        write_done("FAIL", 1)
        sys.exit(1)

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    if result.returncode != 0:
        print("FAIL:", f"cli.py exited {result.returncode}")
        write_done("FAIL", result.returncode)
        sys.exit(1)

    written_path = None
    for line in result.stdout.splitlines():
        candidate = line.strip()
        if candidate.lower().endswith(".json") and os.path.exists(candidate):
            written_path = candidate
            break

    if written_path is None:
        print("FAIL:", "no verifiable .json path found in cli.py stdout")
        write_done("FAIL", 1)
        sys.exit(1)

    print("PASS")
    write_done("PASS", 0)


if __name__ == "__main__":
    main()
