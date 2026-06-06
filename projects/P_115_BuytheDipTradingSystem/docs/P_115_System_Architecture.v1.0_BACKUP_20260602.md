# P_115 — System Architecture
**Project ID:** P_115
**Version:** 1.0
**Last Updated:** 2026-05-27
**Maintained By:** Anthony Zoppi
**Status:** Active

---

## DOCUMENTATION DECISION PROTOCOL
*Read this before creating any new documentation.*

### The Golden Rule
**Always try to fit new content into this master document first.**
Only create a separate file when one of the trigger conditions below is met.

### Decision Flow

```
New content needs to be documented
              |
              v
Does a section in this master doc already cover this topic?
              |
      Yes     |     No
              |
   Add it     |   Is the content > 1 page OR updated frequently
   here       |   OR shared across multiple projects?
              |            |
              |     Yes    |    No
              |            |
              |   Create   |   Add it
              |   separate |   here
              |   file     |
              |            |
              v            v
    Add a reference     Done
    link in the
    relevant section
    of this doc
```

### When to Add Directly to This Document
- Short content (under 1 page)
- Stable content that rarely changes
- Content specific to P_115 only
- Definitions, parameters, rules, checklists

### When to Create a Separate File
- Content exceeds 1 page of detail
- Updated frequently (daily/weekly logs)
- Shared or referenced across multiple projects
- Requires its own version history
- Operational prompts that are copy-pasted regularly

### When Creating a Separate File — Always Ask First

> "Should I add this to the master doc, or create a separate file?
> If separate — does a file already exist that this should merge into?"

**Checklist:**
- [ ] Check if content fits an existing section in this master doc
- [ ] Check if a related file already exists that should be updated instead
- [ ] If creating new — add a reference link in the relevant section here
- [ ] Name the file using project convention: `P_115_[Topic].v[X.X].md`
- [ ] Note the new file in Section 13 Appendix B (Related Documentation)

### Reference Link Format
```
> **Linked Document:** [Filename]
> **Location:** [Project Knowledge / Local Path]
> **Purpose:** [One line description]
> **Last Updated:** [Date]
```

---

## TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [AI Tools & Platforms](#3-ai-tools--platforms)
4. [Requirements](#4-requirements)
5. [Change Log](#5-change-log)
6. [Error Corrections Log](#6-error-corrections-log)
7. [Enhancement Log](#7-enhancement-log)
8. [AI Workflows & Processes](#8-ai-workflows--processes)
9. [Data Design](#9-data-design)
10. [Testing & Validation](#10-testing--validation)
11. [Daily Operations & Session Management](#11-daily-operations--session-management)
12. [Troubleshooting & Support](#12-troubleshooting--support)
13. [Appendices](#13-appendices)

---

## 1. PROJECT OVERVIEW

### 1.1 Purpose
P_115 is a systematic swing trading strategy that identifies high-probability dip-buying opportunities using a multi-tier diagnostic scoring model. It combines fundamental strength validation with technical candle and momentum analysis to produce BUY, ASYM, or PASS verdicts before institutional confirmation — enabling anticipatory entries with defined risk.

**Core Philosophy:** Chart is King, not the news. Technical setups drive decisions; fundamentals validate.

### 1.2 Scope

**What P_115 Covers:**
- Multi-tier signal scoring (Fundamental + Analysis + Candle tiers)
- Step 1 diagnostics → Step 2 position sizing → Step 3 outcome tracking
- Options-first position sizing when viability criteria are met
- Market posture awareness (Rally / Correction mode)
- Cross-validation support for P_117, P_118 signals on exception basis

**What P_115 Does NOT Cover:**
- Pattern-based breakout entries (→ P_118 Eddie Z)
- Options income/bounce strategies (→ P_116)
- External recommendation tracking (→ P_117)
- VantagePoint grid crossover signals (→ P_300)

### 1.3 Project Details

| Field | Value |
|---|---|
| Start Date | December 2025 |
| Current Status | Active — Validation Phase |
| Primary AI Engine | Claude.ai (Claude Desktop with Windows-MCP) |
| Primary Platform | ThinkorSwim (TOS) + Chaikin Analytics + VantagePoint |
| Project Location | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\` |
| Related Projects | P_010 (Posture), P_020 (Tracker), P_116, P_117, P_118, P_300, P_800 (Vault Interface) |

### 1.4 Reference Materials

| Document | Location | Notes |
|---|---|---|
| SESSION_INITIALIZATION_PROMPT.md | Project Knowledge | Current: v3.1 — paste at every session start |
| CLAUDE_ASSISTANT_INSTRUCTIONS_v2_1_.md | Project Knowledge | Current: v2.5 — role and workflow rules |
| Quick_Reference_Prompts_v9_4_1.md | Project Knowledge | Daily shorthand commands |
| Tracker_Log_Schema_v9_4_0_1.md | Project Knowledge | 27-column schema — authoritative |
| P_115_StrategyGuide_ChangeLog.md | Project Knowledge | Full version history v9.1 → V110.x |
| STRATEGY_CHANGE_LOG_V110.md | Project Knowledge | V110, V110.1, V110.2, V110.3 detail |
| P_000_Account_Parameters_Current.md | Local config | Live account parameters (monthly review) |
| P_010_RiskConfig.json | Local config | Live posture — re-read before every STEP 2 |
| POSITION_SIZING_THREE_GATE_REFERENCE.md | Project Knowledge | Three-gate examples |
| OPTIONS_RISK_METHODOLOGY.md | Project Knowledge | Chart-based delta translation method |
| P115_Options_Combined_Summary.md | Project Knowledge | Options concepts reference |
| P_800 vault_interface.py (v1.1) | `C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\python_utils\` | Authoritative Obsidian write interface |

### 1.5 Definitions & Acronyms

| Term | Definition |
|---|---|
| HybridTier | AnalysisTier + Adjusted FundamentalsTier — primary BUY decision input |
| AsymmetricSetup (ASYM) | High-quality signal below BUY threshold — reduced size entry |
| STR / SellTheRip | Distance from 44-day high — risk indicator, gate in SetupScore |
| MTF | Multi-Timeframe — daily + 60-min chart alignment |
| CandleTier | 0-3 score for candle quality, volume, STR, RSI rising |
| SetupScore | 0-4 binary gate score feeding into AnalysisTier |
| ModulatedScore | Composite technical momentum score (≥70 required for gate 2) |
| ATR | Average True Range — volatility input for stop calculation |
| DTE | Days To Expiration — options time value parameter |
| OI | Open Interest — options liquidity gate (≥150 required) |
| TOS | ThinkOrSwim — primary charting and execution platform |
| P_910 | Daily scan that generates candidate tickers for P_115 processing |
| Three-Gate | Position sizing method: smallest of Risk / Cash / Concentration |
| Cash Balance | User-provided buying power per trade — NOT account balance |
| Account Balance | Per `P_000_Account_Parameters_Current.md` — used for risk % calculation |
| Posture | Market regime indicator driving risk scaling |
| STR -2 | Stock 20%+ below recent 44-day high — extra caution required |
| LogEntry | Pipe-delimited diagnostic line on TOS chart — authoritative over Final Verdict bar |
| 200-MA Penalty | V110 value trap filter — adjusts Fund tier based on distance below 200-day MA |
| P_800 Vault Interface | Authoritative Python interface for Obsidian writes — never construct paths directly |

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Flow

```
P_910 Daily Scan (green tickers only)
              |
              v
TOS Chart Review + Chaikin / VantagePoint confirmation
              |
              v
P_115 STEP 1 — Diagnostic Scoring
[FundamentalsTier + AnalysisTier + CandleTier + SetupScore]
[Fund Auto-Verification via stockanalysis.com if Fund>=2]
              |
         Verdict?
    BUY / ASYM / PASS
              |
    BUY or ASYM only
              v
P_115 STEP 2 — Position Sizing
[Posture re-read from P_010_RiskConfig.json — MANDATORY]
[Three-Gate: Risk / Cash / Concentration]
[Options viability check]
              |
              v
Trade Entry (TOS execution)
              |
              v
P_115 STEP 3 — Outcome Tracking
[27-column tracker row written via P_800 vault interface]
              |
              v
Performance Review (monthly)
```

### 2.2 Core Components

#### Component 1: P_910 Scan (Candidate Source)
- **Responsibility:** Generate daily list of dip candidates
- **Inputs:** TOS scan criteria (oversold, pullback conditions)
- **Outputs:** Green ticker list (red tickers rarely produce BUY signals — skip)
- **Tools Used:** ThinkorSwim
- **Key Rule:** Process GREEN tickers only — empirically validated

#### Component 2: P_115 Diagnostic Engine (Step 1)
- **Responsibility:** Score each candidate across 3 tiers → produce verdict
- **Inputs:** TOS chart with LogEntry diagnostic line OR user-pasted shorthand
- **Outputs:** Step1Verdict (BUY / ASYM / PASS) + 27-column row
- **Tools Used:** Claude AI + TOS V110 ThinkScript
- **Dependencies:** Scoring logic V110.x, Fund auto-verification (stockanalysis.com)

#### Component 3: Position Sizing Engine (Step 2)
- **Responsibility:** Calculate optimal position size within risk constraints
- **Inputs:** Entry price, ATR, Cash Slice, Account Balance, **live posture re-read**
- **Outputs:** Share count OR option contracts + TP/SL levels (stock + option prices)
- **Tools Used:** Claude AI + Windows-MCP PowerShell (posture re-read)
- **Dependencies:** Three-gate system, options viability check, V110.x penalty table

#### Component 4: Trade Tracking (Step 3)
- **Responsibility:** Log outcomes, maintain audit trail
- **Inputs:** Trade result from TOS / Schwab
- **Outputs:** Tracker row written via P_800 vault interface + Excel append
- **Tools Used:** Claude AI → `write_to_vault("P115", data)` → Obsidian + Excel tracker
- **Enforcement (NEW v1.0):** STEP 3 must call `write_to_vault()` — never construct paths directly. If vault write fails, log to Comments column and retry next session.

### 2.3 System Independence

P_115 operates as a **parallel independent system**. It is NOT a gatekeeper or master validator for other strategies.

```
P_115 ──────────────── Independent
P_116 ──────────────── Independent
P_117 ──────────────── Independent (optional P_115 recheck on request)
P_118 ──────────────── Independent (optional P_115 recheck on request)
P_300 ──────────────── Independent
```

Cross-validation between systems occurs **only on exception basis** when explicitly requested by Anthony. Never assume hierarchy.

### 2.4 Scoring Architecture Summary

```
FundamentalsTier (0-4)
  └─ ROE>15%=20pts, Debt/Cap<60%=15pts, FCF>0=10pts → base tier
  └─ 200-MA penalty applied → adjusted tier (decimals allowed)

CandleTier (0-3)
  └─ T3 = candle + vol + STR + RSI + MTF
  └─ T2 = candle + (vol OR STR OR RSI)
  └─ T1 = candle only
  └─ T0 = none

SetupScore (0-4)
  └─ 4 binary gates: CandleTier>=2 | ModScore>=70 | STR>0 | RSI>RSI[1]

AnalysisTier (1-4)
  └─ Mapped from SetupScore (>=4=T4, >=3=T3, >=2=T2, <2=T1)

HybridTier = AnalysisTier + Adjusted FundamentalsTier
  └─ >=6 → BUY
  └─ AsymmetricSetup conditions → ASYM
  └─ Neither → PASS
```

### 2.5 Design Rationale

**Why This Architecture?**
- **Simplicity:** Single ThinkScript indicator delivers LogEntry; Claude consumes structured shorthand
- **Claude-Centricity:** Diagnostic scoring, position sizing, and audit trail all run through Claude
- **Maintainability:** 27-column schema locked; changes require explicit version bump
- **Independence:** Operates in parallel with P_116/P_117/P_118/P_300 — no hierarchy
- **Hub-Routed Writes:** All Obsidian writes go through P_800 vault interface — eliminates path drift and schema violations

---

## 3. AI TOOLS & PLATFORMS

### 3.1 Tool Stack

| Tool / Platform | Role in System | Version / Tier | Notes |
|---|---|---|---|
| Claude.ai (Desktop) | Primary AI engine — analysis, decisions, output | Opus 4.7 | Core reasoning layer; Windows-MCP enabled |
| ThinkorSwim | Market data, charting, V110 LogEntry generation | Latest | Custom indicators: P_115_buyTheDipChart_V110, P_910, P_050, D_102 |
| Windows-MCP PowerShell | File I/O, posture re-read, config reads | Latest | Required for INIT and STEP 2 |
| Python (conda p140) | Vault writes, helpers | 3.x | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| P_800 Vault Interface | Obsidian write routing | v1.1 | `vault_interface.py` — authoritative |
| stockanalysis.com | Fund verification (ROE, Debt/Cap, FCF) | Web | Authoritative over TOS Fund value |
| Chaikin Analytics | Supplemental fundamental/sentiment | Web | Tripwire on Fund discrepancies |
| VantagePoint | ML grid/posture data (feeds P_010) | Latest | Optional supplemental |
| Excel | Tracker logging | Latest | 27-column tab-delimited |
| Obsidian | Trade journal vault | Latest | Written via P_800 vault interface |

### 3.2 Claude Project Configuration

| Setting | Value |
|---|---|
| Project Name | Trading System (P_115 active) |
| Knowledge Files | SESSION_INITIALIZATION_PROMPT.md, CLAUDE_ASSISTANT_INSTRUCTIONS, Tracker_Log_Schema, strategy guides, change logs |
| Memory Enabled | Yes |
| Session Init Required | Yes — paste prompt or type "INIT" at start |
| Primary Model | Claude Opus 4.7 |

### 3.3 Prompt Library (Master List)

#### Prompt: P_115 INIT
```
P_115 INIT
```
**Purpose:** Run STEP 0 environment detection, read account params, read posture, display session summary
**When to Use:** First message of every P_115 session
**Last Updated:** 2026-05-09 (v3.1 with STEP 0)

#### Prompt: STEP 1 Signal Analysis (shorthand)
```
P_115_STEP 1 [TICKER] [Fund] [Anal] [Candle] [Setup] [STR] [Verdict]
```
**Purpose:** Parse diagnostics, produce 27-column tracker row
**When to Use:** Per ticker after TOS chart review
**Last Updated:** 2026-05-23 (PASS vocabulary standardized)

#### Prompt: STEP 2 Position Sizing
```
STEP 2 [TICKER] Entry $X.XX Stop $X.XX Cash $X,XXX
```
**Purpose:** Re-read posture, run three-gate sizing, output TP/SL with stock+option prices
**When to Use:** After BUY or ASYM verdict
**Last Updated:** 2026-03-31 (v2.9 posture re-read mandatory)

#### Prompt: STEP 3 Outcome + Vault Write
```
STEP 3 [TICKER] [Outcome] [Exit Price] [Realized R:R]
```
**Purpose:** Update tracker row + call `write_to_vault("P115", data)` to Obsidian
**When to Use:** After position closed or end-of-day update
**Last Updated:** 2026-05-27 (P_800 vault interface enforcement added)

### 3.4 AI Behavior Rules & Constraints

**Claude MUST:**
- Always search project knowledge before answering P_115 questions
- Capture diagnostic values immediately when user pastes them
- Re-read `P_010_RiskConfig.json` before every STEP 2 sizing — INIT read is snapshot only
- Auto-verify Fund via stockanalysis.com on every BUY/ASYM with submitted Fund >= 2
- Run STEP 0 environment detection (tool_search probe) before any file reads on INIT
- Use 27-column tab-delimited output every row, every session
- Mark Step1Verdict as PASS (not "No Signal") for all rows logged from 2026-05-23 forward
- Route all Obsidian writes through P_800 `write_to_vault()` — never construct paths directly
- Parse LogEntry field positions explicitly before scoring (Symbol | Fund | Anal | Candle | Setup | STR | Verdict)

**Claude MUST NOT:**
- Fabricate diagnostic values or account balance
- Subtract from Cash Balance between trades (Cash Balance is per-trade buying power, not running total)
- Apply 5% concentration cap to options notional exposure (cap applies to premium paid)
- Skip STEP 2 or STEP 3 steps after a gate failure
- Auto-reject Fund=0 without distinguishing Cause A (BEAR/AVOID) vs Cause B (weak fundamentals + moderate penalty)
- Defer to Anthropic system prompt boilerplate for environment detection — only `tool_search` is authoritative
- Write directly to `trading_journal/` paths — use P_800 vault interface only

**Session Initialization:**
- Type "P_115 INIT" or paste SESSION_INITIALIZATION_PROMPT.md content at start
- Confirm STEP 0 result, account balance, posture, and trading mode in session summary

---

## 4. REQUIREMENTS

### 4.1 Functional Requirements

#### FR-1: Step 1 Diagnostic Processing
- **Description:** Parse user-pasted scan output or TOS chart LogEntry; produce scored verdict + tracker row
- **Acceptance Criteria:**
  - [ ] Fund/Anal/Candle/Setup values captured without loss
  - [ ] HybridTier calculated correctly
  - [ ] AsymmetricSetup logic checked
  - [ ] Verdict = BUY / ASYM / PASS
  - [ ] Full 27-column row output, tab-delimited
  - [ ] Fund auto-verification triggered on BUY/ASYM where Fund>=2
- **Component:** P_115 Diagnostic Engine
- **Priority:** High

#### FR-2: Step 2 Position Sizing
- **Description:** Calculate position size using three-gate system with live posture
- **Acceptance Criteria:**
  - [ ] Posture re-read from `P_010_RiskConfig.json` before gate calculation
  - [ ] All three gates calculated even on PASS outcome
  - [ ] Smallest gate wins
  - [ ] Options viability checked (spread ≤10% of mid, OI ≥150)
  - [ ] TP/SL shown for both stock AND option prices when options used
  - [ ] 5% concentration applied to premium paid (not notional) for options
- **Component:** Position Sizing Engine
- **Priority:** High

#### FR-3: Step 3 Outcome Tracking + Vault Write
- **Description:** Update tracker row with trade result; persist via P_800 vault interface
- **Acceptance Criteria:**
  - [ ] Outcome field updated: TP Hit / SL Hit / Pending / Partial Close
  - [ ] RecheckStatus updated
  - [ ] Comments updated with result context
  - [ ] `write_to_vault("P115", data, overwrite=False)` called successfully
  - [ ] Vault write success/failure noted in session output
- **Component:** Trade Tracking
- **Priority:** High

#### FR-4: Signal Integrity
- **Description:** Zero fabrication of diagnostic values
- **Acceptance Criteria:**
  - [ ] No invented Fund/Anal/Candle/Setup values
  - [ ] No assumed Account Balance
  - [ ] "--" used for unknown fields, never guessed values
  - [ ] LogEntry field positions read in correct order (Symbol | Fund | Anal | Candle | Setup | STR | Verdict)
- **Component:** All
- **Priority:** Critical

### 4.2 Non-Functional Requirements

#### NFR-1: Data Integrity
- **Requirement:** Zero tolerance for fabricated values
- **Target:** All outputs traceable to user-provided inputs or verified sources
- **Implementation:** Session prompt enforcement, memory rules, Fund auto-verify

#### NFR-2: Format Consistency
- **Requirement:** Output format identical across sessions
- **Target:** 27-column tab-delimited, same column order every row
- **Implementation:** Locked schema in project knowledge, validation checklist on first output

#### NFR-3: Auditability
- **Requirement:** Every signal traceable to source
- **Target:** SignalSource populated on every row; diagnostics captured in Comments; vault row persisted
- **Implementation:** Tracker schema enforcement + P_800 vault interface

#### NFR-4: Resilience
- **Requirement:** Graceful degradation when Windows-MCP unavailable
- **Target:** STEP 0 detection identifies environment; web fallback documented; vault writes deferred not lost
- **Implementation:** SESSION_INITIALIZATION_PROMPT v3.1 STEP 0; vault retry on next session

### 4.3 Requirements Matrix

| ID | Description | Component | Status | Notes |
|---|---|---|---|---|
| FR-1 | Step 1 diagnostic processing | Diagnostic Engine | Complete | V110.x scoring active |
| FR-2 | Step 2 position sizing | Sizing Engine | Complete | Posture re-read enforced v2.9+ |
| FR-3 | Step 3 outcome + vault write | Tracking | Complete | P_800 vault interface v1.1 enforced |
| FR-4 | Signal integrity | All | Complete | Fund auto-verify v3.0+ |
| NFR-1 | Data integrity | All | Complete | Multiple safeguards in place |
| NFR-2 | Format consistency | All | Complete | 27-column schema locked |
| NFR-3 | Auditability | All | Complete | Vault interface authoritative |
| NFR-4 | Resilience | INIT | Complete | STEP 0 detection v3.1 |

---

## 5. CHANGE LOG

> **Linked Document:** P_115_StrategyGuide_ChangeLog.md, STRATEGY_CHANGE_LOG_V110.md
> **Location:** Project Knowledge
> **Purpose:** Full version history from v9.1 through V110.x
> **Last Updated:** 2026-05-23 (PASS vocabulary standardization)

**Summary of major versions:**

| Version | Date | Key Change |
|---|---|---|
| v9.1 | Dec 2025 | Initial production release |
| v9.2 | Dec 17, 2025 | Critical scoring calibration fix — SetupScore ceiling, TierConflict removed, CandleTier 2 relaxed |
| v9.3 | Dec 18, 2025 | P_117 Ad-Hoc signals added, Cash Slice position sizing |
| v9.4 | Jan 2026 | Dual-tracking system, options R:R rule, 27-column lock |
| V110 | Feb 10, 2026 | 200-day MA distance penalty (value trap filter) |
| V110 Corrected | Feb 11, 2026 | Fixed 200-MA penalty — stocks at/above MA were incorrectly penalized |
| V110.1 | Apr 17, 2026 | Fund=0 auto-reject narrowed to falling knife only (Cause A vs Cause B) |
| V110.2 | Apr 22, 2026 | Fund auto-verification rule (P_115 BUY/ASYM, stockanalysis.com authoritative) |
| V110.2 | Apr 27, 2026 | Fund auto-verification scope expanded to all strategies |
| V110.3 | May 8, 2026 | Post-earnings auto-flag rule (3-session stabilization window) |
| INIT v3.1 | May 9, 2026 | STEP 0 environment detection added |
| Vault v1.1 | May 23, 2026 | PASS vocabulary standardized (replaces "No Signal" going forward) |

---

## 6. ERROR CORRECTIONS LOG

*Errors are never deleted. Marked Resolved only. P_115-scoped errors only.*
*Numbered EC-001 onward in chronological order of discovery.*

### 6.1 Summary Table

| ID | Description | Status | Resolution |
| :---- | :---- | :---- | :---- |
| EC-001 | v9.1 Scoring — Mathematically Impossible Thresholds | Fixed | v9.2 calibration — SetupScore ceiling locked, TierConflict removed, CandleTier 2 relaxed |
| EC-002 | Account Balance Confusion | Fixed | `P_000_Account_Parameters_Current.md` created as authoritative source |
| EC-003 | Options Concentration Applied to Notional Exposure | Fixed | 5% cap applies to premium paid only; rule locked in session prompt |
| EC-004 | Option TP/SL Showing Stock Price Only | Fixed | Delta-based stock→option translation required on every options trade |
| EC-005 | 200-MA Penalty Applied to Healthy Stocks (V110 initial) | Fixed | V110 Corrected — NORMAL zone (at/above or 0-3% below) = 0.0 penalty |
| EC-006 | UGRO Posture Re-Read Failure | Fixed | Posture re-read mandatory before every STEP 2 (v2.9) |
| EC-007 | Fund=0 Over-Rejection — Cause A vs Cause B | Fixed | V110.1 — auto-reject only when STR=-2 + Fund=0 together (falling knife) |
| EC-008 | AEO Fund Trust Failure (TOS Data Unreliable) | Fixed | Fund auto-verification via stockanalysis.com on BUY/ASYM with Fund>=2 (v3.0) |
| EC-009 | Post-Earnings False BUY — AMN/ASND | Fixed | 3-session post-earnings stabilization auto-flag (V110.3) |
| EC-010 | STEP 0 Environment Detection Failure | Fixed | tool_search probe mandatory before file reads (INIT v3.1) |
| EC-011 | LogEntry Field Order Misinterpretation — MRAM/POET/AAOI | Fixed | Explicit field-position parse required before scoring; reference cases added |

---

### 6.2 Detailed Error Entries

---

### EC-001: v9.1 Scoring — Mathematically Impossible Thresholds
- **Date Discovered:** 2025-12-17
- **Severity:** Critical
- **Status:** Resolved

**Wrong Behavior:**
SetupScore ceiling = 4, but AnalysisTier thresholds required 5-6. TierConflict veto blocked valid signals. CandleTier 2 required ALL conditions (candle + volume + STR + RSI). System was generating ~40 PASS verdicts from batches that should have produced 6 actionable Buys.

**Correct Behavior:**
- SetupScore ceiling = 4 (locked)
- AnalysisTier mapping: >=4=T4, >=3=T3, >=2=T2, <2=T1
- TierConflict veto removed
- CandleTier 2 relaxed: candle + ANY ONE of (volume / STR / RSI rising)

**Root Cause:** Initial v9.1 calibration error — thresholds set without verifying ceiling math.

**Fix Applied:**
- v9.2 released Dec 17, 2025 with corrected calibration
- Project knowledge updated with new tier mapping
- Validation against known examples: MOD 3-3-2-3 BUY, ATI 3-2-2-3 BUY

**Verification:** Run STEP 1 against MOD 3-3-2-3 → expect BUY verdict. Run against any 2-2-1-2 → expect PASS.

---

### EC-002: Account Balance Confusion
- **Date Discovered:** 2026-01-23
- **Severity:** Critical
- **Status:** Resolved

**Wrong Behavior:**
Using "Cash Balance" as account balance. Defaulting to $20,000 when account balance unknown. Tracking running cash total across trades.

```
Example wrong logic:
"Available cash: $20,000 → after trade 1 ($5,000) = $15,000 → after trade 2 ($3,000) = $12,000"
```

**Correct Behavior:**
- Account Balance = sourced from `P_000_Account_Parameters_Current.md` (monthly review)
- Cash Balance = user-provided buying power per trade, independent value
- These are independent — Claude never subtracts or tracks cash between trades

```
Correct logic:
"Account Balance: $32,812 (per P_000 config)
 Cash Balance for this trade: $5,000 (user-provided)
 Risk Capital = $32,812 × 1.5% = $492.18"
```

**Root Cause:** Conflation of "Cash" and "Account" in initial prompt; no authoritative parameter file at the time.

**Fix Applied:**
- `P_000_Account_Parameters_Current.md` created as authoritative source
- SESSION_INITIALIZATION_PROMPT updated to read this file at INIT
- Memory rule stored: Cash Balance ≠ Account Balance

**Verification:** Type "P_115 INIT" → confirm session summary shows account balance from config file, not assumed $20,000.

---

### EC-003: Options Concentration Limit Applied to Notional Exposure
- **Date Discovered:** 2026-01-23
- **Severity:** Critical
- **Status:** Resolved

**Wrong Behavior:**
Applying 5% max ($1,640.60 at current balance) to notional stock exposure of options contracts.

```
Example wrong logic:
"19 contracts × $97.21 strike × 100 = $184,699 notional → exceeds 5% cap, REJECT"
```

**Correct Behavior:**
5% limit applies to **premium paid only**, not notional.

```
Correct logic:
"19 contracts × $0.265 premium × 100 = $503.50 premium paid → within 5% cap ($1,640.60), APPROVE"
```

**Root Cause:** Confusing options exposure mechanics with stock concentration mechanics in initial sizing logic.

**Fix Applied:**
- `POSITION_SIZING_THREE_GATE_REFERENCE.md` updated
- Rule added to session initialization prompt
- 5% premium cap breach → automatic fallback to stock-only sizing

**Verification:** Run STEP 2 on any options trade → concentration check must reference premium paid, not contracts × strike × 100.

---

### EC-004: Option TP/SL Showing Stock Price Only
- **Date Discovered:** 2026-01-23
- **Severity:** High
- **Status:** Resolved

**Wrong Behavior:**
Outputting TP/SL as stock prices only when trade was in options:

```
TP: $122.49 / SL: $92.07
```

**Correct Behavior:**
Show both stock price AND calculated option price using delta:

```
Entry: Stock $102.21 → Option $9.30
Take Profit: Stock $122.49 → Option ~$17.50 (+88% gain)
Stop Loss: Stock $92.07 → Option ~$0 (-100% loss, max risk $930)
```

**Root Cause:** Initial sizing logic didn't include delta-based price translation for options.

**Fix Applied:**
- Rule locked in memory and SESSION_INITIALIZATION_PROMPT
- Delta-based calculation required every time options are used
- `OPTIONS_RISK_METHODOLOGY.md` created with chart-based delta translation as primary method

**Verification:** Run STEP 2 with options selected → confirm output shows "Stock $X.XX → Option $X.XX" on both TP and SL rows.

---

### EC-005: 200-MA Penalty Applied to Healthy Stocks (V110 Initial Release)
- **Date Discovered:** 2026-02-11
- **Severity:** High
- **Status:** Resolved

**Wrong Behavior:**
Stocks at/above 200-MA and stocks 0-3% below 200-MA received -0.5 penalty in V110 initial release. Resulted in false Fund downgrades on healthy positioning.

**Correct Behavior:**
Authoritative penalty table (V110 Corrected):

```
Zone          Distance from 200-MA     Penalty
---------------------------------------------------
NORMAL        At/above OR 0-3% below   0.0
PULLBACK      3-10% below              -1.0
CORRECTION    10-20% below             -2.0
BEAR/AVOID    >20% below               -4.0 (auto-reject)
```

**Root Cause:** Initial V110 release penalized 200-MA testing (-2%) as if it were vulnerability, when in fact support testing is healthy behavior.

**Fix Applied:**
- V110 Corrected released Feb 11, 2026
- Any stocks rejected Feb 10-11 should be rechecked
- ThinkScript updated to display correct penalty zones

**Verification:** Stock at -2% from 200-MA → Fund tier should equal base Fund (no penalty). Stock at -15% → Fund tier = base − 2.

---

### EC-006: UGRO Posture Re-Read Failure
- **Date Discovered:** 2026-03-31
- **Severity:** Critical
- **Status:** Resolved

**Wrong Behavior:**
UGRO sized at OFF mode (50% risk reduction, simulation-only) using posture from INIT-time read. P_010 automation had already upgraded posture to HALF (75% cap, live entries permitted) intraday. Trade was either under-sized or wrongly flagged as simulation when it should have been live at reduced risk.

```
Wrong sequence:
INIT (8:30 AM): risk_mode = OFF → noted in session summary
STEP 2 (11:45 AM): used OFF parameters from memory → 50% cap, simulation-only
Actual posture at 11:45 AM: risk_mode = HALF (upgraded 10:15 AM)
```

**Correct Behavior:**
Re-read `P_010_RiskConfig.json` immediately before every STEP 2 calculation. INIT read is session summary only — NOT authoritative for trade sizing.

```
Correct sequence:
INIT (8:30 AM): risk_mode = OFF → noted in session summary as snapshot
STEP 2 (11:45 AM): re-read P_010_RiskConfig.json → risk_mode = HALF → apply HALF parameters
Flag in output: "Posture upgraded since INIT: OFF → HALF"
```

**Root Cause:** Original workflow read posture once at INIT and held it for the entire session. P_010 automation runs intraday updates, so any STEP 2 after a posture change used stale data.

**Fix Applied:**
- SESSION_INITIALIZATION_PROMPT v2.9 (Mar 31, 2026) — mandatory posture re-read rule
- CLAUDE_ASSISTANT_INSTRUCTIONS v2.2 (Mar 31, 2026) — mirrors v2.9 rule
- PowerShell command standardized:
  `Get-Content "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json" -Raw | ConvertFrom-Json | ConvertTo-Json`
- Re-read happens before any gate calculation

**Verification:** Run two STEP 2 calls in same session with simulated posture change between them → confirm second call reflects new posture, not stale INIT snapshot.

---

### EC-007: Fund=0 Over-Rejection — Cause A vs Cause B
- **Date Discovered:** 2026-04-17
- **Severity:** High
- **Status:** Resolved

**Wrong Behavior:**
Auto-rejecting all Fund=0 signals as falling knives, regardless of cause. This rejected legitimate signals where base Fund was weak (=1) and a moderate 200-MA penalty (-1.0 PULLBACK) brought the adjusted Fund to 0 — these were not in BEAR/AVOID territory and should not have been auto-rejected.

```
Wrong logic:
"Fund=0 in LogEntry → AUTO-REJECT (falling knife, no analysis)"
Applied to: base Fund=1 + PULLBACK -1.0 = 0 (legitimate scan result, not BEAR/AVOID)
```

**Correct Behavior:**
Distinguish two causes:

```
CAUSE A — BEAR/AVOID Zone (>20% below 200-MA) → AUTO-REJECT
  Penalty = -4.0 wipes any base tier
  Identifier: STR=-2 AND Fund=0 together
  Action: Flag falling knife, no further analysis
  Log: SimulationNotes = "Fund=0 auto-reject -- stock >20% below 200-MA"

CAUSE B — Weak Fundamentals + Moderate Penalty → FLAG FOR REVIEW
  Example: base Fund=1 + PULLBACK -1.0 = adjusted 0 (NOT a falling knife)
  Identifier: Fund=0 with STR > -2
  Action: Manual review, verify 200-MA position before trading
  Log: RecheckStatus=Watch, SimulationNotes="Fund=0 weak-fundamental scan result"
```

**Root Cause:** Initial V110 rule treated Fund=0 as a single category. P_115 scan targets small/mid-cap growth (10M mktcap, 1M vol) where weak Fund scores are common and do not automatically indicate falling knife territory.

**Fix Applied:**
- V110.1 released Apr 17, 2026
- Authoritative penalty table published (NORMAL/PULLBACK/CORRECTION/BEAR-AVOID)
- SESSION_INITIALIZATION_PROMPT Fund=0 handling section updated
- Batch processing logic added: STR=-2 + Fund=0 → Cause A; otherwise → Cause B

**Verification:** Stock at -25% from 200-MA with strong base Fund → auto-reject (Cause A). Stock at -7% with weak base Fund=1 → flag for review, not auto-reject (Cause B).

---

### EC-008: AEO Fund Trust Failure (TOS Fund Data Unreliable)
- **Date Discovered:** 2026-04-21
- **Severity:** Critical
- **Status:** Resolved

**Wrong Behavior:**
Trusted TOS-displayed Fund=4 for AEO on 4/21/2026. Entered position. Live stockanalysis.com data showed actual V110 Fund=2 (ROE 10.73%, below 15% threshold = 20 points lost). Correct HybridTier should have been 3 (PASS), not 5 (BUY). Trade fired that should not have under V110 rules; -44% unrealized next session.

```
Wrong sequence:
LogEntry: AEO | 4 | 3 | 2 | 3 | 0 | BUY → trusted as-is
HybridTier = 4 + 3 = 7 → BUY → traded
Actual: ROE=10.73% (fails 15% threshold) → base Fund=2 → HybridTier=5 → PASS
```

**Correct Behavior:**
Auto-verify Fund via stockanalysis.com on every P_115 BUY/ASYM where submitted Fund >= 2:

```
1. Pull live ROE, Debt/Capital, FCF from stockanalysis.com/stocks/[ticker]/financials/ratios/
2. Recompute Fund per V110 thresholds:
   - ROE > 15%: 20 pts (else 0)
   - Debt/Capital < 60%: 15 pts (else 0)
   - FCF > 0: 10 pts (else 0)
   - Base tier mapping: 40-45=4, 30-39=3, 20-29=2, 10-19=1, 0-9=0
3. Apply 200-MA penalty if known
4. If recomputed Fund is >1 tier below submitted: FLAG BEFORE STEP 2
5. Do NOT proceed to position sizing until user resolves discrepancy
```

**Root Cause:** TOS Fund data pipeline is unreliable for ROE/Debt/FCF inputs. No verification layer existed before live trade entry.

**Fix Applied:**
- V110.2 released Apr 22, 2026 (initial P_115-only scope)
- V110.2 expanded Apr 27, 2026 to all strategies (P_115, P_116, P_117, P_118) after AMGN P_117 ASYM showed same failure mode
- SESSION_INITIALIZATION_PROMPT v3.0 (Apr 22, 2026) — Fund Verification Rule
- CLAUDE_ASSISTANT_INSTRUCTIONS v2.3/v2.4 — same rule mirrored
- Chaikin Analytics added as tripwire (veto only, not trigger)
- Cost: ~10 seconds per BUY signal; zero cost on PASS rows

**Verification:** Run STEP 1 on any BUY signal with Fund>=2 → confirm Claude performs web search and re-derives Fund before producing STEP 2. Submitted Fund=4, recomputed Fund=2 → STEP 2 must NOT proceed; flag displayed.

---

### EC-009: Post-Earnings False BUY Signals — AMN/ASND
- **Date Discovered:** 2026-05-08
- **Severity:** High
- **Status:** Resolved

**Wrong Behavior:**
On 5/8/2026, P_920 batch (AMN, ASND, others) produced BUY signals where the price action driving the BUY was an earnings reaction gap. These were not durable setups — they were earnings-day volatility that would mean-revert within 2-3 sessions.

```
Wrong sequence:
AMN: earnings 5/7 → 5/8 LogEntry shows BUY signal driven by earnings gap
Traded → reverted 5/9-5/10 (typical post-earnings dynamics)
```

**Correct Behavior:**
On every BUY/ASYM across all strategies, auto-flag if ticker has earnings within last 3 trading sessions. Pull earnings date during existing Fund auto-verify pass (zero added cost). Mark as Watch/PASS pending stabilization.

```
Correct rule:
If earnings date is within 3 trading sessions of signal date:
  - Flag: "POST-EARNINGS: stabilization required (X sessions since report)"
  - Default action: Watch (do not trade)
  - Override: User can explicitly proceed with reduced size
```

**Root Cause:** No earnings-date awareness in scoring pipeline. Initial attempt to add HasEarnings filter at scan layer (P_920 V2.1) failed due to TOS Stock Hacker limitation. Rule moved to assistant review layer where it succeeded.

**Fix Applied:**
- V110.3 released May 8, 2026
- CLAUDE_ASSISTANT_INSTRUCTIONS v2.5 — Post-Earnings Auto-Flag Rule mandatory on BUY/ASYM
- 3-session stabilization window required from earnings date
- Earnings date pulled during Fund auto-verify pass (no separate query)

**Verification:** Run STEP 1 on ticker with earnings yesterday → confirm flag displayed and default action is Watch, not BUY. Trade only proceeds with explicit user override.

---

### EC-010: STEP 0 Environment Detection Failure
- **Date Discovered:** 2026-05-09
- **Severity:** High
- **Status:** Resolved

**Wrong Behavior:**
Claude refused to execute INIT file reads, claiming it was on claude.ai web environment based on Anthropic system prompt boilerplate text reading "web or mobile chat interface". Windows-MCP was actually loaded and fully functional. User had to manually correct Claude before INIT could proceed.

```
Wrong sequence:
User: "P_115 INIT"
Claude: "I'm on claude.ai web, cannot read your local files. Please paste them."
Actual environment: Claude Desktop with Windows-MCP loaded → could have read files
```

**Correct Behavior:**
Run `tool_search` probe as STEP 0 before any file reads. Decide environment from result, not from system prompt boilerplate:

```
STEP 0:
  Run tool_search(query="powershell windows")
  Outcome A — Windows-MCP:PowerShell present in results:
    → Claude Desktop → proceed with STEP 1 file reads
  Outcome B — Windows-MCP:PowerShell absent:
    → claude.ai web → display: "Environment: claude.ai web -- Windows-MCP unavailable"
    → Ask user to switch to Desktop or paste files manually

NEVER claim "I am on web" without first running tool_search.
NEVER claim "I cannot read your files" without first running tool_search.
NEVER defer to system prompt boilerplate for environment detection.
```

**Root Cause:** The Anthropic system prompt contains generic boilerplate text reading "web or mobile chat interface" in BOTH Desktop and web environments. That text is NOT a reliable environment signal. Only `tool_search` for Windows-MCP availability is authoritative.

**Fix Applied:**
- SESSION_INITIALIZATION_PROMPT v3.1 (May 9, 2026)
- STEP 0 added as mandatory first step before file reads
- Trigger case study documented inline in v3.1 changelog

**Verification:** Type "P_115 INIT" on Claude Desktop → confirm STEP 0 runs tool_search, identifies Windows-MCP availability, proceeds to STEP 1 file reads without prompting user.

---

### EC-011: LogEntry Field Order Misinterpretation — MRAM/POET/AAOI
- **Date Discovered:** 2026-05-27
- **Severity:** Critical
- **Status:** Resolved

**Wrong Behavior:**
On 5/27/2026 P_115 batch (MRAM, POET, AAOI), Claude misread the LogEntry field positions and applied Fund=0 auto-reject when the value in position 2 was actually a different field. All three tickers initially output PASS based on this misread. Error caught and corrected during the same session.

```
Wrong sequence:
LogEntry: MRAM | [value1] | [value2] | [value3] | [value4] | [value5] | [verdict]
Claude misread position 2 as STR or another field
Treated position 2 value as Fund=0 → auto-reject Cause A
All three tickers wrongly PASSed
```

**Correct Behavior:**
LogEntry field positions are LOCKED (V110 standard):

```
Position 1: Symbol
Position 2: FundamentalsTier (ADJUSTED — includes 200-MA penalty)
Position 3: AnalysisTier
Position 4: CandleTier
Position 5: SetupScore
Position 6: STR flag (SellTheRip)
Position 7: Verdict (BUY / ASYM / NO)

Format: LogEntry: [SYMBOL] | [Fund] | [Anal] | [Candle] | [Setup] | [STR] | [Verdict]
Example: LogEntry: CYTK | 2 | 3 | 2 | 3 | 0 | BUY

LogEntry is authoritative over Final Verdict bar (display artifact conflicts must be flagged).
```

**Root Cause:** No explicit field-order reference in active session memory. Field positions were documented in SESSION_INITIALIZATION_PROMPT but Claude did not cross-reference before parsing. Compounding factor: similarity of single-digit values across positions makes misreads possible when not explicitly anchored to schema.

**Fix Applied:**
- Section 1.5 definitions now include LogEntry field order explicitly
- Section 8.1 STEP 1 workflow updated to require explicit field-position confirmation before scoring
- This document (v1.0) references SESSION_INITIALIZATION_PROMPT LogEntry EXTRACTION PROTOCOL
- Validation against known examples added to STEP 1 checklist: MRAM/POET/AAOI 5/27 corrected outputs become reference cases

**Verification:** Run STEP 1 on any LogEntry → confirm Claude states field-position parse explicitly (e.g., "Symbol=X, Fund=Y, Anal=Z, ...") before applying scoring logic. Misread triggers visible flag.

---

## 7. ENHANCEMENT LOG

### Active Enhancements

#### Enhancement: Z-Score Regime Council Integration
- **Status:** Planned — Phase 1 pilot September 2026
- **Priority:** High
- **Target Date:** Q3 2026
- **Description:** Add Z-Score pre-filter before full P_115 diagnostic run. Reads sumZZ, Regime, CMF_Z, OBV_Z from TOS overlay. GREEN/YELLOW/RED light gates candidates before 5-minute P_115 analysis.
- **Expected Benefit:** Faster batch processing; eliminates clearly-not-ready candidates before full scoring
- **Dependencies:** Z_SCORE_INTEGRATION_SPEC.md (v1.0 complete)
- **Success Criteria:** 20%+ reduction in time spent on PASS-bound candidates

#### Enhancement: Morning Star Pattern (PA6)
- **Status:** Planned
- **Priority:** Medium
- **Target Date:** Q3 2026
- **Description:** Add Morning Star candle pattern recognition to P_115 candle tier scoring
- **Expected Benefit:** Capture bullish reversal setups currently missed
- **Dependencies:** PA4 (DZC) and PA5 (RRR) precede in queue

#### Enhancement: Python Excel Auto-Logger (openpyxl)
- **Status:** In Development
- **Priority:** High
- **Target Date:** Q3 2026
- **Description:** Automate 27-column tracker row writes to Excel via openpyxl. Eliminates copy-paste step.
- **Expected Benefit:** Reduces manual error risk; precursor to Schwab API integration
- **Dependencies:** None
- **Success Criteria:** Zero column misalignment events over 30 trade sample

### Completed Enhancements

| Enhancement | Completed Date | Result |
|---|---|---|
| 200-MA Penalty System (V110) | Feb 10-11, 2026 | Value trap filter active; FISV-class entries blocked |
| Fund Auto-Verification | Apr 22, 2026 | AEO-class failures prevented; expanded to all strategies Apr 27 |
| Posture Re-Read Rule | Mar 31, 2026 | UGRO-class sizing errors eliminated |
| Post-Earnings Auto-Flag | May 8, 2026 | AMN/ASND-class false BUYs prevented |
| STEP 0 Environment Detection | May 9, 2026 | INIT refusal-on-web-claim eliminated |
| PASS Vocabulary Standardization | May 23, 2026 | Tracker entries use BUY/ASYM/PASS going forward |
| P_800 Vault Interface v1.1 | May 23, 2026 | Authoritative path construction for Obsidian writes |
| P_800 Workflow Enforcement | May 27, 2026 | STEP 3 must call `write_to_vault()`; checklist enforced |

### Parked / Deferred

| Enhancement | Reason Deferred | Revisit Date |
|---|---|---|
| Schwab API Integration | Excel auto-logger must complete first | Q4 2026 |
| PA7 (Evening Star), PA8 (Three White Soldiers) | PA4/PA5/PA6 precede in queue | 2027 |

---

## 8. AI WORKFLOWS & PROCESSES

### 8.1 Primary Workflow: P_115 Daily Signal Generation

**Trigger:** Morning P_910 scan results available
**Frequency:** Daily
**Time Required:** 30-45 minutes for 5-10 candidates

**Steps:**
1. Run P_910 scan in TOS; export green ticker list
2. Open Claude Desktop, type "P_115 INIT" → confirm STEP 0, account, posture
3. For each green ticker: review TOS chart with V110 ThinkScript → capture LogEntry
4. Paste shorthand: `P_115_STEP 1 [TICKER] [Fund] [Anal] [Candle] [Setup] [STR] [Verdict]`
5. Verify Claude parses field positions explicitly before scoring
6. For BUY/ASYM with Fund>=2: confirm Fund auto-verification triggered
7. Review 27-column row output; verify tab-delimited format
8. For BUY/ASYM signals only: proceed to STEP 2 with entry/stop/cash

**Expected Output:**
- 27-column tab-delimited row per ticker (BUY / ASYM / PASS)
- Distribution summary at end of batch
- Validation checklist on first output

**Decision Gate:**
```
If Step1Verdict = BUY → proceed to STEP 2
If Step1Verdict = ASYM → proceed to STEP 2 with reduced sizing
If Step1Verdict = PASS → log row, no STEP 2 needed
If Fund verification fails → STOP, hold for user resolution
If post-earnings flag triggers → default Watch, override only on explicit user direction
```

### 8.2 Secondary Workflow: Position Sizing (STEP 2)

**Trigger:** BUY or ASYM verdict from STEP 1
**Frequency:** Per qualifying signal
**Time Required:** 3-5 minutes

**Steps:**
1. User provides: Entry price, Stop price, Cash Balance for this trade
2. Claude re-reads `P_010_RiskConfig.json` via Windows-MCP — MANDATORY
3. Apply current risk_mode to all gate calculations
4. Calculate three gates: Risk-based / Cash availability / Concentration cap
5. Smallest gate wins
6. If options selected: verify spread<=10% of mid, OI>=150, options R:R >= stock R:R
7. Output TP/SL with stock price AND option price translation (if options)
8. R:R minimum check: 2:1 to T1 or T2 (T2-trail-only acceptable when T1 fails)

**Expected Output:**
- Position size (shares or contracts)
- TP1 / TP2 levels with stock + option prices
- SL level with stock + option prices
- R:R calculation for both stock and option scenarios
- Posture flag if changed since INIT

### 8.3 Review Workflow: Daily Trade Outcome (STEP 3) — P_800 Enforcement

**Trigger:** End of trading day or position closed
**Frequency:** Daily
**Time Required:** 5-10 minutes

**Steps:**
1. Pull trade results from TOS / Schwab
2. For each open trade: update RecheckStatus, Comments
3. For each closed trade: update Outcome (TP Hit / SL Hit / Partial Close), realized R:R
4. **MANDATORY:** Write to vault via P_800 interface:
   ```python
   from shared_resources.python_utils.vault_interface import write_to_vault
   write_to_vault("P115", data, overwrite=False)
   ```
5. Append to Excel tracker (tab-delimited paste)
6. Verify vault write success in session output; if failure, log to Comments and queue for retry next session

**Prompt Template:**
```
STEP 3 [TICKER] [Outcome] [Exit Price] [Realized R:R]
```

**Vault Write Rules (P_800 v1.1):**
- Schema keys: P115, P300, P020, P400, KB
- Dates ISO format
- Omit unknown fields (do not pad with `--` in vault payload)
- `signal_source` auto-set by interface
- `market_direction` = P_010 `risk_mode` JSON only (FULL/HALF/OFF); HOT is derived, never in JSON
- Never construct paths or write to `trading_journal/` directly

### 8.4 Exception Workflows

#### Exception: Fund verification discrepancy
- **Trigger:** Recomputed Fund is >1 tier below submitted Fund
- **Action:** STOP. Display "FUND VERIFICATION FAILED: submitted=X, recomputed=Y (reason)". Do NOT proceed to STEP 2.
- **Documentation:** User resolves (accept recomputed, override with justification, or abort). Note in Comments column.

#### Exception: LogEntry vs Final Verdict bar conflict
- **Trigger:** TOS chart shows conflicting values between LogEntry (top-right) and Final Verdict bar
- **Action:** LogEntry is authoritative. Flag conflict, note in Comments as "display artifact".
- **Documentation:** Capture screenshot if persistent; report to TOS ThinkScript maintainer.

#### Exception: Posture changed since INIT
- **Trigger:** Posture re-read at STEP 2 shows different risk_mode than INIT snapshot
- **Action:** Apply new risk_mode. Flag in output: "Posture upgraded/downgraded since INIT: X → Y"
- **Documentation:** Update MarketDirection column to new risk_mode value.

#### Exception: Vault write failure (P_800)
- **Trigger:** `write_to_vault()` raises exception or returns failure
- **Action:** Capture error in session output; do not silently skip. Note in tracker Comments: "Vault write failed [DATE] — retry next session"
- **Documentation:** If failure persists 2+ sessions, escalate to P_800 maintainer (check `vault_interface.py` v1.1 spec)

#### Exception: Signal flipped during processing
- **Trigger:** BUY signal becomes PASS during batch processing (e.g., chart updates)
- **Action:** Retain in log with RecheckStatus="Flipped"
- **Documentation:** SimulationNotes describes the flip reason

---

## 9. DATA DESIGN

### 9.1 Data Inputs

| Data Type | Source | Format | How Fed to Claude |
|---|---|---|---|
| TOS chart with LogEntry | ThinkorSwim V110 ThinkScript | Visual chart + LogEntry text | Screenshot or shorthand paste |
| Scan results | P_910 (TOS scan) | Ticker list | Paste into prompt |
| Account parameters | `P_000_Account_Parameters_Current.md` | Markdown | Windows-MCP PowerShell read |
| Posture | `P_010_RiskConfig.json` | JSON | Windows-MCP PowerShell read |
| Fund verification | stockanalysis.com | Web (HTML) | web_search / web_fetch |
| Cash Balance | User-provided per trade | Numeric value | Paste in STEP 2 prompt |

### 9.2 Data Outputs

| Output Type | Format | Destination | Frequency |
|---|---|---|---|
| Step1 verdict + diagnostics | Tab-delimited row, 27 columns | Excel tracker + Obsidian vault (via P_800) | Per signal |
| Position sizing | Formatted text + R:R table | Manual entry into TOS | Per BUY/ASYM |
| Outcome update | Vault row update | Obsidian via `write_to_vault("P115", data)` | Per closed trade |
| Distribution summary | Formatted text | Chat output | End of batch |
| Validation checklist | Bracketed [OK] checklist | Chat output | First output of session |

### 9.3 Data Schema

> **Linked Document:** Tracker_Log_Schema_v9_4_0_1.md
> **Location:** Project Knowledge
> **Purpose:** Full 27-column schema with valid values per field
> **Last Updated:** 2026-01

**Schema Name:** P_115 Trade Tracker
**Version:** v9.4.1
**Column count:** 27 (locked)

**Column order (locked):**
```
1.  Date
2.  Symbol
3.  SignalSource
4.  Step1Verdict
5.  PatternType
6.  BreakoutVerdict
7.  BreakoutVolumeMultiple
8.  DistributionDayCount
9.  FollowThroughDay
10. MarketDirection
11. RSvsSPY
12. FundamentalsTier
13. AnalysisTier
14. CandleTier
15. SetupScore
16. LiquidityTier
17. Traded
18. EntryPrice
19. TPLevel
20. SLLevel
21. StopLevel
22. RiskPct
23. AccountBalance
24. Outcome
25. RecheckStatus
26. SimulationNotes
27. Comments
```

**Schema Rules:**
- Column order is locked — never reorder
- All 27 columns required on every row, including PASS rows
- Symbol column = ticker only (e.g., ATOM, IBKR) — never expand with company name (breaks P_020 join keys)
- Date format: M/D/YYYY
- MarketDirection = risk_mode value from P_010 JSON (OFF/STANDARD/HOT), not narrative labels
- SignalSource = strategy code only (P_115); scan source goes in Comments as "Source: P_910"
- PatternType / BreakoutVerdict = "--" for P_115 (these belong to P_118)
- Step1Verdict values: BUY / ASYM / PASS (PASS replaces "No Signal" as of 2026-05-23)

### 9.4 Data Integrity Rules

- Never fabricate values — if unknown, use "--" with reason in Comments
- Capture Fund/Anal/Candle/Setup values immediately when pasted
- All outputs tab-delimited inside code blocks for Excel compatibility
- LogEntry field positions parsed in explicit order (Symbol | Fund | Anal | Candle | Setup | STR | Verdict)
- Fund value displayed = adjusted Fund (decimals allowed post-V110)
- Cash Balance is per-trade — never subtracted between trades
- Obsidian writes go through P_800 vault interface — never direct path construction

---

## 10. TESTING & VALIDATION

### 10.1 Testing Approach

**Philosophy:** Claude outputs validated against known examples before accepting as correct. Reference cases anchor expected behavior.

#### Manual Validation (Claude Outputs)
- **Method:** Compare Claude output to known-good examples documented in 10.2
- **Frequency:** First output of each new session
- **Pass Criteria:** All fields match expected format and logic

#### Backtesting (Historical Signals)
- **Data Period:** Trades logged from Dec 2025 forward
- **Method:** Run STEP 1 on archived LogEntry strings, compare to original verdicts
- **Performance Threshold:** Win rate >= 55%, average R:R >= 1.8:1 on closed trades

### 10.2 Known-Good Reference Examples

#### Example 1: MOD BUY signal (v9.2 calibration)
**Input:**
```
P_115_STEP 1 MOD 3 3 2 3 0 BUY
```
**Expected Output:** Verdict = BUY (HybridTier = 3 + 3 = 6, meets threshold)
**Notes:** Standard mid-range BUY, no asymmetric path needed

#### Example 2: ATI BUY signal (v9.2 calibration)
**Input:**
```
P_115_STEP 1 ATI 3 2 2 3 0 BUY
```
**Expected Output:** Verdict = BUY via ASYM path (Anal=2 just below, Fund=3 — verify MTF/wickAlign/rsiBounce4H confirms)
**Notes:** Edge case — verify ASYM conditions met

#### Example 3: Fund=0 BEAR/AVOID (Cause A)
**Input:**
```
P_115_STEP 1 FISV-style 0 3 2 3 -2 NO
```
**Expected Output:** Auto-reject (STR=-2 + Fund=0 = Cause A falling knife)
**Notes:** No further analysis; SimulationNotes documents BEAR/AVOID zone

#### Example 4: AEO Fund Verification Failure
**Input:**
```
P_115_STEP 1 AEO 4 3 2 3 0 BUY (submitted)
```
**Expected Output:** Fund auto-verify triggers → recomputed Fund=2 (ROE 10.73%) → FLAG "FUND VERIFICATION FAILED: submitted=4, recomputed=2"
**Notes:** STEP 2 must NOT proceed until user resolves

### 10.3 Validation Checklist (Run at Session Start)

```
[ ] STEP 0 environment detection passed (Windows-MCP available)
[ ] Account balance matches P_000_Account_Parameters_Current.md
[ ] Posture loaded from P_010_RiskConfig.json
[ ] Trading mode confirmed (OFF / STANDARD / HOT)
[ ] Column order correct (27 columns, locked order)
[ ] No stray dashes after SignalSource
[ ] Tab-delimited format
[ ] 200-MA penalty applied correctly (V110.1 table)
[ ] Fund tier shows adjusted value (decimals allowed)
[ ] Step1Verdict vocabulary = BUY / ASYM / PASS (not "No Signal")
[ ] LogEntry field positions parsed explicitly before scoring
[ ] Posture re-read scheduled before STEP 2
[ ] Fund auto-verification ready for BUY/ASYM with Fund>=2
[ ] Post-earnings auto-flag ready
[ ] P_800 vault interface available for STEP 3 writes
```

### 10.4 Known Issues & Limitations

| Issue ID | Description | Severity | Workaround | Status |
|---|---|---|---|---|
| P115-001 | MCP timeout on INIT (intermittent) | Medium | BYPASS INIT fallback; paste params manually | Monitoring |
| P115-002 | Final Verdict bar display artifacts on TOS chart | Low | LogEntry authoritative; flag in Comments | Monitoring |
| P115-003 | PowerShell Python execution unreliable via MCP | Medium | Use `[System.IO.File]::ReadAllText()` direct I/O | Workaround documented |
| P115-004 | Dollar signs stripped from PowerShell markdown output | Low | Infer currency from context | Workaround documented |
| P115-005 | Vault writes silently skipped on MCP timeout | Medium | Log failure to Comments; retry next session | Workaround documented in 8.4 |

---

## 11. DAILY OPERATIONS & SESSION MANAGEMENT

### 11.1 Session Startup Checklist

```
[ ] Open Claude Desktop (not claude.ai web for full feature access)
[ ] Confirm correct Claude Project loaded (Trading System)
[ ] Type "P_115 INIT" or paste SESSION_INITIALIZATION_PROMPT
[ ] Confirm STEP 0 environment detection passed
[ ] Verify account balance and risk % shown in summary
[ ] Verify posture shown in summary (note: re-read required before STEP 2)
[ ] Confirm P_800 vault interface available (referenced in session output)
[ ] Today's date acknowledged
[ ] One validation check before proceeding (e.g., MOD 3-3-2-3 → BUY)
```

### 11.2 Daily Operating Procedure

**Morning / Pre-Session** (~15 min)
1. Check market posture in P_010 dashboard
2. Run P_910 scan in TOS; export green ticker list
3. Open Claude Desktop, paste INIT or type "P_115 INIT"

**Main Session** (~60 min)
1. Run STEP 1 for each green candidate (paste shorthand or attach chart)
2. For BUY/ASYM with Fund>=2: confirm Fund auto-verification ran
3. Run STEP 2 for BUY/ASYM (re-read posture each time)
4. Verify TP/SL output shows both stock and option prices when options used
5. Execute trades in TOS based on STEP 2 output
6. Log results in 27-column tracker

**Post-Session / Evening Review** (~15 min)
1. Update STEP 3 outcomes for closed trades
2. **Write to vault via P_800 interface** — verify success in output
3. Paste tab-delimited rows into Excel tracker
4. Note any system observations for Enhancement Log

### 11.3 Monthly Maintenance

| Task | Frequency | Owner | Notes |
|---|---|---|---|
| Account parameter review | Monthly | Anthony | Update `P_000_Account_Parameters_Current.md` if 10%+ growth or $35K milestone |
| Performance review | Monthly | Anthony | Win rate, R:R, signal source breakdown |
| Project file cleanup | Monthly | Anthony | Remove superseded files, stay under Claude project limit |
| Prompt library update | As needed | Anthony | Refine prompts that produce drift |
| Schema version review | Quarterly | Anthony | Update if new columns needed |
| Error Corrections Log review | Quarterly | Anthony | Verify all entries still resolved; promote recurring to Hard Rules |
| Vault interface spec review | Quarterly | Anthony | Confirm P_800 v1.1 in use; check for schema changes |

### 11.4 Parameter Registry

*Fixed values that apply to this system. Updated May 1, 2026 monthly review.*

| Parameter | Value | Last Reviewed | Next Review |
|---|---|---|---|
| Account Balance | $32,812.00 | May 1, 2026 | June 2026 (or at $35K milestone / 10% growth) |
| Risk per Trade | 1.5% = $492.18 | May 1, 2026 | June 2026 |
| Max Position (stock) | 5% = $1,640.60 | May 1, 2026 | June 2026 |
| Max Position (options) | 5% of premium paid | May 1, 2026 | June 2026 |
| R:R Minimum | 2:1 to T1 or T2 | Locked | — |
| Options OI threshold | >= 150 | Locked | — |
| Options spread threshold | <= 10% of mid | Locked | — |
| Fund verification threshold | Submitted Fund >= 2 triggers verify | Locked | — |
| Post-earnings stabilization | 3 trading sessions | Locked | — |

---

## 12. TROUBLESHOOTING & SUPPORT

### 12.1 Common Issues & Solutions

#### Issue: Claude gives wrong or unexpected output
- **Symptoms:** Output doesn't match known-good examples, format drift, wrong values
- **Root Cause:** Context window drift, missing session init, conflicting instructions
- **Solution:**
  1. Paste SESSION_INITIALIZATION_PROMPT.md
  2. Restate the specific rule being violated
  3. Show Claude a known-good example (MOD 3-3-2-3 BUY, ATI 3-2-2-3 BUY) and ask it to match
  4. If persistent: open new session and re-paste init prompt
- **Prevention:** Always type "P_115 INIT" at session start

#### Issue: Claude claims it's on web when actually on Desktop
- **Symptoms:** "I'm on claude.ai web, cannot read your files" despite Windows-MCP being available
- **Root Cause:** Claude deferring to Anthropic system prompt boilerplate instead of tool_search probe (see EC-010)
- **Solution:**
  1. Direct Claude to run tool_search(query="powershell windows") immediately
  2. Confirm Windows-MCP:PowerShell appears in results → Claude proceeds
  3. Reference SESSION_INITIALIZATION_PROMPT v3.1 STEP 0 rule
- **Prevention:** STEP 0 is mandatory first step in INIT v3.1

#### Issue: Position sizing produces wrong gate result
- **Symptoms:** Gate selection doesn't match expected smallest-gate logic; risk mode mismatch
- **Root Cause:** Posture not re-read before STEP 2; INIT snapshot used instead of live (see EC-006)
- **Solution:**
  1. Verify Claude re-read P_010_RiskConfig.json before gate calculation
  2. If not: explicitly request re-read, retry sizing
  3. Confirm risk_mode field in output matches current JSON value
- **Prevention:** SESSION_INITIALIZATION_PROMPT v2.9 posture re-read rule

#### Issue: Fund verification skipped on BUY signal
- **Symptoms:** STEP 2 proceeds without stockanalysis.com verification on Fund>=2 signal
- **Root Cause:** Claude failed to trigger Fund Verification Rule v3.0 (see EC-008)
- **Solution:**
  1. Stop STEP 2 immediately
  2. Direct Claude to web_search ROE/Debt/FCF for the ticker
  3. Recompute Fund per V110 thresholds, compare to submitted
  4. Proceed only after verification or user override
- **Prevention:** Fund Verification Rule is mandatory; rule wording in INIT prompt

#### Issue: Vault write skipped or failed
- **Symptoms:** Trade row appears in Excel tracker but missing from Obsidian vault
- **Root Cause:** MCP timeout during P_800 write; Claude did not surface the failure
- **Solution:**
  1. Manually run `write_to_vault("P115", data)` next session
  2. Check `vault_interface.py` v1.1 for schema compliance (ISO dates, market_direction from JSON)
  3. Log failure in tracker Comments
- **Prevention:** Section 8.4 exception workflow added; vault write success/failure must be surfaced explicitly

#### Issue: Claude repeating a corrected error
- **Symptoms:** Error that was fixed in past session reappears
- **Root Cause:** Memory not carried forward, session context reset
- **Solution:**
  1. Check Section 6 Error Corrections Log (by EC ID) for documented fix
  2. Paste the specific rule that was violated
  3. Ask Claude to confirm understanding with an example
  4. If error recurs 2+ times: escalate to project knowledge update
- **Prevention:** Document all recurring errors in Section 6 with EC-XXX numbering

### 12.2 Debug & Audit Trail

**Where to find outputs:**
- Claude session: Current conversation (search via `conversation_search` tool)
- Tracker log: Excel file + Obsidian vault (written via P_800 interface)
- Error log: Section 6 of this document (reference by EC-XXX)
- Code outputs: `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\`

**How to audit a past decision:**
1. Filter tracker by Date and SignalSource = P_115
2. Check Comments column for diagnostic values and Fund verification notes
3. Check SimulationNotes for Fund=0 cause, post-earnings flag, posture change
4. Cross-reference EC-XXX entry in this doc for any flagged errors
5. Locate original Claude session via project conversation history

### 12.3 Escalation Path

| Level | Condition | Action |
|---|---|---|
| Self-resolve | Minor output format issue | Restate rule, show example |
| Session reset | Persistent drift or wrong logic | New session + INIT prompt |
| Documentation update | Same error 2+ times | Add to Section 6 Error Corrections Log as next EC-XXX |
| Rule promotion | Pattern across multiple errors | Promote to Hard Rule in SESSION_INITIALIZATION_PROMPT |
| System redesign | Fundamental logic failure | Open Enhancement Log item, plan fix |

---

## 13. APPENDICES

### Appendix A: Glossary of Terms

| Term | Definition |
|---|---|
| Adjusted Fund | Fund tier after 200-MA penalty applied (V110+) — may include decimals |
| BEAR/AVOID Zone | Stock >20% below 200-MA — auto-reject for Cause A Fund=0 |
| Cause A / Cause B | Fund=0 distinction: A = falling knife (auto-reject), B = weak fundamentals + moderate penalty (flag) |
| Cash Slice | User-provided buying power per trade (Gate 2 input) |
| EC-XXX | Error Correction identifier — sequential numbering in Section 6 |
| Final Verdict bar | TOS chart display element; LogEntry is authoritative on conflict |
| LogEntry | Pipe-delimited diagnostic line on TOS V110 chart (top-right corner) |
| PASS | Step1Verdict for no-trade outcome (replaces "No Signal" effective 2026-05-23) |
| Posture Snapshot | INIT-time posture read; NOT authoritative for trade sizing |
| Posture Re-Read | Mandatory fresh read of `P_010_RiskConfig.json` before every STEP 2 |
| Session Init | Session Initialization Prompt — pasted at session start to load context |
| Project Knowledge | Files uploaded to Claude Project for Claude to search during conversations |
| Prompt Drift | When Claude's outputs gradually deviate from correct format over long session |
| Error Corrections Log | Section 6 of this document — permanent record of discovered and fixed errors |
| STEP 0 | Environment detection via tool_search (Windows-MCP probe) — mandatory before file reads |
| P_800 Vault Interface | Python module routing all Obsidian writes — `from shared_resources.python_utils.vault_interface import write_to_vault` |

### Appendix B: Related Project Documentation

| Document | Location | Purpose |
|---|---|---|
| SESSION_INITIALIZATION_PROMPT.md (v3.1) | Project Knowledge | Paste at session start; STEP 0 env detection + INIT sequence |
| CLAUDE_ASSISTANT_INSTRUCTIONS_v2_1_.md (v2.5) | Project Knowledge | Role and workflow rules across strategies |
| Tracker_Log_Schema_v9_4_0_1.md | Project Knowledge | 27-column schema authoritative reference |
| P_115_StrategyGuide_ChangeLog.md | Project Knowledge | Full version history v9.1 → V110.x |
| STRATEGY_CHANGE_LOG_V110.md | Project Knowledge | V110, V110.1, V110.2, V110.3 detail |
| Quick_Reference_Prompts_v9_4_1.md | Project Knowledge | Daily shorthand commands |
| POSITION_SIZING_THREE_GATE_REFERENCE.md | Project Knowledge | Three-gate examples |
| OPTIONS_RISK_METHODOLOGY.md | Project Knowledge | Chart-based delta translation primary method |
| Z_SCORE_INTEGRATION_SPEC.md | Project Knowledge | Q3 2026 enhancement detail |
| P_000_Account_Parameters_Current.md | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\config\` | Live account parameters |
| P_010_RiskConfig.json | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\` | Live posture (re-read each STEP 2) |
| vault_interface.py (P_800 v1.1) | `C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\python_utils\` | Authoritative Obsidian write routing |
| python-project-architecture SKILL.md | `C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\skills\python-project-architecture\SKILL.md` | Hub-wide Python standards |

### Appendix C: Code Repository

| Field | Value |
|---|---|
| Repository | Local: `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\` |
| Primary Language | ThinkScript (TOS indicators), Python (helpers) |
| Key Files | `P_115_buyTheDipChart_V110.ts` (TOS indicator), `P_910.ts` (scan), `P_050.ts` (scan) |
| Dependencies | Shared resources: `vault_interface.py` (Python P_800), V110 ThinkScript library |

### Appendix D: Architecture Diagram (Detailed)

```
+--------------------------------------+
|   DATA INPUT LAYER                   |
|   - TOS V110 Chart (LogEntry)        |
|   - P_910 Scan (green tickers)       |
|   - P_000_Account_Parameters         |
|   - P_010_RiskConfig.json            |
|   - stockanalysis.com (Fund verify)  |
+----------------+---------------------+
                 |
                 v
+--------------------------------------+
|   AI ANALYSIS LAYER                  |
|   - Claude Desktop (Opus 4.7)        |
|   - Windows-MCP PowerShell           |
|   - Project Knowledge files          |
|   - SESSION_INITIALIZATION_PROMPT    |
+----------------+---------------------+
                 |
                 v
+--------------------------------------+
|   DECISION ENGINE                    |
|   - V110.x scoring                   |
|   - 200-MA penalty table             |
|   - Fund verification gate           |
|   - Post-earnings flag               |
|   - Three-gate sizing                |
|   - Options viability check          |
+----------------+---------------------+
                 |
                 v
+--------------------------------------+
|   OUTPUT / EXECUTION                 |
|   - 27-column tab-delimited row      |
|   - Position sizing + TP/SL          |
|   - P_800 vault_interface write      |
|     write_to_vault("P115", data)     |
|   - Excel tracker append             |
|   - TOS order entry (manual)         |
+--------------------------------------+
```

### Appendix E: Performance Benchmarks

| Metric | Baseline | Target | Current | Last Updated |
|---|---|---|---|---|
| Win Rate (closed trades) | — | >=55% | TBD | Tracking ongoing |
| Average R:R (closed) | — | >=1.8:1 | TBD | Tracking ongoing |
| Signal Accuracy (BUY → profitable) | — | >=50% | TBD | Tracking ongoing |
| Fund Verification Catches | — | All Fund>=2 BUY/ASYM | 100% post-v3.0 | May 27, 2026 |
| Posture Re-Read Compliance | — | 100% of STEP 2 calls | 100% post-v2.9 | May 27, 2026 |
| Vault Write Compliance | — | 100% of STEP 3 calls | Tracking ongoing | May 27, 2026 |

### Appendix F: Configuration Reference

```
# P_115 — Key Configuration Parameters
# Last Updated: 2026-05-27

# Core Parameters (from P_000_Account_Parameters_Current.md)
account_balance       = 32812.00       # USD, updated May 1, 2026
risk_per_trade_pct    = 1.5            # base risk
max_position_pct      = 5              # of account, stock; or of premium paid, options

# Posture (from P_010_RiskConfig.json — re-read each STEP 2)
risk_mode             = [OFF / HALF / STANDARD / HOT]  # authoritative

# AI Settings
primary_ai_engine     = "Claude Desktop"
model_version         = "Opus 4.7"
session_init_required = true
step_0_required       = true           # tool_search probe before file reads

# Scoring (V110.x)
buy_threshold         = 6              # HybridTier minimum
asym_anal_min         = 3
asym_fund_min         = 2
fund_verify_trigger   = 2              # Fund>=2 on BUY/ASYM triggers stockanalysis.com check

# 200-MA Penalty Table (V110.1)
normal_zone           = 0.0            # at/above OR 0-3% below
pullback_zone         = -1.0           # 3-10% below
correction_zone       = -2.0           # 10-20% below
bear_avoid_zone       = -4.0           # >20% below (auto-reject Cause A)

# Options Gates
options_spread_max    = 0.10           # 10% of mid
options_oi_min        = 150
options_rr_min_rule   = "options R:R >= stock R:R"

# R:R
rr_minimum            = 2.0            # 2:1 to T1 or T2
t2_trail_only         = "allowed when T1 fails but T2 clears"

# Post-Earnings
earnings_stabilization_sessions = 3

# P_800 Vault Interface
vault_interface_version = "v1.1"
vault_schema_key        = "P115"
vault_module            = "shared_resources.python_utils.vault_interface"
vault_entry_function    = "write_to_vault(schema_key, data, overwrite=False)"
```

### Appendix G: Document Version Control

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 1.0 | 2026-05-27 | Anthony Zoppi | Initial release of P_115_System_Architecture. Migrated from P_115_BuyTheDip_MasterDoc_v1.0 (Feb 25, 2026). Renamed to System Architecture per template v1.1 convention. EC-XXX numbering applied to Error Corrections Log (EC-001 through EC-011). Section 6.1 summary table added. P_800 vault interface enforcement added to FR-3, Section 8.3 STEP 3 workflow, Section 8.4 exception workflow, and Section 10.4 known issues. Step1Verdict vocabulary standardized to PASS. Parameter registry refreshed to May 1, 2026 monthly review values. |

**Review Schedule:** Monthly (or when system changes significantly)
**Last Review:** 2026-05-27
**Next Review:** 2026-06-27

---

**Document Classification:** Internal
**Document Owner:** Anthony Zoppi
**Template Version:** UNIVERSAL_PROJECT_TEMPLATE_v1_1
**Template Applies To:** P_115 Buy The Dip Trading System

---

*END OF DOCUMENT*
