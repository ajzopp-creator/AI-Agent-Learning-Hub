# P_400 Trade Management System — System Documentation
**Project ID:** P_400
**Version:** 0.1 (Prototype Architecture)
**Last Updated:** 2026-05-26
**Maintained By:** Anthony Zoppi
**Status:** In Development — prototype phase, manual execution

---

## DOCUMENTATION DECISION PROTOCOL
*Read this before creating any new documentation.*

### The Golden Rule
**Always try to fit new content into this master document first.** Only spawn a separate file when content exceeds one page, changes frequently, is shared across projects, or needs its own version history.

### Decision Flow (Standard from template)
Add content here → unless > 1 page OR frequently updated OR shared → then split out and link back.

### When Creating a Separate File — Always Ask First
Before any new file, confirm: "Does this belong in the master doc, or is there an existing file it should merge into?" New files must follow naming: `P_400_[Topic]_v[X.X].md` and be registered in Section 13 Appendix B.

### Reference Link Format
```
> **Linked Document:** [Filename]
> **Location:** [Project Knowledge / Local Path]
> **Purpose:** [One line]
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
**Objective:** P_400 is the trade management engine that takes any validated BUY signal from upstream projects (P_115, P_300, and future signal sources) and produces a Council-reviewed, broker-ready order specification — first for stocks, then for options, ultimately selecting the most profitable vehicle (shares, vertical, debit spread, etc.) automatically. P_400 owns the trade from the moment the BUY signal lands until the position is closed and final P&L is recorded back to the Obsidian vault via the P_800 interface.

Phase 1 (this document) is a **manual-execution prototype**: P_400 outputs a fully-specified order description so precise that Tony types it into Schwab exactly as written, with zero interpretation required.

### 1.2 Scope

**What This System Covers:**
- Reconciliation of upstream BUY signals (P_115, P_300) against live market data
- Live data acquisition (Schwab API primary, web fallback) for current price, ATR, IV, bid/ask, option chains
- Position sizing using account balance and risk-per-trade rules
- Five-role Council review with hard blocks on Quant / Macro / Tape failures
- Production of broker-ready order specifications:
  - Stock orders (single-leg and OCO brackets)
  - Option orders (single contract, vertical spreads, complex 1st-triggers-OCO/All)
- Lifecycle tracking from PENDING → SUBMITTED → FILLED → T1_HIT → TRAILING → CLOSED
- Obsidian vault updates (frontmatter + appended log entries) via P_800's `handle_write()` interface
- Hand-off back to P_020 for final performance recording when position closes

**What This System Does NOT Cover:**
- Generating BUY signals (owned by P_115, P_300, future signal projects)
- Automated order submission to Schwab (Phase 1 is manual entry by Tony)
- Tax-lot accounting or wash-sale tracking
- Knowledge-base article writing (owned by P_800 / KB)
- Schema ownership of `TradeManagementRecord` (owned by P_800)
- Bearish / SELL-signal trade construction (Phase 3 — explicitly out of scope for v0.1)
- Crypto orders on Kraken (Phase 2+ once stock + option workflows are stable)

### 1.3 Project Details

| Field | Value |
|---|---|
| Start Date | 2026-05-26 |
| Current Status | In Development — prototype phase |
| Primary AI Engine | Perplexity Computer (with `p-400-tos-trade-setup` skill) |
| Primary Platform | Schwab (broker), Obsidian (record store), ThinkOrSwim (charting reference) |
| Project Location | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_Trade_Management_System\` |
| Related Projects | P_115 (signal source), P_300 (signal source), P_800 (vault interface), P_020 (performance) |

### 1.4 Reference Materials

| Document | Location | Notes |
|---|---|---|
| P_400-Perplexity-Master-Trade-SetUp-Prompt.md | Project Knowledge | Original master prompt — superseded in part by this doc |
| P_300 Perplexity Council Review Order Prompt.md | Space Files | Council trigger prompt from P_300 |
| HUB_Obsidian_Interface_Architecture.md | Project Knowledge | P_800-owned schema + write interface — P_400 conforms to this |
| `p-400-tos-trade-setup` SKILL.md | Perplexity skill library | Phase 0 order-ticket builder (will be extended for Phase 1) |
| Sample P_115 BUY file | `2024-12-18_AMTM.md` | Upstream input example |
| Sample P_300 BUY file | `2026-05-21_CFG.md` | Upstream input example |

### 1.5 Definitions & Acronyms

| Term / Acronym | Definition |
|---|---|
| BUY signal | Validated long-side entry signal from P_115 or P_300 |
| Council | Five-role decision body that approves/blocks every order |
| Guideline entry | The entry price suggested by the upstream signal — must be reconciled with live price |
| Live reconciliation | P_400's check of current price against guideline; flags drift > threshold |
| OCO | One-Cancels-Other — bracket order pairing limit-target with stop-loss |
| 1st trgs OCO / 1st trgs All | Schwab/TOS complex order types — entry first, then bracket children fire on fill |
| Trigger basis | Whether option exits fire off the underlying stock price or the contract price |
| T1 | First profit target (partial or full exit) |
| Lifecycle status | Current state of the trade — PENDING, SUBMITTED, FILLED, T1_HIT, TRAILING, CLOSED |
| `handle_write()` | P_800's vault write interface — P_400 calls this to update Obsidian records |
| Vehicle | The instrument used to express the BUY thesis (shares, call, vertical, etc.) |

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Flow

```
[Upstream BUY signal: P_115 or P_300 .md file in Obsidian vault]
                         |
                         v
[P_400 Trigger: Tony invokes p-400-tos-trade-setup skill, references the .md]
                         |
                         v
[Step 1: Signal Ingestion — read upstream file, extract symbol/guideline-entry/stop/target]
                         |
                         v
[Step 2: Live Data Acquisition — Schwab API (primary) or web (fallback)]
   - current price, bid/ask, ATR(14), volume, IV (if option in scope)
                         |
                         v
[Step 3: Entry Reconciliation — guideline vs live; flag drift > threshold]
                         |
                         v
[Step 4: Tony Inputs — 4 questions: instrument, sizing inputs, trigger basis, post-T1 rule]
                         |
                         v
[Step 5: Vehicle Selection (Phase 2+: auto; Phase 1: stock-only or user-specified option)]
                         |
                         v
[Step 6: Position Sizing — account_balance × risk_pct ÷ (entry − stop) → shares/contracts]
                         |
                         v
[Step 7: Council Review — 5 roles vote]
   - Quant / Macro / Tape: BLOCK or PASS  (any block → halt)
   - Risk / Behavioral: ANNOTATE
                         |
                  +------+------+
                  |             |
              BLOCKED        APPROVED
                  |             |
                  v             v
[Write BLOCKED      [Step 8: Order Specification Output]
 record to Obsidian]   - Stock: single-leg, OCO bracket, or 1st-triggers complex
                       - Option: contract spec + bracket
                       Exactly as it must be typed into Schwab
                         |
                         v
[Step 9: Tony manually enters order into Schwab → captures order_id + timestamps]
                         |
                         v
[Step 10: Lifecycle Update — write to Obsidian via P_800 handle_write()]
                         |
                         v
[Step 11: Ongoing Management — every meaningful event updates the record]
   - Fill, partial fill, T1 hit, stop move, trail update, close
                         |
                         v
