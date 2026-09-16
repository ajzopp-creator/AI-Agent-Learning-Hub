"""run_this_P115_20260914_103440.py -- emit ADP P_116 signal via P_115 cli.py.

Task: emit SIGNAL_V2 packet for ADP (P_115 STEPS 1-2, SignalSource=P_116) to P_400.
Verification fixed per 2026-09-14 lesson: checks the expected output path directly
(trading_journal\\TradeOrderManagement\\signals\\YYYY-MM-DD_SYMBOL_v2.0.json, same
convention emit_signal uses) via Test-Path-equivalent os.path.exists, not by parsing
cli.py's stdout text.
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DONE_PATH = Path(__file__).with_suffix(".py.done")
SIGNALS_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\signals"
)
EXPECTED_FILE = SIGNALS_DIR / "2026-09-14_ADP_v2.0.json"


def write_done(status: str, exit_code: int, note: str = "") -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = f"{status}\n{exit_code}\n{ts}\n"
    if note:
        body += f"{note}\n"
    DONE_PATH.write_text(body, encoding="utf-8")


def main() -> None:
    cli = Path(
        r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem"
        r"\python\cli.py"
    )
    python_exe = r"C:\Users\Trader\.conda\envs\p140\python.exe"

    args = [
        python_exe, str(cli),
        "--symbol", "ADP",
        "--session-date", "2026-09-14",
        "--timestamp", "2026-09-14T10:34:40Z",
        "--strategy", "bounce_income",
        "--entry", "273.76",
        "--stop", "264.26",
        "--target", "372.74",
        "--horizon", "10-15 trading days",
        "--confidence", "HIGH",
        "--close", "272.895",
        "--volume", "49008",
        "--rationale",
        "P_115 dip engine BUY, HybridTier 7 (Fund 4 NORMAL no penalty, Anal 3, "
        "Candle 2, Setup 3, STR 0); PA Stop structure 264.26; T2 372.74 (chart "
        "shows T1 also 372.74, same value both exits, flagged not normalized); "
        "SignalSource=P_116 bounce/premium",
        "--timeframe", "1D",
        "--source-link", "TradeManagement/P115/2026-09-14_ADP.md",
        "--atm", "6.01",
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
        write_done("FAIL", 1, f"subprocess error: {exc}")
        sys.exit(1)

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    if result.returncode != 0:
        print("FAIL:", f"cli.py exited {result.returncode}")
        write_done("FAIL", result.returncode, "non-zero exit")
        sys.exit(1)

    if not EXPECTED_FILE.exists():
        print("FAIL:", f"expected output not found: {EXPECTED_FILE}")
        write_done("FAIL", 1, f"missing {EXPECTED_FILE}")
        sys.exit(1)

    size = EXPECTED_FILE.stat().st_size
    if size < 100:
        print("FAIL:", f"{EXPECTED_FILE} exists but suspiciously small ({size} bytes)")
        write_done("FAIL", 1, f"{EXPECTED_FILE} only {size} bytes")
        sys.exit(1)

    print(f"PASS -- {EXPECTED_FILE} ({size} bytes)")
    write_done("PASS", 0, f"{EXPECTED_FILE} {size} bytes")


if __name__ == "__main__":
    main()
