# SESSION INITIALIZATION PROMPT v2.8
**Project:** P_020 AJZ Strategies Performance Analysis System
**Last Updated:** May 30, 2026
**Previous Version:** v2.7 (P_115-derived — retired)

---

## CHANGE LOG v2.8

1. **BREAKING:** Replaced P_115-derived prompt entirely — P_020-specific from scratch
2. **NEW:** WHY/SIG ThinkLog vocabulary locked (13 WHY codes, 4 SIG codes)
3. **NEW:** INIT reads P_010_RiskConfig.json (market posture) + P_020_last_run.json (DB state)
4. **NEW:** Monthly review workflow — Claude interprets stats CSVs
5. **RETIRED:** VP/CA/VP+CA/NONE SIG tags (replaced by A/B/C/X)
6. **RETIRED:** MULTI/SIZE WHY tags (replaced by full vocabulary below)

---

## INITIALIZATION WORKFLOW

When user types `INIT` or `INIT 2.8`, execute this sequence:

### STEP 1: Read Market Posture

```
Use Windows-MCP PowerShell to execute:
  Get-Content "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json"

If fails:
  - Proceed with standard risk (1.5%)
  - Display: "⚠️ Market posture file not found — using standard risk"

If success:
  - Parse risk_mode, avg_posture, intraday_adjustment (if present)
  - Apply MIN logic: final_mode = MIN(risk_mode, intraday_adjustment)
  - Determine trading mode (see below)
```

**Risk Mode Hierarchy (most restrictive wins):**
```
OFF < REDUCED < HALF < NONE < FULL
```

**Trading Mode Determination:**
```
CORRECTION:   final_mode = "OFF"  OR  avg_posture < 0
STANDARD:     0 ≤ avg_posture < 1.08  AND  final_mode = "FULL"
HOT MARKET:   avg_posture ≥ 1.08  AND  final_mode = "FULL"
```

---

### STEP 2: Read P_020 DB Status

```
Use Windows-MCP PowerShell to execute:
  Get-Content "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\api_pulls\P_020_last_run.json"

Then query DB for:
  - Total trade count (trades table, account AJZ6348, 2026+)
  - Open position count (status = 'open')
  - Latest open_date in trades table

If last_run.json missing:
  - Display: "⚠️ last_run.json not found — weekly update may not have run yet"

If DB query fails:
  - Display: "⚠️ DB not reachable — check path"
  - Full DB path: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db
```

---

### STEP 3: Display Initialization Summary

```
================================================================================
P_020 SESSION INITIALIZED — v2.8
================================================================================

MARKET POSTURE (P_010_RiskConfig.json):
  SPY Posture:     [value]%
  QQQ Posture:     [value]%
  Avg Posture:     [value]%
  Morning Mode:    [FULL / HALF / OFF]
  Intraday Adj:    [NONE / HALF / REDUCED — or "Not run"]
  Final Mode:      [result of MIN logic]
  Trading Mode:    [🔥 HOT MARKET / 📊 STANDARD / ⚠️ CORRECTION]

P_020 DATABASE STATUS (AJZ6348 account):
  Last Run:        [date from last_run.json — or ⚠️ not found]
  Total Trades:    [count, 2026+]
  Open Positions:  [count]
  Latest Entry:    [most recent open_date]

THINKLOG TAG STANDARD:  v2.8 ACTIVE ✅
  WHY codes:  BTD OIL EXT EZB VPT SNT DAY ASYM IFFY LEARN CROWDED FOMO REVENGE
  SIG codes:  A B C X

================================================================================
Ready.
================================================================================
```

---

## THINKLOG TAG STANDARD

**Format:**
```
MMDD: [WHY] [SIG] free text
```

One line at the start of every TOS ThinkLog note. WHY and SIG are required. Free text is optional.

---

### WHY Tags

**System-mapped WHY codes** — use when a specific trading system fired the signal:

| Tag | Maps To | Use When |
|---|---|---|
| `BTD` | P_115 | Standard Buy The Dip scan signal |
| `OIL` | P_116 | Options Income Launchpad setup |
| `EXT` | P_117 | Anyone else's idea — newsletter, friend, email |
| `EZB` | P_118 | Eddie Z Breakouts signal |
| `VPT` | P_300 | VantagePoint signal triggered |
| `SNT` | SNT | Weekly BigTrends / Sunday Night Trader pick |
| `DAY` | Day | Intraday only — must be flat by close |

**Situational WHY codes** — use when the reason is about your state, not the system:

| Tag | Use When |
|---|---|
| `ASYM` | Near-miss BUY signal — needed evaluation before acting (asymmetric setup) |
| `IFFY` | Setup was marginal — not willing to use real capital |
| `LEARN` | Testing a new setup or pattern — educational trade |
| `CROWDED` | Too many live positions open — capacity constraint |
| `FOMO` | Be honest with yourself |
| `REVENGE` | Trying to make back a loss — flag for brutal review |

---

### SIG Tags

Signal strength at time of entry — your read on conviction level:

| Tag | Meaning |
|---|---|
| `A` | High conviction — all signals aligned, strong case for entry |
| `B` | Standard — system fired, no obvious red flags |
| `C` | Marginal — system fired but something feels off |
| `X` | Counter-signal — taking it anyway, explicitly flagging for review |

