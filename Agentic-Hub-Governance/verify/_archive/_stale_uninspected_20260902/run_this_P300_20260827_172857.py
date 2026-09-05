"""
run_this_P300_20260827_172857.py
WO-P300-E5.006 -- inspect the two files Tony just dropped
(data\bulk\mine\10_Pattern_SPY.xlsx / 10_Pattern_QQQ.xlsx) before
building step 3's actual measurement script. Confirms column names and
date coverage match what's needed (Date, Close Price, Medium Term
Difference, Long Term Difference, daily density, 2021-08-10-present)
rather than assuming the P_300 bulk-ingest naming convention implies a
particular column layout.

Read-only. Does not modify these files or any production DB.
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

FILES = {
    "SPY": Path(
        r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
        r"\data\bulk\mine\10_Pattern_SPY.xlsx"
    ),
    "QQQ": Path(
        r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
        r"\data\bulk\mine\10_Pattern_QQQ.xlsx"
    ),
}

SCRIPT_PATH = Path(__file__).resolve()
DONE_PATH = SCRIPT_PATH.with_suffix(SCRIPT_PATH.suffix + ".done")


def write_done(status, exit_code):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    DONE_PATH.write_text(f"{ts}\n{status}\nexit_code={exit_code}\n", encoding="utf-8")


def main():
    any_fail = False

    for ticker, path in FILES.items():
        print("=" * 60)
        print(f"{ticker}: {path}")
        if not path.exists():
            print(f"FAIL: file not found")
            any_fail = True
            continue

        try:
            xls = pd.ExcelFile(path)
        except Exception as e:
            print(f"FAIL: could not open as Excel: {e}")
            any_fail = True
            continue

        print(f"Sheet names: {xls.sheet_names}")

        df = pd.read_excel(path, sheet_name=xls.sheet_names[0])
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"First 3 rows:\n{df.head(3)}")
        print(f"Last 3 rows:\n{df.tail(3)}")

        # Try to identify a date-like column
        date_col = None
        for c in df.columns:
            if str(c).strip().lower() == "date":
                date_col = c
                break
        if date_col is not None:
            dates = pd.to_datetime(df[date_col], errors="coerce")
            print(f"Date column found: '{date_col}'")
            print(f"Date range: {dates.min()} to {dates.max()}")
            print(f"Row count: {len(df)}, distinct dates: {dates.nunique()}")
        else:
            print("No column literally named 'Date' found -- columns list above, "
                  "need to identify the real date column manually.")

    print()
    if any_fail:
        print("FAIL: see above")
        write_done("FAIL", 1)
        sys.exit(1)

    print("PASS")
    write_done("PASS", 0)


if __name__ == "__main__":
    main()