[Step 12: Position Close → hand off final P&L to P_020]
```

**Description:** A BUY signal arrives as a markdown file from an upstream project. Tony triggers P_400. P_400 fetches live data, reconciles the guideline entry with reality, asks Tony four standardized questions, sizes the position, runs the Council, and emits an order specification precise enough to type into Schwab letter-for-letter. After Tony submits the order, P_400 updates the same Obsidian record on every lifecycle event until the trade closes and is handed to P_020 for performance recording.

### 2.2 Core Components

#### Component 1: Signal Ingestion
- **Responsibility:** Read upstream .md file (P_115 or P_300), parse YAML frontmatter, extract symbol, guideline entry, guideline stop, guideline target, signal source, signal horizon
- **Inputs:** P_115 BUY file or P_300 BUY file from Obsidian vault (`TradeManagement/P115/` or `TradeManagement/P300/`)
- **Outputs:** Structured signal payload (symbol, source, signal_date, guideline_entry, guideline_stop, guideline_target, horizon, confidence stats)
- **Tools Used:** Perplexity skill, file read
- **Dependencies:** HUB_Obsidian_Interface_Architecture schema conformance from upstream

#### Component 2: Live Data Layer
- **Responsibility:** Pull current price, bid/ask, ATR(14), 20-day volume, option chain (if instrument=option), macro event calendar window (48hr)
- **Inputs:** Symbol from Component 1
- **Outputs:** Live market snapshot
- **Tools Used:** Schwab API (primary), Perplexity web search (fallback)
- **Dependencies:** Schwab API credentials (to be wired in Phase 1.5); fallback works without

#### Component 3: Reconciliation Engine
- **Responsibility:** Compare guideline entry against live price; compute `entry_drift_pct`; flag if drift > configurable threshold; recommend revised entry if appropriate
- **Inputs:** Guideline entry (Component 1), live price (Component 2)
- **Outputs:** Reconciled entry value, drift flag, reconciliation note
- **Tools Used:** Skill logic
- **Dependencies:** None

#### Component 4: Tony Input Capture
- **Responsibility:** Ask the four standardized questions in one batch; persist answers to the record
- **Inputs:** Reconciled signal payload
- **Outputs:** Instrument type + contract details (if option), account balance + risk%, stop and target (confirmed or overridden), trigger basis, post-T1 rule
- **Tools Used:** `ask_user_question` tool
- **Dependencies:** None

#### Component 5: Vehicle Selection
- **Responsibility:** Phase 1 — pass through Tony's instrument choice. Phase 2+ — evaluate stock vs option vs vertical for highest expected R:R given current IV, delta, time-to-target, and capital efficiency.
- **Inputs:** Signal payload, live data, Tony inputs
- **Outputs:** Final instrument + contract specification
- **Tools Used:** Skill logic; Phase 2 will add option-chain scoring
- **Dependencies:** Option chain from Component 2

#### Component 6: Position Sizer
- **Responsibility:** Compute share/contract count using `risk_pct × account_balance ÷ (entry − stop)`; for options, convert dollar risk to contracts using contract delta and stop distance
- **Inputs:** Account balance, risk%, entry, stop, instrument type
- **Outputs:** Quantity, dollar risk, R:R ratio
- **Tools Used:** Skill logic
- **Dependencies:** Tony inputs (Component 4)

#### Component 7: Council Review
- **Responsibility:** Apply the five-role decision framework. Quant/Macro/Tape have block authority; Risk/Behavioral annotate. Return overall verdict and per-role notes.
- **Inputs:** Full payload assembled by Components 1–6
- **Outputs:** Council verdict (APPROVED / APPROVED_WITH_CAUTION / BLOCKED / OVERRIDE_REQUIRED), per-role verdict + notes, blocking_role (if any)
- **Tools Used:** Skill logic (deterministic rules), web search for macro context
- **Dependencies:** Macro calendar from Component 2

#### Component 8: Order Specification Builder
- **Responsibility:** Produce the exact text/spec Tony will type into Schwab. For each supported order pattern (see Section 9.3), output every field a human must fill: Spread, Side, Qty, Pos Effect, Symbol, Exp, Strike, Type, Link, Price, Order, TIF, Instruction, Exchange, Advanced Order.
- **Inputs:** Approved payload from Council
- **Outputs:** Order specification block (one block per leg, matching Schwab's order ticket layout)
- **Tools Used:** Skill template engine
- **Dependencies:** Vehicle selection (Component 5)

#### Component 9: Obsidian Writer
- **Responsibility:** Call P_800's `handle_write(schema_name="TradeManagement", data={...}, body=..., overwrite=True)` to persist or update the P_400 record. Always update frontmatter fields AND append a dated log entry to the body.
- **Inputs:** Full assembled payload + any lifecycle event
- **Outputs:** Updated .md file in `TradeManagement/P400/`
- **Tools Used:** P_800 write interface
- **Dependencies:** P_800 schema (Section 9.3 below)

#### Component 10: Lifecycle Manager
- **Responsibility:** Track the trade through PENDING → SUBMITTED → FILLED → T1_HIT → TRAILING → CLOSED. Each transition triggers a Component 9 update.
- **Inputs:** Tony updates (order_id, fill price, fill time), or future Schwab API polling
- **Outputs:** Updated lifecycle_status + appended log entry per event
- **Tools Used:** Skill logic, Schwab API (Phase 2)
- **Dependencies:** Component 9

### 2.3 System Decomposition

```
P_400_Trade_Management_System/
├── docs/
│   ├── P_400_Architecture_v0.1.md       (this document)
│   ├── P_400_Council_Rules_v0.1.md      (detailed Council decision rules — to be created)
│   └── P_400_Order_Patterns_v0.1.md     (Schwab order pattern library — to be created)
├── skills/
│   └── p-400-tos-trade-setup/           (Perplexity skill — Phase 0 exists, will extend)
├── prompts/
│   ├── P_400_Master_Prompt_v0.1.md      (orchestrating session prompt)
│   ├── P_400_Lifecycle_Update_Prompt.md (per-event update prompt)
│   └── P_400_Council_Review_Prompt.md   (Council-only deep review)
├── inputs/
│   └── (symlinks or copies of upstream P_115 / P_300 files for this session)
├── outputs/
│   └── (order specification text snapshots per trade, for audit)
└── logs/
    └── (operational log of every P_400 invocation)
