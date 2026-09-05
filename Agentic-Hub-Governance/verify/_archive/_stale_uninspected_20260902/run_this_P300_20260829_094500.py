"""
FILE: run_this_P300_20260829_094500.py
VERSION: 1.0
DATE: 2026-08-29
AUTHOR: Anthony Zoppi + Claude
LAYER: verify (PEH handoff, read-only, self-contained)
DESCRIPTION:
    WO-P300-E5.006 step 3 pre-check. Verifies the re-exported SPY/QQQ
    10-year VP History Grid files in data/reference/ have the columns
    and date coverage the posture reconstruction needs. Reads only;
    writes nothing except its own .done marker.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

REF_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_300_Vantage_Point_Pattern_Recognition\data\reference"
)
FILES = {"SPY": REF_DIR / "10_Pattern_SPY.xlsx",
         "QQQ": REF_DIR / "10_Pattern_QQQ.xlsx"}
REQUIRED = ["Date", "Close Price",
            "Medium Term Difference", "Long Term Difference"]
MIN_ROWS = 1250
EARLIEST_ANCHOR = pd.Timestamp("2021-08-10")


def _norm(col: object) -> str:
    return re.sub(r"\s+", " ", str(col)).strip()


def _check_one(sym: str, path: Path) -> list[str]:
    problems: list[str] = []
    if not path.exists():
        return [f"{sym}: file missing {path}"]
    df = pd.read_excel(path)
    df.columns = [_norm(c) for c in df.columns]
    print(f"{sym}: rows={len(df)} cols={len(df.columns)}")
    print(f"{sym}: columns={list(df.columns)}")
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        return problems + [f"{sym}: missing columns {missing}"]
    # VP History Grid: first data row is a sub-header (PSI/ROC%/NeuralX),
    # not a bar. Drop it; do not treat it as a null in the required columns.
    df = df.dropna(subset=["Date"]).reset_index(drop=True)
    print(f"{sym}: bars={len(df)} (sub-header dropped)")
    dates = pd.to_datetime(df["Date"], errors="coerce")
    print(f"{sym}: first={dates.min().date()} last={dates.max().date()}")
    nulls = {c: int(df[c].isna().sum()) for c in REQUIRED}
    nulls["Date(parsed)"] = int(dates.isna().sum())
    print(f"{sym}: nulls={nulls}")
    if len(df) < MIN_ROWS:
        problems.append(f"{sym}: only {len(df)} rows (< {MIN_ROWS})")
    if dates.min() > EARLIEST_ANCHOR:
        problems.append(f"{sym}: first date {dates.min().date()} "
                        f"is after {EARLIEST_ANCHOR.date()}")
    if any(v > 0 for v in nulls.values()):
        problems.append(f"{sym}: nulls present {nulls}")
    return problems


def _write_done(status: str, code: int) -> None:
    marker = Path(__file__).with_suffix(".py.done")
    marker.write_text(
        f"timestamp: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"status: {status}\nexit_code: {code}\n", encoding="utf-8",
    )


def main() -> int:
    problems: list[str] = []
    for sym, path in FILES.items():
        problems.extend(_check_one(sym, path))
    if problems:
        for p in problems:
            print("FAIL:", p)
        _write_done("FAIL", 1)
        return 1
    print("PASS")
    _write_done("PASS", 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
