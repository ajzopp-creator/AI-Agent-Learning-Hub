"""batch_2b_disposition.py -- per-symbol cache/vault/archive disposition
for the Tier-2B batch runner, mirroring cmd_evaluate()'s plain-stock path
in commands.py.

Application layer: orchestration only. Bug found 2026-08-07: batch_2b
originally called evaluate_signal() directly with no disposition wrapper,
so a batch-2b-evaluated symbol never left the inbox regardless of
verdict -- a BLOCKED symbol got silently re-evaluated (and re-billed
against the live Schwab API) on every subsequent run, and an APPROVED
one had nothing cached for a later `record` call to find. This file
closes that gap by reusing the exact same functions cmd_evaluate()
already calls for its plain-stock branch, so batch-2b's per-symbol side
effects are identical to running `evaluate SYMBOL` by hand.

Public interface for batch_2b_scoring.py: dispose_evaluation().

WO-P400-E5.003 (bug fix within existing scope -- the WO's own acceptance
criterion is "byte-identical to running individually," which this was
not, until now).
"""

from __future__ import annotations

from config import SPEC_CACHEABLE_VERDICTS, TradeMode
from application.build_order_spec import build_spec
from application.spec_cache import cache_spec_text
from application.stock_fields import build_stock_fields
from infrastructure.eval_cache import write_eval_cache
from infrastructure.record_writer import write_p400_record
from infrastructure.signal_archiver import archive_packet


def dispose_evaluation(packet, eval_result, snapshot: dict, trade_mode: TradeMode) -> None:
    """Cache, vault-write, and archive a symbol batch-2b just evaluated --
    every verdict, unconditionally, matching cmd_evaluate()'s plain-stock
    branch (commands.py) exactly. Vehicle comparison never feeds this; it
    runs afterward (if at all) and is informational/ranking-only -- an
    OPTION/SPREAD recommendation does not change what gets cached here.
    """
    stock_fields = build_stock_fields(eval_result, packet, trade_mode.value)
    if eval_result.verdict in SPEC_CACHEABLE_VERDICTS:
        spec_text = build_spec(eval_result, packet, snapshot)
        cache_spec_text(eval_result.symbol, spec_text, stock_fields)
    else:
        write_eval_cache(eval_result.symbol, stock_fields)

    if eval_result.verdict == "BLOCKED":
        written = write_p400_record(
            symbol=eval_result.symbol,
            verdict="BLOCKED",
            risk_mode=eval_result.posture.risk_mode,
            entry_price=eval_result.effective_entry,
            stop_price=eval_result.effective_stop,
            target_1=packet.guideline_target,
            position_size=0,
            signal_source=packet.signal_source,
            trade_mode_value=trade_mode.value,
            drop_reason="COUNCIL_BLOCK",
            signal_date=packet.signal_metadata.session_date,
        )
        print(f"  BLOCKED record written: {eval_result.symbol}  "
              f"(vault_write={'OK' if written else 'FAILED'})")

    archive_packet(packet.symbol, packet.signal_metadata.session_date)
