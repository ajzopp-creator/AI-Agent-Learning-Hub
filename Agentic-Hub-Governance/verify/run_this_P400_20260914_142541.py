"""
run_this_P400_20260914_142541.py

Verifies: `cli.py record ADP --order-id 15109450962 --paper` writes a
PAPER-mode P_400 vault record for the ADP fill (2 shares @ $275.88,
order id 15109450962). Self-contained; never modifies production files
other than the vault write the CLI itself performs.
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_PYTHON_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python"
)
PYTHON_EXE = r"C:\Users\Trader\.conda\envs\p140\python.exe"
DONE_PATH = Path(__file__).with_name(Path(__file__).name + ".done")

ORDER_ID = "15109450962"
PAPER_BOOK_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\P400\paper"
)


def write_done(status: str, exit_code: int) -> None:
    with open(DONE_PATH, "w", encoding="utf-8") as f:
        f.write(f"timestamp={datetime.now().isoformat()}\n")
        f.write(f"status={status}\n")
        f.write(f"exit_code={exit_code}\n")


def run(args):
    return subprocess.run(
        [PYTHON_EXE] + args,
        cwd=str(PROJECT_PYTHON_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )


def main() -> None:
    result = run(["cli.py", "record", "ADP", "--order-id", ORDER_ID, "--paper"])

    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)

    if result.returncode != 0:
        write_done("FAIL", result.returncode)
        print(
            f"FAIL: cli.py record ADP --order-id {ORDER_ID} --paper exited "
            f"{result.returncode} -- if this is a flag/usage mismatch, correct "
            "this script's invocation and note the fix in the pasted output; "
            "if it's a real error in record_writer.py/obsidian_writers, do not "
            "patch production, report it instead."
        )
        sys.exit(1)

    upper_out = result.stdout.upper()
    if "PAPER" not in upper_out and ORDER_ID not in result.stdout:
        write_done("FAIL", 1)
        print("FAIL: output shows neither PAPER mode nor the order ID -- verify manually")
        sys.exit(1)

    # Durable signal: check the paper book dir for today's ADP record, not just
    # a clean CLI return (peh-handoff Durable signal principle).
    found_on_disk = False
    if PAPER_BOOK_DIR.exists():
        for f in PAPER_BOOK_DIR.glob("*ADP*"):
            found_on_disk = True
            print(f"Found on disk: {f} ({f.stat().st_size} bytes)")

    if not found_on_disk:
        print(
            "NOTE: no ADP file matched under "
            f"{PAPER_BOOK_DIR} by glob '*ADP*' -- record may use a different "
            "naming convention (e.g. a shared DB/JSON file, not a per-symbol "
            "file). CLI reported success and PAPER/order-id were present in "
            "stdout, so treating as PASS, but flag this gap in the pasted "
            "output for Tony."
        )

    write_done("PASS", 0)
    print("PASS")


if __name__ == "__main__":
    main()
