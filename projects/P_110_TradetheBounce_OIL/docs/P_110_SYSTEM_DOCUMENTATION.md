# P_110_TradeTheBounce — System Documentation
**Project ID:** P_110
**Version:** 1.0
**Last Updated:** 2026-09-14
**Maintained By:** Anthony Zoppi
**Status:** Active
**Governed By:** P_000 (`P_000_SYSTEM_DOCUMENTATION.md`) / `Agentic-Hub-Governance\work_orders\`

---

## 1. PROJECT OVERVIEW

### 1.1 Purpose
Systematic, long-only mean-reversion bounce-trading system executed in ThinkOrSwim. Detects price bouncing off multi-touch support with a decoupled setup/confirmation model, with a Python analytics layer (PCA/multicollinearity reduction) planned but not yet built to validate signal independence as live data accumulates.

### 1.2 Scope

**What This System Covers:**
- Daily setup scan → watchlist → strict confirmation scan/chart workflow (the "DailyStrict" lineage: V1 scan, V3→V5 chart)
- A separate multi-timeframe (Daily + 4H) bounce engine with S/R zones, Fibonacci levels, ADX regime filter, and ATR-anchored stops (the "OIL" lineage: v3→V4)
- Signal/paper-trade logging as baseline data for a future validation layer

**What This System Does NOT Cover:**
- Short-side execution — every strategy in the Hub (P_115–P_118, and now P_110) is long-only by design; no strategy has a home for shorting
- Automated order execution — signals are manual-entry only
- Options overlay — that is P_116 (Options Income Launchpad)
- Intraday (VWAP-based) confirmation variants — proposed in the Perplexity summary docs, never built
- On-platform ANN/PCA — ThinkScript cannot run eigen decomposition or train a network; the Research.md spec explicitly recommends external precompute, which has not been implemented

### 1.3 Project Details

| Field | Value |
|---|---|
| Start Date | Not recorded in chat history. Earliest confirmed milestone: first paper trade logged (SNDX, session dated 2026-07-07) |
| Current Status | Active |
| Primary AI Engine | Claude (claude.ai Project) |
| Primary Platform | ThinkOrSwim (ThinkScript); Python (planned, not built) |
| Project Location | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_110_TradetheBounce_OIL\` |
| Related Projects | P_300 (VantagePoint data source, used for the Break-and-Retest validation backtest); P_115–P_118 (sibling long-only strategies, same long-only convention) |
| Python Environment | p140 conda — `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Work Order Ledger | `Agentic-Hub-Governance\work_orders\WO-P110-*.md` — none found on disk as of this writing; P_110 has not yet adopted formal WO tracking |

### 1.4 Reference Materials

| Document | Location | Notes |
|---|---|---|
| Livermore method Break and Retest.md | `docs\` | Spec for the Break-and-Retest strategy — evaluated against P_110 and rejected (see Section 2.5) |
| P_110_Trade the Bounce Research.md | `docs\` | ThinkScript feasibility spec: touch-counting, micro-decay logistic P(bounce), ATR/MAE buffer, ANN/PCA integration patterns |
| P_110 TradeThe Bounce STORM Analysis.md | `docs\` | Plain-language PCA/multicollinearity explainer — why raw indicators need dimensionality reduction before feeding an ANN |
| Bounce_Trading_Ground_Truth.txt | `docs\` | Abstracts of the three academic sources below |
| Evidence_and_Behaviour_of_Support_and_Resistance_L.pdf (Chung & Bellotti, 2021) | `docs\` | SR-level bounce probability formalized: `p(b\|b_prev)` rises with prior touch count, decays over time; confirmed across EURUSD/LLOY/BRENT and rejects simple AR(1) explanations |
| Support for Resistance-Technical Analysis and Intraday Exchange Rates.pdf (Osler, 2000) | `docs\` | Published FX support/resistance levels predict intraday trend interruptions at statistically significant rates (60.8% vs 56.2% baseline); predictive power persists ≥5 business days |
| Swing Trading Strategy using SMA Crossovers, Volume, Super Trend... .pdf (Kadia et al., 2026) | `docs\` | ANN combining SMA crossover + volume + Super Trend outperforms rule-based baselines in their backtest (31.6% annual return, 63.4% win rate, 1.21 Sharpe) — informs the deferred ANN/PCA enhancement, not yet adopted |
| P_110_TrueBounceConfirmation_DailyStrict_Chart_V3.md | `docs\` | Perplexity session establishing the setup-scan/watchlist/strict-scan/chart naming convention |
| P_110_TradeTheBounce_Summary_Perplexity.md / _v2.md | `docs\` | Workflow write-ups: the Setup vs Confirmation design split and why it was necessary (TOS boolean arrows mark every true bar, not just the event bar) |
| P_110_TradeTheBounce_FirstTrade.pdf | `docs\` | Chaikin Analytics snapshot for AKTX, the first live Confirm=YES signal |
| `CLAUDE.md` / `tasks\lessons.md` / `tasks\todo.md` | Not present | Not yet built — per P_000 guidance these earn their place once real accumulated depth exists; audit before adding |

### 1.5 Definitions & Acronyms

| Term / Acronym | Definition |
|---|---|
| TOS | ThinkOrSwim — primary charting and execution platform |
| FSM | Finite State Machine — not used in P_110's own logic, but the framework Break-and-Retest used (relevant to the rejection rationale in 2.5) |
| Setup | Price is in a location where a bounce could develop (near support, trend-aligned) — "watch," not a trade signal |
| Confirmation | Price action shows buyers have actually regained control — "consider action" |
| ATR | Average True Range — volatility input for stop/target sizing |
| ADX | Average Directional Index — trend-strength filter |
| VP | VantagePoint — third-party predictive indicator suite, used as P_300's data source and, incidentally, as the OHLCV source for the Break-and-Retest validation backtest |
| R-multiple | Trade outcome expressed as a multiple of initial risk (entry − stop) |
| OIL | Naming fragment in the multi-timeframe script lineage (`Script_ID_P_110_BounceTrade_OIL_v3` → `P_110_TradeTheBounce_V4`) — origin of the acronym not stated in any reviewed document |

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Flow

```
[TOS Stock Hacker: Loose Setup Scan]
              |
              v
