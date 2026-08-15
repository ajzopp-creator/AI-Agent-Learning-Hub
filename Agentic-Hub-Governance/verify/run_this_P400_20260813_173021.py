"""run_this_P400_20260813_173021.py -- PEH verify for WO-P400-E5.004.

Confirms test_e4005_e4006_market_open_wall_clock_and_holiday_aware, found
already present in tests\\test_p400_known_bugs.py, passes under plain
pytest, then reports the full P_400 python\\ suite pass/fail for the WO's
acceptance criterion. Self-contained, modifies no production files.

Do not change test assertions.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python"
)
SCRIPT_PATH = Path(__file__).resolve()
DONE_PATH = SCRIPT_PATH.with_suffix(SCRIPT_PATH.suffix + ".done")


def write_done(status: str, exit_code: int) -> None:
    DONE_PATH.write_text(
        f"status={status}\nexit_code={exit_code}\ntimestamp={datetime.now().isoformat()}\n",
        encoding="utf-8",
    )


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "pytest"] + args,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )


def main() -> int:
    target = (
        "tests/test_p400_known_bugs.py::"
        "test_e4005_e4006_market_open_wall_clock_and_holiday_aware"
    )

    targeted = run([target, "-v"])
    print("=== TARGETED TEST ===")
    print(targeted.stdout[-4000:])
    print(targeted.stderr[-1500:])
    if targeted.returncode != 0:
        print("FAIL: targeted test did not pass")
        write_done("FAIL", targeted.returncode)
        return 1

    collected = run(["--collect-only", "-q"])
    print("=== FULL SUITE COLLECTED (tail) ===")
    print(collected.stdout[-1500:])

    full = run(["-q"])
    print("=== FULL SUITE RUN (tail) ===")
    print(full.stdout[-3000:])
    print(full.stderr[-1000:])
    if full.returncode != 0:
        print("FAIL: full suite has failures")
        write_done("FAIL", full.returncode)
        return 1

    print("PASS")
    write_done("PASS", 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