```

### 2.4 Design Rationale

**Why This Architecture?**
- **Single-skill orchestration:** One Perplexity skill (`p-400-tos-trade-setup`) drives the full flow. Avoids fragmenting logic across multiple ad-hoc prompts.
- **Schema conformance over schema ownership:** P_400 does not own the Obsidian schema — P_800 does. P_400 proposes field additions to P_800 and writes through the official interface. This prevents drift and keeps all vault writers consistent.
- **Manual execution first:** Phase 1 outputs a textual order spec for Tony to type. This eliminates API risk during prototyping and forces the spec to be unambiguous — if Tony has to interpret anything, the spec failed.
- **Council with teeth on the right roles:** Quant / Macro / Tape can block because their concerns (regime, liquidity, price action) are objective and quantifiable. Risk / Behavioral annotate because their concerns are softer or already enforced upstream (sizing rules, cooldowns).
- **Stocks before options before complex:** Build the simplest pattern (stock OCO) first, validate end-to-end with 5–10 real trades, then layer in single-contract options, then verticals/complex. No premature complexity.
- **Bullish before bearish:** Same reason — stabilize one direction before doubling the rule surface.

**Alternatives Considered:**

| Option | Pros | Cons | Decision |
|---|---|---|---|
| Build P_400 as a Python orchestrator | Fully automated, programmatic Schwab integration | Cannot prototype quickly; debugging Council logic in code is slow | Rejected for Phase 1; revisit Phase 3 |
| Let each upstream project (P_115, P_300) emit its own broker order | No central engine needed | Council logic duplicated; lifecycle tracking fragmented; vehicle selection impossible across signal sources | Rejected — defeats the purpose |
| Skip the Council, trust upstream signals | Faster | Loses the regime/macro/tape safety net that prevents bad trades in hostile conditions | Rejected — Council is the value-add |
| Auto-submit orders via Schwab API in Phase 1 | Removes manual step | Adds API failure modes during prototype; harder to audit | Rejected — manual entry in Phase 1 |

---

## 3. AI TOOLS & PLATFORMS

### 3.1 Tool Stack

| Tool / Platform | Role in System | Version / Tier | Notes |
|---|---|---|---|
| Perplexity Computer | Primary AI engine — runs the skill, executes Council, writes specs | Current | Core reasoning + tool-calling layer |
| `p-400-tos-trade-setup` skill | Orchestration logic | v0.1 (existing) → v1.0 (Phase 1) | Stored in user skill library |
| Schwab (broker) | Order execution | Production | Manual entry in Phase 1; API in Phase 2 |
| ThinkOrSwim | Charting and order-ticket reference | Latest | UI layout drives our spec format |
| Obsidian | Trade record store | Latest | Via P_800 `handle_write()` |
| P_800 write interface | Vault persistence | v1.0 | `handle_write(schema_name, data, body, overwrite)` |
| Schwab API | Live data (Phase 1.5+) and auto-submit (Phase 2+) | TBD | Not wired yet |
| Web search (Perplexity) | Fallback live data + macro context | Built-in | Always available |

### 3.2 Perplexity Project Configuration

| Setting | Value |
|---|---|
| Space Name | P_400_Trade Management System |
| Knowledge Files | P_300 Perplexity Council Image Form.docx, P_300 Perplexity Council Review Order Prompt.md, this document (once finalized) |
| Memory Enabled | Yes |
| Session Init Required | No — skill self-initializes when invoked |
| Primary Model | Default (claude_sonnet_4_6) |
| Skills Loaded | `p-400-tos-trade-setup` (user), `dynamic-thinking` (space), plus existing user skills |

### 3.3 Prompt Library (Master List)

#### Prompt: P_400 Session Trigger
```
Run P_400 on this BUY file: [paste P_115 or P_300 .md content or filename].
Use the p-400-tos-trade-setup skill. Produce the Council review and the
Schwab order specification for manual entry. Update the Obsidian record
via P_800 when complete.
```
**Purpose:** Open a P_400 session against an upstream BUY signal
**When to Use:** Any time a new BUY .md lands in the vault
**Last Updated:** 2026-05-26

#### Prompt: P_400 Lifecycle Update
```
Update the P_400 record for [symbol / date]. Event: [FILLED / T1_HIT /
STOP_MOVED / TRAIL_UPDATED / CLOSED]. Details: [fill price, qty, time,
new stop level, reason, etc.]. Append a dated log entry and update the
relevant frontmatter fields.
```
**Purpose:** Maintain the trade record through its lifecycle
**When to Use:** After every fill, target hit, stop move, or close
**Last Updated:** 2026-05-26

#### Prompt: P_400 Council Deep Review
```
Run a standalone Council review on [symbol]. Pull live data. Score each
role (Quant, Macro, Tape, Risk, Behavioral) with reasoning. Return the
verdict and any blocking role. Do not produce an order — review only.
```
**Purpose:** Council-only check for marginal setups or post-mortem analysis
**When to Use:** When Tony wants the Council vote without committing to an order
**Last Updated:** 2026-05-26

### 3.4 AI Behavior Rules & Constraints

**P_400 MUST:**
- Always read the upstream .md file before doing anything else
- Always attempt live data fetch (Schwab first, web fallback) before reconciliation
- Always ask the four standardized questions in a single batch — never one at a time
- Always run the Council before producing an order specification
- Always block the order if Quant, Macro, or Tape flag a blocking concern
- Always write the Obsidian record on every lifecycle event (creation, fill, T1, close)
- Always include both frontmatter updates AND an appended dated log entry on every write
- Always output the order specification using the exact Schwab field layout (see Section 9.3)

**P_400 MUST NOT:**
- Never fabricate live prices, ATR values, or option data — if a source is unavailable, say so and ask
- Never produce an order when the Council issues BLOCKED — write the blocked record and stop
- Never modify the schema directly — propose changes to P_800
- Never guess at instrument type, account balance, or trigger basis — always ask
- Never proceed with a stale guideline entry without flagging the drift to Tony
- Never auto-submit orders to Schwab in Phase 1 — output text spec only
- Never skip the dated log entry when updating a record

**Session Initialization:**
- No init prompt required — the skill embeds all behavior rules. Tony just invokes it.

---

## 4. REQUIREMENTS

### 4.1 Functional Requirements

#### FR-1: Ingest upstream BUY signals
- **Description:** Read a P_115 or P_300 .md file from the Obsidian vault and parse its YAML frontmatter into a structured payload
- **Acceptance Criteria:**
  - [ ] Reads `source`, `symbol` (or `ticker`), `date`, `signal` / `breakout_verdict`, `entry_price` (when present), any stop/target fields
  - [ ] Distinguishes P_115 vs P_300 by `source` field
  - [ ] Tolerates null fields gracefully — fills them later
- **Component:** Component 1 (Signal Ingestion)
- **Priority:** High

#### FR-2: Fetch live market data
- **Description:** Pull current price, ATR(14), bid/ask, and (for options) the relevant option chain slice
- **Acceptance Criteria:**
  - [ ] Schwab API tried first; web search used on failure
  - [ ] Returns `null` and a flagged note if both sources fail — never fabricates
  - [ ] Stores `data_source` field (`schwab_api` | `web` | `manual`) on the record
- **Component:** Component 2 (Live Data Layer)
- **Priority:** High

#### FR-3: Reconcile guideline entry with live price
- **Description:** Compute drift between upstream guideline entry and current price; flag if > threshold (default 1.5%)
- **Acceptance Criteria:**
  - [ ] `entry_drift_pct` populated on every record
  - [ ] Drift > threshold raises a warning in the Council Tape Reader role
  - [ ] Tony can accept guideline, accept live, or override with a custom entry
- **Component:** Component 3 (Reconciliation)
- **Priority:** High

#### FR-4: Capture Tony's four standardized inputs
- **Description:** Ask instrument type, sizing inputs, trigger basis, post-T1 rule — all in one batch
- **Acceptance Criteria:**
  - [ ] All four asked in a single `ask_user_question` call
  - [ ] If Tony has already answered any in this thread, skip those
  - [ ] Inputs persisted to the Obsidian record
- **Component:** Component 4 (Tony Input Capture)
- **Priority:** High

#### FR-5: Compute position size
- **Description:** Calculate shares or contracts using account balance × risk% ÷ (entry − stop)
- **Acceptance Criteria:**
  - [ ] Returns whole-share or whole-contract count (rounded down)
  - [ ] Returns `dollar_risk` and `r_to_r` ratio
  - [ ] Flags if R:R < 1.5 (annotates, does not block)
- **Component:** Component 6 (Position Sizer)
- **Priority:** High

#### FR-6: Run Council review with selective blocking
- **Description:** Score all five roles. Quant/Macro/Tape can BLOCK; Risk/Behavioral can only ANNOTATE.
- **Acceptance Criteria:**
  - [ ] Each role returns PASS / CAUTION / BLOCK + a one-line reason
  - [ ] Any BLOCK from Quant/Macro/Tape sets council_verdict = BLOCKED and halts order production
  - [ ] CAUTION from any role sets council_verdict = APPROVED_WITH_CAUTION
  - [ ] All five role verdicts and reasons stored in record
- **Component:** Component 7 (Council Review)
- **Priority:** High

#### FR-7: Produce broker-ready order specification
- **Description:** Output an order spec that matches Schwab's order ticket field layout exactly
- **Acceptance Criteria:**
  - [ ] Stock spec includes: Spread, Side, Qty, Pos Effect, Symbol, Type, Link, Price, Order, TIF, Instruction, Exchange, Advanced Order
  - [ ] Option spec adds: Exp, Strike, option Type (CALL/PUT)
  - [ ] Multi-leg specs render each leg as its own row matching the Schwab grid
  - [ ] Output is copy-paste / type-in ready with no interpretation needed
- **Component:** Component 8 (Order Spec Builder)
- **Priority:** High

#### FR-8: Write and update Obsidian records via P_800
- **Description:** Every state change calls `handle_write()` with both frontmatter updates and an appended dated log entry
- **Acceptance Criteria:**
  - [ ] Initial record created with `source=P_400`, `lifecycle_status=PENDING` (or `BLOCKED`)
  - [ ] Every subsequent event updates the same file (overwrite=True)
  - [ ] Body always grows by exactly one dated log entry per event
- **Component:** Component 9 (Obsidian Writer)
- **Priority:** High

#### FR-9: Track lifecycle through to close
- **Description:** Maintain `lifecycle_status` transitions from PENDING → SUBMITTED → FILLED → T1_HIT → TRAILING → CLOSED
- **Acceptance Criteria:**
  - [ ] Each transition is a Tony-triggered prompt in Phase 1
  - [ ] Each transition updates relevant fields (fill_price, current_stop, t1_realized_pnl, final_pnl, etc.)
  - [ ] CLOSED status triggers hand-off note to P_020
- **Component:** Component 10 (Lifecycle Manager)
- **Priority:** High

### 4.2 Non-Functional Requirements

#### NFR-1: Accuracy
- **Requirement:** Never fabricate market data, account values, or upstream signal fields
- **Target:** Zero fabricated values across all records
- **Implementation:** Hard rule in skill behavior; `data_source` field on every record

#### NFR-2: Consistency
- **Requirement:** Order specification format identical across every trade
- **Target:** Same field order, same syntax, same field labels matching the Schwab order ticket
- **Implementation:** Order Pattern Library in Section 9.3, referenced by the skill template

#### NFR-3: Auditability
- **Requirement:** Every order has a traceable upstream signal and a traceable Council verdict
- **Target:** Every P_400 record contains `p115_linked` or `p300_linked`, plus all five role verdicts
- **Implementation:** Schema fields enforced by `handle_write()` validation

#### NFR-4: Determinism
- **Requirement:** Same inputs produce same Council verdict and same position size
- **Target:** No model-driven randomness in sizing or in role-blocking logic
- **Implementation:** Position sizing and blocking rules are deterministic; only role *narrative* text is model-generated

#### NFR-5: Safety
- **Requirement:** Phase 1 never submits an order programmatically
- **Target:** All Schwab interactions in Phase 1 are read-only (data fetch)
- **Implementation:** No Schwab order-submit endpoints invoked from the skill in v1.0

### 4.3 Requirements Matrix

| ID | Description | Component | Status | Notes |
|---|---|---|---|---|
| FR-1 | Ingest upstream signals | C1 | Pending | Skill needs file-read step |
| FR-2 | Fetch live data | C2 | Pending | Schwab API path TBD; web path ready |
| FR-3 | Reconcile entry | C3 | Pending | Threshold default 1.5% |
| FR-4 | Capture 4 Tony inputs | C4 | Partial | Skill v0.1 asks 2; needs to be extended |
| FR-5 | Position sizing | C6 | Pending | Pure math, low risk |
| FR-6 | Council review | C7 | Pending | Need Council Rules doc (linked) |
| FR-7 | Order spec output | C8 | Partial | Skill v0.1 does basic; needs Schwab layout fidelity |
| FR-8 | Obsidian write via P_800 | C9 | Pending | Confirm P_800 `handle_write()` callable from skill |
| FR-9 | Lifecycle tracking | C10 | Pending | Manual triggers in Phase 1 |
| NFR-1 | No fabrication | All | Active | Enforced via skill rules |
| NFR-2 | Consistent spec format | C8 | Pending | Locked in Order Pattern Library |
| NFR-3 | Auditability | C9 | Pending | Schema fields cover it |
| NFR-4 | Determinism | C6, C7 | Pending | Verify in testing |
| NFR-5 | No auto-submit | All | Active | Hard rule |

---

## 5. CHANGE LOG

### Version History

#### v0.1 — 2026-05-26
**Release Type:** Initial Architecture (Prototype)

**Added:**
- Full architecture document covering scope, components, requirements, workflows, data design
- Council enforcement model (Quant/Macro/Tape block; Risk/Behavioral annotate)
- Four-question Tony input batch
- Order Pattern Library skeleton (stock OCO, option single, option vertical, 1st-triggers complex)
- Lifecycle state machine (PENDING → SUBMITTED → FILLED → T1_HIT → TRAILING → CLOSED)
- Integration spec with P_800 `handle_write()` and HUB_Obsidian_Interface_Architecture

**Modified:**
- Existing `p-400-tos-trade-setup` skill (v0.1) scope expanded — needs upgrade to v1.0 to match this architecture

**Breaking Changes:** No (prototype phase — no production users yet)

---

## 6. ERROR CORRECTIONS LOG

*Empty — populate as errors are discovered during prototype execution. Per template rule, any error corrected 2+ times must be documented here permanently.*

---

## 7. ENHANCEMENT LOG

### Active Enhancements

#### Enhancement: Schwab API live data integration
- **Status:** Planned
- **Priority:** High
- **Target Date:** Phase 1.5 (after 5–10 successful manual trades)
- **Description:** Replace web-search fallback with primary Schwab API calls for price, ATR, option chain
- **Expected Benefit:** Sub-second live data; richer option chain access
- **Dependencies:** Schwab API credentials; auth flow tested
- **Success Criteria:** Live price returned in < 2s on 95% of calls; option chains parse cleanly

#### Enhancement: Automated vehicle selection
- **Status:** Planned
- **Priority:** High
- **Target Date:** Phase 2
- **Description:** Given a BUY signal and live data, P_400 scores stock vs ATM call vs vertical and picks the highest expected R:R given capital efficiency
- **Expected Benefit:** Captures option leverage on directional signals without manual selection
- **Dependencies:** Option chain access (FR-2 fully working); IV/delta scoring rules
- **Success Criteria:** Vehicle pick beats fixed-stock-default on simulated backtest

#### Enhancement: Automated Schwab order submission
- **Status:** Planned
- **Priority:** Medium
- **Target Date:** Phase 3
- **Description:** P_400 submits orders directly via Schwab API after Council approval and Tony's final confirmation
- **Expected Benefit:** Removes manual typing; reduces transcription errors
- **Dependencies:** Schwab order API; robust error handling; rollback paths
- **Success Criteria:** 50 consecutive trades submitted without fat-finger errors

#### Enhancement: Bearish / SELL-side workflow
- **Status:** Planned
- **Priority:** Medium
- **Target Date:** Phase 3+
- **Description:** Mirror the BUY workflow for short stock, long put, put vertical, etc.
- **Expected Benefit:** Two-sided system
- **Dependencies:** Bullish workflow stable for 30+ trades

#### Enhancement: Kraken crypto orders
- **Status:** Planned
- **Priority:** Low
- **Target Date:** Phase 4
- **Description:** Extend order spec library to Kraken's order grammar
- **Expected Benefit:** Unified system for stock + crypto
- **Dependencies:** All equity phases stable

### Completed Enhancements

| Enhancement | Completed Date | Result |
|---|---|---|
| Initial `p-400-tos-trade-setup` skill | 2026-05-26 | v0.1 saved to skill library — basic ticket builder |

### Parked / Deferred

| Enhancement | Reason Deferred | Revisit Date |
|---|---|---|
| Real-time portfolio heat from broker API | Need account-aggregation endpoint scoped first | Phase 2 |
| ML-driven Council weighting | Need ≥ 100 trades of baseline data | Phase 3 |

---

## 8. AI WORKFLOWS & PROCESSES

### 8.1 Primary Workflow: BUY Signal → Submitted Order

**Trigger:** A new P_115 or P_300 BUY .md file lands in the vault
**Frequency:** Per signal (1–5/day typically)
**Time Required:** 5–10 minutes per signal

**Steps:**
1. Tony opens this Space in Perplexity, references the BUY .md (drag/drop or path)
2. Tony issues the P_400 Session Trigger prompt (Section 3.3)
3. P_400 reads the file, fetches live data, reconciles entry, flags any drift
4. P_400 asks the four standardized questions in one batch
5. Tony answers; P_400 computes sizing
6. P_400 runs the Council (5 roles) — outputs verdict
7. If BLOCKED → P_400 writes blocked record to Obsidian, stops
8. If APPROVED → P_400 emits the Schwab order specification (Section 9.3 format)
9. Tony reads spec, types it into Schwab order ticket exactly as written
10. Tony confirms submission, reports back order_id and submitted timestamp
11. P_400 writes the initial P_400 record to Obsidian (`source=P_400`, `lifecycle_status=SUBMITTED`)

**Expected Output:**
- One Obsidian record in `TradeManagement/P400/YYYY-MM-DD_SYMBOL_P400.md`
- Order live at Schwab

**Decision Gate:**
```
If Council = BLOCKED            --> write blocked record, no order, stop
If Council = APPROVED_W_CAUTION --> emit spec, flag caution items, Tony decides
If Council = APPROVED           --> emit spec
If Council = OVERRIDE_REQUIRED  --> halt, prompt Tony for explicit override confirmation
```

---

### 8.2 Secondary Workflow: Lifecycle Update

**Trigger:** Any meaningful event on an open P_400 position
**Frequency:** As events occur (fills, target hits, stop moves, closes)
**Time Required:** 1–2 minutes per event

**Steps:**
1. Tony issues the P_400 Lifecycle Update prompt (Section 3.3) with the event type and details
2. P_400 reads the existing record from Obsidian
3. P_400 updates the relevant frontmatter fields
4. P_400 appends a dated log entry to the body
5. P_400 writes back via `handle_write(overwrite=True)`
6. If `lifecycle_status` transitions to CLOSED → P_400 emits a hand-off summary for P_020

**Expected Output:**
- Updated Obsidian record with new lifecycle state + new body log line

---

### 8.3 Review Workflow: Daily Open-Position Sweep

**Trigger:** End of trading day
**Frequency:** Daily
**Time Required:** 5 minutes

**Steps:**
1. Tony asks P_400 to list all open positions (lifecycle_status in [SUBMITTED, FILLED, T1_HIT, TRAILING])
2. P_400 reads `TradeManagement/P400/` for non-CLOSED records
3. For each, P_400 pulls live price and current stop, computes unrealized P&L
4. P_400 flags any position where price is within 1× ATR of the stop
5. Tony reviews flagged positions and decides on adjustments

**Prompt Template:**
```
Sweep all open P_400 positions. Pull live price for each. Compute unrealized
P&L and distance to current stop in ATR multiples. Flag any position where
price < current_stop + 1×ATR. Return a single table.
```

---

### 8.4 Exception Workflows

#### Exception: Live data unavailable from both Schwab and web
- **Trigger:** Both data paths fail in Component 2
- **Action:** P_400 prompts Tony to paste current price + ATR manually; sets `data_source=manual`
- **Documentation:** Flagged in the record body log

#### Exception: Council BLOCKED but Tony wants to proceed
- **Trigger:** Tony explicitly requests override after a BLOCK
- **Action:** P_400 requires Tony to type the exact phrase "OVERRIDE BLOCK ON [SYMBOL] — I ACCEPT RESPONSIBILITY"; sets `council_verdict=OVERRIDE_REQUIRED → APPROVED_BY_OVERRIDE`; appends override reason to body log
- **Documentation:** Permanent annotation on the record

#### Exception: Upstream .md file missing required fields
- **Trigger:** Component 1 cannot extract symbol or guideline entry
- **Action:** Stop. Report missing fields to Tony. Do not proceed.
- **Documentation:** One-line note; no Obsidian record created (since record needs symbol)

#### Exception: Fill price drifts > 1% from spec
- **Trigger:** Tony reports a fill price more than 1% off the planned entry
- **Action:** P_400 recomputes R:R and dollar risk with actual fill; flags if R:R drops below 1.0; updates record
- **Documentation:** Dated log entry showing original vs actual fill

---

## 9. DATA DESIGN

### 9.1 Data Inputs

| Data Type | Source | Format | How Fed to P_400 |
|---|---|---|---|
| BUY signal | P_115 / P_300 .md file in vault | YAML frontmatter + markdown body | File reference in prompt |
| Live price / ATR / volume | Schwab API (primary), web (fallback) | JSON / web text | Skill fetch step |
| Option chain | Schwab API | JSON | Skill fetch step |
| Macro calendar (48hr) | Web search | Text | Skill fetch step |
| Tony inputs | `ask_user_question` | Structured answers | One batched question per session |
| Lifecycle events | Tony prompts | Free text per event | Per-event update prompt |

### 9.2 Data Outputs

| Output Type | Format | Destination | Frequency |
|---|---|---|---|
| Order specification | Structured text matching Schwab grid | Tony's screen (typed into Schwab) | Per approved signal |
| Council verdict block | Structured text | Tony's screen + Obsidian record body | Per signal |
| Obsidian record (initial) | YAML frontmatter + body | `TradeManagement/P400/YYYY-MM-DD_SYMBOL_P400.md` | Per signal |
| Obsidian record (update) | Overwrite same file | Same location | Per lifecycle event |
| P_020 hand-off | Summary block in body | Same record, on CLOSED transition | Once per closed trade |

### 9.3 Data Schema — P_400 Fields on TradeManagementRecord

*P_800 owns the schema. P_400 proposes these field additions. Per HUB_Obsidian_Interface_Architecture, all fields except `date` and `symbol` are optional and P_400 supplies only what it knows.*

**Schema Name:** TradeManagementRecord (P_800 owned)
**Version:** target v1.1 (current v1.0 needs these additions)

**Proposed P_400 field additions:**

| Field Name | Type | Description | Valid Values |
|---|---|---|---|
| `p115_linked` | str | Path or filename of source P_115 file | filename or null |
| `p300_linked` | str | Path or filename of source P_300 file | filename or null |
| `guideline_entry` | float | Entry price suggested by upstream signal | numeric |
| `live_price_at_review` | float | Live price at the moment P_400 ran | numeric |
| `entry_drift_pct` | float | Drift between guideline and live, percent | numeric |
| `entry_reconciled` | float | Final entry used in the order | numeric |
| `data_source` | str | Where live data came from | schwab_api / web / manual |
| `instrument_type` | str | What's being traded | stock / option |
| `option_strike` | float | Strike price (options only) | numeric or null |
| `option_expiry` | date | Expiration (options only) | YYYY-MM-DD or null |
| `option_type` | str | Call or put | call / put / null |
| `option_structure` | str | Single contract or multi-leg | single / vertical_debit / vertical_credit / null |
| `contract_delta` | float | Approximate delta at order time | -1.0 to 1.0 or null |
| `contract_iv` | float | Implied vol at order time | numeric or null |
| `account_balance` | float | Account size used for sizing | numeric |
| `risk_pct` | float | Percent of account risked | numeric |
| `dollar_risk` | float | Computed dollar risk | numeric |
| `position_size` | int | Shares or contracts | integer |
| `stop_level` | float | Initial protective stop | numeric |
| `tp_level` | float | First target (T1) | numeric |
| `risk_reward` | float | (T1 − entry) ÷ (entry − stop) | numeric |
| `atr_14` | float | 14-period ATR at review | numeric |
| `trigger_basis` | str | For options: stock-based or contract-based exits | stock / contract |
| `post_t1_rule` | str | What happens after T1 hits | breakeven / lock_50pct / atr_trail / custom |
| `quant_verdict` | str | Quant Strategist role result | PASS / CAUTION / BLOCK |
| `quant_notes` | str | One-line reason | text |
| `macro_verdict` | str | Macro Economist role result | PASS / CAUTION / BLOCK |
| `macro_notes` | str | One-line reason | text |
| `tape_verdict` | str | Momentum & Tape role result | PASS / CAUTION / BLOCK |
| `tape_notes` | str | One-line reason | text |
| `risk_verdict` | str | Risk Manager role result (annotate-only) | PASS / CAUTION |
| `risk_notes` | str | One-line reason | text |
| `behavioral_verdict` | str | Behavioral Judge role result (annotate-only) | PASS / CAUTION |
| `behavioral_notes` | str | One-line reason | text |
| `council_verdict` | str | Overall outcome | APPROVED / APPROVED_WITH_CAUTION / BLOCKED / OVERRIDE_REQUIRED / APPROVED_BY_OVERRIDE |
| `blocking_role` | str | If blocked, which role(s) | quant / macro / tape / null |
| `council_notes` | str | Overall Council summary | text |
| `broker` | str | Where order will be / was placed | schwab / kraken |
| `order_id` | str | Schwab order ID after submission | text or null |
| `lifecycle_status` | str | Current state | PENDING / SUBMITTED / FILLED / PARTIAL / T1_HIT / TRAILING / CLOSED / BLOCKED |
| `submitted_dt` | datetime | When order entered at Schwab | ISO-8601 or null |
| `filled_dt` | datetime | When order filled | ISO-8601 or null |
| `fill_price` | float | Actual fill price | numeric or null |
| `fill_qty` | int | Actual fill quantity | integer or null |
| `current_stop` | float | Live stop level (may move over time) | numeric |
| `current_target` | float | Live target level | numeric |
| `trail_method` | str | How stop is being trailed | breakeven / lock_50pct / atr_trail / custom / null |
| `t1_hit_dt` | datetime | When T1 hit | ISO-8601 or null |
| `t1_realized_pnl` | float | Realized P&L from T1 leg | numeric or null |
| `closed_dt` | datetime | When position fully closed | ISO-8601 or null |
| `closed_reason` | str | Why it closed | t1_hit / stop_hit / trail_stop / discretionary / time_stop |
| `final_pnl` | float | Total realized P&L | numeric or null |
| `p020_handoff` | bool | Has P_020 received the close? | true / false |

**Schema Rules:**
- All fields are optional; P_400 supplies only fields relevant to its phase of the lifecycle
- Field additions go through P_800 review per HUB_Obsidian_Interface_Architecture governance
- `lifecycle_status=BLOCKED` records still get written — Council vetoes are part of the audit trail

### 9.3.1 Order Pattern Library

These are the canonical Schwab order patterns P_400 emits. Each pattern's output is rendered to match the Schwab order ticket grid exactly (the column layout from `image-2.jpg` for stock and `image-3.jpg` for options).

#### Pattern A — Stock OCO Bracket (most common)

Schwab grid layout:

| Spread | Side | Qty | Pos Effect | Symbol | Exp | Strike | Type | Link | Price | Order | TIF | Instruction | Exchange |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| STOCK | BUY | +N | AUTO | SYM | — | — | ETF/STK | — | ENTRY | LMT | DAY | NONE | BEST |
| STOCK | SELL | −N | AUTO | SYM | — | — | ETF/STK | — | T1 | LMT | DAY | NONE | BEST |
| STOCK | SELL | −N | AUTO | SYM | — | — | ETF/STK | — | — MKT | STOP | DAY | NONE | BEST |
|  |  |  |  |  |  |  |  |  | STOP | STP | STD |  |  |  |

**Advanced Order:** `1st trgs OCO`
**Description:** Entry as limit order. On fill, two children fire: a limit sell at T1 and a stop at the protective level. First to fill cancels the other.

#### Pattern B — Single-Leg Option (long call or long put)

| Spread | Side | Qty | Pos Effect | Symbol | Exp | Strike | Type | Link | Price | Order | TIF | Instruction | Exchange |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SINGLE | BUY | +N | AUTO | SYM | EXP | STRIKE | CALL/PUT | MAN | DEBIT | LMT | DAY | NONE | BEST |
| SINGLE | SELL | −M | AUTO | SYM | EXP | STRIKE | CALL/PUT | MAN | T1_PREMIUM | LMT | GTC | NONE | BEST |
| SINGLE | SELL | −(N−M) | AUTO | SYM | EXP | STRIKE | CALL/PUT | MAN | STOP_REF | STOP | GTC | NONE | BEST |
| SINGLE | SELL | −X | AUTO | SYM | EXP | STRIKE | CALL/PUT | MAN/MARK | TRAIL_OFFSET | TRAILSTOP | GTC | NONE | BEST |

**Advanced Order:** `1st trgs All` (entry fires the three sell children together)
**Description:** Buy N contracts. On fill, three sell children fire:
- Limit sell of M contracts at T1 premium (partial exit)
- Stop sell of remainder at a stock-based or contract-based trigger
- Trailing stop on a portion if desired

**Link field:** `MAN` = manual (stock-based trigger entered as a stock price); `MARK` = trail off the option mark.

#### Pattern C — Vertical Debit Spread

Two legs entered together as a vertical, with a bracket on the spread price:

| Spread | Side | Qty | Pos Effect | Symbol | Exp | Strike | Type | Link | Price | Order | TIF | Instruction | Exchange |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VERTICAL | BUY | +N | AUTO | SYM | EXP | LONG_STRIKE | CALL | — | NET_DEBIT | LMT | DAY | NONE | BEST |
| VERTICAL | SELL | −N | AUTO | SYM | EXP | SHORT_STRIKE | CALL | — | (same row) | LMT | DAY | NONE | BEST |
| VERTICAL | SELL | −N | AUTO | SYM | EXP | both strikes | CALL | — | T1_NET_CREDIT | LMT | GTC | NONE | BEST |
| VERTICAL | SELL | −N | AUTO | SYM | EXP | both strikes | CALL | MAN | STOP_REF | STOP | GTC | NONE | BEST |

**Advanced Order:** `1st trgs OCO`
**Description:** Open the vertical at a net debit. Bracket children close the full vertical at a target net credit or stop out on adverse move.

#### Pattern D — Stock Entry with Triggered Option Hedge (Phase 3+)

Reserved for future. Not in v0.1 scope.

---

### 9.4 Data Integrity Rules

- **Never fabricate** market data, fill prices, or P&L values. Use `null` and flag.
- **Always capture `data_source`** on every record so audit can trace web vs API vs manual.
- **Symbol is canonical uppercase** — `AMTM` not `amtm`.
- **All datetimes ISO-8601** with timezone (`America/New_York`).
- **Per-event log entries are append-only** in the body — never delete prior log lines.
- **Schema changes flow through P_800** — never edit the schema directly from P_400.
- **Quantity rounding:** Always round down to the nearest whole share/contract. Better to undersize than oversize.

---

## 10. TESTING & VALIDATION

### 10.1 Testing Approach

**Philosophy:** P_400 prototype is validated by **trade-by-trade post-mortem against ground truth**. After each trade, Tony compares the P_400 record against actual Schwab activity and notes any drift.

#### Manual Validation (P_400 Outputs)
- **Method:** Compare emitted order spec against the order ticket Tony actually entered into Schwab. Identical text? Pass.
- **Frequency:** First 10 trades, then weekly spot-check
- **Pass Criteria:** Zero transcription disagreements between spec and actual ticket

#### Dry-Run Backtest (no capital at risk)
- **Method:** Run P_400 against the existing AMTM and CFG sample files; verify the full output (reconciliation, Council, spec) before any live trade
- **Pass Criteria:** Both samples produce complete, error-free output

#### Council Determinism Check
- **Method:** Run the same input through P_400 three times; confirm the same `council_verdict` and same `position_size` each time
- **Pass Criteria:** Identical structured outputs (narrative may vary)

### 10.2 Known-Good Reference Examples

*To be populated as the first 3–5 trades complete. Each example will capture: input .md file, Tony inputs, full P_400 output, actual Schwab ticket, actual fill, and any deltas.*

#### Example 1: [TBD — first prototype trade]
**Input:** [TBD]
**Expected Output:** [TBD]
**Notes:** [TBD]

### 10.3 Validation Checklist (Run on Every Trade)

- [ ] Upstream .md was read successfully
- [ ] Live data fetched (data_source captured)
- [ ] Entry drift computed and surfaced
- [ ] All four Tony inputs captured in one batch
- [ ] Position size math shows entry, stop, risk-per-unit, total risk, R:R
- [ ] All five Council role verdicts present
- [ ] If blocked, no order spec emitted
- [ ] Order spec matches Schwab grid layout exactly
- [ ] Obsidian record written with frontmatter + dated log entry
- [ ] `data_source` field populated

### 10.4 Known Issues & Limitations

| Issue ID | Description | Severity | Workaround | Status |
|---|---|---|---|---|
| ID-001 | Schwab API not yet wired — live data via web only | Medium | Web fallback; manual paste if needed | Open (Phase 1.5) |
| ID-002 | P_300 files do not carry current price — must always be reconciled | Low | Mandatory live fetch | Open (by design) |
| ID-003 | Vehicle selection is manual in Phase 1 — no auto stock-vs-option scoring | Low | Tony decides | Open (Phase 2) |
| ID-004 | Position sizing assumes stock-style risk math even for options | Medium | Use delta-adjusted stop distance for options | Open (Phase 1.5 fix) |

---

## 11. DAILY OPERATIONS & SESSION MANAGEMENT

### 11.1 Session Startup Checklist

```
[ ] Open the P_400_Trade Management System Space in Perplexity
[ ] Confirm today's date is correct in the AI context
[ ] Confirm account balance parameter is current (Section 11.4)
[ ] Skim any open positions list (lifecycle_status != CLOSED)
[ ] Have the upstream BUY .md file path or content ready
```

### 11.2 Daily Operating Procedure

**Pre-Market (~10 min)**
1. Pull overnight P_115 and P_300 outputs from the vault
2. Identify which symbols have new BUY signals
3. Note any open P_400 positions and their current stops/targets

**Main Session (~5–10 min per signal)**
1. For each new BUY signal: run the Primary Workflow (Section 8.1)
2. Type approved order specs into Schwab; capture order_ids
3. Update P_400 records with `lifecycle_status=SUBMITTED` and order_id

**Intraday (as events occur)**
1. On any fill, T1 hit, stop move, or close: run the Lifecycle Update Workflow (Section 8.2)

**End of Day (~5 min)**
1. Run the Daily Open-Position Sweep (Section 8.3)
2. Flag any positions for next-day attention

### 11.3 Monthly Maintenance

| Task | Frequency | Owner | Notes |
|---|---|---|---|
| Account balance parameter review | Monthly | Tony | Update if balance changed > 10% |
| Risk per trade review | Quarterly | Tony | Adjust if drawdown patterns warrant |
| Order Pattern Library audit | Quarterly | Tony | Add new patterns from production trades |
| Schema additions review with P_800 | As needed | Tony | Any new field requirements |
| Council rule tuning | Monthly | Tony | Adjust thresholds based on outcomes |

### 11.4 Parameter Registry

| Parameter | Value | Last Reviewed | Next Review |
|---|---|---|---|
| Account balance | [TBD — Tony to set] | — | Monthly |
| Risk per trade (default) | 1.0% (proposed) | 2026-05-26 | 2026-06-26 |
| Max position size (% of account) | 5.0% (proposed) | 2026-05-26 | 2026-06-26 |
| Entry drift threshold | 1.5% | 2026-05-26 | After 10 trades |
| Min acceptable R:R (warning) | 1.5 | 2026-05-26 | After 10 trades |
| Default broker | Schwab | 2026-05-26 | — |
| Default TIF (stock) | DAY | 2026-05-26 | — |
| Default TIF (option child orders) | GTC | 2026-05-26 | — |

---

## 12. TROUBLESHOOTING & SUPPORT

### 12.1 Common Issues & Solutions

#### Issue: Order spec doesn't match what I see in the Schwab ticket
- **Symptoms:** A field in P_400's output is labeled differently than Schwab's UI, or a value doesn't fit a Schwab dropdown
- **Root Cause:** Schwab UI changed, or Order Pattern Library is stale
- **Solution:**
  1. Screenshot the discrepancy
  2. Update the affected pattern in Section 9.3.1
  3. Add an Error Corrections Log entry if it recurs
- **Prevention:** Quarterly Order Pattern Library audit

#### Issue: Council blocks too aggressively
- **Symptoms:** Multiple signals blocked when conditions seem fine
- **Root Cause:** Role thresholds calibrated too tight
- **Solution:**
  1. Review the last 10 BLOCKED records and the actual subsequent price action
  2. If the blocks were saves: keep thresholds
  3. If the blocks were false positives: loosen one role's threshold; log in Enhancement Log
- **Prevention:** Monthly Council rule tuning (Section 11.3)

#### Issue: Live data unavailable
- **Symptoms:** Both Schwab API and web fail
- **Root Cause:** Network issue, API outage, search rate limit
- **Solution:**
  1. P_400 prompts Tony to paste current price and ATR manually
  2. `data_source=manual` recorded
  3. Council proceeds with manual values
- **Prevention:** Schwab API redundancy (Phase 2)

#### Issue: Tony enters the order incorrectly in Schwab
- **Symptoms:** Fill price or order details diverge from spec
- **Root Cause:** Manual transcription error
- **Solution:**
  1. P_400 records actual fill in `fill_price` / `fill_qty`
  2. Recompute R:R and dollar risk with actuals
  3. If divergence > 1%, log in Error Corrections Log
- **Prevention:** Phase 3 Schwab auto-submit removes this risk

#### Issue: Upstream .md file missing required fields
- **Symptoms:** No symbol or no guideline entry in P_115/P_300 output
- **Root Cause:** Upstream project bug
- **Solution:**
  1. P_400 stops, reports the missing field
  2. Tony fixes upstream or supplies the value manually
  3. Open a ticket against the upstream project
- **Prevention:** Upstream schema enforcement at P_115/P_300

### 12.2 Debug & Audit Trail

**Where to find outputs:**
- Perplexity session transcript (this Space)
- P_400 record in `TradeManagement/P400/`
- Actual order at Schwab (Order Status page)
- Final outcome in P_020 (after CLOSED hand-off)

**How to audit a past decision:**
1. Open the P_400 .md for that date+symbol
2. Read the body log entries top-to-bottom — every event is dated
3. Cross-check Council verdicts in frontmatter against the day's market context
4. If discrepancy, locate the original Perplexity session transcript

### 12.3 Escalation Path

| Level | Condition | Action |
|---|---|---|
| Self-resolve | Single-trade quirk | Note in record body; move on |
| Skill update | Same drift on 2+ trades | Update `p-400-tos-trade-setup` skill |
| Documentation update | Recurring error | Add to Section 6 (Error Corrections Log) |
| Architecture revision | Fundamental gap | Open an Enhancement Log entry (Section 7) and revise this doc |

---

## 13. APPENDICES

### Appendix A: Glossary of Terms

| Term | Definition |
|---|---|
| BUY signal | Validated long entry from P_115 or P_300 |
| Council | Five-role review board (Quant, Macro, Tape, Risk, Behavioral) |
| Drift | Difference between guideline entry and live price |
| Guideline entry | Upstream-suggested entry price; not binding until reconciled |
| Lifecycle status | Current state of a trade |
| 1st trgs OCO | Schwab complex order: entry triggers an OCO bracket |
| 1st trgs All | Schwab complex order: entry triggers multiple bracket children together |
| Order Pattern | A canonical Schwab order structure (stock OCO, single option, vertical, etc.) |
| Reconciliation | P_400's adjustment of upstream guideline against live market state |
| Trigger basis | Whether option exits fire on stock price or contract price |
| Vehicle | Instrument chosen to express the BUY (stock, call, vertical, etc.) |

### Appendix B: Related Project Documentation

| Document | Location | Purpose |
|---|---|---|
| HUB_Obsidian_Interface_Architecture.md | Project Knowledge | P_800-owned vault schema and write interface — P_400 conforms to this |
| P_400-Perplexity-Master-Trade-SetUp-Prompt.md | Project Knowledge | Original master prompt (Phase 0 reference) |
| P_300 Perplexity Council Review Order Prompt.md | Space Files | Council prompt from P_300 era |
| P_300 Perplexity Council Image Form.docx | Space Files | Council image-form template |
| `p-400-tos-trade-setup` SKILL.md | Perplexity skill library | Phase 0 skill — to be extended in Phase 1 |
| P_400_Council_Rules_v0.1.md | TBD | Detailed deterministic Council rules — separate file once content > 1 page |
| P_400_Order_Patterns_v0.1.md | TBD | Schwab order pattern library — separate file once it exceeds Section 9.3.1 |
| UNIVERSAL_PROJECT_TEMPLATE_v1_1.md | Hub shared resources | Template this document conforms to |
| python-project-architecture SKILL.md | `C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\skills\python-project-architecture\SKILL.md` | Reserved for Phase 3+ when Python orchestrator is built |

### Appendix C: Code Repository

| Field | Value |
|---|---|
| Repository | N/A in Phase 1 (skill-only, no Python yet) |
| Primary Language | Markdown (skill instructions) |
| Branch Structure | N/A |
| Key Files | `p-400-tos-trade-setup/SKILL.md` |

Reserved for Phase 3+ when a Python orchestrator is built — at that point this section gets populated and python-project-architecture skill applies.

### Appendix D: Architecture Diagram (Detailed)

```
+----------------------------------+
| UPSTREAM SIGNAL LAYER            |
|  P_115 (breakout)                |
|  P_300 (analog pattern)          |
|  → emits .md to Obsidian vault   |
+--------------+-------------------+
               |
               v
