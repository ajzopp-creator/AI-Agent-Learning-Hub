"""run_this_P118_20260914_111254.py -- emit EHC (BUY) + GCT (ASYM) signals via P_115 cli.py.

Task: emit SIGNAL_V2 packets for EHC and GCT. Batch header was "P_118 STEPS 1" with
no new header before these two entries, so SignalSource=P_118 for both per the
2026-08-21 lesson (batch header governs, not the chart indicator shown).

Verification: check the known output path directly (Test-Path equivalent), per the
2026-09-14 lesson -- never parse cli.py's stdout for a bare path.
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DONE_PATH = Path(__file__).with_suffix(".py.done")
SIGNALS_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\signals"
)

TICKERS = [
    {
        "symbol": "EHC",
        "expected": SIGNALS_DIR / "2026-09-14_EHC_v2.0.json",
        "args": [
            "--symbol", "EHC",
            "--session-date", "2026-09-14",
            "--timestamp", "2026-09-14T11:12:54Z",
            "--strategy", "breakout",
            "--entry", "124.35",
            "--stop", "118.74",
            "--target", "155.70",
            "--horizon", "10-15 trading days",
            "--confidence", "HIGH",
            "--close", "123.18",
            "--volume", "11467",
            "--rationale",
            "P_118 batch (SignalSource=P_118 per batch header, chart shown is the "
            "P_115 recheck engine as expected per V111); Flat Base pattern read from "
            "chart (prior high ~127.5, multi-week tight base ~118-123, ~7pct depth, "
            "breakout attempt on 3 up days w/ Bull Signal markers); HybridTier 7 "
            "(Fund 4 NORMAL, Anal 3, Candle 2, Setup 3, STR 0); PA Stop structure "
            "118.74; T2 155.70; Fund Verification clean (ROE ~23-24pct, Debt/Cap "
            "~45-50pct, FCF positive, no hold)",
            "--timeframe", "1D",
            "--source-link", "TradeManagement/P115/2026-09-14_EHC.md",
            "--atm", "2.60",
            "--source", "P_115",
        ],
    },
    {
        "symbol": "GCT",
        "expected": SIGNALS_DIR / "2026-09-14_GCT_v2.0.json",
        "args": [
            "--symbol", "GCT",
            "--session-date", "2026-09-14",
            "--timestamp", "2026-09-14T11:12:54Z",
            "--strategy", "breakout",
            "--entry", "53.45",
            "--stop", "45.76",
            "--target", "59.87",
            "--horizon", "10-15 trading days",
            "--confidence", "MEDIUM",
            "--close", "52.50",
            "--volume", "11388",
            "--rationale",
            "P_118 batch (SignalSource=P_118 per batch header); chart's own Verdict "
            "label is ASYM Setup: Review, HybridTier 5 (Fund 2 NORMAL, Anal 3) does "
            "not clear BUY>=6 but meets AsymmetricSetup (Anal>=3, Fund>=2); Double "
            "Bottom pattern read from chart (two comparable low touches ~44-45 in "
            "mid/late Aug, mid-Aug and again ~9/2-9/3, breakout on 2 up days w/ Bull "
            "Signal markers); PA Stop structure 45.76; T2 59.87; Fund Verification "
            "clean (ROE ~30-32pct, Debt/Cap ~49pct, FCF positive TTM, no hold); "
            "confidence MEDIUM reflects ASYM category itself, not a formula",
            "--timeframe", "1D",
            "--source-link", "TradeManagement/P115/2026-09-14_GCT.md",
            "--atm", "2.46",
            "--source", "P_115",
        ],
    },
]


def write_done(status: str, exit_code: int, note: str = "") -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = f"{status}\n{exit_code}\n{ts}\n"
    if note:
        body += f"{note}\n"
    DONE_PATH.write_text(body, encoding="utf-8")


def main() -> None:
    cli = Path(
        r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem"
        r"\python\cli.py"
    )
    python_exe = r"C:\Users\Trader\.conda\envs\p140\python.exe"
    results = []

    for entry in TICKERS:
        symbol = entry["symbol"]
        args = [python_exe, str(cli)] + entry["args"]
        try:
            result = subprocess.run(
                args, cwd=str(cli.parent), capture_output=True, text=True, timeout=180
            )
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL: {symbol} subprocess error: {exc}")
            write_done("FAIL", 1, f"{symbol} subprocess error: {exc}")
            sys.exit(1)

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        if result.returncode != 0:
            print(f"FAIL: {symbol} cli.py exited {result.returncode}")
            write_done("FAIL", result.returncode, f"{symbol} non-zero exit")
            sys.exit(1)

        expected = entry["expected"]
        if not expected.exists():
            print(f"FAIL: {symbol} expected output not found: {expected}")
            write_done("FAIL", 1, f"{symbol} missing {expected}")
            sys.exit(1)

        size = expected.stat().st_size
        if size < 100:
            print(f"FAIL: {symbol} {expected} suspiciously small ({size} bytes)")
            write_done("FAIL", 1, f"{symbol} only {size} bytes")
            sys.exit(1)

        print(f"{symbol}: PASS -- {expected} ({size} bytes)")
        results.append((symbol, expected, size))

    print("PASS")
    write_done("PASS", 0, "; ".join(f"{s}={p} ({sz}b)" for s, p, sz in results))


if __name__ == "__main__":
    main()
