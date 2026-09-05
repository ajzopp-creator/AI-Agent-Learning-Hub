"""
run_this_P118_20260806_154536.py
WO context: P_118 STEP 2 signal emission -- NTAP (Eddie Z, High Handle BUY)
PEH safety-net script (peh-handoff v1.5) -- staged before the live MCP call.
Self-contained: does not import from the Hub package, only shells out to the
existing production cli.py entry point with the exact STEP 2 args.
"""
import subprocess
import sys
from datetime import datetime

PROJECT_PYTHON_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python"
PYTHON_EXE = r"C:\Users\Trader\.conda\envs\p140\python.exe"

RATIONALE = (
    "P_118 Eddie Z High Handle BUY: HybridTier=6 (Fund3+Anal3), "
    "Candle2/Setup3/STR0. Prior high 195.7 handle resistance after "
    "run-up+pullback base (~4wk); entry above trigger. Fund reverified via "
    "stockanalysis.com (ROE 109.2%, Debt/Cap ~65% fail, FCF+ = Tier3, "
    "matches submitted, no flag). No earnings flag (last 5/28/26, next "
    "8/26/26). RSI 69.8, ADX 33.61 strong trend. HOT posture (avg_posture "
    "10.63). support_1/2 are chart-read MA levels (48EMA/200SMA), not "
    "P_300 IntelliScan output."
)

CLI_ARGS = [
    PYTHON_EXE, "cli.py",
    "--symbol", "NTAP",
    "--session-date", "2026-08-06",
    "--timestamp", "2026-08-06T19:45:36Z",
    "--strategy", "breakout",
    "--entry", "195.80",
    "--stop", "162.67",
    "--target", "202.58",
    "--horizon", "10-20 days",
    "--confidence", "MEDIUM",
    "--close", "191.05",
    "--volume", "1452906",
    "--rationale", RATIONALE,
    "--timeframe", "1D",
    "--source-link", "TOS_NTAP_chart_2026-08-06_session",
    "--support-1", "162.42",
    "--support-2", "122.35",
    "--source", "P_115",
]


def main():
    done_path = __file__ + ".done"
    status = "FAIL"
    exit_code = "N/A"
    reason = ""
    output = ""
    try:
        result = subprocess.run(
            CLI_ARGS,
            cwd=PROJECT_PYTHON_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        exit_code = result.returncode
        output = result.stdout + result.stderr
        print(output)
        if result.returncode == 0 and "Signal written" in output:
            status = "PASS"
        else:
            reason = "cli.py exit code " + str(result.returncode) + " or no 'Signal written' confirmation"
    except Exception as e:
        reason = str(e)

    with open(done_path, "w") as f:
        f.write("status=" + status + "\n")
        f.write("exit_code=" + str(exit_code) + "\n")
        f.write("timestamp=" + datetime.now().isoformat() + "\n")

    if status == "PASS":
        print("PASS")
    else:
        print("FAIL:", reason)
        sys.exit(1)


if __name__ == "__main__":
    main()
