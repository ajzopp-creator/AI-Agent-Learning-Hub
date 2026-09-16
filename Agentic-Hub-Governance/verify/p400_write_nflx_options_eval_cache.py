"""p400_write_nflx_options_eval_cache.py -- manual eval_cache write for
NFLX's options-route record, per the plan confirmed in chat 2026-09-15.

Not an automated evaluate/spec run (the source packet was archived before
the options route could be evaluated -- recovered from
2609_ProcessedJson.zip for signal_source/signal_date only). Liquidity
independently verified via chain_NFLX.json (OI=589 >= 150, spread=1.59%
<= 10%). Stop/target premiums are delta-approximated from Tony's stock-
level SL:76.12 / TP:98.84 (delta=0.449 at fetch) -- not council-computed
sizing. Verdict is APPROVED_WITH_CAUTION specifically to flag that.
"""

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python")
sys.path.insert(0, str(PROJECT_ROOT))
DONE_PATH = Path(__file__).with_suffix(".py.done")


def _write_done(status: str, exit_code: int) -> None:
    content = (
        f"timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"status: {status}\n"
        f"exit_code: {exit_code}\n"
    )
    DONE_PATH.write_text(content, encoding="utf-8")


def main() -> int:
    from infrastructure.eval_cache import write_eval_cache, read_eval_cache

    fields = dict(
        symbol="NFLX",
        verdict="APPROVED_WITH_CAUTION",
        risk_mode="OFF",
        entry_price=78.115,
        stop_price=76.12,
        target_1=98.84,
        position_size=0,
        signal_source="P_115",
        trade_mode_value="PAPER",
        drop_reason=None,
        signal_date="2026-09-14",
        option_method="manual_override_no_auto_sizing",
        option_structure="single_leg",
        option_contract="NFLX261002C79",
        option_entry_premium=1.94,
        option_stop_premium=1.04,
        option_target_premium=11.25,
        option_contracts=4,
        option_override=False,
        iv_rank=0.34556,
    )

    ok = write_eval_cache("NFLX", fields)
    if not ok:
        print("FAIL: write_eval_cache returned False")
        _write_done("FAIL", 1)
        return 1

    # Read back to confirm the write landed and round-tripped correctly.
    readback = read_eval_cache("NFLX")
    if readback is None:
        print("FAIL: read_eval_cache returned None after write")
        _write_done("FAIL", 1)
        return 1

    mismatches = {k: (v, readback.get(k)) for k, v in fields.items() if readback.get(k) != v}
    if mismatches:
        print(f"FAIL: readback mismatches: {mismatches}")
        _write_done("FAIL", 1)
        return 1

    print("Written and verified. Fields:")
    for k, v in fields.items():
        print(f"  {k} = {v}")
    print("PASS")
    _write_done("PASS", 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
