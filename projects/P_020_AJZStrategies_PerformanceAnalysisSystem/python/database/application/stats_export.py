"""
stats_export.py
Phase 3E - Export AI analysis CSVs from P_020 SQLite DB + Schwab API.

Supports both live and paper accounts via --account parameter.
  Live:  --account AJZ6348  (default)  -> data/exports/ai_review/
  Paper: --account PAPER               -> data/exports/paper_ai_review/

Output: 6 CSV files per account (open_positions skipped for PAPER).
"""

import argparse
import csv
import logging
import sqlite3
import sys
from datetime import date
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH      = PROJECT_ROOT / "data" / "database" / "P_020_trades.db"
API_DIR      = PROJECT_ROOT / "python" / "api"

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger(__name__)


# ── Account helpers ────────────────────────────────────────────────────────

def _get_scope(account_id: str) -> str:
    """Return WHERE clause scope for the given account."""
    if account_id.upper() == "PAPER":
        return "account_id = 'PAPER'"
    return "open_date >= '2026-01-01' AND account_id LIKE '%6348%'"


def _get_export_dir(account_id: str) -> Path:
    """Return output directory for the given account."""
    if account_id.upper() == "PAPER":
        return PROJECT_ROOT / "data" / "exports" / "paper_ai_review"
    return PROJECT_ROOT / "data" / "exports" / "ai_review"


def _acct_filter(account_id: str) -> str:
    """Return raw account filter fragment for JOINed queries."""
    if account_id.upper() == "PAPER":
        return "t.account_id = 'PAPER'"
    return "t.account_id LIKE '%6348%' AND t.open_date >= '2026-01-01'"


