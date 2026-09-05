"""
run_this_P118_20260903_145855.py
PEH wrapper: emits P_115 SIGNAL_V2 packet for CXW (P_118-sourced, ASYM verdict,
Fund V111 verified clean, Tony confirmed "Go on CXW" 2026-09-03) via cli.py,
then confirms the output file landed on disk before printing PASS/FAIL.
Invokes cli.py as a subprocess -- does not modify cli.py or emit_signal.py.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

PYTHON = r"C:\Users\Trader\.conda\envs\p140\python.exe"
CLI = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python\cli.py"
SIGNALS_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\signals")
EXPECTED_FILE = SIGNALS_DIR / "2026-09-03_CXW_v2.0.json"

ARGS = [
    PYTHON, CLI,
    "--symbol", "CXW",
    "--session-date", "2026-09-03",
    "--timestamp", "2026-09-03T18:58:55Z",
    "--strategy", "breakout",
    "--entry", "34.60",
    "--stop", "31.59",
    "--target", "38.19",
    "--horizon", "10-15 trading days",
    "--confidence", "MEDIUM",
    "--close", "34.06",
    "--volume", "1612314",
    "--rationale",
    "P_118 Cup and Handle breakout, ASYM via P_115 recheck (Fund2/Anal3/Candle2/Setup3), "
    "Fund V111 verified clean (ROE 9.01% fail, Debt/Cap ~50% pass, FCF +26.1M pass), "
    "200-MA 48.3% NORMAL, no earnings within 3 sessions, breakout volume 3.49x 20d avg",
    "--timeframe", "1D",
    "--source-link", "P_118 STEP 1 batch 2026-09-03, TOS P_115_BuyTheDipChart_V16 recheck screenshot",
    "--atm", "1.38",
    "--source", "P_115",
]


def main() -> None:
    before = EXPECTED_FILE.exists()
    result = subprocess.run(ARGS, capture_output=True, text=True, timeout=170)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    after = EXPECTED_FILE.exists()

    done_path = Path(str(Path(__file__).with_suffix("")) + ".done")

    if result.returncode == 0 and after:
        status = "PASS"
        exit_code = 0
        print(f"PASS: signal file confirmed at {EXPECTED_FILE}")
    else:
        status = "FAIL"
        exit_code = 1
        print(f"FAIL: returncode={result.returncode} file_existed_before={before} file_exists_after={after}")

    with open(done_path, "w", encoding="utf-8") as f:
        f.write(f"status={status}\n")
        f.write(f"exit_code={exit_code}\n")
        f.write(f"timestamp={datetime.now(timezone.utc).isoformat()}\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
