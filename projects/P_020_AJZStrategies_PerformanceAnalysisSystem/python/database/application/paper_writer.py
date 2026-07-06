"""
paper_writer.py -- Application layer.

Writes trade dicts (each with an optional "_exits" list, see
infrastructure/paper_csv_reader.py) to the trades and exits tables.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\application\\paper_writer.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List

DB_PATH = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
)


def _trades_schema(conn: sqlite3.Connection) -> List[str]:
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(trades)")
    return [row[1] for row in cur.fetchall()]


def _is_duplicate(conn: sqlite3.Connection, t: Dict) -> bool:
    cur = conn.cursor()
    cur.execute(
        "SELECT trade_id FROM trades WHERE account_id=? AND underlying_symbol=? "
        "AND open_date=? AND entry_price=? AND source=? LIMIT 1",
        (t["account_id"], t["underlying_symbol"], t["open_date"],
         t["entry_price"], t["source"]),
    )
    row = cur.fetchone()
    return row[0] if row else None


def _insert_exits(conn: sqlite3.Connection, trade_id: int, exits: List[Dict]) -> int:
    """Insert exit rows for a trade_id. Skips any exit_number already
    present for that trade_id (safe to re-run against existing trades)."""
    cur = conn.cursor()
    cur.execute("SELECT exit_number FROM exits WHERE trade_id=?", (trade_id,))
    existing = {row[0] for row in cur.fetchall()}
    inserted = 0
    for e in exits:
        if e["exit_number"] in existing:
            continue
        conn.execute(
            "INSERT INTO exits (trade_id, exit_number, exit_date, qty_exited, "
            "exit_price, exit_commissions, exit_pnl, hold_days) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (trade_id, e["exit_number"], e["exit_date"], e["qty_exited"],
             e["exit_price"], e["exit_commissions"], e["exit_pnl"], e["hold_days"]),
        )
        inserted += 1
    return inserted


def write_trades(trades: List[Dict], db_path: Path = DB_PATH) -> Dict:
    stats = {"inserted": 0, "skipped_dup": 0, "errors": 0, "exits_inserted": 0}
    if not trades:
        return stats

    conn = sqlite3.connect(db_path)
    try:
        schema_cols = set(_trades_schema(conn))
        for t in trades:
            try:
                existing_id = _is_duplicate(conn, t)
                exits = t.get("_exits", [])
                if existing_id is not None:
                    stats["skipped_dup"] += 1
                    stats["exits_inserted"] += _insert_exits(conn, existing_id, exits)
                    conn.execute(
                        "UPDATE trades SET status=? WHERE trade_id=? AND status != ?",
                        (t["status"], existing_id, t["status"]),
                    )
                    continue
                cols = [k for k in t.keys() if k in schema_cols]
                if not cols:
                    stats["errors"] += 1
                    continue
                placeholders = ",".join("?" for _ in cols)
                col_list = ",".join(cols)
                values = [t[k] for k in cols]
                cur = conn.execute(
                    f"INSERT INTO trades ({col_list}) VALUES ({placeholders})",
                    values,
                )
                stats["inserted"] += 1
                stats["exits_inserted"] += _insert_exits(conn, cur.lastrowid, exits)
            except sqlite3.Error:
                stats["errors"] += 1
        conn.commit()
    finally:
        conn.close()
    return stats
