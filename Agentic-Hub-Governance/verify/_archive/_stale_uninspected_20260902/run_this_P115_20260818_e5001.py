"""run_this_P115_20260818_e5001.py -- WO-P115-E5.001 verification.

Verifies cli.py's --horizon default resolves to config.DEFAULT_SIGNAL_HORIZON
WITHOUT calling emit_signal() / write_to_vault() -- deliberately does not
write a throwaway signal into the live P_400 inbox (trading_journal\\
TradeOrderManagement\\signals\\), since that's a real automated pickup
location, not a sandbox. argparse-level check only.
"""
import sys
from pathlib import Path

PROJ = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python")
sys.path.insert(0, str(PROJ))

import cli  # noqa: E402
import config  # noqa: E402

required_no_horizon = [
    "--symbol", "ZZTEST",
    "--session-date", "2026-08-18",
    "--timestamp", "2026-08-18T14:42:58Z",
    "--strategy", "dip_buy",
    "--entry", "100.0",
    "--stop", "90.0",
    "--target", "120.0",
    "--confidence", "MEDIUM",
    "--close", "99.5",
    "--volume", "500000",
    "--rationale", "WO-P115-E5.001 verification run, not a real signal",
    "--timeframe", "1D",
    "--source-link", "WO-P115-E5.001-verification",
]

sys.argv = ["cli.py"] + required_no_horizon
args = cli._parse_args()

print(f"args.horizon = {args.horizon!r}")
print(f"config.DEFAULT_SIGNAL_HORIZON = {config.DEFAULT_SIGNAL_HORIZON!r}")
print(f"MATCH = {args.horizon == config.DEFAULT_SIGNAL_HORIZON}")

# Also confirm explicit override still works
sys.argv = ["cli.py"] + required_no_horizon + ["--horizon", "2-3 weeks"]
args2 = cli._parse_args()
print(f"override args.horizon = {args2.horizon!r}")
print(f"OVERRIDE_OK = {args2.horizon == '2-3 weeks'}")
