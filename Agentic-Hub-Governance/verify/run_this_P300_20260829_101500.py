"""
FILE: run_this_P300_20260829_101500.py
VERSION: 1.0
DATE: 2026-08-29
AUTHOR: Anthony Zoppi + Claude
LAYER: verify (PEH handoff, read-only, self-contained)
DESCRIPTION:
    WO-P300-E5.006 step 3. Market-regime stratification of BUY win rate.
    Posture is VP-RECONSTRUCTED from the SPY/QQQ 10-year grids (P_010
    keeps no history). Buckets, bar, and floor are pre-registered in the
    sibling _context.txt -- do not change them here.
"""
from __future__ import annotations

import csv
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
OUT_CSV = Path(__file__).with_name("posture_strat_20260829_101500.csv")
SPREAD_BAR_PP = 5.0
MIN_N = 30
BUCKET_ORDER = ["OFF", "HALF", "FULL"]


def load_avg_posture() -> dict[date, float]:
    """avg_posture per date, P_010 formula, exact-date join of SPY+QQQ."""
    per_sym: dict[str, dict[date, float]] = {}
    for sym, path in GRIDS.items():
        parse = parse_bulk_file(path)
        per_sym[sym] = {b.bar_date: (b.mtdiff + b.ltdiff) / 2.0
                        for b in parse.bars}
        print(f"{sym}: {len(parse.bars)} bars "
              f"{parse.bars[0].bar_date} -> {parse.bars[-1].bar_date}")
    common = set(per_sym["SPY"]) & set(per_sym["QQQ"])
    return {d: (per_sym["SPY"][d] + per_sym["QQQ"][d]) / 2.0 for d in common}


def load_chosen_rows() -> list[dict]:
    """One row per pattern: the is_chosen_horizon=True line of the report."""
    rows: list[dict] = []
    with REPORT.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["is_chosen_horizon"] != "True":
                continue
            rows.append({
                "pid": int(r["pattern_instance_id"]),
                "symbol": r["symbol"],
                "anchor_date": datetime.strptime(
                    r["anchor_date"], "%Y-%m-%d").date(),
                "signal": r["final_signal_class"],
                "horizon": int(r["chosen_horizon"]),
                "profitable": (None if r["actual_is_profitable"] == ""
                               else r["actual_is_profitable"] == "True"),
            })
    print(f"report: {len(rows)} chosen-horizon rows")
    return rows


def bucket_of(avg_posture: float) -> str:
    """P_010 determine_risk_mode cuts -- pre-registered, do not edit."""
    if avg_posture >= 1.0:
        return "FULL"
    if avg_posture >= 0.0:
        return "HALF"
    return "OFF"


def tag_rows(rows: list[dict], posture: dict[date, float]) -> tuple[list[dict], int]:
    tagged: list[dict] = []
    unmatched = 0
    for r in rows:
        p = posture.get(r["anchor_date"])
        if p is None or r["profitable"] is None:
            unmatched += 1
            continue
        tagged.append({**r, "avg_posture": p, "bucket": bucket_of(p)})
    print(f"joined: {len(tagged)} patterns, excluded {unmatched} "
          f"(no posture date match or no realized outcome)")
    return tagged, unmatched


def win_table(tagged: list[dict], signal: str | None) -> dict[str, tuple[int, int]]:
    """bucket -> (n, wins) for one signal class (None = all classes)."""
    acc: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for r in tagged:
        if signal is not None and r["signal"] != signal:
            continue
        acc[r["bucket"]][0] += 1
        acc[r["bucket"]][1] += int(r["profitable"])
    return {b: (v[0], v[1]) for b, v in acc.items()}


def quartile_view(tagged: list[dict]) -> None:
    """Informational only -- does not feed the decision."""
    buys = sorted((r["avg_posture"], r["profitable"])
                  for r in tagged if r["signal"] == "BUY")
    if len(buys) < 4:
        return
    q = len(buys) // 4
    print("  BUY by posture quartile (informational):")
    for i in range(4):
        chunk = buys[i * q:(i + 1) * q] if i < 3 else buys[3 * q:]
        n = len(chunk)
        wr = sum(int(p) for _, p in chunk) / n * 100.0
        print(f"    Q{i + 1} posture {chunk[0][0]:+.3f}..{chunk[-1][0]:+.3f}"
              f"  n={n:5d}  win={wr:5.1f}%")


def report_and_verdict(tagged: list[dict]) -> list[str]:
    lines: list[str] = []
    for label, sig in (("BUY", "BUY"), ("WATCH", "WATCH"), ("ALL", None)):
        tbl = win_table(tagged, sig)
        print(f"  {label}:")
        for b in BUCKET_ORDER:
            n, w = tbl.get(b, (0, 0))
            wr = (w / n * 100.0) if n else 0.0
            flag = "" if n >= MIN_N else "  (n<30, excluded)"
            print(f"    {b:5s} n={n:6d}  wins={w:6d}  win={wr:5.1f}%{flag}")
            lines.append(f"{label},{b},{n},{w},{wr:.2f}")
    buy = win_table(tagged, "BUY")
    rates = [w / n * 100.0 for b, (n, w) in buy.items() if n >= MIN_N]
    spread = (max(rates) - min(rates)) if len(rates) >= 2 else float("nan")
    print(f"  BUY spread across primary buckets (n>={MIN_N}): {spread:.2f}pp "
          f"vs bar {SPREAD_BAR_PP:.1f}pp")
    if spread != spread:
        print("  VERDICT: INDETERMINATE -- fewer than 2 buckets clear n>=30")
    elif spread < SPREAD_BAR_PP:
        print("  VERDICT: UNDER BAR -- no usable regime signal; recommend close")
    else:
        print("  VERDICT: OVER BAR -- bring to Tony before any code")
    lines.append(f"SPREAD_PP,BUY,,,{spread:.2f}")
    return lines


def _write_done(status: str, code: int) -> None:
    Path(__file__).with_suffix(".py.done").write_text(
        f"timestamp: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"status: {status}\nexit_code: {code}\n", encoding="utf-8")


def main() -> int:
    posture = load_avg_posture()
    print(f"posture dates (SPY&QQQ common): {len(posture)}")
    rows = load_chosen_rows()
    if len(rows) != 44399:
        print(f"FAIL: expected 44399 chosen rows, got {len(rows)}")
        _write_done("FAIL", 1)
        return 1
    tagged, _ = tag_rows(rows, posture)
    lines = report_and_verdict(tagged)
    quartile_view(tagged)
    OUT_CSV.write_text("signal,bucket,n,wins,win_pct\n" + "\n".join(lines)
                       + "\n", encoding="utf-8")
    print(f"csv: {OUT_CSV}")
    print("PASS")
    _write_done("PASS", 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
