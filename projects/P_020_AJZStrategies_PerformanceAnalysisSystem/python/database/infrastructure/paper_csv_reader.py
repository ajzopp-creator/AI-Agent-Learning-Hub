"""
paper_csv_reader.py -- Infrastructure layer.

Reads the _OPTIONS_IMPORT.csv / _STOCKS_IMPORT.csv files produced by the
TOS parser and builds trade dicts ready for the trades table, each with
an attached "_exits" list (built via domain/exit_builder.py) ready for
the exits table.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\infrastructure\\paper_csv_reader.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   infrastructure
"""
from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from domain.exit_builder import build_exits  # noqa: E402

PAPER_ACCOUNT_ID = "PAPER"
SOURCE_TAG = "tos_paper_csv"
DEFAULT_SYSTEM = "TOS_Import"


def _parse_trade_date(s: str) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _to_float(s) -> Optional[float]:
    if s is None or s == "":
        return None
    try:
        return float(str(s).replace(",", "").replace("$", "").strip())
    except ValueError:
        return None


def _clean_system(s: Optional[str]) -> str:
    if not s or not s.strip():
        return DEFAULT_SYSTEM
    return s.strip()


def _derive_status(qty: Optional[float], exits: List[Dict]) -> str:
    if not exits:
        return "open"
    qty_closed = sum(e["qty_exited"] for e in exits)
    if qty is not None and qty_closed < qty:
        return "partial"
    return "closed"


def read_options_csv(path: Path) -> List[Dict]:
    trades = []
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            symbol = (row.get("Symbol") or "").strip().upper()
            if not symbol:
                continue
            trade_type = (row.get("Trade Type") or "").strip().lower()
            asset_type = trade_type if trade_type in ("call", "put") else "call"
            direction = "long" if (row.get("Long/Short") or "").strip().lower() == "long" else "short"
            open_date = _parse_trade_date(row.get("Trade Date", ""))
            entry_price = _to_float(row.get("Entry $$"))

            exit_slots = [
                {"price": _to_float(row.get("Exit #1 $")), "qty": _to_float(row.get("# Exited")), "date": _parse_trade_date(row.get("Exit Date", ""))},
                {"price": _to_float(row.get("Exit #2 $")), "qty": _to_float(row.get("# Exited2")), "date": _parse_trade_date(row.get("Exit Date3", ""))},
                {"price": _to_float(row.get("Exit #3 $")), "qty": _to_float(row.get("# Exited5")), "date": _parse_trade_date(row.get("Exit Date6", ""))},
            ]
            qty = _to_float(row.get("Contracts"))
            exits = build_exits(entry_price, direction, asset_type, open_date, exit_slots)
            trades.append({
                "account_id": PAPER_ACCOUNT_ID,
                "system": _clean_system(row.get("System")),
                "underlying_symbol": symbol,
                "asset_type": asset_type,
                "direction": direction,
                "open_date": open_date,
                "qty": qty,
                "entry_price": entry_price,
                "total_commissions": _to_float(row.get("Comm.")),
                "status": _derive_status(qty, exits),
                "notes": (row.get("Trade Comments") or "").strip() or None,
                "source": SOURCE_TAG,
                "reason": None,
                "signal_strength": None,
                "_exits": exits,
            })
    return trades


def read_stocks_csv(path: Path) -> List[Dict]:
    trades = []
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            symbol = (row.get("Symbol") or "").strip().upper()
            if not symbol:
                continue
            direction = "long" if (row.get("Long/Short") or "").strip().lower() == "long" else "short"
            open_date = _parse_trade_date(row.get("Trade Date", ""))
            entry_price = _to_float(row.get("Entry Price"))

            exit_slots = [
                {"price": _to_float(row.get("Exit #1")), "qty": _to_float(row.get("# Exited")), "date": _parse_trade_date(row.get("Exit Date", ""))},
                {"price": _to_float(row.get("Exit #2")), "qty": _to_float(row.get("# Exited2")), "date": _parse_trade_date(row.get("Exit Date3", ""))},
            ]
            qty = _to_float(row.get("Shares"))
            exits = build_exits(entry_price, direction, "stock", open_date, exit_slots)
            trades.append({
                "account_id": PAPER_ACCOUNT_ID,
                "system": _clean_system(row.get("System")),
                "underlying_symbol": symbol,
                "asset_type": "stock",
                "direction": direction,
                "open_date": open_date,
                "qty": qty,
                "entry_price": entry_price,
                "total_commissions": _to_float(row.get("Comm.")),
                "status": _derive_status(qty, exits),
                "notes": (row.get("Trade Comments") or "").strip() or None,
                "source": SOURCE_TAG,
                "reason": None,
                "signal_strength": None,
                "_exits": exits,
            })
    return trades
