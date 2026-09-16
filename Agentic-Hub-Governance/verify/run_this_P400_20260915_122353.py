"""run_this_P400_20260915_122353.py -- live diagnostic for WO-P400-E8.002.

Not a WO build step -- Tony pasted a live Tier-1 screen result (6 PASS
symbols: NFLX, EHC, SELF, FLNT, TTWO, CARG) and this checks whether the
E8.002 gate actually fired for those exact symbols against today's real
cache (pulled 2026-08-19, 27 days old at time of WO-P400-E8.002 build).
Read-only -- does not run batch-2b itself, does not write anything to the
vault or any book. Calls build_entries_for_symbols() directly, the same
function batch-2b's run_batch_2b() calls, against the real on-disk cache.
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
    from application.earnings_lookup import (
        SOURCE_CONFIRMED_CLEAR,
        SOURCE_GATE_UNCERTAIN,
        build_entries_for_symbols,
    )
    from infrastructure.earnings_calendar_cache import (
        cache_age_days,
        is_stale,
        is_valid_for_current_gate,
        load_cache,
    )

    cache = load_cache()
    if cache is None:
        print("FAIL: no cache on disk")
        _write_done("FAIL", 1)
        return 1

    age = cache_age_days(cache)
    print(f"cache.pulled_date = {cache.pulled_date}  (age {age} days)")
    print(f"is_stale() = {is_stale(cache)}")
    print(f"is_valid_for_current_gate() = {is_valid_for_current_gate(cache)}")
    print()

    pass_symbols = ["NFLX", "EHC", "SELF", "FLNT", "TTWO", "CARG"]
    entries = build_entries_for_symbols(pass_symbols)

    print(f"{'SYMBOL':<8}{'IN_CACHE':<10}{'SOURCE':<32}{'next_earnings_date':<20}{'date_confirmed'}")
    for sym in pass_symbols:
        e = entries[sym]
        in_cache = sym in cache.entries
        print(f"{sym:<8}{str(in_cache):<10}{e.source:<32}{str(e.next_earnings_date):<20}{e.date_confirmed}")

    n_uncertain = sum(1 for s in pass_symbols if entries[s].source == SOURCE_GATE_UNCERTAIN)
    n_confirmed = sum(1 for s in pass_symbols if entries[s].source == SOURCE_CONFIRMED_CLEAR)
    n_from_cache = sum(1 for s in pass_symbols if s in cache.entries)
    print()
    print(f"from_cache={n_from_cache}  confirmed_clear={n_confirmed}  gate_uncertain={n_uncertain}")

    print("PASS")
    _write_done("PASS", 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
