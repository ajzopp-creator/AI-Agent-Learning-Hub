import subprocess
import json
from pathlib import Path

CLI_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python"
PYTHON = r"C:\Users\Trader\.conda\envs\p140\python.exe"

cmd = [
    PYTHON, "cli.py",
    "--symbol", "DXYZ",
    "--session-date", "2026-08-13",
    "--timestamp", "2026-08-13T19:35:00Z",
    "--strategy", "dip_buy",
    "--entry", "32.00",
    "--stop", "22.04",
    "--target", "38.37",
    "--horizon", "10-15 days",
    "--confidence", "MEDIUM",
    "--close", "32.01",
    "--volume", "2009062",
    "--rationale", "P_115 ASYM signal; HybridTier=5 (Anal3+Fund2); AsymmetricSetup confirmed (Anal>=3 Fund>=2, chart ASYM Setup:Review agrees with LogEntry); Fund Verification caveat - DXYZ is a closed-end fund (private-tech holding vehicle, not operating company), ROE/Debt/FCF do not map cleanly to V110 framework, recomputed approx tier3 (above submitted, low-confidence); post-earnings N/A (fund reports NAV quarterly, next report ~11/9/26, clear); PA Stop 22.04 structure; 200-MA 4.7pct NORMAL label overrides raw pct",
    "--timeframe", "1D",
    "--source-link", "P_115_STEP1_DXYZ_2026-08-13.md",
    "--source", "P_115",
]

result = subprocess.run(cmd, cwd=CLI_DIR, capture_output=True, text=True, timeout=150)

output = {
    "returncode": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
}

verify_out = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_P115_20260813_193500_output.json")
verify_out.write_text(json.dumps(output, indent=2), encoding="utf-8")

done_marker = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_P115_20260813_193500.py.done")
status = "PASS" if result.returncode == 0 else "FAIL"
done_marker.write_text(f"status={status}\nexit_code={result.returncode}\ntimestamp=2026-08-13T19:35:00Z\n", encoding="utf-8")

print(json.dumps(output, indent=2))
