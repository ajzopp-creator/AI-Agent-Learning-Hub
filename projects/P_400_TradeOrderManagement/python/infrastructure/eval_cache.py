"""eval_cache.py -- per-symbol cache of the last evaluate/spec result.

Infrastructure layer: I/O only. No business logic.

Why this exists (WO-P400-E3.006): by the time Tony reports an order_id
back, evaluate/spec has already archived the source signal packet out of
the inbox. The `record` command needs entry/stop/target/size/verdict --
and for options/spread trades, the option_*/spread_* fields too -- to
write the vault note, but re-running evaluate would re-archive the
packet a second time (the exact bug that produced duplicate zip entries
on 2026-07-05). Caching the result here means `record` never touches the
packet, the archiver, or Council again.

Deliberately schema-agnostic: caller passes a flat dict of whatever
write_p400_record() kwargs apply (stock-only, or options, or spread --
this file does not know or care which). Cache lives at
python\eval_cache\SYMBOL.json -- one file per symbol, overwritten on
every evaluate/spec run (most recent result wins).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger("p400.eval_cache")

_CACHE_DIR = Path(__file__).resolve().parent.parent / "eval_cache"


def _cache_path(symbol: str) -> Path:
    return _CACHE_DIR / f"{symbol.upper()}.json"


def write_eval_cache(symbol: str, fields: dict) -> bool:
    """Write/overwrite the cached evaluate result for a symbol.

    `fields` should be a flat dict of write_p400_record() kwargs (symbol,
    verdict, risk_mode, entry_price, stop_price, target_1, position_size,
    signal_source, signal_date, trade_mode_value, plus any option_*/
    spread_* fields that apply for that run). Never raises -- a cache
    write failure should not block evaluate/spec from completing.
    """
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _cache_path(symbol).write_text(json.dumps(fields, indent=2), encoding="utf-8")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("eval_cache: write failed for %s -- %s", symbol, exc)
        return False


def read_eval_cache(symbol: str) -> dict | None:
    """Read the cached evaluate result for a symbol.

    Returns None if no cache file exists or it fails to parse -- caller
    (record_commands.py) is responsible for surfacing a clear error to
    Tony rather than fabricating missing fields.
    """
    path = _cache_path(symbol)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        logger.warning("eval_cache: read failed for %s -- %s", symbol, exc)
        return None