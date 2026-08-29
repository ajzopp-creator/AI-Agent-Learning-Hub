"""
FILE: run_this_P300_20260829_103000.py
VERSION: 1.0
DATE: 2026-08-29
AUTHOR: Anthony Zoppi + Claude
LAYER: verify (PEH handoff, read-only, self-contained)
DESCRIPTION:
    WO-P300-E5.006 step 4. Repeatability (by calendar year) and return
    magnitude check on step 3's regime stratification. Same sources and
    join as step 3. return_pct is a decimal fraction -- x100 at display
    only (M-020). Informational; no decision bar.
"""
from __future__ import annotations

import csv
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

PROJECT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_300_Vantage_Point_Pattern_Recognition"
)
sys.path.insert(0, str(PROJECT / "python"))

from infrastructure.bulk_grid_reader import parse_bulk_file  # noqa: E402

REPORT = (PROJECT / "outputs" / "reports" / "eval"
          / "walkforward_staging_ingest_mined_default_20260826_130212.txt")
GRIDS = {"SPY": PROJECT / "data" / "reference" / "10_Pattern_SPY.xlsx",
         "QQQ": PROJECT / "data" / "reference" / "10_Pattern_QQQ.xlsx"}
HERE = Path(__file__).parent
CSV_YEARLY = HERE / "step4_yearly_20260829_103000.csv"
CSV_MAG = HERE / "step4_magnitude_20260829_103000.csv"
MIN_N = 30
BUCKETS = ["OFF", "HALF", "FULL"]


def load_avg_posture() -> dict[date, float]:
    per_sym: dict[str, dict[date, float]] = {}
    for sym, path in GRIDS.items():
        parse = parse_bulk_file(path)
        per_sym[sym] = {b.bar_date: (b.mtdiff + b.ltdiff) / 2.0
                        for b in parse.bars}
    common = set(per_sym["SPY"]) & set(per_sym["QQQ"])
    return {d: (per_sym["SPY"][d] + per_sym["QQQ"][d]) / 2.0 for d in common}


def bucket_of(avg_posture: float) -> str:
    if avg_posture >= 1.0:
        return "FULL"
    if avg_posture >= 0.0:
        return "HALF"
    return "OFF"


def load_tagged(posture: dict[date, float]) -> list[dict]:
    """One dict per pattern with signal, year, bucket, ret (fraction)."""
    out: list[dict] = []
    with REPORT.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["is_chosen_horizon"] != "True" or r["actual_return_pct"] == "":
                continue
            d = datetime.strptime(r["anchor_date"], "%Y-%m-%d").date()
            p = posture.get(d)
            if p is None:
                continue
            out.append({"signal": r["final_signal_class"], "year": d.year,
                        "bucket": bucket_of(p),
                        "ret": float(r["actual_return_pct"]),
                        "win": r["actual_is_profitable"] == "True"})
    print(f"joined: {len(out)} patterns with realized outcome + posture")
    return out


def _win_pct(rows: list[dict]) -> float:
    return sum(r["win"] for r in rows) / len(rows) * 100.0 if rows else 0.0


def yearly_tables(tagged: list[dict]) -> list[str]:
    """BUY win% and BUY lift over ALL, by year x bucket."""
    by = defaultdict(list)
    for r in tagged:
        by[(r["year"], r["bucket"])].append(r)
    years = sorted({r["year"] for r in tagged})
    lines: list[str] = []
    print("  BUY win% by year x regime  [n]   (lift = BUY% - ALL% same cell)")
    print("  year   " + "".join(f"{b:>22s}" for b in BUCKETS))
    for y in years:
        cells = []
        for b in BUCKETS:
            rows = by.get((y, b), [])
            buys = [r for r in rows if r["signal"] == "BUY"]
            if len(buys) < MIN_N:
                cells.append(f"{'n<30':>10s} [{len(buys):5d}]")
                lines.append(f"{y},{b},{len(buys)},,,")
                continue
            wp, ap = _win_pct(buys), _win_pct(rows)
            cells.append(f"{wp:5.1f}% {wp - ap:+5.1f} [{len(buys):5d}]")
            lines.append(f"{y},{b},{len(buys)},{wp:.2f},{ap:.2f},{wp - ap:.2f}")
        print(f"  {y}   " + "".join(f"{c:>22s}" for c in cells))
    return lines


def _pct(vals: list[float], q: float) -> float:
    s = sorted(vals)
    k = max(0, min(len(s) - 1, int(round(q * (len(s) - 1)))))
    return s[k]


def magnitude_row(label: str, b: str, rows: list[dict]) -> str:
    rets = [r["ret"] * 100.0 for r in rows]
    wins = [x for x in rets if x > 0]
    losses = [x for x in rets if x <= 0]
    n = len(rets)
    if n == 0:
        print(f"    {b:5s} n=0")
        return f"{label},{b},0,,,,,,,"
    wp = len(wins) / n * 100.0
    aw = statistics.mean(wins) if wins else 0.0
    al = statistics.mean(losses) if losses else 0.0
    exp = wp / 100.0 * aw + (1 - wp / 100.0) * al
    mean, med = statistics.mean(rets), statistics.median(rets)
    p10, p90 = _pct(rets, 0.10), _pct(rets, 0.90)
    print(f"    {b:5s} n={n:6d} win={wp:5.1f}% mean={mean:+6.2f}% "
          f"med={med:+6.2f}% p10={p10:+6.2f}% p90={p90:+6.2f}% "
          f"avgW={aw:+5.2f}% avgL={al:+5.2f}% expct={exp:+5.2f}%")
    return (f"{label},{b},{n},{wp:.2f},{mean:.3f},{med:.3f},{p10:.3f},"
            f"{p90:.3f},{aw:.3f},{al:.3f},{exp:.3f}")


def magnitude_tables(tagged: list[dict]) -> list[str]:
    lines: list[str] = []
    for label, sig in (("BUY", "BUY"), ("WATCH", "WATCH"), ("ALL", None)):
        print(f"  {label} return magnitude by regime (percent, x100 at display):")
        for b in BUCKETS:
            rows = [r for r in tagged if r["bucket"] == b
                    and (sig is None or r["signal"] == sig)]
            lines.append(magnitude_row(label, b, rows))
    return lines


def _write_done(status: str, code: int) -> None:
    Path(__file__).with_suffix(".py.done").write_text(
        f"timestamp: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"status: {status}\nexit_code: {code}\n", encoding="utf-8")


def main() -> int:
    tagged = load_tagged(load_avg_posture())
    if len(tagged) != 44399:
        print(f"FAIL: expected 44399 joined patterns, got {len(tagged)}")
        _write_done("FAIL", 1)
        return 1
    yl = yearly_tables(tagged)
    ml = magnitude_tables(tagged)
    CSV_YEARLY.write_text(
        "year,bucket,n_buy,buy_win_pct,all_win_pct,lift_pp\n"
        + "\n".join(yl) + "\n", encoding="utf-8")
    CSV_MAG.write_text(
        "signal,bucket,n,win_pct,mean_pct,median_pct,p10_pct,p90_pct,"
        "avg_win_pct,avg_loss_pct,expectancy_pct\n"
        + "\n".join(ml) + "\n", encoding="utf-8")
    print(f"csv: {CSV_YEARLY}")
    print(f"csv: {CSV_MAG}")
    print("PASS")
    _write_done("PASS", 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
