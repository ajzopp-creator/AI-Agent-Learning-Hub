"""
P_025 PEH — Deploy check for IRA=True + analysis modes (full/yearly/ytd)
Does NOT rmtree live python. After you extract the zip onto the project,
run this PEH from verify/ with HUB_ROOT set.

Timestamp: 20260822_145900
"""
from __future__ import annotations

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

HUB = Path(os.environ.get("HUB_ROOT", r"C:\Users\Trader\AI-Agent-Learning-Hub"))
os.environ["HUB_ROOT"] = str(HUB)

PROJ = HUB / "projects" / "P_025_AJZ_Institutional_Portfolio_Tracker"
PYDIR = PROJ / "python"
PYTHON = Path(r"C:\Users\Trader\.conda\envs\p140\python.exe")


def write_done(status: str, exit_code: int) -> None:
    done_path = Path(__file__).with_suffix(Path(__file__).suffix + ".done")
    done_path.write_text(
        f"status={status}\nexit_code={exit_code}\ntimestamp={datetime.now().isoformat()}\n",
        encoding="utf-8",
    )


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    write_done("FAIL", 1)
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def main() -> int:
    print("=" * 60)
    print("P_025 PEH 20260822_145900 — mode + IRA deploy check")
    print("=" * 60)
    print(f"HUB_ROOT = {HUB}")
    print(f"PYDIR    = {PYDIR}")

    if not HUB.exists():
        fail(f"Hub root missing: {HUB}")
    if not PYDIR.exists():
        fail(f"python folder missing: {PYDIR} — extract zip onto project first")
    if not PYTHON.exists():
        fail(f"p140 python missing: {PYTHON}")

    env = os.environ.copy()
    env["HUB_ROOT"] = str(HUB)
    env["PYTHONPATH"] = str(PYDIR)
    pydir_s = str(PYDIR)

    code = (
        "import sys\n"
        f"sys.path.insert(0, r'{pydir_s}')\n"
        "from config import IRA_FEED_READY, ANALYSIS_MODE, LOOKBACK_DAYS_YEARLY, resolve_start_date\n"
        "from datetime import date\n"
        "assert IRA_FEED_READY is True, f'IRA_FEED_READY={IRA_FEED_READY}'\n"
        "assert LOOKBACK_DAYS_YEARLY == 365\n"
        "d = date(2026, 8, 22)\n"
        "assert resolve_start_date(d, 'yearly') == date(2025, 8, 22)\n"
        "assert resolve_start_date(d, 'ytd') == date(2026, 1, 1)\n"
        "assert resolve_start_date(d, 'full') == date(2023, 8, 23)\n"
        "print('config OK: IRA=True, modes resolve')\n"
        "from application.build_portfolio import run_full_build\n"
        "import inspect\n"
        "sig = inspect.signature(run_full_build)\n"
        "assert 'mode' in sig.parameters, 'run_full_build missing mode param'\n"
        "print('build_portfolio OK: mode param present')\n"
    )

    r = subprocess.run(
        [str(PYTHON), "-c", code],
        cwd=pydir_s,
        env=env,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        fail("Import/config smoke failed — extract package python\\ onto project python\\ first")

    r2 = subprocess.run(
        [str(PYTHON), "cli.py", "build", "--help"],
        cwd=pydir_s,
        env=env,
        capture_output=True,
        text=True,
    )
    help_text = r2.stdout + r2.stderr
    if r2.returncode != 0 or "--mode" not in help_text:
        print(help_text)
        fail("cli.py does not expose --mode")
    ok("cli.py exposes --mode")

    ok("IRA_FEED_READY=True")
    ok("resolve_start_date full/yearly/ytd")
    print("=" * 60)
    print("PEH PASS — launcher.bat build --mode yearly should work")
    print("=" * 60)
    write_done("PASS", 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