+----------------------------------+
| P_400 INGESTION (C1)             |
|  read .md frontmatter            |
|  extract symbol, guideline       |
+--------------+-------------------+
               |
               v
+----------------------------------+
| LIVE DATA LAYER (C2)             |
|  Schwab API → fallback: web      |
|  price, ATR, IV, option chain    |
+--------------+-------------------+
               |
               v
+----------------------------------+
| RECONCILIATION (C3)              |
|  guideline vs live → drift flag  |
+--------------+-------------------+
               |
               v
+----------------------------------+
| TONY INPUT CAPTURE (C4)          |
|  one batched ask:                |
|   instrument, sizing, trigger,   |
|   post-T1 rule                   |
+--------------+-------------------+
               |
               v
+----------------------------------+
| VEHICLE SELECTION (C5)           |
|  Phase 1: pass-through           |
|  Phase 2+: stock vs option score |
+--------------+-------------------+
               |
               v
+----------------------------------+
| POSITION SIZER (C6)              |
|  bal × risk% ÷ (entry − stop)    |
+--------------+-------------------+
               |
               v
+----------------------------------+
| COUNCIL (C7)                     |
|  Quant  → block authority        |
|  Macro  → block authority        |
|  Tape   → block authority        |
|  Risk   → annotate               |
|  Behav  → annotate               |
+--------+----------+--------------+
         |          |
    BLOCKED     APPROVED
         |          |
         v          v
