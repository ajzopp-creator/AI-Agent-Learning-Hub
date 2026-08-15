import subprocess
import json
from pathlib import Path

CLI_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python"
PYTHON = r"C:\Users\Trader\.conda\envs\p140\python.exe"

cmd = [
    PYTHON, "cli.py",
    "--symbol", "FLY",
    "--session-date", "2026-08-13",
    "--timestamp", "2026-08-13T20:28:50Z",
    "--strategy", "dip_buy",
    "--entry", "26.90",
    "--stop", "19.17",
    "--target", "33.37",
    "--horizon", "10-15 days",
    "--confidence", "LOW",
    "--close", "26.90",
    "--volume", "2929669",
    "--rationale", "P_115 ASYM signal; HybridTier=5 (Anal3+Fund2); AsymmetricSetup confirmed (chart ASYM Setup:Review agrees with LogEntry); POST-EARNINGS OVERRIDE - Tony explicit direction, signal is Day 2/3 post Q2 2026 report (8/11/26 AMC, revenue $117.7M beat vs $15.5M YoY, EPS miss -0.42 vs -0.22 est); Fund Verification weak - recomputed approx tier1 (ROE deeply negative -62 to -269pct range across sources, FCF deeply negative -96M to -257M range, Debt/Equity 0.05 low) vs submitted Fund=2, 1-tier gap; PA Stop 19.17 structure; 200-MA -2pct NORMAL label",
    "--timeframe", "1D",
    "--source-link", "P_115_STEP1_FLY_2026-08-13.md",
    "--source", "P_115",
]

result = subprocess.run(cmd, cwd=CLI_DIR, capture_output=True, text=True, timeout=150)

output = {
    "returncode": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
}

verify_out = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_P115_20260813_202850_output.json")
verify_out.write_text(json.dumps(output, indent=2), encoding="utf-8")

done_marker = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_P115_20260813_202850.py.done")
status = "PASS" if result.returncode == 0 else "FAIL"
done_marker.write_text(f"status={status}\nexit_code={result.returncode}\ntimestamp=2026-08-13T20:28:50Z\n", encoding="utf-8")

print(json.dumps(output, indent=2))
