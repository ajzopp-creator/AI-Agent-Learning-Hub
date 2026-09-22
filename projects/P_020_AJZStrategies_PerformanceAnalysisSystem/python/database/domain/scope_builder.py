"""Trade-query scope builders + export-path resolution (WO-P020-E1.020).

Pure logic -- no file reads/writes, no network, no DB access. Builds the
SQL WHERE-clause fragments stats_export.py needs (two shapes: bare-column
queries against v_trade_summary, and JOINed t.-aliased queries against
trades/exits), plus the account-derived output paths stats_export.py and
generate_dashboard.py both need so the two stop duplicating this logic.

Callers resolve the default start date from config.py themselves (this
module never imports config) and pass an explicit start_date in -- that
keeps the account/date decision in the application layer where it belongs.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\domain\\scope_builder.py
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_date(date_str: str) -> None:
    """Raise ValueError if date_str isn't a plain YYYY-MM-DD string."""
    if not _DATE_RE.match(date_str):
        raise ValueError(
            f"Invalid start date {date_str!r} -- expected YYYY-MM-DD"
        )


def get_scope(account_id: str, start_date: str = None) -> str:
    """WHERE clause for queries against v_trade_summary (bare columns)."""
    if account_id.upper() == "PAPER":
        clause = "account_id = 'PAPER'"
    else:
        clause = "account_id LIKE '%6348%'"
    if start_date:
        clause += f" AND open_date >= '{start_date}'"
    return clause


def get_acct_filter(account_id: str, start_date: str = None) -> str:
    """WHERE clause for JOINed queries (t. alias) against trades/exits."""
    if account_id.upper() == "PAPER":
        clause = "t.account_id = 'PAPER'"
    else:
        clause = "t.account_id LIKE '%6348%'"
    if start_date:
        clause += f" AND t.open_date >= '{start_date}'"
    return clause


def get_export_dir(account_id: str) -> Path:
    """Directory stats_export.py writes CSVs into for this account."""
    if account_id.upper() == "PAPER":
        return PROJECT_ROOT / "data" / "exports" / "paper_ai_review"
    return PROJECT_ROOT / "data" / "exports" / "ai_review"


def get_dashboard_output_path(account_id: str, start_date: str = None) -> Path:
    """HTML file generate_dashboard.py writes for this account.

    start_date, when given, is folded into the filename (e.g.
    P_020_Dashboard_Since_2026-06-01.html) so a custom-scoped run doesn't
    overwrite the account's default-scope dashboard file. The caller is
    responsible for passing None when start_date equals that account's
    own default (WO-P020-E1.021 follow-up) -- collapsing that case back
    to the plain, unsuffixed filename keeps the original bookmark/path
    stable for the common no-flag run.
    """
    base = "P_020_Dashboard_Paper" if account_id.upper() == "PAPER" else "P_020_Dashboard"
    if start_date:
        return PROJECT_ROOT / "docs" / f"{base}_Since_{start_date}.html"
    return PROJECT_ROOT / "docs" / f"{base}.html"
