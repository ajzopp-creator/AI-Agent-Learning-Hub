"""batch_drop_rr_invalid.py -- One-off utility: drop the 06-30 Tier-1
RR_BELOW_MIN failures as REVIEWED_NO_TRADE/RR_INVALID records.

Not part of the layered cli.py/commands.py pipeline -- a single-run
script so Tony doesn't need 17 separate terminal round-trips. Hardcoded
symbol list (not "everything that currently fails screen") so the scope
is explicit and reviewable, not silently whatever the screen happens to
return at run time.

Run from python/ dir, p140 env, PYTHONPATH set to hub root -- same as
every other cli.py invocation this session.
"""

from __future__ import annotations

from application.commands import _find_packet
from application.drop_signal import drop_signal
from config import TradeMode

# Exact 06-30 morning Tier-1 RR_BELOW_MIN list (screen-all output,
# posture=OFF). ADBE (the one PASS) and the 06-22/06-23 batches are
# handled separately -- not included here.
SYMBOLS_BATCH_1 = [
    "TTD", "TR", "AMYZF", "LULU", "WIX", "WU", "TDC", "PI",
    "OTEX", "HQY", "HTGC", "CHGG", "TYL", "DOCU", "BL", "FICO", "FIVN",
]

# Exact 06-30 afternoon Tier-1 RR_BELOW_MIN list (screen-all output,
# posture=HALF). ARCC (the one PASS, later BLOCKED at evaluate) handled
# separately. Added per WO-P400-E2.018 -- manual precedent batch.
SYMBOLS_BATCH_2 = [
    "QS", "OPEN", "STWD", "KNDI", "APP", "TWLO", "VOC", "WRAP", "ZETA",
    "JVA", "ZDGE",
]

SYMBOLS = SYMBOLS_BATCH_1 + SYMBOLS_BATCH_2


def main() -> int:
    results = []
    for symbol in SYMBOLS:
        packet = _find_packet(symbol)
        if packet is None:
            print(f"[SKIP] {symbol}: no valid v2 packet found in inbox")
            results.append((symbol, False, False))
            continue
        ok = drop_signal(packet, "RR_INVALID", TradeMode.REAL)
        print(f"{'OK  ' if ok else 'FAIL'} {symbol}: drop_signal -> {ok}")
        results.append((symbol, True, ok))

    print("=" * 60)
    succeeded = sum(1 for _, found, ok in results if found and ok)
    failed = [s for s, found, ok in results if not found or not ok]
    print(f"BATCH DROP COMPLETE: {succeeded}/{len(SYMBOLS)} succeeded")
    if failed:
        print(f"  FAILED/SKIPPED: {', '.join(failed)}")
    print("=" * 60)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())