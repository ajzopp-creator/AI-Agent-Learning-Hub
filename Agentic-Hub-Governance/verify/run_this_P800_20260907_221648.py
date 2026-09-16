"""
run_this_P800_20260907_221648.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 11 of 18,
part 1 of 3: infrastructure\\vault_note_scanner.py).

Uses a TEMPORARY directory with synthetic note files -- obsidian_writers.
config.VAULT_FOLDER_MAP/VAULT_ROOT are monkeypatched to point there
before anything runs. The real trading_journal\\ vault is never opened,
read, or written by this script.

Do not change test assertions.
"""
from __future__ import annotations

import py_compile
import shutil
import sys
import tempfile
import warnings
from datetime import datetime
from pathlib import Path

HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
TARGET = (
    HUB_ROOT / "projects" / "P_800_Automation_Note_Taking" / "python"
    / "p400_regenerate" / "infrastructure" / "vault_note_scanner.py"
)

DONE_MARKER = Path(__file__).with_suffix(".py.done")


def _write_done(status: str, exit_code: int) -> None:
    DONE_MARKER.write_text(
        f"timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"status: {status}\n"
        f"exit_code: {exit_code}\n"
    )


def _fail(reason: str, tmp_root: Path | None = None) -> None:
    print(f"FAIL: {reason}")
    if tmp_root is not None:
        shutil.rmtree(tmp_root, ignore_errors=True)
    _write_done("FAIL", 1)
    sys.exit(1)


NOTE_TEMPLATE = """---
signal_date: {signal_date}
run_date: {run_date}
run_ts: {run_ts}
written_by: P_400/cli_evaluate
ticker: {ticker}
council_verdict: APPROVED
lifecycle_status: SUBMITTED
order_id: {order_id}
entry_price: {entry_price}
---
Note body text, not part of frontmatter.
"""


def main() -> None:
    if not TARGET.exists():
        _fail(f"target file not found on disk: {TARGET}")
    line_count = len(TARGET.read_text().splitlines())
    print(f"Line count: {line_count}")
    if not (50 <= line_count <= 110):
        _fail(f"line count {line_count} outside expected [50, 110]")

    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        try:
            py_compile.compile(str(TARGET), doraise=True)
        except (py_compile.PyCompileError, SyntaxWarning, SyntaxError) as exc:
            _fail(f"compile error under warnings-as-errors: {exc}")
    print("Compile check: PASS (warnings-as-errors)")

    sys.path.insert(
        0,
        str(HUB_ROOT / "projects" / "P_800_Automation_Note_Taking" / "python"),
    )
    import p400_regenerate.infrastructure.vault_note_scanner as scanner_mod  # noqa: E402
    import obsidian_writers.config as ow_config  # noqa: E402

    # Build a fully synthetic vault under a temp dir -- never touches the
    # real trading_journal\ vault.
    tmp_root = Path(tempfile.mkdtemp(prefix="p400_regen_test_"))
    p400_dir = tmp_root / "TradeOrderManagement" / "P400"
    p400_paper_dir = tmp_root / "TradeOrderManagement" / "P400" / "paper"
    p400_dir.mkdir(parents=True)
    p400_paper_dir.mkdir(parents=True)

    # Note 1: in P400/, order_id=7001 -- the target.
    (p400_dir / "2026-09-01_AAPL.md").write_text(
        NOTE_TEMPLATE.format(
            signal_date="2026-09-01", run_date="2026-09-01",
            run_ts="2026-09-01T09:30:00", ticker="AAPL",
            order_id="7001", entry_price="150.00",
        )
    )
    # Note 2: in P400/, different order_id -- decoy.
    (p400_dir / "2026-09-02_MSFT.md").write_text(
        NOTE_TEMPLATE.format(
            signal_date="2026-09-02", run_date="2026-09-02",
            run_ts="2026-09-02T09:30:00", ticker="MSFT",
            order_id="7002", entry_price="300.00",
        )
    )
    # Note 3: malformed (no frontmatter at all) -- must not crash the scan.
    (p400_dir / "2026-09-03_BROKEN.md").write_text("not a real note, no frontmatter")
    # Note 4: in P400_PAPER/, order_id=8001 -- confirms BOTH folders searched.
    (p400_paper_dir / "2026-09-04_TSLA.md").write_text(
        NOTE_TEMPLATE.format(
            signal_date="2026-09-04", run_date="2026-09-04",
            run_ts="2026-09-04T10:00:00", ticker="TSLA",
            order_id="8001", entry_price="250.00",
        )
    )

    ow_config.VAULT_ROOT = tmp_root
    ow_config.VAULT_FOLDER_MAP = {
        "P400": "TradeOrderManagement/P400",
        "P400_PAPER": "TradeOrderManagement/P400/paper",
    }

    try:
        # Test 1: find the P400 note by order_id.
        result = scanner_mod.find_note_by_order_id("7001")
        if result is None:
            _fail("expected to find order_id=7001, got None", tmp_root)
        if result.get("ticker") != "AAPL" or result.get("signal_date") != "2026-09-01":
            _fail(f"wrong note matched for order_id=7001: {result}", tmp_root)
        if result.get("_schema") != "P400":
            _fail(f"_schema should be 'P400', got {result.get('_schema')!r}", tmp_root)
        if not result.get("_note_path", "").endswith("2026-09-01_AAPL.md"):
            _fail(f"_note_path wrong: {result.get('_note_path')!r}", tmp_root)
        print("Find-by-order_id (P400) check: PASS")

        # Test 2: find the P400_PAPER note -- confirms both folders searched.
        result2 = scanner_mod.find_note_by_order_id("8001")
        if result2 is None or result2.get("ticker") != "TSLA":
            _fail(f"expected to find order_id=8001 (paper), got {result2}", tmp_root)
        if result2.get("_schema") != "P400_PAPER":
            _fail(f"_schema should be 'P400_PAPER', got {result2.get('_schema')!r}", tmp_root)
        print("Find-by-order_id (P400_PAPER) check: PASS (both folders searched)")

        # Test 3: no match -- returns None, doesn't raise.
        result3 = scanner_mod.find_note_by_order_id("9999999")
        if result3 is not None:
            _fail(f"expected None for a non-existent order_id, got {result3}", tmp_root)
        print("No-match check: PASS (returns None)")

        # Test 4: malformed note (2026-09-03_BROKEN.md) didn't crash the scan --
        # already proven by tests 1-3 succeeding despite it being present in
        # the same folder.
        print("Malformed-note-tolerance check: PASS (scan completed despite BROKEN.md present)")

    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("PASS: vault_note_scanner.py validated against a synthetic vault (real vault untouched).")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
