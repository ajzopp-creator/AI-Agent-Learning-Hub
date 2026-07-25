"""spec_cache.py -- same-day cache of a rendered order-spec string.

Application layer: thin orchestration over infrastructure.eval_cache.
Exists so `spec` can reuse the result `evaluate` already produced in the
same session instead of re-running evaluate_signal() and re-archiving
the source packet (WO-P400-E3.009).

Reuses eval_cache.py's existing per-symbol JSON file (WO-P400-E3.006) --
adds two extra keys (`spec_text`, `cache_written_at`) to whatever flat
fields dict the caller already builds for record-writing. Does not
change eval_cache.py itself -- its schema-agnostic caller contract
already supports this.
"""

from __future__ import annotations

from datetime import date

from infrastructure.eval_cache import read_eval_cache, write_eval_cache


def cache_spec_text(symbol: str, spec_text: str, base_fields: dict) -> bool:
    """Write the eval_cache entry with a rendered spec_text attached.

    `base_fields` is the same flat dict already passed to write_eval_cache
    elsewhere (record-writing kwargs) -- this adds two keys and writes
    once, so the record cache and spec cache stay the same file.
    """
    fields = dict(base_fields)
    fields["spec_text"] = spec_text
    fields["cache_written_at"] = date.today().isoformat()
    return write_eval_cache(symbol, fields)


def read_cached_spec_text(symbol: str) -> str | None:
    """Return today's cached spec_text for symbol, or None.

    None on: no cache file, no spec_text key (e.g. verdict wasn't
    APPROVED at evaluate time), or cache_written_at isn't today -- a
    spec cached in a prior session is never trusted as current.
    """
    cached = read_eval_cache(symbol)
    if not cached:
        return None
    if cached.get("cache_written_at") != date.today().isoformat():
        return None
    return cached.get("spec_text")