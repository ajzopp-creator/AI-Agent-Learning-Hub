"""Generate P_020_Dashboard.html from ai_review export CSVs.

Account-aware since WO-P020-E1.020: --account selects AJZ6348 (default,
writes docs/P_020_Dashboard.html) or PAPER (writes
docs/P_020_Dashboard_Paper.html). --start-date re-runs the analyze step
for that account before building, so the dashboard always matches the
CSVs it reads. open_positions.csv is optional -- not produced for PAPER.

Filename per start_date (WO-P020-E1.021 follow-up): a --start-date that
matches the account's own config.py default writes the plain filename
above, same as before. Any OTHER start_date gets its own file --
docs/P_020_Dashboard_Since_<date>.html (or _Paper_Since_<date> for
PAPER) -- so a custom-scoped run never clobbers the default-scope
dashboard, and multiple scoped views can coexist on disk at once.
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import PAPER_ANALYSIS_START_DATE, LIVE_ANALYSIS_START_DATE
from domain.scope_builder import get_export_dir, get_dashboard_output_path, validate_date
from infrastructure.dashboard_html import build_html
from infrastructure.systems_registry import get_system_display_order

SYSTEM_ORDER = get_system_display_order()


def read_csv(path):
    """Return rows from path, or [] if it doesn't exist (PAPER has no open_positions.csv)."""
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sort_systems(systems):
    order = {s: i for i, s in enumerate(SYSTEM_ORDER)}
    return sorted(
        [s for s in systems if s["system"] in order],
        key=lambda s: order[s["system"]]
    )


def _period_labels(account_id: str, start_date: str):
    """Return (account_label, period_badge, scope_span) header/footer/span text."""
    account_label = "PAPER ACCOUNT" if account_id == "PAPER" else "ACCOUNT ...6348"
    dt = datetime.strptime(start_date, "%Y-%m-%d")
    if dt.month == 1 and dt.day == 1:
        period_badge = f"YTD {dt.year}"
    else:
        period_badge = f"SINCE {dt.strftime('%b %Y').upper()}"
    scope_span = dt.strftime("%b %Y").upper()
    return account_label, period_badge, scope_span


def compute_kpis(systems, equity, monthly, account_id, start_date):
    active = list(systems)

    net_pnl  = float(equity[-1]["cumulative_pnl"]) if equity else 0.0
    wins     = sum(int(s["wins"])   for s in active)
    losses   = sum(int(s["losses"]) for s in active)
    closed   = wins + losses
    win_rate = (wins / closed * 100) if closed else 0.0

    total_r  = sum(
        float(s["avg_R"]) * (int(s["wins"]) + int(s["losses"]))
        for s in active
    )
    expectancy = total_r / closed if closed else 0.0

    best  = max(active, key=lambda s: float(s["total_pnl"]), default=None)
    worst = min(active, key=lambda s: float(s["total_pnl"]), default=None)

    recent = monthly[-3:] if len(monthly) >= 3 else monthly
    month_sub = ("  ".join(
        f"{r['month'][5:]} {'▲' if float(r['total_pnl']) >= 0 else '▼'}"
        f"${abs(float(r['total_pnl'])):,.0f}"
        for r in recent
    ) if recent else "No closed trades in range")

    open_total = sum(int(s["open_trades"]) for s in active)
    account_label, period_badge, scope_span = _period_labels(account_id, start_date)

    return {
        "net_pnl"      : net_pnl,
        "wins"         : wins,
        "losses"       : losses,
        "closed"       : closed,
        "open_total"   : open_total,
        "win_rate"     : win_rate,
        "expectancy"   : expectancy,
        "best"         : best,
        "worst"        : worst,
        "month_sub"    : month_sub,
        "as_of"        : datetime.now().strftime("%b %d, %Y").upper(),
        "account_label": account_label,
        "period_badge" : period_badge,
        "scope_span"   : scope_span,
    }


def build_dashboard(account_id: str = "AJZ6348", start_date: str = None, run_analyze: bool = True):
    """Build the HTML dashboard for account_id. Returns the output Path.

    run_analyze=True (default) re-runs stats_export.export_all_stats first
    so the CSVs match start_date. Pass False to build from whatever CSVs
    are already on disk.
    """
    account_id = (account_id or "AJZ6348").upper()
    default_start = PAPER_ANALYSIS_START_DATE if account_id == "PAPER" else LIVE_ANALYSIS_START_DATE
    if start_date:
        validate_date(start_date)
    else:
        start_date = default_start

    if run_analyze:
        from application.stats_export import export_all_stats
        export_all_stats(account_id=account_id, start_date=start_date)

    exports = get_export_dir(account_id)
    # Custom scope gets its own file (WO-P020-E1.021 follow-up); the
    # account's own default scope keeps the plain, unsuffixed filename.
    out = get_dashboard_output_path(
        account_id, start_date if start_date != default_start else None
    )

    print("Loading CSVs...", flush=True)
    raw_systems = read_csv(exports / "summary_by_system.csv")
    equity      = read_csv(exports / "equity_curve.csv")
    monthly     = read_csv(exports / "monthly_summary.csv")

    data = {
        "systems" : sort_systems(raw_systems),
        "monthly" : monthly,
        "equity"  : equity,
        "drawdown": read_csv(exports / "drawdown.csv"),
        "r_dist"  : [r for r in read_csv(exports / "r_distribution.csv") if r["bucket"] != "TOTAL"],
        "open_pos": read_csv(exports / "open_positions.csv"),
    }
    data["kpis"] = compute_kpis(raw_systems, equity, monthly, account_id, start_date)

    print("Building dashboard...", flush=True)
    html = build_html(data)
    out.write_text(html, encoding="utf-8")
    print(f"Written: {out.name}", flush=True)
    print(f"As of  : {data['kpis']['as_of']}", flush=True)
    print(f"Closed : {data['kpis']['closed']} trades  |  Open: {data['kpis']['open_total']}", flush=True)
    return out


def main():
    parser = argparse.ArgumentParser(description="P_020 Dashboard Generator")
    parser.add_argument("--account", default="AJZ6348",
                        help="Account ID: AJZ6348 (default) or PAPER")
    parser.add_argument("--start-date", default=None,
                        help="Override start date YYYY-MM-DD (default: config.py per-account value)")
    parser.add_argument("--no-analyze", action="store_true",
                        help="Skip re-running analyze; build from CSVs already on disk")
    args = parser.parse_args()
    try:
        build_dashboard(account_id=args.account, start_date=args.start_date,
                         run_analyze=not args.no_analyze)
    except ValueError as e:
        print(f"ERROR: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