[Dynamic Watchlist: P_110_TtradeTheBounceSetup_mmddyy]
              |
              v
[Strict Confirmation Scan]  <-- daily aggregation
              |
              v
[Chart Verification: DailyStrict Chart V5  -or-  P_110_TradeTheBounce_V4]
              |
              v
[Manual Trade Entry / Paper Trade]
              |
              v
[Ad Hoc Signal Log  ->  (planned) Python PCA Validation Layer]
```

**Description:** A loose daily scan finds candidates near support with soft oversold/range characteristics and saves them to a watchlist. A stricter scan (or, separately, either chart study) re-evaluates that watchlist for an actual confirmation bar. The chart study is the visual source of truth for entry timing — Setup=YES/Confirm=NO means watch only; Setup=YES/Confirm=YES means the reclaim bar has printed. Trades are entered manually and logged ad hoc; that log is meant to eventually feed a Python PCA/ANN validation module, which does not yet exist.

### 2.2 Core Components — Two Parallel Lineages

P_110 currently runs **two independently-developed confirmation systems** that were not cross-referenced with each other until this document. Both are long-only, both use a daily aggregation, both had the identical structural bug, and both have now been fixed — but they are not the same script and use different parameter sets (Section 11.4).

#### Lineage A: DailyStrict (single-timeframe)
- **Files:** `P_110_TradeTheBounceSetupScan_v1` (scan) → `P_110_TradeTheBounceBounce_DailyStrict_Scan_V2` (scan) → `P_110_TrueBounceConfirmation_DailyStrict_Chart_V3` → `V4` (condition pruning) → `V5` (rolling-window fix)
- **Responsibility:** Lightweight daily setup/confirm signal off a single timeframe — support proximity, RSI softness, range, prior-high reclaim, EMA reclaim, relative volume
- **Status:** **Live-validated.** First-ever Confirm=YES fired on AKTX (Chaikin snapshot dated 2026-08-14); first paper trade logged on SNDX (2026-07-07)
- **Tools Used:** ThinkScript, TOS Stock Hacker, TOS chart

#### Lineage B: OIL / Multi-Timeframe
- **Files:** `Script_ID_P_110_BounceTrade_OIL_v3` → `P_110_TradeTheBounce_V4` (this session, 2026-09-14)
- **Responsibility:** Broader Daily+4H confluence engine — pivot and Fibonacci S/R zones, ADX regime filter, structural ATR stop, dashboard labels
- **Status:** **Not yet live-tested.** v3 had the same same-bar timing bug DailyStrict V5 had already fixed, plus four other defects (Section 6). V4 fixes all of them but has fired zero live signals as of this writing.
- **Tools Used:** ThinkScript, TOS chart (no dedicated scan built for this lineage)

**Design decision (2026-09-14):** the two lineages are intentionally different, not accidentally so. Lineage B (OIL) is deliberately looser on proximity (2.0% vs. 0.5%) and RSI depth (<30 vs. <45) because it carries extra confluence Lineage A doesn't have -- daily+4H trend alignment. Lineage A is the precise, validated entry trigger; Lineage B is a broader confluence filter. Not merged, and not planned to be -- the parameter gap in Section 11.4 is documented design intent, not an unreconciled accident.

### 2.3 System Decomposition

```
P_110_TradeTheBounce
├── DailyStrict Lineage
│   ├── Setup Scan (v1)
│   ├── Strict Confirmation Scan (V2)
│   └── Chart Study (V3 -> V4 -> V5)
├── OIL / Multi-Timeframe Lineage
│   └── Chart Study (v3 -> V4)
├── Signal Logging (ad hoc, not yet a formal schema)
└── Python PCA Validation Layer (planned, not built)
```

### 2.4 Project Directory Structure

**Actual, as of 2026-09-14:**

```
P_110_TradetheBounce_OIL\
├── data\
├── docs\                          # research papers, prior script versions as .md, media
├── outputs\
├── python\                        # conftest.py only -- PCA module not started
├── strategies\
│   ├── backtests\
│   └── rules\
├── tos_scripts\                   # was empty until this session -- P_110_TradeTheBounce_V4.txt added
├── README.md
└── README_backup_2026-06-30.md
```

No `CLAUDE.md` or `tasks\` folder — not yet warranted per P_000 guidance (audit first; build once real accumulated depth exists).

**Shared, Hub-root resources this project draws on:**

| What | Canonical Path |
|---|---|
| p140 interpreter | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| VantagePoint bulk data (cross-project, read-only) | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\bulk\mine\` |
| Work order ledger | `Agentic-Hub-Governance\work_orders\` (not yet used by P_110) |

### 2.5 Design Rationale

**Why This Architecture?**
- **Setup/Confirmation split:** TOS boolean-arrow plots mark *every* bar where a condition holds, not just the triggering bar. Early single-stage versions plotted arrow clusters. Splitting "price is near support" (a zone/state) from "buyers have regained control" (a single event) fixed this, per the Perplexity workflow summaries.
- **Long-only:** every other strategy in the Hub (P_115 Buy The Dip, P_116 Options Income Launchpad, P_117, P_118) is long-only. No strategy has short-side infrastructure. P_110's OIL lineage originally carried full short-side logic (SellSignal, stops, alerts) inconsistent with this; it was stripped in V4.
- **Rolling-window confirmation, not same-bar:** both lineages independently ran into the same bug — requiring the setup condition and the trigger/breakout condition to be true on the identical bar. Real bounces resolve over 1–3 bars (low prints on day T, reclaim happens T+1/T+2). Both are now fixed with `Sum(setupCondition, N) > 0` decoupling.
- **Structural, not pure-ATR, stops (OIL V4 only):** a stop measured purely as ATR-off-entry-close can end up floating above the actual support/fib level the trade thesis depends on, especially since confirmation can now fire several bars into the setup window. OIL V4 anchors the stop to the support/fib floor instead.

**Alternatives Considered:**

| Option | Pros | Cons | Decision |
|---|---|---|---|
| Break-and-Retest (trend-continuation strategy, separate spec) | Different regime coverage (trend continuation vs. mean reversion); FSM-based design was cleanly portable to Python | 111-symbol, 10-year backtest showed the apparent edge (0.27R avg, n=35) collapsed to 0.07R at full sample (n=463) — an illusory edge from time-based exits diluting the assumed fixed R:R | Rejected. Logged in `decisions-and-learnings.md`; P_110 confirmed as the stronger, live-validated strategy by comparison |
| Full ANN/PCA pipeline running inside ThinkScript | Matches the academic literature's stated approach (Research.md, STORM Analysis.md) | ThinkScript cannot perform eigen decomposition or train/run a network; Research.md itself recommends external precompute | Deferred. External-precompute pattern documented in Research.md Section 5 but not implemented; planned Python module (Section 7) is the intended path |
| Merge OIL lineage into DailyStrict | Single source of truth, less parameter drift | OIL's multi-timeframe confluence and structural stop are architecturally different enough that merging isn't a small change | Not decided — flagged as an open question in 2.2, not resolved by this document |

---

## 3. AI TOOLS & PLATFORMS

### 3.1 Tool Stack

| Tool / Platform | Role in System | Version / Tier | Notes |
|---|---|---|---|
| Claude.ai | Primary AI engine — script review, debugging, strategy evaluation, documentation | Sonnet (Project-based) | Core reasoning layer for this Hub project |
| ThinkOrSwim | Charting, scans, execution | Not recorded | Both script lineages live here |
| Python | Planned analytics layer (PCA/multicollinearity) | p140 conda env | Not yet built for P_110 specifically; `conftest.py` is the only file present |
| VantagePoint | Data source for the (separate, rejected) Break-and-Retest validation backtest | Not recorded | Not used by P_110's own signal logic — only by the ad hoc validation script under `validation\BreakAndRetest_Backtest\` |
| windows-mcp / filesystem MCP | Direct file read/write to the Hub on Tony's machine | — | Used this session to inspect and correct the OIL script directly |

### 3.2 Claude Project Configuration

| Setting | Value |
|---|---|
| Project Name | P_110_TradeTheBounce (claude.ai Project) |
| Knowledge Files | Research.md, STORM Analysis.md, Ground Truth.txt, both Perplexity summaries, DailyStrict_Chart_V3.md, FirstTrade.pdf, and the two academic PDFs (Osler 2000; Chung & Bellotti 2021), plus the swing-trading ANN paper (Kadia et al. 2026) |
| Memory Enabled | Yes — persistent memory filesystem in use across sessions |
| Session Init Required | Not formally defined for P_110 specifically; Hub-wide `system-doc-initializer` skill pattern applies |
| Primary Model | Not fixed to a specific model in project settings |

### 3.3 Prompt Library (Master List)
Not currently maintained as a discrete prompt library. Work in this project has proceeded conversationally (script review → fix → deliver), not via saved prompt templates. If a repeatable pattern emerges (e.g., a standard "review this ThinkScript for gaps" prompt), it belongs here.

### 3.4 AI Behavior Rules & Constraints

**Claude MUST:**
- Produce and get approval on a plan before writing code (Hub-wide plan-before-build gate)
- Give one clear recommendation, not a list of options
- State the full Windows save path with every file reference
- Never fabricate diagnostic values (RSI/RVOL/ADX must come from what TOS or the data actually shows)
- Confirm cross-project file access before use (e.g., reading P_300's VantagePoint exports)

**Claude MUST NOT:**
- Assume ThinkScript compiles cleanly without verification — this session's OIL V4 draft had two variable-scoping errors that only surfaced on actual compile
- Treat a small-sample backtest result as validated (see the Break-and-Retest 11-symbol vs. 111-symbol collapse in Section 6)
- Add short-side trade execution logic — no strategy in the Hub trades short

**Session Initialization:**
Not formally defined for this project. No SESSION_INITIALIZATION_PROMPT.md observed in `docs\`.

---

## 4. REQUIREMENTS

### 4.1 Functional Requirements

#### FR-1: Detect a valid bounce setup
- **Description:** Identify price near a multi-touch support zone with trend-aligned context
- **Acceptance Criteria:**
  - [x] Support level detected via non-repainting pivot logic
  - [x] Proximity to that level configurable (proximityPercent)
  - [ ] Multi-touch clustering (≥3 touches) formalized — DailyStrict uses a single pivot lookback, not a touch-count cluster; OIL V4 also uses single-pivot proximity, not clustering
- **Component:** Setup Scan (Lineage A) / `nearSupportSetup` (Lineage B, OIL V4)
- **Priority:** High

#### FR-2: Confirm the bounce without requiring same-bar coincidence
- **Description:** Decouple the setup bar from the trigger/reclaim bar
- **Acceptance Criteria:**
  - [x] Rolling-window `Sum(setupCondition, N) > 0` pattern implemented
  - [x] Live-validated (AKTX, Lineage A)
  - [ ] Live-validated for Lineage B (OIL V4) — not yet, built this session
- **Component:** `setupWindow` / `confirmationRaw` in both lineages
- **Priority:** High

#### FR-3: Structural, thesis-anchored stop-loss
- **Description:** Stop placement tied to the support/fib level, not a floating ATR distance
- **Acceptance Criteria:**
  - [x] Implemented in OIL V4 (`structuralFloor - ATR buffer`)
  - [ ] Not present in DailyStrict lineage (no stop/target logic in that chart study at all — it is a signal-only indicator)
- **Component:** OIL V4 Controller
- **Priority:** Medium

#### FR-4: Long-only signal generation
- **Description:** No short-side execution artifacts
- **Acceptance Criteria:**
  - [x] OIL V4 strips SellSignal/stopLossSell/targetSell/sell alert
  - [x] DailyStrict lineage was never symmetric (bullish-only by design)
- **Component:** Both lineages
- **Priority:** High

#### FR-5: Log every signal/paper trade for future validation
- **Description:** Capture enough metadata per signal to eventually feed a PCA/ANN module
- **Acceptance Criteria:**
  - [x] AKTX and SNDX logged as baseline data points
  - [ ] No structured schema or file exists yet — logging has been ad hoc within chat sessions
- **Component:** Not yet built
- **Priority:** Medium

### 4.2 Non-Functional Requirements

#### NFR-1: Accuracy
- **Requirement:** No fabricated diagnostic values
- **Target:** RSI/RVOL/ADX/price levels shown on-chart must match live TOS or actual data
- **Implementation:** Chart-side `AddLabel` diagnostics; manual cross-check against known-good examples (Section 10.2)

#### NFR-2: Consistency
- **Requirement:** Setup/Confirm terminology and behavior standardized
- **Target:** Both lineages now share the Setup=YES/Confirm=YES semantics and the rolling-window pattern (as of this document)
- **Implementation:** V5 (Lineage A) and V4 (Lineage B) both implement the same core fix, though with different parameter values (Section 11.4)

#### NFR-3: Auditability
- **Requirement:** Every fired signal traceable to symbol, date, and diagnostic snapshot
- **Target:** Not fully met — no structured log file exists (see FR-5)
- **Implementation:** Currently only via chat history and the Chaikin PDF snapshot for AKTX

### 4.3 Requirements Matrix

| ID | Description | Component | Status | Notes |
|---|---|---|---|---|
| FR-1 | Bounce setup detection | Both lineages | In Progress | Touch clustering not formalized in either |
| FR-2 | Rolling-window confirmation | Both lineages | Complete (A) / Complete but unvalidated (B) | |
| FR-3 | Structural stop | OIL V4 only | Complete (B) / Not Applicable (A) | |
| FR-4 | Long-only | Both lineages | Complete | |
| FR-5 | Signal logging | Neither (ad hoc only) | Pending | Blocks the planned PCA module |

---

## 5. CHANGE LOG

### Version History

---

#### DailyStrict V3 — Date not recorded
**Release Type:** Major (initial strict chart study)
**Added:** 8-condition confirmation logic (green bar, strong close, close>prior close, close>prior high, relative volume, short-EMA reclaim, trend-improvement check)

---

#### DailyStrict V4 — Date not recorded
**Release Type:** Minor
**Modified:** Pruned redundant conditions from 8 to 5 — `abovePriorClose` was logically implied by `abovePriorHigh` (dead code); `trendImprove` was neutralized by mandatory `emaReclaim` (non-functional toggle); `greenBar` was redundant given the stricter `strongClose`
**Breaking Changes:** No — identical signal behavior at default settings

---

#### DailyStrict V5 — 2026-08-07
**Release Type:** Major (structural fix)
**Fixed:** Same-bar structural timing flaw — `confirmationRaw` required `bounceSetup` and all four confirmation conditions on the identical bar, which real multi-day bounces essentially never satisfy. Replaced with `setupWindow = Sum(bounceSetup, confirmWindowBars) > 0`.
**Breaking Changes:** Yes — signal frequency increases substantially; this fix is what allowed the first-ever Confirm=YES (AKTX) to fire

---

#### OIL v3 — Uploaded 2026-09-14 (build date not recorded)
**Release Type:** N/A (this document's first record of this lineage)
**Notes:** Independent multi-timeframe engine, never cross-referenced against the DailyStrict lineage's V5 fix. Carried the identical same-bar bug, plus four additional defects (Section 6).

---

#### P_110_TradeTheBounce_V4 (renamed from OIL v4) — 2026-09-14
**Release Type:** Major
**Added:** Structural stop, `arrowCooldownBars` dedup, Setup/Confirm dashboard labels
**Modified:** `volumeLookback` 5→20; `bullishEngulfing` redefined as true body engulfment; `nearSupport`/`nearSupport4H` now test LOW touching the zone instead of CLOSE already reclaimed
**Fixed:** Same-bar composite firing (ported V5's rolling-window pattern); ADX asymmetry between uptrend/downtrend classification; `weakeningUptrend` compile errors (see Error Corrections Log)
**Removed / Deprecated:** All short-side execution (SellSignal, stopLossSell, targetSell, sell alert, bearishEngulfing)
**Breaking Changes:** Yes — this is a different signal profile than OIL v3, and has not yet fired a live signal

---

## 6. ERROR CORRECTIONS LOG

---

### Error: Same-bar structural timing flaw (DailyStrict)
- **Date Discovered:** 2026-08-07
- **Severity:** Critical
- **Status:** Resolved

**Wrong Behavior:** `confirmationRaw` required `bounceSetup` (near support) and `abovePriorHigh`/`emaReclaim` (the actual breakout, typically 1–2 bars later) to be true on the identical bar. Structurally near-impossible for a real bounce sequence.

**Correct Behavior:** `setupWindow = Sum(bounceSetup, confirmWindowBars) > 0` decouples the setup bar from the confirmation bar, letting the trigger fire up to `confirmWindowBars` bars after the setup.

**Root Cause:** Initial design didn't account for bounces developing across multiple bars rather than resolving instantly.

**Fix Applied:**
- Rolling-window `Sum()` pattern replacing the same-bar `bounceSetup` gate

**Verification:** First-ever live Confirm=YES fired on AKTX shortly after deployment (Chaikin snapshot dated 2026-08-14: RVOL 3.4x, RSI 42.3 vs. 45 threshold, daily+4H downtrend context, ADX 21, price 31.4% below 200-SMA)

---

### Error: Same flaw reintroduced, independently, in the OIL lineage
- **Date Discovered:** 2026-09-14
- **Severity:** High
- **Status:** Resolved

**Wrong Behavior:** OIL v3's `bullishBounce` required `finalUptrend`, `finalUptrend4H`, `nearSupport`, `nearSupport4H`, and a trigger condition all true on the identical bar — the same category of bug as the DailyStrict V4→V5 fix, in a script that had never been cross-referenced against it.

**Root Cause:** Two confirmation-script lineages developed independently under the same project without a shared review pass.

**Fix Applied:**
- Ported the rolling-window pattern into OIL V4
- Documented the dual-lineage structure explicitly in Section 2.2 of this document so it isn't missed a third time

**Verification:** Not yet live-validated (Lineage B has fired zero live signals as of this writing)

---

### Error: ThinkScript forward-reference compile failure in OIL V4 draft
- **Date Discovered:** 2026-09-14
- **Severity:** Medium
- **Status:** Resolved

**Wrong Behavior:** `weakeningUptrend` (and its 4H equivalent) was declared as a separate variable referencing `finalUptrend[1]` before `finalUptrend` was declared later in the script. Compiler returned `No such variable: finalUptrend` / `finalUptrend4H`.

```
Example of wrong logic:
def weakeningUptrend = finalUptrend[1] and (...);   # finalUptrend not yet declared
def finalUptrend = isUptrend and !weakeningUptrend;
```

**Correct Behavior:** Fold the weakening check directly into `finalUptrend`'s own self-referential definition — same-line self-reference to a historical offset of itself is valid ThinkScript (it's the same pattern `supportLevel`/`resistanceLevel` already use); a forward reference to a *different*, not-yet-declared def is not.

```
Example of correct logic:
def finalUptrend = isUptrend and !(finalUptrend[1] and (...));
```

**Root Cause:** Incorrect assumption that ThinkScript resolves declarative dependency graphs the way a self-referential recursive persistence pattern does, regardless of which def is doing the referencing. It does not — same-line self-reference is a special-cased allowance, not general forward-reference support.

**Fix Applied:**
- Single self-referential def per trend classification, daily and 4H

**Verification:** Re-delivered script compiled without the two reported errors (per Tony's follow-up message)

---

### Error: Break-and-Retest illusory edge from small-sample backtest
- **Date Discovered:** 2026-08-26
- **Severity:** High
- **Status:** Resolved (strategy rejected, not a code bug)

**Wrong Behavior:** An 11-symbol backtest run showed a 0.27R average per trade, above the naive 3:1 target-to-stop breakeven of 25% win rate. This was read as a mild positive edge.

**Correct Behavior:** The full 111-symbol, 10-year run (463 signals) showed the average collapse to 0.07R — statistical noise, not edge. Win rate held roughly steady (34.3%→34.6%), but the average win size was diluted by trades exiting on a time-based cutoff at whatever partial R the price happened to be at, not the assumed fixed 3R target.

**Root Cause:** Small-sample luck, compounded by an initial breakeven-math assumption (every win pays exactly 3R) that doesn't hold once time-based exits are in the mix.

**Fix Applied:**
- Ran the full available dataset before drawing a conclusion
- Documented the general lesson in `decisions-and-learnings.md`: "any backtest using time exits must account for [variable R-multiples] or risk illusory edge"
- Break-and-Retest closed out; P_110 confirmed as the stronger strategy by comparison

**Verification:** 463-trade sample is large enough that the 0.07R result is treated as reliable

---

## 7. ENHANCEMENT LOG

### Active Enhancements

#### Enhancement: Python PCA/multicollinearity validation module
- **Status:** Planned
- **Priority:** Medium
- **Target Date:** Not set — deferred, awaiting trigger
- **Description:** 9-file structure, ~465 lines, p140 conda env, pandas/scikit-learn/pydantic. Consumes TOS OHLCV CSV exports, outputs a correlation matrix and PCA loadings report.
- **Expected Benefit:** Confirms whether indicators feeding future signal logic are genuinely independent, per the multicollinearity concern raised in STORM Analysis.md
- **Dependencies:** More accumulated live/paper signal data (currently only AKTX + SNDX)
- **Success Criteria:** Not yet defined

#### Enhancement: Structured signal-log schema
- **Status:** Planned
- **Priority:** Medium
- **Description:** Replace ad hoc chat-logged signals (AKTX, SNDX) with a defined file schema
- **Expected Benefit:** Unblocks the PCA module (FR-5) and formal backtesting of the bounce logic itself
- **Dependencies:** None — could be built independently of the PCA module

#### Enhancement: Intraday (15-min / 1-hour) VWAP-based confirmation
- **Status:** Planned
- **Priority:** Low
- **Description:** Per the Perplexity workflow docs — VWAP becomes a meaningful reclaim reference intraday in a way it isn't on daily bars
- **Expected Benefit:** Earlier, more tactical entries than the daily-only workflow currently supports

### Completed Enhancements

| Enhancement | Completed Date | Result |
|---|---|---|
| DailyStrict condition pruning (8→5) | Date not recorded | Same signal behavior, less redundancy |
| DailyStrict rolling-window fix (V5) | 2026-08-07 | Unblocked first-ever live Confirm=YES (AKTX) |
| OIL lineage full fix pass (V4) | 2026-09-14 | 9 defects fixed; not yet live-validated |

### Parked / Deferred

| Enhancement | Reason Deferred | Revisit Date |
|---|---|---|
| Full on-platform ANN/PCA execution | Not feasible in ThinkScript (eigen decomposition, network training unsupported) | When external-precompute Python module is built |
| 4H ADX-equivalent trend-strength gate (OIL lineage) | ThinkScript's cross-timeframe DMI reference syntax not verifiable without a live compile test | Next OIL revision |
| Merging the two script lineages | Decided against on 2026-09-14 -- intentionally different roles (Lineage A = precise trigger, Lineage B = looser confluence filter), not an oversight to fix | Closed, not deferred |

---

## 8. AI WORKFLOWS & PROCESSES

### 8.1 Primary Workflow: Daily Setup → Confirmation (Lineage A)

**Trigger:** After close / before next session open
**Frequency:** Daily
**Time Required:** Not recorded

**Steps:**
1. Run `P_110_TradeTheBounceSetupScan_v1` on daily aggregation
2. Save results to dynamic watchlist `P_110_TtradeTheBounceSetup_mmddyy`
3. Run `P_110_TradeTheBounceBounce_DailyStrict_Scan_V2` against that watchlist
4. Verify visually on the DailyStrict chart study (Setup/Confirm labels)
5. If Confirm=YES, evaluate manually and log the trade

**Expected Output:** A short list (often one or a few names) of confirmed reclaim bars, ready for manual trade evaluation.

**Decision Gate:**
```
If Setup=YES and Confirm=NO --> watchlist candidate, not a trade
If Setup=YES and Confirm=YES --> consider entry
```

### 8.2 Secondary Workflow: OIL Multi-Timeframe Review (Lineage B)

**Trigger:** Ad hoc — no dedicated scan feeds this lineage yet
**Frequency:** Not established
**Steps:** Load `P_110_TradeTheBounce_V4` on a chart, read the Setup/Confirm/trend labels directly — no watchlist-driven workflow exists for this lineage as of this document.

### 8.4 Exception Workflows

#### Exception: The two lineages disagree on a symbol
- **Trigger:** DailyStrict shows Confirm=YES while OIL V4 doesn't (or vice versa) on the same symbol/date
- **Action:** Treat DailyStrict V5 as the validated baseline (it has a live-confirmed signal); treat OIL V4 as unvalidated until it produces its own
- **Documentation:** Note which script sourced a given signal when logging it — not currently enforced by any schema (see Enhancement Log)

---

## 9. DATA DESIGN

### 9.1 Data Inputs

| Data Type | Source | Format | How Fed to Claude |
|---|---|---|---|
| Chart data | TOS (live) | Chart / screenshot | Visual review during script debugging |
| VantagePoint bulk exports | P_300's `data\bulk\mine\` (cross-project, read-only) | `.xlsx` | Used only by the separate Break-and-Retest validation script, not by P_110's own signal logic |
| Scan results | TOS Stock Hacker | Ticker list | Not typically pasted to Claude — used directly in TOS |

### 9.2 Data Outputs

| Output Type | Format | Destination | Frequency |
|---|---|---|---|
| Setup/Confirm chart labels | On-chart text | TOS chart | Every bar |
| Buy signal arrow | Chart plot | TOS chart | On confirmed bounce |
| Trade/signal log entries | Ad hoc chat notes | Not centralized | Per trade (2 recorded to date: AKTX, SNDX) |

### 9.3 Data Schema
Not formalized. This is the direct blocker for FR-5 and the planned PCA module (Section 7).

### 9.4 Data Integrity Rules
- Never fabricate diagnostic values — RSI/RVOL/ADX must reflect what the platform actually shows
- VantagePoint bulk exports require defensive coercion before use in Python: literal `'∞'` strings (division-by-zero in `roc_pct`), blank pre-backfill cells (map to 0.0), and non-standard `neural_index` markers like `'n/a'` (map to `'unknown'`) — documented during the Break-and-Retest backtest build and directly relevant if the planned PCA module ever ingests VP data

---

## 10. TESTING & VALIDATION

### 10.1 Testing Approach

**Philosophy:** Live/paper validation against real TOS behavior, not a formal backtest harness. **This is an honest limitation, not an oversight** — the only rigorous, large-sample backtest run under the P_110 umbrella was for Break-and-Retest, a *different* strategy that was then rejected. The bounce logic that P_110 actually trades (both lineages) has not itself been backtested end-to-end; it has two live/paper data points.

### 10.2 Known-Good Reference Examples

#### Example 1: AKTX — first live Confirm=YES (DailyStrict V5)
**Context:** Chaikin Analytics snapshot dated 2026-08-14. RVOL 3.4x, RSI 42.3 against a 45 threshold, daily and 4H downtrend context, ADX 21 (weak trend), price 31.4% below the 200-SMA.
**Notes:** A legitimate bounce-off-local-support signal within a larger downtrend — consistent with the strategy's design (support/resistance can interrupt trends without reversing them, per Osler 2000).

#### Example 2: SNDX — first paper trade
**Context:** BOT 75 SNDX @ 19.89, Order ID 5380336831, session dated 2026-07-07.
**Notes:** Baseline data point, logged before the V5 timing fix — sourced from the loose setup scan rather than a confirmed Confirm=YES bar.

### 10.4 Known Issues & Limitations

| Issue ID | Description | Severity | Workaround | Status |
|---|---|---|---|---|
| ID-001 | OIL V4 has never fired a live signal | Medium | Treat as unvalidated; rely on DailyStrict V5 for actual trading until OIL V4 proves itself | Open |
| ID-002 | No 4H ADX-equivalent gate in either OIL trend leg | Low | Deferred — cross-timeframe DMI syntax unverified | Open |
| ID-003 | No formal end-to-end backtest of the bounce logic itself | Medium | Only 2 live/paper data points exist; treat any read of "win rate" as anecdotal until the PCA/logging enhancement lands | Open |
| ID-004 | No structured signal log | Medium | Blocks FR-5 and the PCA module | Open |

---

## 11. DAILY OPERATIONS & SESSION MANAGEMENT

### 11.1 Session Startup Checklist
Not formally defined for this project.

### 11.4 Parameter Registry

**DailyStrict V5:**

| Parameter | Value |
|---|---|
| supportLookback | 5 |
| proximityPercent | 0.50% |
| rsiOversold | 45 |
| volumeMultiplier | 1.1x |
| confirmWindowBars | 5 |
| arrowCooldownBars | 5 |

**OIL / P_110_TradeTheBounce_V4:**

| Parameter | Value |
|---|---|
| proximityPercent | 2.0% |
| rsiOversold | 30 |
| adxThreshold | 25 |
| volumeLookback | 20 |
| confirmWindowBars | 5 |
| arrowCooldownBars | 5 |
| atrMultiplierStop | 1.5 (buffer below structural floor) |
| atrMultiplierTarget | 3.0 |

**Note:** these two parameter sets are meaningfully different (proximity 0.5% vs. 2.0%, RSI oversold 45 vs. 30) by design, not oversight (decided 2026-09-14, see Section 2.2). Lineage B trades proximity/RSI looseness for daily+4H confluence Lineage A doesn't have; Lineage A stays the tight, validated trigger. No reconciliation planned.

### 11.5 Work Order Governance
Not yet adopted for this project — no `WO-P110-*.md` files found under `Agentic-Hub-Governance\work_orders\` as of this writing, despite it being the Hub-wide standard.

---

## 12. TROUBLESHOOTING & SUPPORT

### 12.1 Common Issues & Solutions

#### Issue: No signals generating
- **Symptoms:** Confirm never shows YES despite plausible setups
- **Root Cause:** Historically, the same-bar structural timing bug (Section 6) — this was the root cause in *both* lineages independently
- **Solution:**
  1. Confirm the script version in use is V5+ (DailyStrict) or V4+ (OIL) — V3/V4-DailyStrict and OIL v3 all have the bug
  2. Check the Setup label first — if Setup never shows YES, the issue is upstream in zone/trend detection, not the confirmation window
- **Prevention:** Any future confirmation-logic script in this project should be checked against this exact failure mode before being trusted

#### Issue: ThinkScript compile error referencing a variable used before declaration
- **Symptoms:** `No such variable: X` at a specific line/column
- **Root Cause:** A def referencing another def's `[1]` historical offset before that def is declared elsewhere in the script — not valid, unlike same-line self-reference
- **Solution:** Fold the cross-referencing logic into a single self-referential def (see Section 6 fix)
- **Prevention:** When persistence/state logic is needed across bars, prefer the `def x = if cond then val else x[1];` self-reference pattern already used for `supportLevel`/`resistanceLevel` in this project, rather than splitting state into a separately-named def

### 12.3 Escalation Path

| Level | Condition | Action |
|---|---|---|
| Self-resolve | Minor output format issue | Restate the rule, show a known-good example |
| Documentation update | Same error 2+ times | Add to Error Corrections Log (Section 6) — already done for the dual-lineage timing bug |
| System redesign | Fundamental logic failure | Open Enhancement Log item |

---

## 13. APPENDICES

### Appendix A: Glossary of Terms

| Term | Definition |
|---|---|
| Lineage A | The DailyStrict single-timeframe script family (scan → V5 chart) |
| Lineage B | The OIL multi-timeframe script family (v3 → V4) |
| Bounce probability p(b\|b_prev) | From Chung & Bellotti (2021) — probability price bounces off a level given `b_prev` prior bounces on that same level; positively correlated with `b_prev`, decays with time |

### Appendix B: Related Project Documentation

| Document | Location | Purpose |
|---|---|---|
| Livermore method Break and Retest.md | `docs\` | Rejected alternative strategy spec — kept for reference |
| P_110_Trade the Bounce Research.md | `docs\` | ThinkScript feasibility + ANN/PCA integration patterns |
| P_110 TradeThe Bounce STORM Analysis.md | `docs\` | PCA/multicollinearity rationale |
| Evidence_and_Behaviour...pdf / Support for Resistance...pdf | `docs\` | Academic backing for support/resistance bounce predictability |
| **P_000_SYSTEM_DOCUMENTATION.md** | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\docs\` | Master Hub architecture reference |

### Appendix C: Code Repository

| Field | Value |
|---|---|
| Repository | Local only — `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_110_TradetheBounce_OIL\` |
| Primary Language | ThinkScript (both lineages); Python planned |
| Key Files | `tos_scripts\P_110_TradeTheBounce_V4.txt` (new, this session); DailyStrict V5 exists only in chat history, not yet saved to disk — flagged as a gap |
| Dependencies | None (ThinkScript is self-contained); planned Python module would need pandas, scikit-learn, pydantic in p140 |

### Appendix D: Architecture Diagram (Detailed)

```
+--------------------------------+
|   DATA INPUT LAYER             |
|   TOS Live Chart Data          |
|   (VantagePoint, separately,   |
|    only for validation work)   |
+---------------+----------------+
                |
                v
