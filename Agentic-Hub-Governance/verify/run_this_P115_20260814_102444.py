"""
PEH run_this script -- P_115 STEP 2 signal emission for SBLK, 2026-08-14.
Self-contained. Does not modify production files (cli.py is invoked as a
subprocess, not imported/edited). See sibling _context.txt for full rationale.
"""
import subprocess
import sys
import os
import glob
from datetime import datetime, timezone

PROJECT_PY_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python"
PYTHON_EXE = r"C:\Users\Trader\.conda\envs\p140\python.exe"
SIGNALS_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\signals"
DONE_MARKER = __file__ + ".done"

SESSION_DATE = "2026-08-14"
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

CLI_ARGS = [
    PYTHON_EXE, "cli.py",
    "--symbol", "SBLK",
    "--session-date", SESSION_DATE,
    "--timestamp", TIMESTAMP,
    "--strategy", "dip_buy",
    "--entry", "29.15",
    "--stop", "27.06",
    "--target", "37.17",
    "--horizon", "3-5 days",
    "--confidence", "HIGH",
    "--close", "29.15",
    "--volume", "1303844",
    "--rationale", "ASYM setup, Anal=3 Fund=2 adjusted (verified), STR=0, PA Stop structure, entry zone 29-31 per Tony",
    "--timeframe", "1D",
    "--source-link", "P_115_STEP1_SBLK_2026-08-14",
    "--atm", "0.92",
    "--source", "P_115",
]


def write_done(status, detail):
    with open(DONE_MARKER, "w", encoding="utf-8") as f:
        f.write(f"status={status}\n")
        f.write(f"timestamp={datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"detail={detail}\n")


def main():
    before = set(glob.glob(os.path.join(SIGNALS_DIR, "2026-08-14_SBLK_*.json")))

    try:
        result = subprocess.run(
            CLI_ARGS,
            cwd=PROJECT_PY_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except Exception as exc:
        print("FAIL: subprocess exception:", exc)
        write_done("FAIL", f"subprocess exception: {exc}")
        sys.exit(1)

    stdout = result.stdout or ""
    stderr = result.stderr or ""

    after = set(glob.glob(os.path.join(SIGNALS_DIR, "2026-08-14_SBLK_*.json")))
    new_files = sorted(after - before)

    if result.returncode != 0:
        print("FAIL: cli.py returned non-zero exit code", result.returncode)
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        write_done("FAIL", f"exit={result.returncode} stderr={stderr[:500]}")
        sys.exit(1)

    if not new_files:
        print("FAIL: cli.py exited 0 but no new signal file found in", SIGNALS_DIR)
        print("STDOUT:", stdout)
        write_done("FAIL", "no new signal file found despite exit 0")
        sys.exit(1)

    signal_path = new_files[-1]
    size = os.path.getsize(signal_path)
    if size == 0:
        print("FAIL: signal file written but zero bytes:", signal_path)
        write_done("FAIL", f"zero-byte file: {signal_path}")
        sys.exit(1)

    print("PASS")
    print("Signal written:", signal_path, f"({size} bytes)")
    print("STDOUT:", stdout)
    write_done("PASS", f"signal_path={signal_path} size={size}")


if __name__ == "__main__":
    main()
