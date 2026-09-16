"""size_option_standalone.py -- packet-free options sizing + spec entry
point (WO-P400-E8.003).

Application layer: orchestration + printing (matches commands.py's cmd_*
convention -- other cmd_* functions in this codebase print directly, not
a separate CLI-only printing layer).

Exists because evaluate_options() needs a live signal packet only for
three scalar values (symbol, guideline_stop, guideline_target) -- WO-
P400-E8.002/E8.003's WHY: once a symbol's packet is archived (spec or
batch-2b already consumed it), there was no way back into the real
sizer+council+macro-gate pipeline, only manual guessing. This reuses
evaluate_options() exactly -- not a simplified stand-in -- by supplying
those three values directly instead of from a packet.

stock_rr (needed for the options-council R:R parity gate) is computed
here from the same entry/stop/target already required, rather than asked
of Tony as a fourth, redundant number.

Writes an immediate P400 record (any verdict, matching
write_options_eval_record()'s "full audit trail, not BLOCK-only")
AND populates eval_cache so `record --order-id` can upgrade it to
SUBMITTED later -- same two writes the live-packet path makes, just
via write_p400_record() directly rather than record_writer.py's
packet/stock_result-coupled _build_options_fields() (that helper's
stock-level-BLOCK-override logic doesn't apply here -- there is no
separate stock evaluation in this path).

Known limitation: write_p400_record() has no target_2 parameter yet
(P_800/obsidian_writers owns that schema, out of scope for this WO) --
the vault record carries the primary target only; target_2 is fully
reflected in the printed spec (Pattern B scale-out) and in eval_cache,
just not in the vault frontmatter yet.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Optional

from application.evaluate_options import evaluate_options
from infrastructure.eval_cache import write_eval_cache
from infrastructure.posture_reader import read_posture
from infrastructure.record_writer import write_p400_record

_VERDICT_MAP = {"PASS": "APPROVED", "CAUTION": "APPROVED_WITH_CAUTION", "BLOCK": "BLOCKED"}


def _occ_contract(symbol: str, expiration: str, option_type: str, strike: float) -> str:
    """Same simple OCC-ish format record_writer.py's _build_options_fields
    uses for the vault/eval_cache option_contract field (distinct from
    build_option_spec.py's true-OCC symbol used in the printed order text
    -- two different pre-existing formats in this codebase, not unified
    here; out of scope)."""
    cp = expiration.replace("-", "")[2:]
    cp_type = "C" if option_type == "call" else "P"
    return f"{symbol}{cp}{cp_type}{strike:g}"


def cmd_size_option(
    symbol: str,
    snapshot_path: str,
    chain_path: str,
    stock_stop: float,
    cash: float,
    stock_target: Optional[float] = None,
    stock_target_2: Optional[float] = None,
    is_paper: bool = False,
    signal_source: str = "MANUAL",
    signal_date: Optional[str] = None,
) -> int:
    """Packet-free options sizing + spec + record write.

    Args:
        symbol: Underlying ticker.
        snapshot_path: Path to snapshot_SYMBOL.json (same format --options
            already requires).
        chain_path: Path to chain_SYMBOL.json.
        stock_stop: Underlying stop price.
        cash: Per-trade buying power.
        stock_target: T1. At least one of stock_target/stock_target_2 required.
        stock_target_2: T2. When both are given, renders a two-bracket
            scale-out spec (build_option_spec_scaleout.py via
            build_option_spec()'s stock_target_2 param).
        is_paper: If True, prepends PAPER TRADE banner and writes PAPER
            trade_mode.
        signal_source: No live packet to inherit this from -- defaults to
            "MANUAL".
        signal_date: Defaults to today (ISO date) if not given.

    Returns:
        0 if the tool ran to completion (any verdict, including BLOCK --
        a clean BLOCK is a legitimate outcome, not a tool failure). 1 only
        on a usage error (neither target given).
    """
    if stock_target is None and stock_target_2 is None:
        print("[ERROR] size-option requires --target, --target-2, or both.")
        return 1

    primary_target = stock_target if stock_target is not None else stock_target_2
    # Only a real, distinct second target triggers the scale-out path --
    # target-2-only is "the one target happens to be called T2", a single
    # bracket, not a degenerate scale-out against itself.
    effective_target_2 = stock_target_2 if (stock_target is not None and stock_target_2 is not None) else None
    signal_date = signal_date or date.today().isoformat()

    snapshot_raw = json.loads(open(snapshot_path, encoding="utf-8").read())
    stock_entry = snapshot_raw["price"]

    risk = stock_entry - stock_stop
    stock_rr = round((primary_target - stock_entry) / risk, 3) if risk > 0 else 0.0

    opt_result = evaluate_options(
        symbol=symbol, stock_stop=stock_stop, stock_target=primary_target,
        snapshot_raw=snapshot_raw, chain_path=chain_path, cash_available=cash,
        stock_rr=stock_rr, is_paper=is_paper, stock_target_2=effective_target_2,
    )

    print("=" * 60)
    print(f"OPTIONS COUNCIL: {opt_result.symbol}  |  verdict={opt_result.verdict}  "
          f"(packet-free -- WO-P400-E8.003)")
    for b in opt_result.council.blocks:
        print(f"  BLOCK: {b}")
    for c in opt_result.council.cautions:
        print(f"  CAUTION: {c}")
    print("=" * 60)
    if opt_result.spec_text:
        print(opt_result.spec_text)
    else:
        print(f"[NO SPEC -- {symbol}] Options council BLOCKED. No order spec generated.")

    posture = read_posture()
    sizing = opt_result.sizing
    contracts = max(sizing.contracts, 1) if sizing.override_required else sizing.contracts
    verdict = _VERDICT_MAP.get(opt_result.verdict, opt_result.verdict)
    drop_reason = "COUNCIL_BLOCK" if opt_result.verdict == "BLOCK" else None
    occ = _occ_contract(symbol, opt_result.chain.expiration, opt_result.chain.option_type,
                        opt_result.chain.strike)

    fields = dict(
        symbol=symbol, verdict=verdict, risk_mode=posture.risk_mode,
        entry_price=stock_entry, stop_price=stock_stop,
        target_1=primary_target, target_2=effective_target_2, position_size=0,
        signal_source=signal_source,
        trade_mode_value=("PAPER" if is_paper else "REAL"),
        drop_reason=drop_reason, signal_date=signal_date,
        option_method=sizing.method,
        option_structure=("single_leg" if effective_target_2 is None else "scale_out"),
        option_contract=occ,
        option_entry_premium=sizing.option_entry, option_stop_premium=sizing.option_stop,
        option_target_premium=sizing.option_target, option_contracts=contracts,
        option_override=sizing.override_required, iv_rank=opt_result.chain.iv,
    )

    written = write_p400_record(**fields)
    write_eval_cache(symbol, fields)
    print(f"P400 record written: {symbol}  verdict={verdict}  "
          f"(vault_write={'OK' if written else 'FAILED'}, eval_cache=OK)")
    if effective_target_2 is not None:
        print(f"NOTE: vault record carries target_1={primary_target:.2f} only -- "
              f"target_2={effective_target_2:.2f} is in the spec above and eval_cache, "
              f"not yet in the vault schema (write_p400_record has no target_2 param).")

    return 0
