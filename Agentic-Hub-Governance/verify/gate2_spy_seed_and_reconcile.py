import os
import subprocess
import sqlite3

DB = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
STATEMENT = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\tos_exports\paper\D_020_2026-07-27_YTD_AccountStatement.csv"
PY = r"C:\Users\Trader\.conda\envs\p140\python.exe"
CLI_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
OUT = r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\gate2_spy_result.txt"

lines = []

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM orders")
lines.append(f"orders rows before seed: {cur.fetchone()[0]}")

cur.execute("""
    INSERT INTO orders (
        account_id, symbol, side, qty, planned_entry_price,
        planned_stop_price, planned_target_price, trade_mode,
        submitted_ts, schwab_order_id, status, council_verdict,
        why_code, sig_code, source_project, confidence_tier,
        entry_date, close_date, realized_pnl, entry_fill_price,
        asset_type, put_call
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "IRA9885", "SPY", "short", 1, 3.16,
    None, None, "PAPER",
    "2026-07-27T11:08:42", "5375345511", "pending", None,
    None, None, "P400", "CONFIRMED",
    None, None, None, None,
    None, None,
))
conn.commit()
seeded_order_id = cur.lastrowid
lines.append(f"Seeded orders row #{seeded_order_id}: SPY short 1 (IRON CONDOR primary leg, 745 CALL) @3.16, schwab_order_id=5375345511")
conn.close()

env = os.environ.copy()
env["PYTHONPATH"] = r"C:\Users\Trader\AI-Agent-Learning-Hub"
result = subprocess.run(
    [PY, "cli.py", "reconcile", "--paper", "--statement", STATEMENT],
    cwd=CLI_DIR, env=env, capture_output=True, text=True, timeout=120,
)
lines.append(f"\n--- CLI exit code: {result.returncode} ---")
lines.append("STDOUT:\n" + result.stdout)
lines.append("STDERR:\n" + result.stderr)

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT * FROM orders WHERE order_id = ?", (seeded_order_id,))
row = dict(cur.fetchone())
lines.append(f"\n--- orders row #{seeded_order_id} after reconcile ---")
for k, v in row.items():
    lines.append(f"  {k}: {v}")

cur.execute("SELECT * FROM trades WHERE schwab_transaction_id = ?", ("5375345511",))
trow = cur.fetchone()
if trow:
    lines.append(f"\n--- matching trades row ---")
    for k, v in dict(trow).items():
        lines.append(f"  {k}: {v}")
    tid = dict(trow)["trade_id"]
    cur.execute("SELECT * FROM exits WHERE trade_id = ?", (tid,))
    erow = cur.fetchone()
    if erow:
        lines.append(f"\n--- matching exits row ---")
        for k, v in dict(erow).items():
            lines.append(f"  {k}: {v}")
    else:
        lines.append("\n--- no exits row found ---")
else:
    lines.append("\n--- no matching trades row found ---")
conn.close()

with open(OUT, "w") as f:
    f.write("\n".join(lines))
print("done")