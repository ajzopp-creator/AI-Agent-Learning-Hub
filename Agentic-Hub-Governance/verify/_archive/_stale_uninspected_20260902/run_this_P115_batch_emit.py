import subprocess

signals = [
    {
        "symbol": "SBLK",
        "entry": "29.31",
        "stop": "27.06",
        "target": "38.27",
        "close": "29.84",
        "volume": "440777",
        "atm": "0.92",
        "rationale": ("P_118 High Handle pattern, stairstep uptrend with tight pullbacks before each push, "
                      "fresh high $29.91 today. ASYM (HybridTier=5: Fund2/Anal3/Candle2/Setup3). Fund verified "
                      "clean: ROE 3.41%, Debt/Cap 33.3%, FCF+ (2/3 criteria, matches submitted). 200-MA +26.1% "
                      "NORMAL (well above MA, no penalty). No earnings flag (last 8/5/26, next ~Nov). "
                      "Confidence MEDIUM: RVOL 0.34 well below Eddie Z's 3x breakout-volume standard. "
                      "NOTE: Tony already holds an open paper position in SBLK from the 8/14/26 P_115 ASYM "
                      "signal (+54sh @28.96) -- this is a second, separate entry on the same ticker."),
    },
    {
        "symbol": "DGX",
        "entry": "240.10",
        "stop": "229.24",
        "target": "289.91",
        "close": "236.01",
        "volume": "71045.5",
        "atm": "5.2",
        "rationale": ("P_118 High Handle pattern, shallow tight pullback (~1.7%) off fresh high $240.13 "
                      "following post-earnings breakout. ASYM (HybridTier=5: Fund2/Anal3/Candle2/Setup3). "
                      "Fund verified clean: ROE 13.9-14.2%, Debt/Cap 47.4%, FCF+ (2/3 criteria, matches "
                      "submitted). 200-MA +19.9% NORMAL (well above MA, no penalty). No earnings flag "
                      "(last 7/23/26, next ~10/27/26). Confidence MEDIUM: RVOL 0.11 very weak, well below "
                      "Eddie Z's 3x breakout-volume standard."),
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
        "--strategy", "breakout",
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

with open(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\batch_emit_result.txt", "w", encoding="utf-8") as f:
    for sym, rc, out, err in results:
        f.write("=== " + sym + " (rc=" + str(rc) + ") ===\n")
        f.write("STDOUT:\n" + out + "\n")
        f.write("STDERR:\n" + err + "\n\n")

print("done", [(s, rc) for s, rc, o, e in results])
