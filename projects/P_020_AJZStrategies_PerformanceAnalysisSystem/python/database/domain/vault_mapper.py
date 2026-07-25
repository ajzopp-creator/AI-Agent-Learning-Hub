"""
vault_mapper.py -- Domain layer (pure logic, no I/O).

Maps a v_trade_summary row to the field dict expected by P020Record
(obsidian_writers.domain.vault_schemas). Resolves WO-P020-E1.005's
Open Decisions 1 and 2:

  Decision 1 (outcome vocabulary): pass v_trade_summary.outcome through
  unchanged (WIN/LOSS/SCRATCH/OPEN). No translation to TP Hit/SL Hit/
  Manual -- that vocabulary was never wired and P020Record's comment is
  stale (P_800-side doc fix, not touched here).

  Decision 2 (multi-leg exits): only exit_1_price is carried into the
  vault note. Partial-exit detail (exit_2/exit_3) is dropped -- P020Record
  has a single exit_price field. Extending it is a P_800 schema change,
  out of scope for this WO.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\domain\\vault_mapper.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   domain
"""
from __future__ import annotations

from typing import Any, Dict, Optional

WRITTEN_BY = "P_020/write_to_obsidian"


def build_vault_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    """Convert one v_trade_summary row into a P020Record-shaped dict.

    Args:
        row: Dict of column name -> value from v_trade_summary (a
            sqlite3.Row cast to dict). Must include at minimum
            underlying_symbol and open_date.

    Returns:
        Dict ready to pass as `data` to
        shared_resources.python_utils.vault_interface.write_to_vault(
            "P020", data).

    Raises:
        ValueError: If underlying_symbol is missing -- the vault
            filename builder requires it and a silent "UNKNOWN" note
            would be worse than failing loudly here.
    """
    symbol = row.get("underlying_symbol")
    if not symbol:
        raise ValueError(
            f"Row missing underlying_symbol -- trade_id={row.get('trade_id')}"
        )

    close_date = row.get("last_exit_date") or row.get("open_date")

    return {
        "trade_id": _to_str(row.get("trade_id")),
        "signal_date": close_date,
        "written_by": WRITTEN_BY,
        "symbol": symbol,
        "account_id": row.get("account_id"),
        "system": row.get("system"),
        "why_code": row.get("reason"),
        "sig_code": row.get("signal_strength"),
        "open_date": row.get("open_date"),
        "close_date": close_date,
        "entry_price": row.get("entry_price"),
        "exit_price": row.get("exit_1_price"),
        "qty": _to_int(row.get("qty")),
        "realized_pnl": row.get("realized_pnl"),
        "realized_R": row.get("realized_R"),
        "risk_amount": row.get("risk_amount"),
        "days_held": row.get("max_hold_days"),
        "outcome": row.get("outcome"),
    }


def _to_int(value: Optional[float]) -> Optional[int]:
    """Round a qty value to int, passing None through unchanged.

    Args:
        value: Raw qty from the DB (may be float from SUM/aggregate math).

    Returns:
        Rounded int, or None if value is None.
    """
    if value is None:
        return None
    return int(round(value))


def _to_str(value: Optional[int]) -> Optional[str]:
    """Cast trade_id to str for the P020Record schema, None-safe.

    Args:
        value: Raw trade_id from the DB (int, sqlite INTEGER PK).

    Returns:
        String form of value, or None if value is None.
    """
    if value is None:
        return None
    return str(value)
