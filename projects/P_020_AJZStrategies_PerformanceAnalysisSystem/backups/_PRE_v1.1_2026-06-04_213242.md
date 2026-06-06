# P_020 INIT v2.9
_Last updated: 2026-05-31_

---

## ON INIT

Run a single Python script that reads all three data sources and prints the formatted block.

**Step 1 — Claude attempts MCP auto-run:**
```powershell
Start-Process -FilePath "C:\Users\Trader\.conda\envs\p140\python.exe" `
  -ArgumentList "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\P_020_INIT.py" `
  -Wait -NoNewWindow `
  -RedirectStandardOutput "C:\Temp\init_out.txt" `
  -RedirectStandardError "C:\Temp\init_err.txt"
Start-Sleep -Seconds 3
Get-Content "C:\Temp\init_out.txt"
Get-Content "C:\Temp\init_err.txt"
```

**Step 2 — If MCP times out, give Tony this one-liner:**
```
C:\Users\Trader\.conda\envs\p140\python.exe "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\P_020_INIT.py"
```
Tony pastes output into chat. Claude reads and displays the block.

**Script location:**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\P_020_INIT.py
```

**Output format:**
```
=== P_020 v2.8c ===
MARKET:  SPY[x]% QQQ[x]% Avg[x]% | Morning:[mode] Intraday:[adj] Final:[mode] | [HOT/STD/CORR]
DB:      LastRun:[date] Trades:[n] Open:[n] Latest:[date]
ACCOUNT: Balance:$[total] Cash:$[cash] BuyPow:$[bp] AsOf:[date]  ** [flags if any]
TAGS:    WHY=BTD|OIL|EXT|EZB|VPT|SNT|DAY|ASYM|IFFY|LEARN|CROWDED|FOMO|REVENGE  SIG=A|B|C|X
===================
```

**What the script reads:**
- `P_010_RiskConfig.json` → SPY/QQQ/Avg posture, risk_mode, intraday_adjustment → computes final mode + HOT/STD/CORR
- `P_020_last_run.json` → last run date
- `P_020_trades.db` → trade count (AJZ6348, 2026+), open count, latest open_date, latest account_balances row

**Account parameter thresholds (in script constants):**
- Baseline: $35,000
- THRESHOLD flag: total_value >= $38,500 (+10%) or <= $31,500 (-10%)
- STALE flag: snapshot_date > 14 days ago
- When either flag appears: remind Tony to review position sizing

---

## THINKLOG TAG STANDARD

Format: `MMDD: [WHY] [SIG] free text`
WHY + SIG required. Free text optional. Parser captures WHY->reason, SIG->signal_strength.

**WHY -- system:**
BTD=P_115 | OIL=P_116 | EXT=P_117 | EZB=P_118 | VPT=P_300 | SNT=BigTrends | DAY=intraday-flat

**WHY -- situational:**
ASYM=near-miss BUY needs eval | IFFY=marginal setup | LEARN=educational | CROWDED=at capacity | FOMO=be honest | REVENGE=making back a loss->review

**SIG:**
A=high conviction all aligned | B=standard system fired | C=marginal feels off | X=counter-signal flagged

**Examples:**
```
0530: [BTD] [A] bounce off 50DMA RSI28
0530: [VPT] [B] VP signal only
0530: [ASYM] [C] near-miss BTD watching
0530: [FOMO] [X] everyone in this trade
0530: [REVENGE] [X] lost TSLA yesterday
```

---

## MONTHLY REVIEW

Trigger: "monthly review" or first session of month.

**Tony runs:**
```
cd ...\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database
C:\Users\Trader\.conda\envs\p140\python.exe P_020_Trade_Manager.py analyze --account AJZ6348
```
Outputs: `data\exports\ai_review\` -- summary_by_system, monthly_summary, equity_curve, r_distribution, open_positions, drawdown

**Tony pastes all 6 CSVs. Claude interprets in order:**
1. P&L health -- monthly total, vs prior month
2. System performance -- win rate per system, flag <40%, avg P&L, zero-trade systems
3. Equity curve -- shape, flag drawdown >5%, recovery
4. WHY/SIG analysis -- FOMO/REVENGE cost, A vs X outcomes
5. Open positions -- age, flag >30 days, missing stops
6. Data quality -- TOS_Import untagged, bad R values, SNVXX/SWPPX as trades
7. Account parameters -- compare latest balance_history total_value to baseline $35,000; if +-10% crossed, state new balance, % change, ask Tony to confirm updated baseline; note position sizing should be revisited
8. 1-2 concrete observations, flag journal-worthy items

Claude does NOT advise trades, interpret open positions as signals, or fix data without instruction.

---

## FAILURE RULES

| Situation | Action |
|---|---|
| MCP auto-run times out | Give Tony the one-liner above, wait for paste |
| Any single read inside script fails | Script prints inline warning, continues -- Claude notes in display |
| Monthly CSV missing | Ask Tony to re-run analyze |
| WHY/SIG absent from DB | Note gap, run review on available data |
| Tony corrects tag/output | Apply immediately, flag for SKILL.md if rule change |

---

## VERSION
2.9  2026-05-31 -- Replaced 3-step chained PowerShell INIT with single P_020_INIT.py script.
                   MCP auto-run attempt first; one-liner fallback if timeout.
                   Read 1/2/3 now internal to script. Doc updated to match.
2.8c 2026-05-30 -- Added Read 3 (account balance from DB), account parameters step in monthly review.
2.8  2026-05-30 -- P_020-specific rewrite. WHY/SIG locked. INIT + monthly review.
2.7  2026-02-10 -- P_115-derived (retired).
