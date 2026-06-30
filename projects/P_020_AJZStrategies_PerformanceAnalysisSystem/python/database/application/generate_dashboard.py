"""Generate P_020_Dashboard.html from ai_review export CSVs."""

import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from infrastructure.dashboard_html import build_html

EXPORTS = Path(__file__).resolve().parents[3] / "data" / "exports" / "ai_review"
OUT     = Path(__file__).resolve().parents[3] / "docs" / "P_020_Dashboard.html"

SYSTEM_ORDER = ["P_118", "P_115", "P_300", "P_117", "P_910", "SNT", "P_116"]


def read_csv(name):
    path = EXPORTS / name
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sort_systems(systems):
    order = {s: i for i, s in enumerate(SYSTEM_ORDER)}
    return sorted(
        [s for s in systems if s["system"] in order],
        key=lambda s: order[s["system"]]
    )


def compute_kpis(systems, equity, monthly):
    active = [s for s in systems]

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

    best = max(active, key=lambda s: float(s["total_pnl"]))
    worst = min(active, key=lambda s: float(s["total_pnl"]))

    # Monthly sub-line (last 3 months)
    recent = monthly[-3:] if len(monthly) >= 3 else monthly
    month_sub = "  ".join(
        f"{r['month'][5:]} {'▲' if float(r['total_pnl']) >= 0 else '▼'}"
        f"${abs(float(r['total_pnl'])):,.0f}"
        for r in recent
    )

    open_total = sum(int(s["open_trades"]) for s in active)

    return {
        "net_pnl"    : net_pnl,
        "wins"       : wins,
        "losses"     : losses,
        "closed"     : closed,
        "open_total" : open_total,
        "win_rate"   : win_rate,
        "expectancy" : expectancy,
        "best"       : best,
        "worst"      : worst,
        "month_sub"  : month_sub,
        "as_of"      : datetime.now().strftime("%b %d, %Y").upper(),
    }


def main():
    print("Loading CSVs...", flush=True)
    raw_systems = read_csv("summary_by_system.csv")
    equity      = read_csv("equity_curve.csv")
    monthly     = read_csv("monthly_summary.csv")

    data = {
        "systems" : sort_systems(raw_systems),
        "monthly" : monthly,
        "equity"  : equity,
        "drawdown": read_csv("drawdown.csv"),
        "r_dist"  : [r for r in read_csv("r_distribution.csv") if r["bucket"] != "TOTAL"],
        "open_pos": read_csv("open_positions.csv"),
    }
    data["kpis"] = compute_kpis(data["systems"], equity, monthly)

    print("Building dashboard...", flush=True)
    html = build_html(data)
    OUT.write_text(html, encoding="utf-8")
    print(f"Written: {OUT.name}", flush=True)
    print(f"As of  : {data['kpis']['as_of']}", flush=True)
    print(f"Closed : {data['kpis']['closed']} trades  |  Open: {data['kpis']['open_total']}", flush=True)


if __name__ == "__main__":
    main()
