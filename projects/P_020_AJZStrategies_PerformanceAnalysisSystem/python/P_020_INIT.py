"""
P_020_INIT.py
Session initialization diagnostic for P_020 AJZ Strategies.
Reads market posture, DB status, and account balance in one pass.
Prints formatted INIT block to stdout.
"""

import json
import sqlite3
from datetime import date
from pathlib import Path

# --- Paths ---
HUB = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
PROJECT = HUB / "projects" / "P_020_AJZStrategies_PerformanceAnalysisSystem"
RISK_CONFIG = HUB / "projects" / "P_010_Current_Market_Posture" / "P_010_RiskConfig.json"
LAST_RUN = PROJECT / "data" / "api_pulls" / "P_020_last_run.json"
DB_PATH = PROJECT / "data" / "database" / "P_020_trades.db"
BALANCE_BASELINE = 35_000.0
BALANCE_WARN_HIGH = 38_500.0
BALANCE_WARN_LOW = 31_500.0
STALE_DAYS = 14

# --- Mode hierarchy for MIN() logic ---
MODE_RANK = {"OFF": 0, "REDUCED": 1, "HALF": 2, "NONE": 3, "FULL": 4}
RANK_MODE = {v: k for k, v in MODE_RANK.items()}


def fmt_dollars(val) -> str:
    """Format a numeric value as dollars, or return N/A if None."""
    if val is None:
        return "N/A"
    return f"${val:,.0f}"


def read_market_posture() -> str:
    try:
        data = json.loads(RISK_CONFIG.read_text())
        spy = data.get("spy_posture", 0.0)
        qqq = data.get("qqq_posture", 0.0)
        avg = data.get("avg_posture", 0.0)
        risk_mode = data.get("risk_mode", "FULL")
        intraday = data.get("intraday_adjustment", None)

        rm_rank = MODE_RANK.get(risk_mode, 4)
        ia_rank = MODE_RANK.get(intraday, 4) if intraday else 4
        final_rank = min(rm_rank, ia_rank)
        final_mode = RANK_MODE[final_rank]

        if final_mode in ("OFF", "REDUCED") or avg < 0:
            posture_icon = "CORR"
        elif avg >= 1.08 and final_mode == "FULL":
            posture_icon = "HOT"
        else:
            posture_icon = "STD"

        intraday_str = intraday if intraday else "NONE"
        return (
            f"SPY{spy:+.2f}% QQQ{qqq:+.2f}% Avg{avg:+.2f}% | "
            f"Morning:{risk_mode} Intraday:{intraday_str} Final:{final_mode} | "
            f"[{posture_icon}]"
        )
    except Exception as e:
        return f"MARKET READ FAILED: {e}"


def read_last_run() -> str:
    try:
        data = json.loads(LAST_RUN.read_text())
        return data.get("last_run_date", "UNKNOWN")
    except Exception as e:
        return f"UNKNOWN ({e})"


def read_db_status() -> tuple[str, str, str]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM trades "
            "WHERE account_id LIKE '%6348%' AND strftime('%Y', open_date) >= '2026'"
        )
        total = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM trades "
            "WHERE account_id LIKE '%6348%' AND status = 'open'"
        )
        open_count = cur.fetchone()[0]
        cur.execute(
            "SELECT MAX(open_date) FROM trades "
            "WHERE account_id LIKE '%6348%' AND strftime('%Y', open_date) >= '2026'"
        )
        latest = cur.fetchone()[0] or "NONE"
        conn.close()
        return str(total), str(open_count), latest
    except Exception as e:
        return f"ERR({e})", "ERR", "ERR"


def read_balance() -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "SELECT snapshot_date, total_value, cash_available, buying_power "
            "FROM account_balances "
            "WHERE account_id LIKE '%6348%' "
            "ORDER BY snapshot_date DESC LIMIT 1"
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return "NO BALANCE DATA"
        snap_date, total, cash, bp = row
        flags = []
        if total is not None and (total >= BALANCE_WARN_HIGH or total <= BALANCE_WARN_LOW):
            pct = ((total - BALANCE_BASELINE) / BALANCE_BASELINE) * 100
            flags.append(f"THRESHOLD {pct:+.1f}% from baseline")
        try:
            days_old = (date.today() - date.fromisoformat(snap_date)).days
            if days_old > STALE_DAYS:
                flags.append(f"STALE {days_old}d")
        except Exception:
            flags.append("DATE_PARSE_ERR")
        flag_str = "  ** " + " | ".join(flags) if flags else ""
        return (
            f"Balance:{fmt_dollars(total)} Cash:{fmt_dollars(cash)} "
            f"BuyPow:{fmt_dollars(bp)} AsOf:{snap_date}{flag_str}"
        )
    except Exception as e:
        return f"BALANCE READ FAILED: {e}"


def main() -> None:
    market = read_market_posture()
    last_run = read_last_run()
    total, open_count, latest = read_db_status()
    balance = read_balance()
    tags = "WHY=BTD|OIL|EXT|EZB|VPT|SNT|DAY|ASYM|IFFY|LEARN|CROWDED|FOMO|REVENGE  SIG=A|B|C|X"

    print("=== P_020 v2.9 ===")
    print(f"MARKET:  {market}")
    print(f"DB:      LastRun:{last_run} Trades:{total} Open:{open_count} Latest:{latest}")
    print(f"ACCOUNT: {balance}")
    print(f"TAGS:    {tags}")
    print("==================")


if __name__ == "__main__":
    main()
