"""run_this_P400_20260915_120605.py -- WO-P400-E8.002 full-suite regression.

Runs the ENTIRE P_400 tests/ folder (not just the files this WO touched)
to confirm no other consumer of earnings_lookup.build_entries_for_symbols()
or batch_2b_scoring._process_symbol() broke. Same discipline this Hub's
other WOs report at close ("full suite clean, N passed").

Self-contained, read-only against production files. Writes its own
<script>.py.done marker before exit.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python")
DONE_PATH = Path(__file__).with_suffix(".py.done")


def _write_done(status: str, exit_code: int) -> None:
    content = (
        f"timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"status: {status}\n"
        f"exit_code: {exit_code}\n"
    )
    DONE_PATH.write_text(content, encoding="utf-8")


def main() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    print(result.stdout[-6000:])
    if result.stderr:
        print("--- stderr (tail) ---")
        print(result.stderr[-2000:])

    if result.returncode == 0:
        print("PASS")
        _write_done("PASS", 0)
        return 0
    else:
        print(f"FAIL: pytest exited {result.returncode}")
        _write_done("FAIL", result.returncode)
        return 1


if __name__ == "__main__":
    sys.exit(main())
