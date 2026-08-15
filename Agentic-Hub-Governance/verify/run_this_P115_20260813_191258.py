import subprocess
import json
from pathlib import Path

CLI_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python"
PYTHON = r"C:\Users\Trader\.conda\envs\p140\python.exe"

cmd = [
    PYTHON, "cli.py",
    "--symbol", "DAL",
    "--session-date", "2026-08-13",
    "--timestamp", "2026-08-13T19:12:58Z",
    "--strategy", "bounce",
    "--entry", "91.44",
    "--stop", "87.07",
    "--target", "131.86",
    "--horizon", "10-15 days",
    "--confidence", "MEDIUM",
    "--close", "91.46",
    "--volume", "2154982",
    "--rationale", "P_116 Bounce signal; HybridTier=7 (Anal3+Fund4); Fund verified clean ROE 20.12pct Debt/Cap 49.1pct FCF positive (matches submitted Fund=4); post-earnings clear (7/10/26, 24 sessions); RVOL 0.52 below avg20 - moderate volume conviction; PA Stop 87.07 structure",
    "--timeframe", "1D",
    "--source-link", "P_116_STEP1_DAL_2026-08-13.md",
    "--source", "P_115",
]

result = subprocess.run(cmd, cwd=CLI_DIR, capture_output=True, text=True, timeout=150)

output = {
    "returncode": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
}

verify_out = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_P115_20260813_191258_output.json")
verify_out.write_text(json.dumps(output, indent=2), encoding="utf-8")

done_marker = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_P115_20260813_191258.py.done")
status = "PASS" if result.returncode == 0 else "FAIL"
done_marker.write_text(f"status={status}\nexit_code={result.returncode}\ntimestamp=2026-08-13T19:12:58Z\n", encoding="utf-8")

print(json.dumps(output, indent=2))
if result.returncode == 0:
    print("PASS")
else:
    print("FAIL:", result.stderr[:500])
