"""run_this_P110_20260914_121257.py -- emit SELF (ASYM) via P_115 cli.py.

Task: emit SIGNAL_V2 packet for SELF. SignalSource=P_110 (TradeTheBounce project,
per Tony's clarification -- distinct from P_116/OIL subscription service). Fund
Verification ran under the general rule (no documented exclusion exists for P_110,
unlike P_116) and came back clean; BBNX and NRXS from the same batch are held per
Tony's explicit instruction, not touched by this script.

Verification: check the known output path directly, per the 2026-09-14 lesson --
never parse cli.py's stdout for a bare path.
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DONE_PATH = Path(__file__).with_suffix(".py.done")
EXPECTED = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement"
    r"\signals\2026-09-14_SELF_v2.0.json"
)


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
        "--symbol", "SELF",
        "--session-date", "2026-09-14",
        "--timestamp", "2026-09-14T12:12:57Z",
        "--strategy", "bounce",
        "--entry", "5.15",
        "--stop", "5.01",
        "--target", "5.92",
        "--horizon", "10-15 trading days",
        "--confidence", "MEDIUM",
        "--close", "5.15",
        "--volume", "3441",
        "--rationale",
        "P_110 TradeTheBounce batch (SOURCE:P_110 explicit header, distinct from "
        "P_116/OIL); chart Verdict is ASYM Setup: Review, HybridTier 5 (Fund 2 "
        "NORMAL, Anal 3) does not clear BUY>=6 but meets AsymmetricSetup "
        "(Anal>=3, Fund>=2); Fund Verification ran under general rule (no P_110 "
        "exclusion documented, unlike P_116) -- clean: ROE ~4-6pct (below 15pct "
        "threshold but not a wipeout), Debt/Cap ~25-26pct, FCF positive "
        "(~$4-4.7M) -- consistent with submitted Fund=2, no hold triggered "
        "(unlike BBNX/NRXS from the same batch, held separately per Tony); "
        "PA1(BOSS) code present; chart shows T1=T2=5.92, flagged not normalized; "
        "PA Stop structure 5.01; T2 5.92",
        "--timeframe", "1D",
        "--source-link", "TradeManagement/P115/2026-09-14_SELF.md",
        "--atm", "0.16",
        "--source", "P_115",
    ]

    try:
        result = subprocess.run(
            args, cwd=str(cli.parent), capture_output=True, text=True, timeout=180
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

    if not EXPECTED.exists():
        print("FAIL:", f"expected output not found: {EXPECTED}")
        write_done("FAIL", 1, f"missing {EXPECTED}")
        sys.exit(1)

    size = EXPECTED.stat().st_size
    if size < 100:
        print("FAIL:", f"{EXPECTED} exists but suspiciously small ({size} bytes)")
        write_done("FAIL", 1, f"{EXPECTED} only {size} bytes")
        sys.exit(1)

    print(f"PASS -- {EXPECTED} ({size} bytes)")
    write_done("PASS", 0, f"{EXPECTED} {size} bytes")


if __name__ == "__main__":
    main()