+--------+    +-----------------------+
| Write  |    | ORDER SPEC BUILDER(C8)|
| blocked|    | Schwab grid layout    |
| record |    | Stock / Option / Cmplx|
| & stop |    +----------+------------+
+--------+               |
                         v
               +----------------------+
               | Tony types in Schwab |
               | captures order_id    |
               +----------+-----------+
                          |
                          v
               +----------------------+
               | OBSIDIAN WRITER (C9) |
               | via P_800            |
               | handle_write()       |
               +----------+-----------+
                          |
                          v
               +----------------------+
               | LIFECYCLE MGR (C10)  |
               | SUBMITTED → FILLED   |
               | → T1_HIT → TRAILING  |
               | → CLOSED             |
               +----------+-----------+
                          |
                          v
               +----------------------+
               | Hand-off to P_020    |
               | (final P&L recorded) |
               +----------------------+
```

### Appendix E: Performance Benchmarks (to be populated)

| Metric | Baseline | Target | Current | Last Updated |
|---|---|---|---|---|
| Spec accuracy (order matches Schwab ticket) | n/a | 100% | TBD | — |
| Council deterministic repeat rate | n/a | 100% | TBD | — |
| Time from BUY .md to submitted Schwab order | n/a | < 5 min | TBD | — |
| Win rate of APPROVED trades | n/a | TBD after 30 trades | TBD | — |
| Win rate of APPROVED_WITH_CAUTION trades | n/a | TBD | TBD | — |
| Live-data fetch success rate | n/a | ≥ 95% | TBD | — |

### Appendix F: Configuration Reference

```
# P_400 Configuration — Phase 1 Prototype
# Last Updated: 2026-05-26