# ── DB / CSV helpers ───────────────────────────────────────────────────────

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def write_csv(path: Path, rows: list, fieldnames: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    log.info(f"Wrote {len(rows)} rows -> {path.name}")


# ── Export functions ───────────────────────────────────────────────────────

def export_summary_by_system(conn, scope: str, export_dir: Path):
    sql = f"""
        SELECT system,
            COUNT(*) AS total_trades,
            SUM(CASE WHEN outcome='WIN'    THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN outcome='LOSS'   THEN 1 ELSE 0 END) AS losses,
            SUM(CASE WHEN outcome='SCRATCH' THEN 1 ELSE 0 END) AS scratches,
            SUM(CASE WHEN status='open'    THEN 1 ELSE 0 END) AS open_trades,
            ROUND(100.0*SUM(CASE WHEN outcome='WIN' THEN 1 ELSE 0 END)
                /NULLIF(SUM(CASE WHEN outcome IN ('WIN','LOSS') THEN 1 ELSE 0 END),0),1) AS win_rate_pct,
            ROUND(100.0*SUM(CASE WHEN outcome='LOSS' THEN 1 ELSE 0 END)
                /NULLIF(SUM(CASE WHEN outcome IN ('WIN','LOSS') THEN 1 ELSE 0 END),0),1) AS loss_rate_pct,
            ROUND(COALESCE(SUM(realized_pnl),0),2) AS total_pnl,
            ROUND(SUM(CASE WHEN realized_pnl>0 THEN realized_pnl ELSE 0 END),2) AS net_gains,
            ROUND(SUM(CASE WHEN realized_pnl<0 THEN realized_pnl ELSE 0 END),2) AS net_losses,
            ROUND(AVG(CASE WHEN outcome='WIN'  THEN realized_pnl END),2) AS avg_win,
            ROUND(AVG(CASE WHEN outcome='LOSS' THEN realized_pnl END),2) AS avg_loss,
            ROUND(AVG(CASE WHEN outcome='WIN'  THEN realized_R END),2) AS avg_win_R,
            ROUND(AVG(CASE WHEN outcome='LOSS' THEN realized_R END),2) AS avg_loss_R,
            ROUND(AVG(realized_R),2) AS avg_R,
            ROUND(NULLIF(SUM(CASE WHEN realized_pnl>0 THEN realized_pnl ELSE 0 END),0)
                /NULLIF(ABS(SUM(CASE WHEN realized_pnl<0 THEN realized_pnl ELSE 0 END)),0),2) AS profit_factor,
            ROUND(AVG(max_hold_days),1) AS avg_hold_days
        FROM v_trade_summary WHERE {scope}
        GROUP BY system ORDER BY total_pnl DESC"""
    rows = [dict(r) for r in conn.execute(sql).fetchall()]

    for r in rows:
        wr  = (r.get("win_rate_pct")  or 0) / 100.0
        lr  = (r.get("loss_rate_pct") or 0) / 100.0
        awr = r.get("avg_win_R")  or 0.0
        alr = r.get("avg_loss_R") or 0.0
        rr  = round(awr / abs(alr), 2) if alr and alr != 0 else None
        r["rr_ratio"]      = rr
        r["expectancy_r"]  = round((wr * awr) + (lr * alr), 2) if rr is not None else None
        r["kelly_pct"]     = round((wr - (lr / rr)) * 100, 1) if rr else None
        r["breakeven_pct"] = round((1.0 / (1.0 + rr)) * 100, 1) if rr else None

    write_csv(export_dir / "summary_by_system.csv", rows,
        ["system", "total_trades", "wins", "losses", "scratches", "open_trades",
         "win_rate_pct", "loss_rate_pct",
         "total_pnl", "net_gains", "net_losses",
         "avg_win", "avg_loss", "avg_win_R", "avg_loss_R", "avg_R",
         "rr_ratio", "expectancy_r", "kelly_pct", "breakeven_pct",
         "profit_factor", "avg_hold_days"])


def export_equity_curve(conn, acct_filter: str, export_dir: Path):
    sql = f"""
        SELECT e.exit_date, t.system, SUM(e.exit_pnl) AS daily_pnl
        FROM exits e JOIN trades t ON t.trade_id = e.trade_id
        WHERE {acct_filter} AND e.exit_date IS NOT NULL
        GROUP BY e.exit_date, t.system ORDER BY e.exit_date"""
    raw     = conn.execute(sql).fetchall()
    systems = sorted(set(r["system"] for r in raw))
    date_pnl = defaultdict(lambda: defaultdict(float))
    for r in raw:
        date_pnl[r["exit_date"]][r["system"]] += r["daily_pnl"]
    cum = 0.0; cum_sys = defaultdict(float); rows = []
    for dt in sorted(date_pnl.keys()):
        day_total = sum(date_pnl[dt].values())
        cum += day_total
        row = {"exit_date": dt, "daily_pnl": round(day_total, 2),
               "cumulative_pnl": round(cum, 2)}
        for s in systems:
            cum_sys[s] += date_pnl[dt].get(s, 0.0)
            row[f"cum_{s}"] = round(cum_sys[s], 2)
        rows.append(row)
    write_csv(export_dir / "equity_curve.csv", rows,
        ["exit_date", "daily_pnl", "cumulative_pnl"] + [f"cum_{s}" for s in systems])


def export_r_distribution(conn, scope: str, export_dir: Path):
    sql = f"""SELECT realized_R FROM v_trade_summary
        WHERE {scope} AND realized_R IS NOT NULL AND status != 'open'"""
    r_values = [r["realized_R"] for r in conn.execute(sql).fetchall()]
    buckets  = [
        ("<-2R",       lambda r: r < -2),
        ("-2R to -1R", lambda r: -2 <= r < -1),
        ("-1R to 0R",  lambda r: -1 <= r < 0),
        ("0R scratch", lambda r: r == 0),
        ("0R to +1R",  lambda r: 0 < r <= 1),
        ("+1R to +2R", lambda r: 1 < r <= 2),
        ("+2R to +3R", lambda r: 2 < r <= 3),
        (">+3R",       lambda r: r > 3),
    ]
    rows = []
    for label, fn in buckets:
        vals = [r for r in r_values if fn(r)]
        rows.append({"bucket": label, "count": len(vals),
            "pct":   round(100.0 * len(vals) / len(r_values), 1) if r_values else 0,
            "avg_R": round(sum(vals) / len(vals), 2) if vals else 0})
    rows.append({"bucket": "TOTAL", "count": len(r_values), "pct": 100.0,
        "avg_R": round(sum(r_values) / len(r_values), 2) if r_values else 0})
    write_csv(export_dir / "r_distribution.csv", rows,
        ["bucket", "count", "pct", "avg_R"])


def export_monthly_summary(conn, scope: str, export_dir: Path):
    sql = f"""
        SELECT strftime('%Y-%m', last_exit_date) AS month,
            COUNT(*) AS trades_closed,
            SUM(CASE WHEN outcome='WIN'  THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN outcome='LOSS' THEN 1 ELSE 0 END) AS losses,
            ROUND(100.0*SUM(CASE WHEN outcome='WIN' THEN 1 ELSE 0 END)
                /NULLIF(SUM(CASE WHEN outcome IN ('WIN','LOSS') THEN 1 ELSE 0 END),0),1) AS win_rate_pct,
            ROUND(SUM(realized_pnl), 2) AS total_pnl,
            ROUND(AVG(realized_R), 2) AS avg_R,
            ROUND(AVG(max_hold_days), 1) AS avg_hold_days
        FROM v_trade_summary
        WHERE {scope} AND last_exit_date IS NOT NULL AND status != 'open'
        GROUP BY month ORDER BY month"""
    rows = [dict(r) for r in conn.execute(sql).fetchall()]
    write_csv(export_dir / "monthly_summary.csv", rows,
        ["month", "trades_closed", "wins", "losses", "win_rate_pct",
         "total_pnl", "avg_R", "avg_hold_days"])


def export_open_positions(export_dir: Path):
    """Pull live positions from Schwab API. Skipped for PAPER account."""
    if str(API_DIR) not in sys.path:
        sys.path.insert(0, str(API_DIR))
    try:
        from P_020_Schwab_Token_Manager import get_client
        client       = get_client()
        resp         = client.get_account_numbers()
        if resp.status_code != 200:
            log.error(f"get_account_numbers: {resp.status_code}"); return
        account_hash = next((e["hashValue"] for e in resp.json()
            if str(e.get("accountNumber", "")).endswith("6348")), None)
        if not account_hash:
            log.error("Account ...6348 not found"); return
        resp2 = client.get_account(account_hash, fields=client.Account.Fields.POSITIONS)
        if resp2.status_code != 200:
            log.error(f"get_account: {resp2.status_code}"); return
        skip = {"SNVXX", "SNSXX", "SWVXX"}
        rows = []
        for pos in resp2.json().get("securitiesAccount", {}).get("positions", []):
            inst = pos.get("instrument", {})
            sym  = (inst.get("symbol") or "").strip().upper()
            atype = inst.get("assetType", "").upper()
            if sym in skip or atype == "CASH_EQUIVALENT":
                continue
            qty = pos.get("longQuantity", 0.0) or -pos.get("shortQuantity", 0.0)
            rows.append({
                "as_of_date":    date.today().isoformat(),
                "symbol":        sym,
                "asset_type":    atype,
                "qty":           qty,
                "avg_price":     pos.get("averagePrice", 0.0),
                "market_value":  pos.get("marketValue", 0.0),
                "unrealized_pnl": (pos.get("longOpenProfitLoss")
                                   or pos.get("shortOpenProfitLoss") or 0.0),
                "day_pnl":       pos.get("currentDayProfitLoss", 0.0),
            })
        write_csv(export_dir / "open_positions.csv", rows,
            ["as_of_date", "symbol", "asset_type", "qty", "avg_price",
             "market_value", "unrealized_pnl", "day_pnl"])
    except Exception as e:
        log.error(f"open_positions failed: {e}")


def export_drawdown(conn, acct_filter: str, export_dir: Path):
    sql = f"""
        SELECT e.exit_date, SUM(e.exit_pnl) AS daily_pnl
        FROM exits e JOIN trades t ON t.trade_id = e.trade_id
        WHERE {acct_filter} AND e.exit_date IS NOT NULL
        GROUP BY e.exit_date ORDER BY e.exit_date"""
    raw = conn.execute(sql).fetchall()
    cum = 0.0; peak = 0.0; rows = []
    for r in raw:
        cum  += r["daily_pnl"]; peak = max(peak, cum)
        dd    = cum - peak
        rows.append({
            "exit_date":       r["exit_date"],
            "cumulative_pnl":  round(cum, 2),
            "peak_pnl":        round(peak, 2),
            "drawdown_dollar": round(dd, 2),
            "drawdown_pct":    round((dd / peak * 100) if peak > 0 else 0.0, 2),
        })
    write_csv(export_dir / "drawdown.csv", rows,
        ["exit_date", "cumulative_pnl", "peak_pnl", "drawdown_dollar", "drawdown_pct"])


# ── Main entry point (used by Trade Manager cmd_analyze) ──────────────────

def export_all_stats(account_id: str = "AJZ6348"):
    """Run all exports for the given account. Called by Trade Manager."""
    account_id  = (account_id or "AJZ6348").upper()
    scope       = _get_scope(account_id)
    acct_filter = _acct_filter(account_id)
    export_dir  = _get_export_dir(account_id)
    is_paper    = account_id == "PAPER"

    log.info(f"Account    : {account_id}")
    log.info(f"Scope      : {scope}")
    log.info(f"Export dir : {export_dir}")

    if not DB_PATH.exists():
        log.error(f"Database not found: {DB_PATH}")
        sys.exit(1)

    conn = get_conn()
    try:
        export_summary_by_system(conn, scope, export_dir)
        export_equity_curve(conn, acct_filter, export_dir)
        export_r_distribution(conn, scope, export_dir)
        export_monthly_summary(conn, scope, export_dir)
        export_drawdown(conn, acct_filter, export_dir)
    finally:
        conn.close()

    if is_paper:
        log.info("open_positions skipped — PAPER account has no Schwab API connection.")
    else:
        export_open_positions(export_dir)

    log.info(f"Export complete -> {export_dir}")


# ── CLI entry point ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="P_020 Stats Export")
    parser.add_argument("--account", default="AJZ6348",
                        help="Account ID: AJZ6348 (default) or PAPER")
    args = parser.parse_args()
    export_all_stats(account_id=args.account)


if __name__ == "__main__":
    main()
