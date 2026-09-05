import subprocess
import sys

rationale = ("P_117 SNT PUT rec cross-validated via P_115 core engine, came out BUY "
             "(HybridTier=6: Fund 3/Anal 3/Candle 2/Setup 3). Fund verified clean "
             "(ROE 23.69%, D/C 55.2%, FCF+, matches submitted base 4). 200-MA -4% "
             "PULLBACK penalty (-1) correctly applied, adjusted Fund 3. No earnings "
             "flag (last 6/30/26, next ~5/27/27). Confidence MEDIUM: outside PUT call "
             "disagrees with engine BUY, RVOL 0.91, ADX 13.33 weak trend, HybridTier "
             "exactly at threshold not above it.")

source_link = "P_117 SNT PUT rec (contradicts P_115 BUY) - TOS chart cross-validation 2026-08-17"

cmd = [
    r"C:\Users\Trader\.conda\envs\p140\python.exe",
    "cli.py",
    "--symbol", "STZ",
    "--session-date", "2026-08-17",
    "--timestamp", "2026-08-17T14:28:07Z",
    "--strategy", "dip_buy",
    "--entry", "139.18",
    "--stop", "129.52",
    "--target", "162.90",
    "--horizon", "10-15 trading days",
    "--confidence", "MEDIUM",
    "--close", "139.18",
    "--volume", "1432261",
    "--rationale", rationale,
    "--timeframe", "1D",
    "--source-link", source_link,
    "--atm", "3.38",
    "--source", "P_115",
]

result = subprocess.run(
    cmd,
    cwd=r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python",
    capture_output=True,
    text=True,
)

with open(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\stz_emit_result.txt", "w", encoding="utf-8") as f:
    f.write("RETURNCODE: " + str(result.returncode) + "\n")
    f.write("STDOUT:\n" + result.stdout + "\n")
    f.write("STDERR:\n" + result.stderr + "\n")

print("done", result.returncode)
