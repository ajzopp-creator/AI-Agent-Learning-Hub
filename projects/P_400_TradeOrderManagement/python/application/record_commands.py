"""record_commands.py -- WO-P400-E3.006: submitted/declined disposition
for a signal that already came back APPROVED from evaluate/spec.

Application layer: orchestration only. Reads the cached result from
infrastructure/eval_cache.py (never re-touches the archived packet or
re-runs Council) and calls record_writer.write_p400_record() directly.
"""

from __future__ import annotations

from infrastructure.eval_cache import read_eval_cache
from infrastructure.record_writer import write_p400_record

# Keys spec_cache.py (WO-P400-E3.009) adds onto the same eval_cache file
# that write_p400_record()'s kwargs come from -- write_p400_record()
# doesn't accept them, so they must be stripped before **cached unpacks
# here. Regression found live 2026-07-14 (WMT record submit failed with
# TypeError: unexpected keyword argument 'spec_text').
from config import TradeMode

_CACHE_ONLY_KEYS = ("spec_text", "cache_written_at")


def _strip_cache_only_keys(cached: dict) -> dict:
    """Return a copy of cached with spec-cache-only keys removed."""
    return {k: v for k, v in cached.items() if k not in _CACHE_ONLY_KEYS}


def cmd_record_submit(symbol: str, order_id: str, paper: bool = False) -> int:
    """Write a SUBMITTED vault record for a symbol Tony executed.

    Requires a prior evaluate/spec run this session (or since the last
    eval_cache overwrite) -- the cache is the only source of truth here,
    by design, to avoid re-archiving the signal packet a second time.

    `paper` (WO-P400-E5.001): Tony decides paper-vs-real at the fill, not
    at evaluate/spec time. When True, overrides the cached trade_mode_value
    to PAPER for this write only -- the eval_cache file on disk is never
    mutated, so a later `record` call for the same symbol isn't silently
    stuck in PAPER mode from an unrelated earlier call.
    """
    cached = read_eval_cache(symbol)
    if cached is None:
        print(f"[ERROR] No cached evaluate/spec result for {symbol}. "
              f"Run `evaluate` or `spec` for {symbol} first, then `record`.")
        return 1

    verdict = cached.get("verdict")
    if verdict not in ("APPROVED", "APPROVED_WITH_CAUTION", "APPROVED_WITH_SEVERE_WARNING"):
        print(f"[ERROR] Cached verdict for {symbol} is {verdict!r} -- "
              f"only APPROVED/APPROVED_WITH_CAUTION/APPROVED_WITH_SEVERE_WARNING can be submitted.")
        return 1

    fields = _strip_cache_only_keys(cached)
    if paper:
        fields = {**fields, "trade_mode_value": TradeMode.PAPER.value}

    written = write_p400_record(order_id=order_id, **fields)
    print(f"SUBMITTED record written: {symbol}  order_id={order_id}  "
          f"mode={fields['trade_mode_value']}  "
          f"(vault_write={'OK' if written else 'FAILED'})")
    return 0 if written else 1


def cmd_record_decline(symbol: str) -> int:
    """Write a MANUAL_DECLINE vault record for an APPROVED signal Tony
    chose not to execute -- distinguishes "approved but skipped" from
    "never evaluated" in the audit trail (WO-P400-E3.006).
    """
    cached = read_eval_cache(symbol)
    if cached is None:
        print(f"[ERROR] No cached evaluate/spec result for {symbol}. "
              f"Run `evaluate` or `spec` for {symbol} first, then `record`.")
        return 1

    verdict = cached.get("verdict")
    if verdict not in ("APPROVED", "APPROVED_WITH_CAUTION", "APPROVED_WITH_SEVERE_WARNING"):
        print(f"[ERROR] Cached verdict for {symbol} is {verdict!r} -- "
              f"decline only applies to an APPROVED signal.")
        return 1

    cached = _strip_cache_only_keys(cached)
    cached["drop_reason"] = "MANUAL_DECLINE"
    written = write_p400_record(**cached)
    print(f"DECLINED record written: {symbol}  (vault_write={'OK' if written else 'FAILED'})")
    return 0 if written else 1