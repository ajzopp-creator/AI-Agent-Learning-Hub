"""
run_this_P020_20260907_224552.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 12 of 18 --
infrastructure\\paper_order_history_parser.py, the largest single lift
in this build).

Uses a synthetic CSV file built from REAL row data copied verbatim from
data\\tos_exports\\paper\\D_020_2026-07-27_YTD_AccountStatement.csv
(MRCY bracket, SPY IRON CONDOR multi-leg, EMR expired order) -- not
invented fixtures. One MRCY OCO child's status was changed from WORKING
to FILLED (the real file had both still open) so Tier-1 reconciliation
has something to actually resolve; that is the only deviation from the
verbatim source rows. A temp file holds this synthetic CSV; the real
production statement file is never opened by this script.

Also confirms the CORE CLAIM behind this file's whole design -- that
order_linkage.build_order_chain() and order_reconciler.reconcile_order()
run completely UNCHANGED on this parser's output (Tony's explicit
requirement: same logic for paper and live).

Do not change test assertions.
"""
from __future__ import annotations

import py_compile
import sys
import tempfile
import warnings
from datetime import date
from pathlib import Path

DATABASE_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
)
TARGET = DATABASE_DIR / "infrastructure" / "paper_order_history_parser.py"

DONE_MARKER = Path(__file__).with_suffix(".py.done")

# Verbatim rows from the real 2026-07-27 YTD paper statement (see header
# note above) -- only the MRCY WORKING->FILLED status change is not verbatim.
SYNTHETIC_CSV = """Account Statement for D-68748526 (ira) since 1/1/26 through 8/17/26

Account Order History
Notes,,Time Placed,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,PRICE,,TIF,Status,Order ID
,,7/24/26 10:31:28,STOCK,SELL,-10,TO CLOSE,MRCY,,,STOCK,~,MKT,GTC,FILLED,="5374526395"
,,,TRG BY #5374526392,,,,,,,,BASE-6.43,STP,STD,,
,,,OCO #5374526393,,,,,,,,99.83,STP,,,
,,7/24/26 10:31:28,STOCK,SELL,-10,TO CLOSE,MRCY,,,STOCK,BASE+1.00,LMT,GTC,CANCELED,="5374526394"
,,,TRG BY #5374526392,,,,,,,,107.26,LMT,,,
,,,OCO #5374526393,,,,,,,,,,,,
,,7/24/26 10:31:28,STOCK,BUY,+10,TO OPEN,MRCY,,,STOCK,106.26,LMT,DAY,FILLED,="5374526392"
,,7/27/26 15:59:19,IRON CONDOR,BUY,+1,TO CLOSE,SPY,31 JUL 26,745,CALL,3.13,LMT,GTC,FILLED,="5375656086"
,,,,SELL,-1,TO CLOSE,SPY,31 JUL 26,750,CALL,DEBIT,,,,
,,,,BUY,+1,TO CLOSE,SPY,31 JUL 26,735,PUT,,,,,
,,,,SELL,-1,TO CLOSE,SPY,31 JUL 26,730,PUT,,,,,
,,7/24/26 09:48:05,STOCK,BUY,+10,TO OPEN,EMR,,,STOCK,146.38,LMT,DAY,(0) EXPIRED,="5374405691"

Futures Statements
Trade Date,Exec Date,Exec Time,Type,Ref #,Description,Misc Fees,Commissions & Fees,Amount,Balance
"""


def _write_done(status: str, exit_code: int) -> None:
    DONE_MARKER.write_text(
        f"timestamp: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"status: {status}\n"
        f"exit_code: {exit_code}\n"
    )


def _fail(reason: str) -> None:
    print(f"FAIL: {reason}")
    _write_done("FAIL", 1)
    sys.exit(1)