+--------------------------------+
|   LINEAGE A: DailyStrict       |     +--------------------------------+
|   Setup Scan -> Strict Scan    |     |   LINEAGE B: OIL / MTF         |
|   -> Chart V5 (rolling window) |     |   Chart V4 (rolling window +   |
|                                 |     |   structural stop, Daily+4H)   |
+---------------+----------------+     +---------------+----------------+
                |                                       |
                +-------------------+-------------------+
                                    |
                                    v
                  +--------------------------------+
                  |   MANUAL TRADE ENTRY            |
                  |   (no automated execution)      |
                  +---------------+----------------+
                                    |
                                    v
                  +--------------------------------+
                  |   AD HOC SIGNAL LOG             |
                  |   (AKTX, SNDX so far --         |
                  |    no formal schema)            |
                  +---------------+----------------+
                                    |
                                    v
                  +--------------------------------+
                  |   PYTHON PCA VALIDATION LAYER   |
                  |   (planned, not built)          |
                  +--------------------------------+
```

### Appendix E: Performance Benchmarks

| Metric | Baseline | Target | Current | Last Updated |
|---|---|---|---|---|
| Win Rate | Not established | Not set | Not measurable — only 2 live/paper data points | 2026-09-14 |
| Avg R:R | Not established | Not set | Not measurable | 2026-09-14 |

*Not filled with invented numbers — see Section 10.4, ID-003. This table should be populated once the structured signal log (Section 7) has accumulated enough trades to mean anything.*

### Appendix G: Document Version Control

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 1.0 | 2026-09-14 | Anthony Zoppi (assembled by Claude) | Initial document — built from project chat history, uploaded research PDFs/summaries, and the on-disk project structure. First formal record of the dual-lineage (DailyStrict vs. OIL) architecture. |

**Review Schedule:** Not yet set — recommend after the next live signal from either lineage, or once the structured signal log exists.
**Last Review:** 2026-09-14
**Next Review:** Not scheduled

---

**Document Classification:** Internal
**Document Owner:** Anthony Zoppi
**Template Version:** MASTER_PROJECT_TEMPLATE_v_2.0

---

*END OF DOCUMENT*