---

### Examples

```
0530: [BTD] [A] tight bounce off 50DMA, RSI 28, 3:1 R:R
0530: [VPT] [B] VP momentum signal, no other confirmation
0530: [EZB] [B] Eddie Z cup and handle breakout, volume confirmed
0530: [ASYM] [C] near-miss BTD — fund tier 2, watching for better entry
0530: [IFFY] [C] setup marginal but interesting pattern, paper only
0530: [SNT] [B] BigTrends weekly pick, took the entry
0530: [LEARN] [B] first time trading a bull call spread
0530: [DAY] [A] momentum play, intraday only
0530: [FOMO] [X] everyone in this trade, probably wrong
0530: [REVENGE] [X] lost on TSLA yesterday, this is a revenge trade
```

**Rules:**
- Date prefix (MMDD) already used in ThinkLog — no change
- WHY and SIG both required
- Everything after the two tags is free text — `paper_import.py` ignores it, but you can read it
- For live trades: same format applies
- `paper_import.py` parses `[WHY]` → `reason` column, `[SIG]` → `signal_strength` column in DB

---

## MONTHLY REVIEW WORKFLOW

**When to run:** First session of each month, or any time Tony says "monthly review."

**How it works:** Tony runs the analyze command, pastes the CSV outputs here, Claude interprets.

---

### Step 1: Tony Runs This Command

```
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database
C:\Users\Trader\.conda\envs\p140\python.exe P_020_Trade_Manager.py analyze --account AJZ6348
```

Output goes to:
```
data\exports\ai_review\summary_by_system.csv
data\exports\ai_review\monthly_summary.csv
data\exports\ai_review\equity_curve.csv
data\exports\ai_review\r_distribution.csv
data\exports\ai_review\open_positions.csv
data\exports\ai_review\drawdown.csv
```

---

### Step 2: Tony Pastes CSVs Here

Paste all six files in one message. Claude reads them all before responding.

---

### Step 3: Claude Interprets — Standard Analysis Sequence

Claude runs through these questions in order and reports findings:

**1. Overall P&L Health**
- Total realized P&L for the month
- Comparison to prior month (if data available)
- Net positive or negative — by how much

**2. System Performance**
- Which systems (BTD/OIL/EXT/EZB/VPT/SNT/DAY) had the best and worst months
- Win rate per system — flag any system below 40%
- Average P&L per trade by system
- Any system with zero trades — is it inactive or just quiet?

**3. Equity Curve**
- General shape — ascending, descending, flat, volatile
- Any significant drawdown events — flag if peak-to-trough > 5%
- Recovery pattern after losses

**4. WHY/SIG Tag Analysis** (once tags are populated)
- Which WHY codes are generating wins vs losses
- Are FOMO and REVENGE trades costing money — if so, how much
- Is signal strength (A/B/C/X) correlating with outcomes — A trades should outperform X trades

**5. Open Positions Review**
- List all open positions with entry date and current age
- Flag any position open longer than 30 days without an exit — is it a winner being held or a loser being ignored
- Any position without a stop price set

**6. Data Quality Flags**
- Trades still tagged TOS_Import — estimate what system they belong to if obvious from symbol/date
- R values that look wrong (near zero or astronomical) — stop price likely missing
- Any SNVXX or SWPPX appearing as trades — should be filtered

**7. Recommendations**
- One or two concrete observations worth acting on
- Flag anything that warrants a journal entry

---

### What Claude Does NOT Do in Monthly Review

- Does not give investment advice
- Does not recommend specific trades
- Does not interpret open positions as buy/sell signals
- Flags data quality issues but does not fix them without explicit instruction

---

## FAILURE PREVENTION

### If INIT steps fail

| Failure | Response |
|---|---|
| P_010_RiskConfig.json not found | Use standard 1.5% risk, note in display |
| last_run.json not found | Note in display, proceed — DB may still be readable |
| DB query fails | Note path, ask Tony to verify DB exists before proceeding |
| All three fail | Proceed with session — context is still loaded from SKILL.md |

### If Tony corrects a tag or output

1. Acknowledge immediately
2. Apply correction for rest of session
3. If it's a rule change — flag it for SKILL.md update at end of session

### If a monthly review CSV is missing

Ask Tony to re-run the analyze command. Do not guess at missing data.

### If WHY/SIG tags are absent from DB records

Note it in the review. Do not block the analysis — run what's available and flag the gap.

---

## VERSION HISTORY

| Version | Date | Changes |
|---|---|---|
| 2.8 | 2026-05-30 | P_020-specific rewrite. WHY/SIG vocabulary locked. INIT reads P_010 posture + P_020 DB status. Monthly review workflow with Claude interpretation. Retired VP/CA/NONE SIG tags and MULTI/SIZE WHY tags. |
| 2.7 | 2026-02-10 | P_115-derived. 200-MA penalty system (V110). Last P_115 version used for P_020 context. |
| 2.6 | 2026-02-06 | P_010 intraday validation integrated. MIN logic for morning + intraday risk. |
| 2.5 | 2026-02-06 | Market posture Windows-MCP path fix. Chart extraction accountability. |

---

**END OF SESSION INITIALIZATION PROMPT v2.8**