def main() -> None:
    if not TARGET.exists():
        _fail(f"target file not found on disk: {TARGET}")
    line_count = len(TARGET.read_text().splitlines())
    print(f"Line count: {line_count}")
    if not (150 <= line_count <= 260):
        _fail(f"line count {line_count} outside expected [150, 260]")

    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        try:
            py_compile.compile(str(TARGET), doraise=True)
        except (py_compile.PyCompileError, SyntaxWarning, SyntaxError) as exc:
            _fail(f"compile error under warnings-as-errors: {exc}")
    print("Compile check: PASS (warnings-as-errors)")

    sys.path.insert(0, str(DATABASE_DIR))
    import infrastructure.paper_order_history_parser as parser_mod  # noqa: E402
    import domain.order_linkage as linkage_mod  # noqa: E402
    import domain.order_reconciler as recon_mod  # noqa: E402

    tmp_dir = Path(tempfile.mkdtemp(prefix="paper_order_history_test_"))
    csv_path = tmp_dir / "synthetic_statement.csv"
    csv_path.write_text(SYNTHETIC_CSV, encoding="utf-8")

    try:
        roots = parser_mod.parse_order_history(csv_path)

        if len(roots) != 3:
            _fail(f"expected 3 root orders (MRCY entry, SPY condor, EMR), got {len(roots)}: "
                  f"{[r['orderId'] for r in roots]}")

        by_id = {r["orderId"]: r for r in roots}
        if set(by_id) != {5374526392, 5375656086, 5374405691}:
            _fail(f"wrong root order_ids: {sorted(by_id)}")
        print("Root order count/identity check: PASS (3 roots, correct IDs)")

        mrcy_root = by_id[5374526392]
        if mrcy_root["orderStrategyType"] != "TRIGGER":
            _fail(f"MRCY root should be TRIGGER (has children), got {mrcy_root['orderStrategyType']}")
        if len(mrcy_root["childOrderStrategies"]) != 2:
            _fail(f"MRCY root should have 2 children, got {len(mrcy_root['childOrderStrategies'])}")
        child_ids = {c["orderId"] for c in mrcy_root["childOrderStrategies"]}
        if child_ids != {5374526395, 5374526394}:
            _fail(f"MRCY children wrong: {child_ids}")
        print("MRCY bracket reassembly check: PASS (TRIGGER root, 2 children correctly nested)")

        emr_root = by_id[5374405691]
        if emr_root["status"] != "EXPIRED":
            _fail(f"EMR status cleanup wrong: expected 'EXPIRED', got {emr_root['status']!r}")
        print("Status cleanup check: PASS ('(0) EXPIRED' -> 'EXPIRED')")

        spy_root = by_id[5375656086]
        if spy_root["orderStrategyType"] != "SINGLE":
            _fail(f"SPY condor root should collapse to SINGLE (v1 simplification), got {spy_root['orderStrategyType']}")
        if spy_root["orderLegCollection"][0]["quantity"] != 1:
            _fail(f"SPY condor primary leg qty wrong: {spy_root['orderLegCollection'][0]}")
        print("Multi-leg combo collapse check: PASS (IRON CONDOR collapsed to primary leg only)")

        # ---- Core claim: order_linkage/order_reconciler run UNCHANGED ----
        mrcy_chain = linkage_mod.build_order_chain(mrcy_root)
        if mrcy_chain.root.order_id != 5374526392 or len(mrcy_chain.descendants) != 2:
            _fail(f"build_order_chain() didn't walk the paper-sourced dict correctly")

        filled_child = mrcy_chain.find(5374526395)
        if filled_child is None or filled_child.status != "FILLED":
            _fail(f"expected order 5374526395 to be FILLED in the walked chain")

        result = recon_mod.reconcile_order(side="long", entry_chain=mrcy_chain)
        if result is None:
            _fail("reconcile_order() returned None for a fully-resolvable paper bracket")
        if result.matched_tier != 1:
            _fail(f"expected Tier 1 match, got {result.matched_tier}")
        if result.entry_date != date(2026, 7, 24):
            _fail(f"entry_date wrong: {result.entry_date}")
        # MRCY entry price 106.26, exit (order 5374526395) price '~' (MKT) ->
        # None -- P&L correctly comes back None rather than a fabricated
        # number, per this file's documented MKT-order limitation.
        if result.realized_pnl is not None:
            _fail(
                f"expected realized_pnl=None (MKT exit has no recoverable "
                f"price in this section), got {result.realized_pnl}"
            )
        print(
            "order_linkage.py + order_reconciler.py UNCHANGED-code check: PASS "
            "(Tier 1 matched, entry_date correct, MKT-order P&L correctly None not fabricated)"
        )

    finally:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("PASS: paper_order_history_parser.py validated -- same reconciliation code path as live orders.")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
