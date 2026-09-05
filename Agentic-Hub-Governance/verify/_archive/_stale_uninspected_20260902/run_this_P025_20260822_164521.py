"""
PEH run_this — P_025 Full package deploy + verify
Timestamp: 20260822_164521

Intended use:
  1. Unzip run_this_P025_20260822_164521.zip
  2. Run this script with p140
  3. It copies python\\ into the Hub project (if needed), then verifies imports
     and that Cost_Basis / key modules exist.

Does not run a full yfinance rebuild (network-heavy). Use cli.py build separately.
Prints PASS when package is in place and importable.
"""

from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
PROJECT_ROOT = HUB_ROOT / "projects" / "P_025_AJZ_Institutional_Portfolio_Tracker"
TARGET_PYTHON = PROJECT_ROOT / "python"

# Folder containing this script after unzip (same dir as python\ payload)
HERE = Path(__file__).resolve().parent
SOURCE_PYTHON = HERE / "python"

REQUIRED = [
    "config.py",
    "schemas.py",
    "cli.py",
    "domain/trade_processor.py",
    "infrastructure/excel_writer.py",
    "infrastructure/analytics_sheets.py",
    "application/build_portfolio.py",
    "application/format_analytics.py",
]


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


def main() -> int:
    print("=" * 60)
    print("P_025 Package Deploy + Verify — 20260822_164521")
    print("=" * 60)
    print(f"Script dir : {HERE}")
    print(f"Target     : {TARGET_PYTHON}")

    if not PROJECT_ROOT.exists():
        fail(f"Project root missing: {PROJECT_ROOT}")

    # Deploy from zip payload if present
    if SOURCE_PYTHON.exists() and (SOURCE_PYTHON / "config.py").exists():
        print("\n=== Deploying python\\ from zip payload ===")
        TARGET_PYTHON.mkdir(parents=True, exist_ok=True)
        # Copy tree; do not delete TARGET so local config tweaks can be re-applied
        for item in SOURCE_PYTHON.iterdir():
            dest = TARGET_PYTHON / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
        print("  OK  python\\ synchronized from package")
    else:
        print("\n=== No python\\ payload beside script — verifying existing install ===")

    if not TARGET_PYTHON.exists():
        fail(f"python\\ missing at {TARGET_PYTHON}")

    print("\n=== Required files ===")
    for rel in REQUIRED:
        p = TARGET_PYTHON / rel
        if not p.exists():
            fail(f"Missing {rel}")
        print(f"  OK  {rel}")

    if str(TARGET_PYTHON) not in sys.path:
        sys.path.insert(0, str(TARGET_PYTHON))

    print("\n=== Import smoke test ===")
    try:
        import config  # noqa: F401
        from domain.trade_processor import build_cost_basis_rows  # noqa: F401
        from application.build_portfolio import run_full_build  # noqa: F401
        from application.format_analytics import run_format_analytics  # noqa: F401
        print("  OK  config, trade_processor, build_portfolio, format_analytics")
    except Exception as exc:
        fail(f"Import failed: {type(exc).__name__}: {exc}")

    print("\n=== Config sanity ===")
    import config as cfg
    print(f"  P020_DB_PATH     = {cfg.P020_DB_PATH}")
    print(f"  IRA_FEED_READY   = {cfg.IRA_FEED_READY}")
    print(f"  WORKBOOK_PATH    = {cfg.WORKBOOK_PATH}")
    if not hasattr(cfg, "SHEET_COST_BASIS"):
        fail("config missing SHEET_COST_BASIS")
    print("  OK  SHEET_COST_BASIS present")

    print("\n" + "=" * 60)
    print("PASS")
    print("=" * 60)
    print("Next: run full build when ready:")
    print(f"  {sys.executable} {TARGET_PYTHON / 'cli.py'} build")
    write_done("PASS", 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
