# P_400 Trade Order Management ? System Architecture
**Project ID:** P_400
**Version:** 2.4 (Council Evidence Frameworks, Two-Tier Signal Flow, Deterministic Python Core, Guidelines Merged, Systems Lens, Phase E4 Live Data Automation, Post-Earnings Stabilization Check)
**Last Updated:** 2026-07-24
**Maintained By:** Anthony Zoppi
**Status:** Phase E2 CLOSED ? Phase E3 Design Locked
**Supersedes:** Architecture v1.0 (2026-06-03); P_400_TradeordermanagementGuidelines_v1.1 (merged into Section 3)

---

## DOCUMENTATION DECISION PROTOCOL
*Read this before creating any new documentation.*

### The Golden Rule
**Always try to fit new content into this master document first.** Only spawn a separate file when content exceeds one page, changes frequently, is shared across projects, or needs its own version history. Guidelines v1.1 has been merged into this document (Section 3) per this rule ? it is no longer maintained separately.

### Reference Link Format
> **Linked Document:** [Filename]
> **Location:** [Path]
> **Purpose:** [One line]
> **Last Updated:** [Date]

---

## TABLE OF CONTENTS

1. [Project Overview & Current State](#1-project-overview--current-state)
2. [System Architecture & Two-Tier Signal Flow](#2-system-architecture--two-tier-signal-flow)
3. [Governance & Authority (Normative ? merged Guidelines)](#3-governance--authority)
4. [Council v2.0 ? Evidence Frameworks & Deterministic Blocks](#4-council-v20)
5. [Systems-Thinking Lens (Meadows)](#5-systems-thinking-lens)
6. [Data Design](#6-data-design)
7. [Phase E2 Implementation Plan](#7-phase-e2-implementation-plan)
8. [Configuration Reference & Version Control](#8-configuration-reference--version-control)

---

## 1. PROJECT OVERVIEW & CURRENT STATE

### 1.1 Purpose

P_400 is the trade order management engine. It takes any validated BUY signal from upstream projects (P_115, P_300, future sources) and produces a Council-reviewed, broker-ready order specification, then owns the trade from signal landing until the position closes and final P&L is handed to P_020. Phase E2 remains a manual-execution system: P_400 outputs an order spec precise enough to type into Schwab letter-for-letter. Auto-submission stays out of scope until Phase 3.

### 1.2 What Changed Since v1.0

v1.0 was written before the SIGNAL_V2 migration completed. The following v1.0 references are retired and corrected throughout this document:

| v1.0 (stale) | v2.0 (current) |
|---|---|
| P400SIG schema, `*_signal.json` packets | SIGNAL_V2, `*_v2.0.json` packets |
| Schema owned inside P_800 internals | `shared_resources\python_utils\signal_schemas.py` ? neutral cross-project contract; P_400 imports `SignalV2` from here only |
| Per-project work order folders (`work_orders\PHASE_E1\`) | Shared single ledger: `04-Shared-Resources\work_orders\` (alias `Agentic-Hub-Governance\work_orders\`), 1-to-many schema, OWNER_DONE vs CLOSED lifecycle |
| Project path `P_400_Trade_Management_System` | `projects\P_400_TradeOrderManagement\` |
| Primary AI engine: Perplexity | **Primary AI engine: Claude Desktop** with windows-mcp toolchain; Perplexity artifacts archived under `docs\Perplexity\` |
| P_400 reader: PENDING | **BUILT and CLOSED** (WO-P400-E1.001): nine files, layered architecture, 4/4 tests, 34 live packets validated |
| min_acceptable_rr = 1.5 | **min_acceptable_rr = 2.0 at T1** (Guidelines rule wins; see 3.6) |

### 1.3 Current Asset Inventory

| Asset | Location | Status |
|---|---|---|
| Signal reader (v2.0) | `projects\P_400_TradeOrderManagement\python\` | CLOSED ? application/domain/infrastructure layers + cli, config, schemas, tests |
| Signal inbox | `trading_journal\TradeOrderManagement\signals\` | Live ? `*_v2.0.json` packets from P_115/P_300 via P_800 `write_to_vault("P400SIG"?SIGNAL_V2 route)` |
| Shared schema contract | `shared_resources\python_utils\signal_schemas.py` | `SignalV2`, `SignalContext`, `SignalMetadata` |
| Open-position book | `trading_journal\TradeOrderManagement\P400\` | `*_P400.md` records (empty at v2.0 publication ? no open positions) |
| Account parameters | `projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` | Read live, never hard-coded |
| Market posture | `P_010_RiskConfig.json` (path discovered by glob) | Re-read fresh before every size calculation |
| Session INIT prompt | `docs\P_400_SESSION_INITIALIZATION_PROMPT_v1_2.md` | To be revved to v2.0 in WO-P400-E2.004 |

### 1.4 Scope Boundary

*Order management* (signal ? live order at Schwab) and *trade management* (open position ? close) share one record but run on different clocks. Phase-3 auto-submission attaches to the order-management boundary only.

**Out of scope:** signal generation (P_115/P_300 own it), automated submission, tax-lot accounting, SELL-side construction (Phase 3+), crypto (Phase 4), schema ownership of the shared signal contract (neutral; governed by work order, consumed by all).

### 1.5 Definitions

| Term | Definition |
|---|---|
| SIGNAL_V2 packet | `*_v2.0.json` file conforming to `SignalV2`; the only valid upstream input |
| Council | Five-role decision body; deterministic numeric blocks, model-generated narrative |
| Tier-1 screen | Fast deterministic pass over all inbox signals; no web calls |
| Tier-2 dossier | Full technical workup (Section 4.2) on signals Tony selects |
| Straight-to-trade | Tier-2 path that skips the full dossier narrative but never skips live data or Council |
| Snapshot dict | The live-market data block Claude assembles and hands to the Python pipeline |
| OWNER_DONE / CLOSED | WO lifecycle: deliverable verified / all consumers Ack'd |

---

## 2. SYSTEM ARCHITECTURE & TWO-TIER SIGNAL FLOW

### 2.1 High-Level Flow (v2.0)

```
[P_115 / P_300 emit SignalV2] --> write_to_vault() --> P_800 routes JSON
                                                          |
                                                          v
                          [Inbox: trading_journal\TradeOrderManagement\signals\*_v2.0.json]
                                                          |
                                                          v
              +---------------------- TIER 1: DETERMINISTIC SCREEN (all signals, no web) ----------------------+
              | Python: screen.py                                                                              |
              |  - Validate packet (reader, already built)                                                     |
              |  - Packet R:R check vs 2.0 minimum (guideline entry/stop/target)                               |
              |  - Duplicate check vs open-position book                                                       |
              |  - Heat / position-count headroom check                                                        |
              |  - Posture gate: current risk_mode sizing applied to packet (would Gate 1 produce >= 1 share?) |
              |  - Signal age check (stale packets flagged)                                                    |
              |  Output: ranked table -- PASS / FAIL per signal with reason codes                              |
              +-----------------------------------------------------------------------------------------------+
                                                          |
                                       Tony picks from PASS list, per signal:
                                                          |
                              +---------------------------+---------------------------+
                              |                                                       |
                              v                                                       v
              [TIER 2A: FULL DOSSIER]                                  [TIER 2B: STRAIGHT TO TRADE]
              Claude builds the complete                               Claude fetches live snapshot only
              technical workup (Section 4.2)                           (price, ATR, spread, earnings date)
              + live snapshot                                          No dossier narrative
                              |                                                       |
                              +---------------------------+---------------------------+
                                                          |
                                                          v
                                  [SNAPSHOT DICT handed to Python pipeline]
                                                          |
                                                          v
                                  [evaluate_signal.py orchestrates:]
                                   1. Reconciliation (drift, directional)
                                   2. Re-read P_010 posture (fresh, never INIT snapshot)
                                   3. Three-gate sizing (sizing.py)
                                   4. Portfolio governance (portfolio.py)
                                   5. Council deterministic blocks (council.py)
                                                          |
                                            +-------------+-------------+
                                            |                           |
                                        BLOCKED                     APPROVED
                                            |                           |
                                            v                           v
                                  [Write BLOCKED record]    [build_order_spec.py -->
                                   via P_800, stop]          Schwab-grid order spec]
                                                                        |
                                                                        v
                                                        [Tony types order into Schwab,
                                                         reports order_id back]
                                                                        |
                                                                        v
                                                        [Obsidian record via P_800
                                                         handle_write(); lifecycle
                                                         PENDING -> SUBMITTED -> FILLED
                                                         -> T1_HIT -> TRAILING -> CLOSED]
                                                                        |
                                                                        v
                                                        [CLOSED -> P_020 hand-off]
```

### 2.2 Runtime Split ? Who Does What

**Python owns everything deterministic.** Sizing, gates, heat, Council block decisions, screen ranking, order-spec field math. Same inputs always produce the same outputs. No network calls inside the deterministic core ? it receives data, it never fetches it.

**Claude owns everything that touches the world.** Live price/ATR/IV/earnings acquisition (web now, Schwab API Phase 1.5), the Tier-2A dossier narrative, Council role narration, the four-question Tony input batch, Obsidian writes via P_800, lifecycle event capture, and session orchestration.

**The boundary object is the snapshot dict.** Claude assembles it; Python consumes it. Every snapshot carries `data_source` and `price_timestamp` so staleness blocks are checkable inside the deterministic core. This split keeps the code small and dumb on purpose: arithmetic and threshold checks only, Pydantic the sole dependency beyond stdlib, every rule unit-testable without a network.

### 2.3 Component Map (v2.0)

| # | Component | Runtime | Status |
|---|---|---|---|
| C1 | Signal ingestion + validation | Python (built) | CLOSED ? WO-P400-E1.001 |
| C1.5 | Tier-1 deterministic screen | Python `domain\screen.py` | Phase E2 build |
| C2 | Live data layer (snapshot assembly) | Claude (web), Schwab API Phase 1.5 | Active (manual fallback) |
| C3 | Reconciliation engine (directional drift) | Python, inside `evaluate_signal.py` | Phase E2 build |
| C4 | Tony input capture (one batched ask) | Claude | Active |
| C5 | Vehicle selection + IV-rank gate | Claude Phase E2; scoring Phase 2 | Pass-through |
| C6 | Three-gate position sizer | Python `domain\sizing.py` | Phase E2 build |
| C6.5 | Portfolio governance | Python `domain\portfolio.py` | Phase E2 build |
| C7 | Council deterministic blocks | Python `domain\council.py`; narrative by Claude | Phase E2 build |
| C8 | Order spec builder (Schwab grid) | Python `application\build_order_spec.py` | Phase E2 build |
| C9 | Obsidian writer | Claude via P_800 `handle_write()` | Active |
| C10 | Lifecycle manager | Claude + record state | Active |

### 2.4 Directional Drift Rule (carried from v1.0, unchanged)

Drift *toward target* beyond threshold invalidates the original thesis and stop ? re-derive the stop from live structure/ATR and re-check R:R, or block if R:R collapses below 2.0. Drift *away* (deeper dip on a dip-buy) may improve the entry. Drift is directional, never symmetric.

### 2.5 Exception Workflows (carried from v1.0, all retained)

1. **Symbol already open:** surface existing position; ask scale-in / replace / skip; route per answer; log decision.
2. **Partial entry fill:** resize OCO children to actual fill qty; recompute dollar risk; dated log entry.
3. **Stale price / market closed:** block construction; prompt for fresh price or explicit pre-market flag.
4. **Both data paths fail:** prompt Tony for manual price + ATR; `data_source=manual`; flag in record.
5. **Council BLOCKED, Tony wants to proceed:** require exact phrase "OVERRIDE BLOCK ON [SYMBOL] -- I ACCEPT RESPONSIBILITY"; `council_verdict=APPROVED_BY_OVERRIDE`; permanent annotation.
6. **Packet missing required fields:** reader rejects (no repair); report; no record created.
7. **Fill drifts > 1% from spec:** recompute R:R and dollar risk on actual fill; flag if R:R < 1.0; update record.

---

## 3. GOVERNANCE & AUTHORITY
*Normative. This section absorbs P_400_TradeordermanagementGuidelines_v1.1 in full. That file is superseded; in any conflict between a legacy document and this section, this section controls.*

### 3.1 Authority Rule

All order management decisions default to P_400: stock sizing, options sizing, stop methodology, target hierarchy, risk-to-reward validation, fallback rules, override handling, and final broker-ready order formatting. Strategy documents (P_115, P_300, etc.) define entry logic and setup context only. Any legacy document referencing P_115 for sizing or order handling is historical context unless explicitly restated here.

### 3.2 System Scope

P_400 governs across all active strategies: P_115, P_116, P_117, P_118, P_300. Strategy integration exists *inside* the P_400 workflow, never beside it as a separate authority.

### 3.3 Position Sizing Standard ? Three Gates

Every position passes the three-gate system; the smallest gate wins. No exception without explicit override and documented justification.

```
Gate 1 (Risk):          posture_adjusted_risk$ / (entry - stop)
Gate 2 (Cash):          user-provided per-trade cash / entry
Gate 3 (Concentration): max_position$ / entry  (options: premium paid, not notional)
Final size = SMALLEST of the three
```

Gate 1 risk dollars come from the **P_010 risk_mode re-read fresh at size time** ? never the INIT snapshot, never recomputed independently from balance. Account parameters come from P_000's Risk Mode Adjustments table.

**Options risk:** dollar risk capped at premium-at-risk to the stop, delta-adjusted with a theta/IV-crush haircut. Never `(entry - stop)` stock math on a contract.

**Cash is per-trade, not tracked:** Tony provides available buying power per trade. Do not subtract trades from a running cash balance between gates.

### 3.4 Risk Mode Standard

`P_010_RiskConfig.json` is authoritative. Re-read before every STEP 2 / size evaluation. Modes and multipliers live in P_000's Account Parameters file (OFF/CORRECTION 50%, HALF 75%, STANDARD/FULL 100%, HOT tiered). Older fixed sizing values in P_115-derived references are not the active control set.

### 3.5 Target Selection Standard

P_400 controls targets. Standard setups use resistance-based targets. Price-discovery setups (no visible overhead resistance) use the Confluence-Based Target Framework: ATR extension, round-number alignment, measured move when visually confirmed, prior structure when available. ATR alone is never sufficient; confluence governs.

### 3.6 Reward-to-Risk Rule ? 2:1 AT T1 (LOCKED v2.0)

**T1 must produce at least 2:1 reward-to-risk from entry or the setup is invalid.** This resolves the v1.0 conflict (config said 1.5) in favor of the Guidelines rule. `min_acceptable_rr = 2.0` is now the configuration value and the Quant block threshold.

- R:R is computed on **realistic fills**: entry at ask (or mid + half-spread), exit at bid (or mid - half-spread), commissions netted. Mid-to-mid R:R is never reported as the trade R:R.
- When T1 passes, T2 becomes the continuation objective. After T1 hits, stop moves to breakeven and trailing logic manages T2.
- **Fabricating a target to satisfy 2:1 is prohibited.** If no honest confluence target produces 2:1, the setup fails. Period.
- Worked consequence: the 2026-06-12 VFC evaluation (R:R 1.63 at T1 on realistic fills) is a Quant BLOCK under this rule.

### 3.7 Stop Architecture

P_400 controls stops for stocks and options. Stock stop = the more conservative of ATR-based or chart-structure logic. Stops tighter than 1x ATR are blocked (whipsaw); stops so wide they break the 2:1 rule are blocked. Option stops translate from underlying stock movement through delta-aware methodology.

### 3.8 Options Management

P_400 is the governing authority. Options must pass viability gates: spread width, open interest, and reward-to-risk parity versus the stock setup. Then either the chart-based primary method or risk-budget-first secondary method applies, per setup quality. If gate math yields zero contracts: fallback to stock or explicit override.

**Management trigger:** underlying STOCK price by default ? never the option Mark unless the trade plan explicitly says Mark. Exits use stop-limit structure with bid-aware option pricing where spreads are wide (P_000 Options Rule).

**Display rule:** every options plan shows BOTH stock and option prices for entry, take-profit, and stop, with delta-derived option estimates and the leverage multiple.

### 3.9 Options Data Priority

Live chain data: Thinkorswim first, then ChartExchange, then Yahoo Finance, then Barchart/Nasdaq. Stop at the first usable source. Never aggregate across sources.

### 3.10 Execution Formatting

Final output is broker-ready and concise: council status, stock order format, and option order format when applicable, with option management tied to the underlying stock trigger by default.

### 3.11 Legacy Reference Replacement Table

| Legacy reference pattern | Replacement rule |
|---|---|
| "P_115 asset sizing requirements" | P_400 three-gate sizing framework (3.3) |
| "P_115 execution decision logic" | P_400 trade order management workflow (Section 2) |
| "P_115 options handling" | P_400 options translation and hybrid risk methodology (3.8) |
| "P_115 order notes / TOS logic" | P_400 broker-ready Thinkorswim order format (6.3) |
| "P_115 manages exits" | P_400 manages stops, T1/T2, breakeven transitions, trailing (3.6, 3.7) |

### 3.12 Work Order Governance

Work orders live in the shared single ledger `04-Shared-Resources\work_orders\` as plain filesystem markdown (never in the Obsidian vault). One Owner, many Affects, per-consumer Acks. OWNER_DONE = deliverable shipped and verified; CLOSED = all consumers Ack'd. Every P_400 session runs the STEP 0.5 Work Order Review gate before work proceeds. WO closure follows the P_000 Completion Gate checklist (WO-P000-E3.001) once that WO lands.

---

## 4. COUNCIL v2.0

### 4.1 Principle ? Evidence Frameworks Structure the Inputs; Math Makes the Blocks

v2.0 upgrades each Council role with an institutional evidence framework adapted from desk-analyst practice. The frameworks govern **what evidence is gathered and how it is organized**. They never change the verdict logic: every BLOCK remains a deterministic threshold check on captured numbers (`council.py`). The model narrates; the math blocks. This preserves determinism, auditability, and back-testability (same captured snapshot = same verdict, always).

### 4.2 Quant Strategist ? Technical Dossier Framework (Tier 2A)

When Tony selects the full dossier, the Quant role's evidence is the complete technical workup:

1. Trend analysis ? primary trend on daily, weekly, monthly timeframes -- COMPUTED (WO-P400-E4.003, cli.py dossier SYMBOL)
2. Support and resistance ? exact price levels, R3/R2/R1 over S1/S2/S3 -- COMPUTED (pivot S/R, WO-P400-E4.003)
3. Moving averages ? 20/50/100/200-day positions and crossover state -- COMPUTED (WO-P400-E4.003)
4. RSI (14) ? current value with interpretation, divergence note -- COMPUTED (Wilder RSI, WO-P400-E4.003); divergence note stays Claude-narrated
5. MACD ? signal-line cross state, histogram momentum, divergence detection -- COMPUTED (WO-P400-E4.003); divergence detection stays Claude-narrated
6. Bollinger Bands ? position within bands, squeeze/expansion status -- COMPUTED (WO-P400-E4.003)
7. Volume ? confirming or contradicting the move; vs average; insider activity noted -- COMPUTED vs 20d avg (WO-P400-E4.003); insider activity stays Claude-narrated
8. Fibonacci retracement ? key levels from the most recent significant swing -- COMPUTED (WO-P400-E4.003). Corrected 2026-07-24: uses a simple rolling max(high)/min(low) over the lookback window, matching P_400_2A_Analysis_Chart's ThinkScript exactly -- NOT P_300's pivot algorithm, which was tried first and confirmed wrong via live TOS comparison (P_300 solves a different problem: nearest local resistance pivot, not simple window extent)
9. Chart pattern identification -- CLAUDE-NARRATED ONLY, NEVER AUTO-COMPUTED (WO-P400-E4.003 explicit decision). Geometric pattern shape ID (H&S, double top, cup-and-handle, flags) is a judgment call, not arithmetic -- unreliable even in mature commercial TA software. Claude reasons over the computed items 1-8 table from cli.py dossier, same as before but without the screenshot dependency. A future session must not "fix" this by writing a pattern-shape detector; explicit "what it is NOT" still required.
10. Trade setup synthesis ? entry zone, stop basis, T1/T2 with realistic-fill R:R

The dossier renders as a structured note with a trade-plan summary block on top. In Tier 2B (straight-to-trade), items 1-9 are skipped; only the live snapshot fields needed by the deterministic core are gathered.

**Quant deterministic blocks (either tier):**
- R:R at T1 below 2.0 on realistic fills
- Stop tighter than 1x ATR(14)
- Stop wide enough that 2:1 cannot be honestly met

### 4.3 Risk Manager ? Portfolio Risk Framework

Evidence framework adapted from portfolio-level risk practice: position beta vs market regime, correlation to existing holdings, drawdown context, concentration exposure. Beta and correlation **annotate**; as of 2026-07-20 (Tony directive) the five governance checks below **never block** -- they raise **SEVERE_WARNING**, the highest annotation severity, always with the current open-position list attached so Tony can see exactly what is counting against the cap:

- Portfolio heat breach: open dollar risk + new trade risk > 12% of account
- Max concurrent positions breach: > 8 open
- Daily-loss circuit-breaker tripped: realized day loss > 3% of account
- Sector concentration breach: > 2 positions in one sector
- Cash below risk-per-trade: `--cash` < posture-adjusted risk$ for this trade (new 2026-07-20)

Heat math note: 12% cap / 1.5% base risk = 8 concurrent full-risk positions, consistent by construction.

RISK's ceiling was BLOCK through v2.1; superseded 2026-07-20 (domain/risk_vote.py) -- see Section 4.8 for how SEVERE_WARNING slots into verdict assembly. The matching Tier-1 change lives in domain/screen.py: HEAT_BREACH/POSITION_COUNT there are now WARN, not FAIL, so packets are never silently auto-disposed on these two checks (WO-P400-E2.018's dispose_failed() already skips anything non-FAIL).

### 4.4 Macro Economist ? Event Risk Framework

Evidence framework adapted from earnings-analysis practice: next earnings date, historical earnings-day move (average and median), options implied move where available, known binary events (FDA, court, macro prints) across the **full expected holding period** ? never a fixed 48-hour window.

**Macro deterministic block:** earnings or known binary event inside the holding period, unless Tony confirms reduced size or a defined-risk structure (which converts BLOCK to CAUTION with annotation).

### 4.5 Momentum & Tape

- **Blocks:** adverse directional drift past threshold with collapsed R:R; price staleness beyond `price_staleness_threshold_sec`; market closed without explicit pre-market flag.
- **Annotates:** volume character, relative strength vs SPY/QQQ posture, gap risk.

### 4.6 Behavioral Judge ? Annotate Only

Never blocks. Flags revenge-trade patterns (new signal in a symbol that just stopped out), overtrading (order count vs daily norm), streak-chasing (size creep after consecutive wins). Annotations are written to the record so P_020 can correlate behavioral flags with outcomes over time.

### 4.7 Vehicle Selection Gate (C5) ? Options Structuring Framework

Phase E2: pass-through of Tony's instrument choice plus the IV-rank gate ? IV rank above 50 on a long single-leg flags expensive premium and recommends a defined-risk spread. Phase 2 adds structure scoring adapted from options-desk practice: outlook translated to structure category, exact strikes/expiry, max profit / max loss / breakeven, probability of profit from IV, Greeks exposure, adjustment plan, exit rules. Structure choice maximizes expected R:R per unit of capital subject to the viability gates in 3.8.

### 4.8 Verdict Assembly

```
All roles PASS                          -> APPROVED
Any CAUTION, no SEVERE_WARNING/BLOCK    -> APPROVED_WITH_CAUTION (Tony decides)
Any RISK SEVERE_WARNING, no BLOCK       -> APPROVED_WITH_SEVERE_WARNING (Tony decides;
                                            outranks plain CAUTION; open-position list shown)
Any deterministic BLOCK (QUANT/MACRO/TAPE only) -> BLOCKED (record written, stop)
Tony invokes override after BLOCK      -> OVERRIDE_REQUIRED -> APPROVED_BY_OVERRIDE
                                           (exact phrase required, permanent annotation)
```

Priority: BLOCKED > APPROVED_WITH_SEVERE_WARNING > APPROVED_WITH_CAUTION > APPROVED. RISK never contributes to BLOCKED as of 2026-07-20 -- only QUANT/MACRO/TAPE retain block authority (can_block=True). RISK and BEHAVIORAL are both can_block=False, but RISK's SEVERE_WARNING still outranks an ordinary CAUTION from another role when both fire together.

BLOCKED records are always written -- Council vetoes are part of the audit trail.

---

### 4.9 Council Narrative Templates

**QUANT**
- ALL_CLEAR: "Quant PASS: R:R [X] clears 2.0. Stop >= 1x ATR."
- RR_BELOW_MIN: "Quant BLOCK: R:R [X] < 2.0. T1 at [price] insufficient."
- STOP_TOO_TIGHT: "Quant BLOCK: Stop [X] < 1x ATR ([Y]). Widen to structure."
- STOP_BREAKS_RR: "Quant BLOCK: Target [X] fabrication check — honest confluence only."

**RISK**
- ALL_CLEAR: "Risk PASS: Heat $[X]/$[Y]. Positions [N]/8. Cash $[X] >= risk $[Y]."
- HEAT_BREACH: "Risk SEVERE WARNING: Heat $[X] over $[Y] cap. Open ([N]): [symbols]."
- POSITION_COUNT: "Risk SEVERE WARNING: [N]/8 -- at max. Open ([N]): [symbols]."
- DAILY_LOSS: "Risk SEVERE WARNING: Day loss $[X] hit $[Y] circuit breaker (3%). Open ([N]): [symbols]."
- SECTOR_CONCENTRATION: "Risk SEVERE WARNING: [X] sector at [N]/2 max. Open ([N]): [symbols]."
- CASH_BELOW_RISK: "Risk SEVERE WARNING: Cash $[X] below risk-per-trade $[Y] for this posture. Open ([N]): [symbols]." (new 2026-07-20)

**MACRO**
- ALL_CLEAR: "Macro PASS: No binary events in holding window."
- EARNINGS_IN_WINDOW (BLOCK): "Macro BLOCK: Earnings inside hold period. Confirm defined-risk to convert to CAUTION."
- EARNINGS_IN_WINDOW (CAUTION): "Macro CAUTION: Earnings inside window — defined-risk confirmed."
- POST_EARNINGS_STABILIZATION (CAUTION, never BLOCK, WO-P400-E2.023): "Macro CAUTION: Earnings [N] session(s) ago — inside stabilization window. Structure/ATR may be stale."

**TAPE**
- ALL_CLEAR: "Tape PASS: Price fresh ([N]s). No adverse drift."
- PRICE_STALE: "Tape BLOCK: Price [N]s old, over 120s. Refresh snapshot."
- MARKET_CLOSED: "Tape BLOCK: Market closed, no pre-market flag."
- ADVERSE_DRIFT: "Tape BLOCK: Drift [X]% collapsed R:R to [Y]. Recalculate."
- SPREAD_TOO_WIDE: "Tape BLOCK: Spread [X]% of price exceeds [Y]% plausibility threshold. Fill quality unacceptable." (WO-P400-E4.004)

**BEHAVIORAL (annotates only — never blocks)**
- ALL_CLEAR: "Behavioral: No flags."
- BEHAVIORAL_REVENGE: "Behavioral NOTE: [SYMBOL] recently stopped out. Logged for P_020."
- BEHAVIORAL_OVERTRADING: "Behavioral NOTE: [N] orders today vs [M] norm."
- BEHAVIORAL_STREAK_CHASING: "Behavioral NOTE: [N] consecutive wins — size-creep watch."

**OPTIONS VIABILITY (options path only — runs before stock Council gates)**
- OI_TOO_LOW: "Options BLOCK: OI=[N] < 150. Find different strike or expiry."
- SPREAD_TOO_WIDE: "Options BLOCK: Spread=[X]% of mid > 10%. Fill quality unacceptable."
- RR_PARITY_FAIL: "Options BLOCK: Option R:R=[X] < stock R:R=[Y]. Use stock or find better strike."
- RR_BELOW_MIN: "Options BLOCK: Option R:R=[X] < 2.0."
- IV_HIGH: "Options CAUTION: IV=[X]% > 50 — spread preferred. Confirm or switch."
- ZERO_CONTRACTS: "Options CAUTION: 0 contracts from gate math. Override required — document justification."

## 5. SYSTEMS-THINKING LENS
*Design rationale, Meadows framework. This section explains WHY the architecture is shaped this way; it adds no operational steps.*

### 5.1 Stocks and Flows

| Stock | Inflows | Outflows |
|---|---|---|
| Account balance | Winning closes, deposits | Losing closes, costs |
| Portfolio heat (open $ risk) | New FILLED positions | Closes, stop-to-breakeven moves |
| Open position count | Fills | Closes |
| Signal inbox depth | P_115/P_300 emissions | Tier-1 screen disposition |
| Trust in the system (unmeasured) | Specs that match reality, blocks that prove right | Fabricated data, silent breakage, stale docs |

The unmeasured stock matters most. Every NFR in this document (no fabrication, determinism, audit trail) exists to protect it.

### 5.2 Feedback Loops

**Balancing (the system's brakes):**
- B1 ? Posture-adjusted sizing: market deteriorates -> P_010 risk_mode drops -> Gate 1 shrinks -> less new risk in bad regimes. Re-reading P_010 fresh at size time shortens this loop's delay to near zero (Meadows leverage point 9: delays).
- B2 ? Heat cap: more open risk -> closer to 12% -> Risk role blocks -> heat stops growing.
- B3 ? Daily-loss circuit-breaker: losses accumulate -> breaker trips -> no new orders today.
- B4 ? 2:1 gate: marginal setups get blocked before they consume capital and attention.

**Reinforcing (the loops being watched):**
- R1 ? Win-streak size creep: wins -> confidence -> bigger sizing pressure. Behavioral role annotates; three-gate math caps it structurally.
- R2 ? Revenge trading: loss -> urge to re-enter same symbol -> worse entry -> loss. Duplicate detection plus Behavioral flag interrupt the loop at the trigger point.

### 5.3 System Traps and Their Escapes

| Trap (Meadows) | Where it appeared | Structural escape now in place |
|---|---|---|
| Drift to low performance | Stale docs, silent contract breakage between projects | OWNER_DONE vs CLOSED distinction; per-consumer Acks; STEP 0.5 governance gate |
| Shifting the burden | Quick inline fixes instead of shared contracts | Neutral schema in shared_resources; work-order-governed changes |
| Seeking the wrong goal | Optimizing trade count instead of expectancy | 2:1 hard gate; Council blocks recorded and reviewed against outcomes via P_020 |
| Policy resistance | Strategy docs and order docs fighting over authority | Section 3 single-authority rule with replacement table |

### 5.4 Leverage Points Applied

The deepest leverage in this build is not parameters (level 12 ? risk percentages) but **information flows (level 6)** ? fresh posture at size time, live earnings across the hold window, heat visible before every order ? and **system rules (level 5)** ? deterministic blocks the model cannot talk its way around. The 2:1 rule and the override-phrase ritual are rules-level interventions: they change what the system is allowed to do, not just how much.

---

## 6. DATA DESIGN

### 6.1 Inputs

| Data | Source | Format | Fed via |
|---|---|---|---|
| BUY signal | Inbox `*_v2.0.json` | SignalV2 (Pydantic) | Reader (built) |
| Account parameters | P_000 config file | Markdown tables | Claude read at INIT; Python `params_reader.py` at size time |
| Market posture | P_010_RiskConfig.json | JSON | Python `posture_reader.py`, fresh per size |
| Live market snapshot | Claude web fetch (Schwab API Phase 1.5) | Snapshot dict | Claude -> Python boundary |
| Open-position book | `TradeOrderManagement\P400\*_P400.md` | YAML frontmatter | Python `book_loader.py` |
| Tony inputs | One batched ask | Structured answers | Claude session |
| Lifecycle events | Tony reports | Free text | Claude session |

### 6.2 Snapshot Dict Contract (Claude -> Python boundary object)

```python
snapshot = {
    "symbol": str,
    "price": float,                  # last trade
    "bid": float, "ask": float,
    "price_timestamp": str,          # ISO-8601
    "price_delay_seconds": int,
    "atr_14": float,
    "avg_volume_20d": float,
    "today_volume": float | None,
    "next_earnings_date": str | None,   # YYYY-MM-DD
    "last_earnings_date": str | None,    # YYYY-MM-DD, WO-P400-E2.023
    "binary_events": list[str],         # inside hold window
    "sector": str | None,
    "iv_rank": float | None,            # options only
    "option_chain_ref": dict | None,    # options only
    "data_source": str,                 # "web" | "schwab_api" | "manual"
}
```

Missing required keys = pipeline refuses to run (no fabrication, no defaults for market data). `null` is honest; an invented number is not.


**snapshot_SYMBOL.json — JSON template (save in python\):**
Never fabricate — use `null` for unknown optional fields.
```json
{
  "symbol": "SYMBOL", "price": 0.00, "bid": 0.00, "ask": 0.00,
  "price_timestamp": "YYYY-MM-DDTHH:MM:SSZ", "price_delay_seconds": 0,
  "atr_14": 0.00, "avg_volume_20d": 0, "data_source": "web",
  "today_volume": null, "next_earnings_date": null, "last_earnings_date": null, "binary_events": [],
  "sector": null, "iv_rank": null, "option_chain_ref": null, "market_open": true
}
```

### 6.3 Record Schema and Order Pattern Library

The P_400 record field set (lifecycle, council verdicts, sizing fields, options fields, `p400_*` namespaced prototype fields) and the Schwab Order Pattern Library (Pattern A stock OCO bracket, Pattern B single-leg option 1st-trgs-All, Pattern C vertical debit spread, Pattern D reserved) carry forward from v1.0 Sections 9.3-9.3.1 **unchanged**, with one addition:

| New field | Type | Description |
|---|---|---|
| `screen_tier` | str | TIER1_ONLY / TIER2A_DOSSIER / TIER2B_DIRECT |
| `screen_reason_codes` | str | Tier-1 PASS/FAIL reason codes at evaluation time |

> **Linked Document:** P_400_TradeOrderManagement_Architecture_v1_0.md
> **Location:** projects\P_400_TradeOrderManagement\docs\
> **Purpose:** Historical reference for the full field table and order pattern grids (v2.0 normative for all rules)
> **Last Updated:** 2026-06-03

Two Pydantic models remain separate by design: `P400SignalRecord`-lineage signal packet (`SignalV2`) and the lifecycle record (`P400Record`). Different lifecycle stages, different fields, different write formats. Never merge them.

### 6.4 Data Integrity Rules

1. Never fabricate prices, ATR, IV, fills, or P&L ? `null` plus a flag, always.
2. Every record carries `data_source` and `price_timestamp`.
3. Malformed packets are rejected, never repaired.
4. Every lifecycle event appends a dated log entry; frontmatter and body update together.
5. BLOCKED records are written ? vetoes are audit trail.

### 6.5 Entry Resolution Rule (WO-P400-E2.009)

P_300 stamps guideline_entry as the close price at eval time ? a reference price, not an
execution target. P_400 resolves the actual entry using the live snapshot price:

| Case | Condition | Action |
|---|---|---|
| Favorable pullback | live_price < guideline_entry | Use live_price as entry. R:R improves. No block. |
| Within threshold |   <= drift_pct <= ENTRY_DRIFT_THRESHOLD_PCT (1.5%) | Use guideline_entry as limit. R:R holds. No block. |
| Entry missed | drift_pct > ENTRY_DRIFT_THRESHOLD_PCT | Recalculate R:R at live_price. If R:R < 2.0 ? REVIEWED_NO_TRADE, drop_reason=ENTRY_MISSED. |

Drift is directional (Section 2.4). Negative drift (favorable) never triggers a block.
The live snapshot price field is always the entry used in sizing and Council ? never the
guideline. valuate_signal.py applies this rule at the reconciliation boundary.

---

## 7. PHASE E2 IMPLEMENTATION PLAN

### 7.1 Build Sequence and Work Orders

Four work orders, strictly ordered. Each lands in the shared ledger with P_400 as Owner. All Python goes under the existing `projects\P_400_TradeOrderManagement\python\` layered structure; every file <= 300 lines, every function <= 50.

**WO-P400-E2.001 ? Deterministic Core (sizing + council + screen)**

| File | Layer | Est. lines | Contents |
|---|---|---|---|
| `domain\sizing.py` | domain | ~120 | `three_gate_size()`, posture multiplier table, options premium-at-risk with theta/IV haircut, realistic-fill R:R |
| `domain\council.py` | domain | ~180 | Per-role deterministic checks, verdict assembly per 4.8, reason-code constants |
| `domain\screen.py` | domain | ~100 | Tier-1 checks: packet R:R vs 2.0, dup check, headroom, posture gate, signal age; ranked result list |
| `test_sizing.py` | tests | ~100 | Gate math incl. OFF-mode 50%, options haircut, smallest-gate selection |
| `test_council.py` | tests | ~100 | Every block threshold hit and missed; verdict table |
| `test_screen.py` | tests | ~100 | PASS/FAIL reason codes against fixture packets |

Verify: all tests pass under p140; re-run cli against the live inbox produces a ranked screen table with zero exceptions.

**WO-P400-E2.002 ? Portfolio + External Readers**

| File | Layer | Est. lines | Contents |
|---|---|---|---|
| `domain\portfolio.py` | domain | ~120 | Heat sum, position count, sector counts, dup detection against book |
| `infrastructure\posture_reader.py` | infra | ~60 | P_010 JSON read with glob path discovery, schema check |
| `infrastructure\params_reader.py` | infra | ~70 | P_000 markdown table parse -> typed params |
| `infrastructure\book_loader.py` | infra | ~80 | Frontmatter parse of `*_P400.md`, non-CLOSED filter |

Verify: heat/count math correct against synthetic book fixtures; live P_010 and P_000 files parse on the real filesystem.

**WO-P400-E2.003 ? Orchestrator + Order Spec + CLI**

| File | Layer | Est. lines | Contents |
|---|---|---|---|
| `application\evaluate_signal.py` | app | ~150 | snapshot+packet+book+posture -> reconcile -> size -> govern -> council -> result object |
| `application\build_order_spec.py` | app | ~130 | Pattern A/B/C rendering to Schwab grid text |
| `cli.py` (extend) | ? | ~80 added | `screen-all`, `evaluate SYMBOL --snapshot file.json`, `spec SYMBOL` |

Verify: end-to-end on a real inbox packet with a hand-built snapshot dict; BLOCK paths produce reason codes; APPROVED path renders a typed-ready Pattern A spec.

**WO-P400-E2.004 ? Session Prompt v2.0**

Rev `P_400_SESSION_INITIALIZATION_PROMPT` to v2.0: two-tier flow in STEP sequence, 2:1 rule, snapshot-dict handoff, Python CLI invocation points (commands delivered as plain text for Tony's terminal), Council narrative templates referencing `council.py` reason codes. Saved to `docs\prompts\`.

Verify: one full live session executes the v2.0 sequence with no improvised steps.

### 7.2 Execution Constraints (environment-hardened)

- All Python runs in Tony's terminal via `C:\Users\Trader\.conda\envs\p140\python.exe` ? Claude provides commands as plain text (windows-mcp hangs on python.exe invocation).
- File writes via PowerShell `Set-Content -Encoding UTF8`; `create_file`/`str_replace` are banned on Windows paths.
- Until WO-P000-E2.002 closes, scripts outside hub root need `PYTHONPATH=C:\Users\Trader\AI-Agent-Learning-Hub` or `sys.path.insert(0, hub_root)`.
- No sys.path side-channels in committed code (WO-P000-E2.003); imports resolve via the hub editable install once it lands.

### 7.3 Definition of Done ? Live End-to-End Run

Phase E2 is DONE when one real signal travels: inbox packet -> Tier-1 screen -> Tony selects -> live snapshot -> deterministic pipeline -> Council verdict -> order spec -> typed into Schwab -> SUBMITTED record in Obsidian via P_800 -> first lifecycle update. After 5 completed trades, review against Appendix-E-style benchmarks (spec accuracy 100%, deterministic repeat rate 100%, signal-to-order < 5 min).

---

## 7.3 Phase E3 ? Options Pipeline

**Goal:** Extend P_400 to evaluate, size, and spec single-leg call/put trades using the P_115 Hybrid Options Methodology as the authoritative framework. Vertical debit spreads added in E3.002 as the fallback when premium or notional exceeds account constraints. Manual chain data input throughout; automated fetch deferred to E3.5+.

**Scope boundary:** P_400 owns options method selection, delta translation, sizing, viability gates, and order spec. Signal generation remains stock-only. Options are a P_400 execution decision layered on top of any signal ? stock APPROVED or stock zero-sized due to account constraints.

**Methodology authority:** `OPTIONS_RISK_METHODOLOGY.md` (P_115 docs) is the canonical reference. No parallel logic invented in P_400.

---

### Two Entry Points (both supported from E3.001)

**Path 1 ? Stock APPROVED, Tony opts into options:**
Stock signal passes Council ? Tony adds `--options` flag ? options evaluation runs alongside stock spec.

**Path 2 ? Stock zero-sized or R:R fails:**
Stock fails Gate 3 (price too high for account) OR stock R:R < 2:1 minimum ? options evaluated as the primary vehicle. `--options` flag triggers this path automatically when stock sizing returns 0 shares or R:R block fires.

---

### Two Methods (inherited directly from P_115 OPTIONS_RISK_METHODOLOGY.md)

**Chart-Based (PRIMARY)** ? use when clear technical stop exists:
1. Stock stop already established (from dossier or packet)
2. Option stop = entry premium + (delta ? stock price movement to stop)
3. Risk/contract = (entry premium ? option stop) ? 100
4. Size via three gates on contract count
5. Gate 3 = premium paid ? contracts ? max_position$ (not notional)

**Risk-Budget-First (SECONDARY)** ? use when no clear technical structure:
1. Risk budget = posture-adjusted risk$ (e.g. $245.02 at OFF)
2. Risk-budget stop = entry premium ? (risk budget ? 100)
3. 2?ATR floor stop = entry premium ? (delta ? 2 ? ATR)
4. Final stop = tighter of the two
5. If resulting risk > budget ? override or reject

**Method selection rule:** Chart-Based is standard. Risk-Budget-First only when setup has no defensible technical stop. Document method used in every record.

---

### WO-P400-E3.001 ? Single-Leg Options Evaluation

| File | Layer | Est. lines | Contents |
|---|---|---|---|
| `domain\options_sizer.py` | domain | ~130 | Chart-Based and Risk-Budget-First methods; delta translation; 2?ATR floor; three-gate sizing on contracts; override flag when Gate 1 rounds to 0 |
| `domain\options_council.py` | domain | ~80 | Viability gates: OI ? 150, spread ? 10% of mid, option R:R ? stock R:R; IV-rank gate (>50 ? spread recommendation); verdict assembly |
| `application\build_option_spec.py` | app | ~120 | Pattern B (single-leg 1st-trgs-All) Schwab grid; stock + option prices at entry/stop/T1; delta-derived estimates; leverage multiple; override annotation when applicable |
| `test_options_sizer.py` | tests | ~100 | Chart-Based delta translation; Risk-Budget-First 2?ATR floor; Gate 3 premium cap; 0-contract override path |
| `test_options_council.py` | tests | ~60 | OI block; spread block; R:R parity block; IV-rank caution |

**Chain data input:** Tony provides chain data via `--chain chain_SYMBOL.json`. Required fields: symbol, expiration, strike, option_type, bid, ask, delta, iv, open_interest, underlying_price. Template delivered in E3.003.

**CLI change:** `cli.py evaluate SYMBOL --snapshot FILE --cash DOLLARS --options --chain chain_SYMBOL.json`

**Chain data source order (per Section 3.9):** TOS first ? ChartExchange ? Yahoo Finance ? Barchart/Nasdaq. Stop at first usable source. Manual entry always valid.

**Verify:** one real signal (Path 1 or Path 2) ? chain file supplied ? method selected ? contract count sized ? viability gates checked ? Pattern B spec rendered ? record written with options fields populated.

---

### WO-P400-E3.002 ? Vertical Debit Spread Evaluation

Triggered when: IV rank > 50 on single-leg evaluation, OR premium on single-leg exceeds Gate 3, OR Tony explicitly requests spread via `--spread` flag.

| File | Layer | Est. lines | Contents |
|---|---|---|---|
| `domain\spread_sizer.py` | domain | ~130 | Long ATM strike + short OTM strike at T1 or next resistance; max loss = debit ? 100 ? contracts; Gate 3 = max loss ? max_position$; R:R = (spread width ? debit) ? debit |
| `application\build_spread_spec.py` | app | ~110 | Pattern C (vertical debit spread) Schwab grid; max profit / max loss / breakeven; probability of profit note from IV |
| `test_spread_sizer.py` | tests | ~80 | Max loss gate; R:R on spread; spread width selection logic |

**Verify:** one real spread trade ? IV rank > 50 or premium breach ? spread recommended ? chain file ? spread spec rendered ? record written.

---

### WO-P400-E3.003 ? Chain Template + Record Schema + INIT Prompt Update

**chain_SYMBOL.json template:**
```json
{
  "symbol": "SYMBOL",
  "underlying_price": 0.00,
  "expiration": "YYYY-MM-DD",
  "strike": 0.00,
  "option_type": "call",
  "bid": 0.00,
  "ask": 0.00,
  "mid": 0.00,
  "delta": 0.00,
  "iv": 0.00,
  "open_interest": 0,
  "spread_pct_of_mid": 0.00,
  "data_source": "tos",
  "chain_timestamp": "YYYY-MM-DDTHH:MM:SSZ"
}
```

**`iv` units (WO-P400-E3.004 item 3):** decimal fraction, NOT a percentage.
`0.41` for 41% IV -- never `41.00`. `options_sizer.py` computes `chain.iv *
100` for display; entering a whole-number percentage silently produces a
nonsensical displayed IV (e.g. 4069.0%) and falsely trips the IV-rank-50
spread-preference flag. No code defect -- this is a manual chain-entry
trap. Same fraction convention applies to `spread_pct_of_mid`, which IS a
percentage already (e.g. `7.79` for 7.79%) -- do not confuse the two
fields' conventions when transcribing from TOS.

**P400Record options fields** (additions to vault_schemas.py):
- `option_method` ? "chart_based" | "risk_budget_first"
- `option_structure` ? "single_leg" | "vertical_spread"
- `option_contract` ? e.g. "MCHP260320C80"
- `option_entry_premium` ? float
- `option_stop_premium` ? float
- `option_target_premium` ? float
- `option_contracts` ? int
- `option_override` ? bool
- `option_override_justification` ? str | null
- `iv_rank` ? float | null

**INIT prompt:** options path added to STEP 2 (Tier Selection) and STEP 4 (Snapshot + Pipeline). Council narrative templates extended with options viability blocks.

**Architecture doc:** version bumped and component statuses updated on completion.

---

### 7.4 Phase E3 Definition of Done

One real single-leg options trade and one real spread trade travel the full path: stock signal ? Council APPROVED (or stock zero-sized / R:R blocked) ? `--options` flag ? chain file supplied ? method selected (Chart-Based or Risk-Budget-First) ? viability gates checked ? spec rendered ? typed into Schwab ? record written with all options fields populated.

---

### 7.5 Phase E3.5 — Chain Data Automation (SHIPPED, WO-P400-E4.002, CLOSED 2026-07-24)

No longer deferred. `fetch-snapshot SYMBOL` and `fetch-chain SYMBOL --type call|put` now pull live price/bid/ask/ATR14(computed)/volume/chain data directly from Schwab, replacing manual TOS-screenshot transcription for Bucket A snapshot fields and for chain data. Auto-selects the optimal contract by DTE window (21-45 days) and closest-to-target delta (0.50) when `--strike`/`--expiration` aren't given; those flags remain valid manual overrides. Live-verified against MRCY 2026-07-24 (both fetch-snapshot and fetch-chain). `next_earnings_date`/`sector` remain web-search-sourced by design (Tony's explicit call, 2026-07-21) -- not part of this automation's scope.

---

## 8. CONFIGURATION REFERENCE & VERSION CONTROL

### 8.1 Configuration (v2.0)

```
# Core
base_risk_per_trade_pct        = 1.5        # P_000 authoritative; read live
max_position_pct               = 5.0
min_acceptable_rr              = 2.0        # CHANGED from 1.5 -- Guidelines rule wins (3.6)
entry_drift_threshold_pct      = 1.5
price_staleness_threshold_sec  = 120
min_stop_atr_multiple          = 1.0
option_iv_rank_spread_pref     = 50
signal_file_dir                = "trading_journal\TradeOrderManagement\signals\"
posture_source                 = "P_010_RiskConfig.json"   # glob-discovered, fresh per size
params_source                  = "projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md"

# Portfolio governance (Risk role block authority)
portfolio_heat_max_pct         = 12.0
max_concurrent_positions       = 8
daily_loss_circuit_breaker_pct = 3.0
max_sector_exposure            = 2

# Council
quant_can_block = true | macro_can_block = true | tape_can_block = true
risk_can_block  = false | behavioral_can_block = false   # RISK ceiling changed BLOCK -> SEVERE_WARNING 2026-07-20 (Tony directive); doc-only flag, enforced per-vote in domain/risk_vote.py

# Data & broker
primary_data_source  = "web"      # Schwab API at Phase 1.5
fallback_data_source = "manual"
default_broker       = "schwab"
default_stock_tif    = "DAY"
default_option_child_tif = "GTC"
auto_submit_orders   = false      # hard-locked through Phase E2

# Lifecycle
require_dated_log_entry = true
overwrite_records       = true
```

### 8.2 Version Control

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 1.0 | 2026-06-03 | Anthony Zoppi | Finalized Phase 1 manual prototype; Enhancement 1 signal-file handoff |
| 2.0 | 2026-06-12 | Anthony Zoppi / Claude | SIGNAL_V2 reality documented (reader CLOSED, shared schema, shared WO ledger); Claude Desktop primary engine; Guidelines v1.1 merged as Section 3 (superseded); R:R locked at 2:1 T1; Council v2.0 evidence frameworks (technical dossier, portfolio risk, event risk, options structuring) with deterministic blocks unchanged in authority; two-tier signal flow (deterministic screen -> dossier or straight-to-trade); Python deterministic core / Claude world-boundary runtime split with snapshot-dict contract; systems-thinking design lens; Phase E2 implementation plan (WO-P400-E2.001 through E2.004) |

| 2.1 | 2026-06-16 | Anthony Zoppi / Claude | Phase E3 Options Pipeline plan added (WO-P400-E3.001 through E3.003); two entry paths (stock APPROVED + stock zero-sized/R:R blocked); P_115 Hybrid Methodology confirmed as authority; chain template defined; record schema options fields added; Phase E2 status updated to CLOSED |

| 2.2 | 2026-07-20 | Anthony Zoppi / Claude | RISK role never blocks (Tony directive): heat/position-count/daily-loss/sector checks downgraded BLOCK -> SEVERE_WARNING (domain/risk_vote.py, extracted from council.py); new CASH_BELOW_RISK check added; open-position list attached to every RISK annotation; matching Tier-1 change in domain/screen.py (HEAT_BREACH/POSITION_COUNT downgraded FAIL -> WARN, no longer auto-disposed); verdict assembly gains APPROVED_WITH_SEVERE_WARNING tier, outranking plain CAUTION, still subordinate to BLOCKED from QUANT/MACRO/TAPE |

| 2.3 | 2026-07-24 | Anthony Zoppi / Claude | Phase E4 Live Data Automation: WO-P400-E4.001 (shared Schwab API client, shared_resources\python_utils\schwab_auth.py/schwab_client.py, OWNER_DONE, live-verified); WO-P400-E4.002 (automated snapshot/chain fetch, domain\chain_selector.py auto-select at 0.50 delta / 21-45 DTE, OWNER_DONE, live-verified); WO-P400-E4.003 (technical dossier -- SMA/RSI/MACD/Bollinger/pivot-S-R/Fibonacci computed via cli.py dossier, item 9 chart-pattern-ID remains Claude-narrated-only by explicit design, never auto-computed) |

| 2.4 | 2026-07-24 | Anthony Zoppi / Claude | WO-P400-E2.023: backward-looking post-earnings stabilization check added to MACRO role -- CAUTION-only, never BLOCK (Tony's call), config-driven threshold (POST_EARNINGS_STABILIZATION_SESSIONS, default 3, matches P_115 V110.3 precedent). Snapshot Dict Contract (6.2) gains last_earnings_date. Found live same session: SXT (P_115, same-day earnings, BLOCKED on drift) and CLF (P_300, 1-session-old earnings, R:R at the bare 2.0 floor pre-move) both slipped through Tier-1 screen with no deterministic catch. |

**Review Schedule:** after every 5 completed trades, then monthly
**Next Review:** after 5 Phase-E2 trades

---

**Document Classification:** Internal
**Document Owner:** Anthony Zoppi
**Canonical Location:** projects\P_400_TradeOrderManagement\docs\P_400_TradeOrderManagement_Architecture_v2_0.md

*END OF DOCUMENT*