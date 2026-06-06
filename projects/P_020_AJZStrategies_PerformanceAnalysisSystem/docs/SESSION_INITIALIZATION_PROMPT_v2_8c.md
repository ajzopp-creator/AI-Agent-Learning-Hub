# P_020 INIT v2.8c
_Last updated: 2026-05-30_

---

## ON INIT

Run these 3 reads, then display summary block.

**Read 1 — Market posture:**
```
Get-Content "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json"
```
Parse: `risk_mode`, `avg_posture`, `intraday_adjustment` (optional)
`final_mode = MIN(risk_mode, intraday_adjustment)` | hierarchy: OFF < REDUCED < HALF < NONE < FULL
Mode: CORRECTION = final OFF or avg<0 | STANDARD = 0≤avg<1.08 + FULL | HOT = avg≥1.08 + FULL
Fail → use standard 1.5%, note ⚠️

**Read 2 — DB status:**
```
Get-Content "...\P_020_AJZStrategies_PerformanceAnalysisSystem\data\api_pulls\P_020_last_run.json"
```
Query DB: trade count (AJZ6348, 2026+), open count (status='open'), latest open_date
DB path: `...\data\database\P_020_trades.db`
Fail → note ⚠️ and proceed

**Read 3 — Account balance (from DB):**
```sql
SELECT snapshot_date, total_value, cash_available, buying_power
FROM account_balances
WHERE account_id LIKE '%6348%'
ORDER BY snapshot_date DESC LIMIT 1
```
Compare `total_value` to baseline $35,000.
Flag if change ≥ ±10% from baseline OR if last snapshot > 14 days old.
Fail → note ⚠️ and proceed

**Display:**
```
=== P_020 v2.8c ===
MARKET:  SPY[x]% QQQ[x]% Avg[x]% | Morning:[mode] Intraday:[adj] Final:[mode] | [🔥HOT/📊STD/⚠️CORR]
DB:      LastRun:[date] Trades:[n] Open:[n] Latest:[date]
ACCOUNT: Balance:$[total_value] Cash:$[cash_available] AsOf:[snapshot_date] [⚠️ if stale or ±10% threshold crossed]
TAGS:    WHY=BTD|OIL|EXT|EZB|VPT|SNT|DAY|ASYM|IFFY|LEARN|CROWDED|FOMO|REVENGE  SIG=A|B|C|X
===================
```

**Account parameter thresholds:**
- Baseline: $35,000 (update this value when Tony confirms a new baseline)
- ⚠️ flag triggers if: total_value ≥ $38,500 (+10%) or ≤ $31,500 (-10%)
- ⚠️ flag triggers if: snapshot_date > 14 days ago
- When flag triggers: note in display and remind Tony to review position sizing

---

## THINKLOG TAG STANDARD

Format: `MMDD: [WHY] [SIG] free text`
WHY + SIG required. Free text optional. Parser captures WHY→reason, SIG→signal_strength.

**WHY — system:**
BTD=P_115 | OIL=P_116 | EXT=P_117 | EZB=P_118 | VPT=P_300 | SNT=BigTrends | DAY=intraday-flat

**WHY — situational:**
ASYM=near-miss BUY needs eval | IFFY=marginal setup | LEARN=educational | CROWDED=at capacity | FOMO=be honest | REVENGE=making back a loss→review

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
Outputs: `data\exports\ai_review\` — summary_by_system, monthly_summary, equity_curve, r_distribution, open_positions, drawdown

**Tony pastes all 6 CSVs. Claude interprets in order:**
1. P&L health — monthly total, vs prior month
2. System performance — win rate per system, flag <40%, avg P&L, zero-trade systems
3. Equity curve — shape, flag drawdown >5%, recovery
4. WHY/SIG analysis — FOMO/REVENGE cost, A vs X outcomes
5. Open positions — age, flag >30 days, missing stops
6. Data quality — TOS_Import untagged, bad R values, SNVXX/SWPPX as trades
7. Account parameters — compare latest balance_history total_value to baseline $35,000; if ±10% crossed, state new balance, % change, ask Tony to confirm updated baseline; note position sizing should be revisited
8. 1-2 concrete observations, flag journal-worthy items

Claude does NOT advise trades, interpret open positions as signals, or fix data without instruction.

---

## FAILURE RULES

| Situation | Action |
|---|---|
| Any INIT read fails | Note ⚠️, proceed |
| Monthly CSV missing | Ask Tony to re-run analyze |
| WHY/SIG absent from DB | Note gap, run review on available data |
| Tony corrects tag/output | Apply immediately, flag for SKILL.md if rule change |

---

## VERSION
2.8c 2026-05-30 — Added Read 3 (account balance from DB), account parameters step in monthly review.
2.8  2026-05-30 — P_020-specific rewrite. WHY/SIG locked. INIT + monthly review.
2.7  2026-02-10 — P_115-derived (retired).
