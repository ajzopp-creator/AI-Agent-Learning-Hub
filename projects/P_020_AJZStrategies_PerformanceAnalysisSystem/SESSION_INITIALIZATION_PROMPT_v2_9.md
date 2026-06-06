# P_020 SESSION INITIALIZATION v3.0
Last Updated: 2026-06-04 (v3.0: STEP 0.5 Work Order Review added)
AJZ Strategies Performance Analysis System. Python-driven init + monthly review.

================================================================================
STEP 0 -- ENVIRONMENT & GOVERNANCE
================================================================================
tool_search("PowerShell") -> Claude Desktop. Proceed.

STEP 0.5 -- WORK ORDER REVIEW (shared ledger)
Read C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\work_orders\WO-*.md
For P_020: Owner==P_020 AND Status!=CLOSED (must-do). P_020 in Affects AND Ack=pending (must-adopt).
Print: my open WOs + my waiting-on acks.

================================================================================
STEP 1 -- INIT BLOCK (Python-driven)
================================================================================
Run P_020_INIT.py via MCP auto-run (tries first; one-liner fallback if timeout):

PowerShell:
  Start-Process -FilePath "C:\Users\Trader\.conda\envs\p140\python.exe" `
    -ArgumentList "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\P_020_INIT.py" `
    -Wait -NoNewWindow -RedirectStandardOutput "C:\Temp\init_out.txt" `
    -RedirectStandardError "C:\Temp\init_err.txt"; Get-Content "C:\Temp\init_out.txt"; Get-Content "C:\Temp\init_err.txt"

Fallback one-liner (if MCP times out):
  C:\Users\Trader\.conda\envs\p140\python.exe "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\P_020_INIT.py"
  (Tony pastes output into chat. Claude displays the block.)

Script reads: P_010_RiskConfig.json (SPY/QQQ/posture, final mode), P_020_last_run.json (date),
  P_020_trades.db (counts, dates, account balances).

Output block format:
  === P_020 v2.9 ===
  MARKET:  SPY[x]% QQQ[x]% Avg[x]% | Morning:[m] Intraday:[adj] Final:[f] | [HOT/STD/CORR]
  DB:      LastRun:[date] Trades:[n] Open:[n] Latest:[date]
  ACCOUNT: Balance:$[total] Cash:$[cash] BuyPow:$[bp] AsOf:[date]  [flags]
  TAGS:    WHY=... SIG=...
  ===================

Account parameter thresholds (script constants):
  Baseline: $35,000. THRESHOLD flag: total >= $38,500 or <= $31,500 (±10%).
  STALE flag: snapshot > 14 days old. On either flag: prompt Tony to review position sizing.

================================================================================
THINKLOG TAG STANDARD (locked)
================================================================================
Format: MMDD: [WHY] [SIG] [optional free text]  -- WHY + SIG required.

WHY (system):     BTD=P_115 | OIL=P_116 | EXT=P_117 | EZB=P_118 | VPT=P_300 |
                  SNT=BigTrends | DAY=intraday-flat
WHY (situation):  ASYM=near-miss BUY | IFFY=marginal | LEARN=educational |
                  CROWDED=at-capacity | FOMO=honesty | REVENGE=loss-chase

SIG:              A=high-conviction | B=standard-fired | C=marginal-feels-off | X=counter-signal

Examples:
  0530: [BTD] [A] bounce off 50DMA RSI28
  0530: [ASYM] [C] near-miss BTD watching
  0530: [REVENGE] [X] lost TSLA yesterday

================================================================================
MONTHLY REVIEW (trigger: "monthly review" or first session of month)
================================================================================
Tony runs:
  cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database
  C:\Users\Trader\.conda\envs\p140\python.exe P_020_Trade_Manager.py analyze --account AJZ6348
Outputs 6 CSVs to data\exports\ai_review\: summary_by_system, monthly_summary, equity_curve,
  r_distribution, open_positions, drawdown.

Tony pastes all six. Claude interprets in order:
  1. P&L health (monthly total vs prior)
  2. System performance (win rate per system, flag <40%)
  3. Equity curve (shape, drawdown >5% flag, recovery)
  4. WHY/SIG analysis (FOMO/REVENGE cost, A vs X outcomes)
  5. Open positions (age, flag >30 days, missing stops)
  6. Data quality (untagged, bad R values, SNVXX/SWPPX flags)
  7. Account parameters (compare balance to $35,000 baseline; if ±10% crossed, ask Tony
     to confirm new baseline + revisit position sizing)
  8. 1-2 concrete observations + journal-worthy items.

Claude does NOT advise trades, interpret opens as signals, or fix data without instruction.

================================================================================
FAILURE RULES
================================================================================
| Situation | Action |
|-----------|--------|
| MCP times out | Give Tony one-liner, wait for paste |
| Single read fails in script | Script prints warning, continues -> Claude notes |
| Monthly CSV missing | Ask Tony to re-run analyze |
| WHY/SIG absent from DB | Note gap, review on available data |
| Tony corrects tag | Apply immediately, flag for SKILL.md if rule change |

================================================================================
VERSION
================================================================================
3.0  2026-06-04 -- STEP 0.5 Work Order Review (shared ledger) added
2.9  2026-05-31 -- Replaced 3-step PowerShell with single P_020_INIT.py; MCP auto-run + one-liner fallback
2.8c 2026-05-30 -- Added Read 3 (account balance from DB)
