"""test_spec_cache.py -- WO-P400-E3.009: same-day spec-text cache.

Follows test_eval_cache.py's convention: real cache dir, ZZZ-prefixed
test symbols, self-cleanup via infrastructure.eval_cache._cache_path.
"""

from __future__ import annotations

from datetime import date, timedelta

import infrastructure.eval_cache as eval_cache
from application.spec_cache import cache_spec_text, read_cached_spec_text


def _clear(symbol: str) -> None:
    path = eval_cache._cache_path(symbol)
    if path.exists():
        path.unlink()


def test_no_cache_returns_none():
    _clear("ZZZSPECNONE")
    assert read_cached_spec_text("ZZZSPECNONE") is None


def test_same_day_cache_hit_returns_exact_text():
    _clear("ZZZSPECHIT")
    text = "BUY 10 ZZZSPECHIT @ 100.00 LIMIT, DAY"
    ok = cache_spec_text("ZZZSPECHIT", text, {"symbol": "ZZZSPECHIT", "verdict": "APPROVED"})
    assert ok is True
    assert read_cached_spec_text("ZZZSPECHIT") == text
    _clear("ZZZSPECHIT")


def test_stale_cache_from_prior_day_returns_none():
    _clear("ZZZSPECSTALE")
    fields = {
        "symbol": "ZZZSPECSTALE", "verdict": "APPROVED",
        "spec_text": "stale spec text",
        "cache_written_at": (date.today() - timedelta(days=1)).isoformat(),
    }
    eval_cache.write_eval_cache("ZZZSPECSTALE", fields)
    assert read_cached_spec_text("ZZZSPECSTALE") is None
    _clear("ZZZSPECSTALE")


def test_cache_without_spec_text_key_returns_none():
    # Mirrors a BLOCKED-verdict evaluate run, which never calls
    # cache_spec_text() -- only write_eval_cache() with no spec_text key.
    _clear("ZZZSPECNOTEXT")
    fields = {"symbol": "ZZZSPECNOTEXT", "verdict": "BLOCKED"}
    eval_cache.write_eval_cache("ZZZSPECNOTEXT", fields)
    assert read_cached_spec_text("ZZZSPECNOTEXT") is None
    _clear("ZZZSPECNOTEXT")


def test_base_fields_preserved_alongside_spec_text():
    _clear("ZZZSPECFIELDS")
    base = {"symbol": "ZZZSPECFIELDS", "verdict": "APPROVED", "entry_price": 55.00}
    cache_spec_text("ZZZSPECFIELDS", "spec text here", base)
    got = eval_cache.read_eval_cache("ZZZSPECFIELDS")
    assert got["entry_price"] == 55.00
    assert got["verdict"] == "APPROVED"
    assert got["spec_text"] == "spec text here"
    assert got["cache_written_at"] == date.today().isoformat()
    _clear("ZZZSPECFIELDS")