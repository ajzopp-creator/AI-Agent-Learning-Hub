"""run_this_P800_20260908_182141.py -- PEH verification for WO-P800-E6.001
(P_805 Consensus Dashboard). Read-only: does NOT write to Dashboard.md.

Validates:
1. Every p805_consensus module compiles under -W error::SyntaxWarning.
2. The real MTD/YTD read + join pipeline runs against live P_805
   ranked.csv files and the live Tracker Log workbook, and produces a
   row per email source with plausible counts.

Does not modify any production file. Writing Dashboard.md is a separate,
explicit next step after Tony reviews these numbers.
"""

import subprocess
import sys
import datetime as _dt
from datetime import date
from pathlib import Path

PROJECT_PYTHON_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\python"
)
sys.path.insert(0, str(PROJECT_PYTHON_DIR))

DONE_MARKER = Path(__file__).with_suffix(".py.done")

MODULES_TO_COMPILE = [
    r"p805_consensus\__init__.py",
    r"p805_consensus\config.py",
    r"p805_consensus\schemas.py",
    r"p805_consensus\domain\__init__.py",
    r"p805_consensus\domain\consensus_join.py",
    r"p805_consensus\infrastructure\__init__.py",
    r"p805_consensus\infrastructure\ranked_csv_reader.py",
    r"p805_consensus\infrastructure\tracker_reader.py",
    r"p805_consensus\infrastructure\dashboard_section_writer.py",
    r"p805_consensus\application\__init__.py",
    r"p805_consensus\application\consensus_dashboard_runner.py",
    r"p805_consensus\cli.py",
]


def write_done(status: str, exit_code: int) -> None:
    """Write the .done completion marker next to this script."""
    DONE_MARKER.write_text(
        f"status={status}\n"
        f"exit_code={exit_code}\n"
        f"timestamp={_dt.datetime.now().isoformat()}\n",
        encoding="utf-8",
    )


def check_compile() -> list[str]:
    """Compile every module under -W error::SyntaxWarning. Returns errors."""
    errors: list[str] = []
    for rel in MODULES_TO_COMPILE:
        full = PROJECT_PYTHON_DIR / rel
        code = f"compile(open(r'{full}', 'rb').read(), r'{full}', 'exec')"
        result = subprocess.run(
            [sys.executable, "-W", "error::SyntaxWarning", "-c", code],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            errors.append(f"{rel}: {result.stderr.strip()}")
    return errors


def check_pipeline() -> tuple[bool, str]:
    """Run the real read+join pipeline read-only, no vault write."""
    try:
        from p805_consensus.domain.consensus_join import (
            aggregate_by_source,
            candidates_in_window,
            month_to_date_start,
            year_to_date_start,
        )
        from p805_consensus.infrastructure.ranked_csv_reader import read_candidates
        from p805_consensus.infrastructure.tracker_reader import read_tracker_rows
    except Exception as exc:  # noqa: BLE001
        return False, f"Import failed: {exc}"

    as_of = date.today()
    mtd_start = month_to_date_start(as_of)
    ytd_start = year_to_date_start(as_of)

    try:
        all_candidates = read_candidates(ytd_start, as_of)
    except Exception as exc:  # noqa: BLE001
        return False, f"read_candidates failed: {exc}"

    today_candidates = candidates_in_window(all_candidates, as_of, as_of)
    mtd_candidates = candidates_in_window(all_candidates, mtd_start, as_of)

    try:
        tracker_rows = read_tracker_rows()
    except Exception as exc:  # noqa: BLE001
        return False, f"read_tracker_rows failed: {exc}"

    rows = aggregate_by_source(
        today_candidates, mtd_candidates, all_candidates, tracker_rows
    )

    print(
        f"Candidates YTD: {len(all_candidates)}  MTD: {len(mtd_candidates)}  "
        f"Today: {len(today_candidates)}"
    )
    print(f"Tracker rows loaded: {len(tracker_rows)}")
    print()
    print(
        "| Email Source | Today | MTD Cand | YTD Cand | MTD BUY/ASYM | "
        "YTD BUY/ASYM |"
    )
    for r in sorted(rows, key=lambda row: row.email_source):
        print(
            f"| {r.email_source} | {len(r.today_symbols)} | {r.mtd_candidates} "
            f"| {r.ytd_candidates} | {r.mtd_buy_asym} | {r.ytd_buy_asym} |"
        )

    return True, f"{len(rows)} source rows computed, 0 vault writes"


def main() -> int:
    compile_errors = check_compile()
    if compile_errors:
        for e in compile_errors:
            print("COMPILE ERROR:", e)
        write_done("FAIL", 1)
        print("FAIL: compile errors above")
        return 1

    ok, detail = check_pipeline()
    print(detail)
    if not ok:
        write_done("FAIL", 1)
        print("FAIL:", detail)
        return 1

    write_done("PASS", 0)
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())