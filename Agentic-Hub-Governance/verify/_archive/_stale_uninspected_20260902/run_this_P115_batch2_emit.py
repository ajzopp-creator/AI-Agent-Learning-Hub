import subprocess

signals = [
    {
        "symbol": "AXTI",
        "entry": "92.22",
        "stop": "59.00",
        "target": "107.70",
        "close": "92.22",
        "volume": "6490476",
        "atm": "10.32",
        "rationale": ("P_115 dip_buy ASYM (HybridTier=5: Fund2/Anal3/Candle2/Setup3/STR-2). Fund verified: "
                      "ROE -5.0% TTM fails (despite explosive Q2 turnaround to $11.1M GAAP net income, trailing "
                      "figure lags), Debt/Cap ~19% passes, FCF still negative TTM (-$11.7M Q1 operating CF) fails. "
                      "1/3 criteria -- recomputed Fund~1 vs submitted 2, exactly 1 tier down, within tolerance but "
                      "weakest match today. 200-MA +82% NORMAL (well above MA). No earnings flag (next 10/29/26). "
                      "STR=-2 co-occurs with a batch-wide regime signal -- 14/14 tickers scanned today read STR=-2 "
                      "despite FULL/HOT posture. RVOL 0.5 weak. Confidence MEDIUM."),
    },
    {
        "symbol": "IONQ",
        "entry": "45.49",
        "stop": "39.28",
        "target": "51.14",
        "close": "46.59",
        "volume": "5911003",
        "atm": "3.03",
        "rationale": ("P_115 dip_buy ASYM (HybridTier=5: Fund2/Anal3/Candle2/Setup3/STR-2). Fund verified: "
                      "ROE -60.5% fails hard, Debt/Cap ~2% passes, FCF -$484M fails. 1/3 criteria -- recomputed "
                      "Fund~1 vs submitted 2, 1 tier down, within tolerance. Pre-profitability quantum-computing "
                      "name, weakest fundamental profile of today's batch. 200-MA +3.1% NORMAL. No earnings flag "
                      "(reported 8/5/26, past 3-session stabilization window). STR=-2 co-occurs with batch-wide "
                      "regime signal (14/14 tickers today). RVOL 0.28 weak. T1/T2 touch count=1 (lower structural "
                      "confirmation on those levels). Confidence MEDIUM."),
    },
    {
        "symbol": "NOK",
        "entry": "11.03",
        "stop": "9.06",
        "target": "11.94",
        "close": "11.03",
        "volume": "43339927",
        "atm": "0.61",
        "rationale": ("P_115 dip_buy ASYM (HybridTier=5: Fund2/Anal3/Candle2/Setup3/STR-2). Fund verified clean: "
                      "ROE 3.45% fails, Debt/Cap ~13% passes, FCF+ passes. 2/3 criteria, recomputed Fund=2 matches "
                      "submitted exactly -- cleanest Fund match of today's three ASYM picks. 200-MA +17.6% NORMAL. "
                      "No earnings flag (last ~7/23/26). STR=-2 co-occurs with batch-wide regime signal (14/14 "
                      "tickers today). NOTE: Daily AND 4H both reading Downtrend on DMI/RegimeCounsel despite BULL "
                      "price trend -- short-term divergence worth watching. RVOL 0.61. Confidence MEDIUM."),
    },
]

results = []
for sig in signals:
    cmd = [
        r"C:\Users\Trader\.conda\envs\p140\python.exe",
        "cli.py",
        "--symbol", sig["symbol"],
        "--session-date", "2026-08-17",
        "--timestamp", "2026-08-17T14:45:27Z",
        "--strategy", "dip_buy",
        "--entry", sig["entry"],
        "--stop", sig["stop"],
        "--target", sig["target"],
        "--horizon", "10-15 trading days",
        "--confidence", "MEDIUM",
        "--close", sig["close"],
        "--volume", sig["volume"],
        "--rationale", sig["rationale"],
        "--timeframe", "1D",
        "--source-link", "TradeOrderManagement/P115",
        "--atm", sig["atm"],
        "--source", "P_115",
    ]
    result = subprocess.run(
        cmd,
        cwd=r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python",
        capture_output=True,
        text=True,
    )
    results.append((sig["symbol"], result.returncode, result.stdout, result.stderr))

with open(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\batch2_emit_result.txt", "w", encoding="utf-8") as f:
    for sym, rc, out, err in results:
        f.write("=== " + sym + " (rc=" + str(rc) + ") ===\n")
        f.write("STDOUT:\n" + out + "\n")
        f.write("STDERR:\n" + err + "\n\n")

print("done", [(s, rc) for s, rc, o, e in results])