# Core Parameters
account_balance               = [TBD — Tony to set]
risk_per_trade_pct            = 1.0
max_position_pct              = 5.0
entry_drift_threshold_pct     = 1.5
min_acceptable_rr             = 1.5

# Council Behavior
quant_can_block               = true
macro_can_block               = true
tape_can_block                = true
risk_can_block                = false
behavioral_can_block          = false

# Data Sources
primary_data_source           = "web"        # phase 1.5 will flip to "schwab_api"
fallback_data_source          = "manual"

# Broker
default_broker                = "schwab"
default_stock_tif             = "DAY"
default_option_child_tif      = "GTC"
auto_submit_orders            = false        # hard-locked false in Phase 1

# Lifecycle
require_dated_log_entry       = true
overwrite_records             = true
```

### Appendix G: Document Version Control

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 0.1 | 2026-05-26 | Anthony Zoppi | Initial architecture document — prototype phase |

**Review Schedule:** After every 5 completed trades during prototype, then monthly
**Last Review:** 2026-05-26
**Next Review:** After 5 prototype trades

---

**Document Classification:** Internal
**Document Owner:** Anthony Zoppi
**Template Version:** UNIVERSAL_PROJECT_TEMPLATE_v1_1
**Template Applies To:** P_400 Trade Management System

---

*END OF DOCUMENT*
