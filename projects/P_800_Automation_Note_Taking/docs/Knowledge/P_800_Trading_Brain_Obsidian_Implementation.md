# 🧠 Trading Brain – Integrated Obsidian Implementation
**Author:** Anthony | P_115 Framework
**Version:** v1.0 | May 2026
**Classification:** Confidential – Internal Use Only

> *"This system bridges the gap between price action theory and institutional execution — equipping the Trading Brain with a repeatable, structured Obsidian workflow for reading liquidity, anticipating absorption events, and timing momentum entries with precision."*

---

## 📌 HOW TO USE THIS FILE

This is your master implementation document. It contains three integrated layers:

| Layer | What It Is | Where It Lives |
|---|---|---|
| **Vault Architecture** | Folder structure, file naming, tag system | Section 1 |
| **Templates** | Pre-market, Trade Setup, Journal, Weekly Review | Section 2 |
| **P_115 Knowledge Base** | Full trading system embedded as Obsidian notes | Section 3–10 |

**Implementation order:** Build the vault structure first → install templates → paste knowledge base notes → activate Dataview → begin daily workflow.

---

# SECTION 1 — VAULT ARCHITECTURE

## 1.1 Folder Structure

Copy this exact structure into your Obsidian vault root:

```
📁 Trading Brain/
│
├── 📁 00 – Dashboard/
│   ├── 🏠 Home.md
│   ├── 📊 Daily Dashboard.md
│   └── 📈 Weekly Review Hub.md
│
├── 📁 01 – Pre-Market/
│   ├── 📅 [YYYY-MM-DD] Pre-Market Prep.md   ← daily file
│   └── 📁 Archive/
│
├── 📁 02 – Trade Setups/
│   ├── 📋 [YYYY-MM-DD] [TICKER] Setup.md    ← one per setup
│   └── 📁 Archive/
│
├── 📁 03 – Trade Journal/
│   ├── 📓 [YYYY-MM-DD] [TICKER] Trade.md    ← one per trade
│   └── 📁 Archive/
│
├── 📁 04 – Weekly Reviews/
│   └── 📅 Week of [YYYY-MM-DD].md
│
├── 📁 05 – P_115 Knowledge Base/
│   ├── 📖 P_115 Master Index.md
│   ├── 📖 01 Liquidity Theory.md
│   ├── 📖 02 Absorption Mechanics.md
│   ├── 📖 03 Stop Hunt Mechanics.md
│   ├── 📖 04 Momentum Phases.md
│   ├── 📖 05 Cycle Integration.md
│   ├── 📖 06 Execution Framework.md
│   ├── 📖 07 Diagram Reference.md
│   └── 📖 08 Quick Reference Card.md
│
├── 📁 06 – Concepts & Definitions/
│   ├── 🔑 BSL – Buy-Side Liquidity.md
│   ├── 🔑 SSL – Sell-Side Liquidity.md
│   ├── 🔑 Stop Hunt.md
│   ├── 🔑 Absorption.md
│   ├── 🔑 Compression Phase.md
│   ├── 🔑 Expansion Phase.md
│   ├── 🔑 Kill Zones.md
│   ├── 🔑 Confluence Stack.md
│   ├── 🔑 Liquidity Void.md
│   └── 🔑 Wyckoff Model.md
│
├── 📁 07 – Playbooks/
│   ├── 🎯 Bullish Stop Hunt Playbook.md
│   ├── 🎯 Bearish Stop Hunt Playbook.md
│   └── 🎯 Confluence Stack Playbook.md
│
├── 📁 08 – Metrics & Stats/
│   ├── 📊 Win Rate Tracker.md
│   ├── 📊 R-Multiple Log.md
│   └── 📊 Phase Accuracy Log.md
│
└── 📁 09 – Resources/
    ├── 🗓️ Session Kill Zone Reference.md
    ├── 📐 ATR Stop Calculator.md
    └── 📚 Glossary.md
```

---

## 1.2 Tag Taxonomy

Apply these tags consistently across every note for Dataview queries to work:

### Trade Status Tags
```
#trade/open
#trade/closed
#trade/invalidated
#trade/missed
```

### Setup Type Tags
```
#setup/bullish-stop-hunt
#setup/bearish-stop-hunt
#setup/confluence-stack
#setup/breakout-entry
#setup/aggressive-entry
#setup/conservative-entry
```

### Phase Tags
```
#phase/compression
#phase/liquidity-hunt
#phase/expansion
#phase/distribution
```

### Outcome Tags
```
#outcome/win
#outcome/loss
#outcome/breakeven
#outcome/target1
#outcome/target2
#outcome/target3
```

### Liquidity Tags
```
#liquidity/bsl
#liquidity/ssl
#liquidity/equal-highs
#liquidity/equal-lows
#liquidity/void
```

### Session Tags
```
#session/london
#session/ny-open
#session/ny-lunch
#session/ny-afternoon
#session/asian
```

### Review Tags
```
#review/daily
#review/weekly
#review/monthly
#needs-review
```

---

## 1.3 Naming Conventions

| File Type | Format | Example |
|---|---|---|
| Pre-market | `[YYYY-MM-DD] Pre-Market Prep` | `2026-05-30 Pre-Market Prep` |
| Setup | `[YYYY-MM-DD] [TICKER] Setup` | `2026-05-30 ES Setup` |
| Trade journal | `[YYYY-MM-DD] [TICKER] Trade` | `2026-05-30 NQ Trade` |
| Weekly review | `Week of [YYYY-MM-DD]` | `Week of 2026-05-25` |
| Concept note | `[Concept Name]` (Title Case) | `Stop Hunt` |

---

## 1.4 Wiki-Link Map (Core Connections)

Every trade note should link to these knowledge base nodes:

```
[[P_115 Master Index]]
[[BSL – Buy-Side Liquidity]]
[[SSL – Sell-Side Liquidity]]
[[Stop Hunt]]
[[Absorption]]
[[Kill Zones]]
[[Confluence Stack]]
```

Every pre-market note links forward to any setups and trades opened that day:
```
→ [[2026-05-30 ES Setup]]
→ [[2026-05-30 NQ Trade]]
```

---

# SECTION 2 — TEMPLATES

> **Installation:** In Obsidian → Settings → Templates → set template folder to `09 – Resources/Templates/`. Then use Cmd/Ctrl+T to insert any template into a new note.

---

## 2.1 Template: Pre-Market Prep

```markdown
---
date: {{date:YYYY-MM-DD}}
type: pre-market
tags: [review/daily]
---

# 🌅 Pre-Market Prep — {{date:dddd, MMMM D, YYYY}}

## HTF Bias (Higher Timeframe)
| Timeframe | Bias | Key Level | Notes |
|---|---|---|---|
| Monthly | | | |
| Weekly | | | |
| Daily | | | |

**Overall HTF Directional Bias:** `BULLISH / BEARISH / NEUTRAL`

---

## Liquidity Map for Today
### Buy-Side Liquidity (BSL) — Above Price
- [ ] Level 1: _____ (description: _______)
- [ ] Level 2: _____ (description: _______)
- [ ] Level 3: _____ (description: _______)

### Sell-Side Liquidity (SSL) — Below Price
- [ ] Level 1: _____ (description: _______)
- [ ] Level 2: _____ (description: _______)
- [ ] Level 3: _____ (description: _______)

### Equal Highs / Equal Lows (Highest-Priority Targets)
- [ ] Equal Highs at: _____
- [ ] Equal Lows at: _____

### Prior Session Levels
| Level | Price | Type |
|---|---|---|
| Yesterday's High | | BSL |
| Yesterday's Low | | SSL |
| Prior Week High | | BSL |
| Prior Week Low | | SSL |

---

## Phase Assessment (Current Market State)
**Current Phase:** `Phase 1 – Compression / Phase 2 – Liquidity Hunt / Phase 3 – Expansion / Phase 4 – Distribution`

**ATR Reading:** _____  **ATR Status:** `Contracting / Expanding / Elevated`
**Volume Context:** `Dry / Average / Elevated`

---

## Kill Zone Watch List
| Kill Zone | Time (ET) | Watch Level | Expected Event |
|---|---|---|---|
| London Open | 2:00–5:00 AM | | |
| NY Open | 8:30–11:00 AM | | |
| NY Lunch | 11:30 AM–1:30 PM | Avoid | |
| NY Afternoon | 1:30–4:00 PM | | |

---

## Session Bias & Game Plan
**Today I am watching for:**
- Primary Scenario: ___________
- Alternate Scenario: ___________
- Invalidation: ___________

**Key Economic Events Today:**
- 

**No-Trade Conditions Today (if any):**
- 

---

## Setups to Watch
- [ ] [[{{date:YYYY-MM-DD}} Setup 1]]
- [ ] [[{{date:YYYY-MM-DD}} Setup 2]]

---

## End of Day Reflection
*(Complete after market close)*

**What happened vs. plan:**

**Setups identified correctly:**

**Mistakes / misreads:**

**Link to trades taken:**
- [[{{date:YYYY-MM-DD}} Trade]]
```

---

## 2.2 Template: Trade Setup

```markdown
---
date: {{date:YYYY-MM-DD}}
ticker: 
type: setup
tags: [setup/, phase/, liquidity/, session/]
---

# 🎯 Trade Setup — {{date:YYYY-MM-DD}} | [TICKER]

**Linked Pre-Market:** [[{{date:YYYY-MM-DD}} Pre-Market Prep]]
**Setup Type:** `Bullish Stop Hunt / Bearish Stop Hunt / Confluence Stack / Breakout`
**Direction:** `LONG / SHORT`

---

## Pre-Trade Checklist
| Step | Question | Result |
|---|---|---|
| 1 | HTF directional bias confirmed? | `PASS / FAIL` |
| 2 | Liquidity pool clearly identified? | `PASS / FAIL` |
| 3 | Stop hunt triggered and completed? | `PASS / FAIL` |
| 4 | Phase 3 breakout candle confirmed? | `PASS / FAIL` |
| 5 | Entry level precisely defined? | `PASS / FAIL` |
| 6 | Stop loss placed correctly? | `PASS / FAIL` |
| 7 | Target marked and R:R ≥ 1:2? | `PASS / FAIL` |
| 8 | In a kill zone or primary session? | `YES / NO` |

> [!warning] NO-TRADE RULE
> Any FAIL on items 1–7 = **automatic no-trade**. Do not proceed.

---

## Liquidity Context
**SSL Zone (below price):** _____
**BSL Zone (above price):** _____
**Equal Highs at:** _____
**Equal Lows at:** _____
**Phase 1 Compression Range:** _____ to _____

---

## Setup Details
**Phase Identified:** `Phase 1 / 2 / 3 / 4`
**Stop Hunt Confirmed?** `YES / NO`
**Reversal Candle Timeframe:** `15m / 5m / 1H`
**Volume on Sweep:** `Above Average / Average / Below Average`

---

## Trade Parameters
| Parameter | Value |
|---|---|
| Entry Price | |
| Entry Type | `Aggressive / Conservative / Breakout` |
| Stop Loss | |
| Stop Distance (pts) | |
| ATR at Entry | |
| Target 1 (BSL/SSL) | |
| Target 2 | |
| Target 3 (optional) | |
| Risk-Reward (T1) | |
| Risk-Reward (T2) | |
| Position Size | |
| Max $ Risk | |

---

## Chart Annotations (describe what you see)
**HTF Structure:**

**Compression Zone Description:**

**Stop Hunt Description:**

**Reversal Candle Description:**

---

## Setup Status
- [ ] Setup Identified
- [ ] Pre-trade checklist passed
- [ ] Order placed
- [ ] → Trade: [[{{date:YYYY-MM-DD}} [TICKER] Trade]]
```

---

## 2.3 Template: Trade Journal

```markdown
---
date: {{date:YYYY-MM-DD}}
ticker: 
type: trade
direction: 
outcome: 
r_multiple: 
tags: [trade/closed, outcome/, setup/, phase/]
---

# 📓 Trade Journal — {{date:YYYY-MM-DD}} | [TICKER]

**Setup Note:** [[{{date:YYYY-MM-DD}} [TICKER] Setup]]
**Pre-Market:** [[{{date:YYYY-MM-DD}} Pre-Market Prep]]

---

## Trade Summary
| Field | Value |
|---|---|
| Ticker | |
| Direction | `LONG / SHORT` |
| Entry Time | |
| Entry Price | |
| Exit Time | |
| Exit Price | |
| Stop Loss | |
| Target 1 | |
| Target 2 | |
| Outcome | `WIN / LOSS / BREAKEVEN` |
| R-Multiple | |
| $ P&L | |
| Session | `London / NY Open / NY Afternoon / Other` |

---

## Execution Review

### Entry Execution
**Entry type used:** `Aggressive / Conservative / Breakout`
**Did price behave as anticipated after entry?** `YES / NO`
**Entry timing quality:** `Early / On-point / Late / Missed`

### Stop Placement Review
**Stop placed at:** _____
**Was stop structural (beyond thesis invalidation)?** `YES / NO`
**Did stop get hit?** `YES / NO`
**If hit — was the thesis actually wrong?** `YES / NO`

### Target Review
| Target | Price | Hit? | Action Taken |
|---|---|---|---|
| T1 | | `YES/NO` | 50% exit + moved stop to BE |
| T2 | | `YES/NO` | Exit 30–40% + trail |
| T3 | | `YES/NO` | Exit final |

---

## Phase Identification Accuracy
**Phase I identified before entry:** `1 / 2 / 3 / 4`
**Was identification correct?** `YES / NO`
**Phase 2 stop hunt confirmed before entry?** `YES / NO`
**Did I wait for the reversal candle?** `YES / NO`
**HTF bias alignment?** `ALIGNED / AGAINST / NEUTRAL`

---

## Trade Management Review
- [ ] Moved stop to breakeven after T1
- [ ] Scaled out 50% at T1
- [ ] Exited on Phase 4 signal (if applicable)
- [ ] Did NOT add to losing position
- [ ] Did NOT chase Phase 3 late entry

---

## Mistakes Made
*(Be specific and honest)*
1. 
2. 
3. 

## What I Did Well
1. 
2. 

## Lesson / Rule Reinforced
> 

---

## Trade Score (self-assessment)
| Category | Score (1–5) | Notes |
|---|---|---|
| Setup quality | | |
| Entry execution | | |
| Stop placement | | |
| Position sizing | | |
| Trade management | | |
| Emotional control | | |
| **Total** | **/30** | |

---

## Related Notes
- [[Stop Hunt]] | [[Absorption]] | [[Kill Zones]]
- [[BSL – Buy-Side Liquidity]] | [[SSL – Sell-Side Liquidity]]
```

---

## 2.4 Template: Weekly Review

```markdown
---
week_start: {{date:YYYY-MM-DD}}
type: weekly-review
tags: [review/weekly]
---

# 📅 Weekly Review — Week of {{date:MMMM D, YYYY}}

---

## Week at a Glance
| Metric | Value |
|---|---|
| Total Trades | |
| Wins | |
| Losses | |
| Breakeven | |
| Win Rate | % |
| Average R-Multiple | |
| Best Trade (R) | |
| Worst Trade (R) | |
| Total $ P&L | |
| Days Traded | |
| No-Trade Days | |

---

## Daily Trade Links
| Day | Pre-Market | Setups | Trades | Outcome |
|---|---|---|---|---|
| Monday | [[...]] | | | |
| Tuesday | [[...]] | | | |
| Wednesday | [[...]] | | | |
| Thursday | [[...]] | | | |
| Friday | [[...]] | | | |

---

## Phase Identification Accuracy This Week
| Phase | Identified Correctly | Missed | False Positive |
|---|---|---|---|
| Phase 1 – Compression | | | |
| Phase 2 – Liquidity Hunt | | | |
| Phase 3 – Expansion | | | |
| Phase 4 – Distribution | | | |

**Phase Accuracy Rate:** _____%

---

## Liquidity & Stop Hunt Accuracy
**Stop hunts correctly identified this week:** ___
**Stop hunts missed:** ___
**False stop hunts (thought it was a hunt, was a true breakout):** ___

---

## Common Mistakes This Week
1. 
2. 
3. 

## Strengths Demonstrated This Week
1. 
2. 

---

## HTF Bias Assessment for Next Week
| Timeframe | Bias | Key Level | Key Liquidity |
|---|---|---|---|
| Weekly | | | |
| Daily | | | |

**Anticipated Liquidity Targets for Next Week:**
- BSL: _____
- SSL: _____

---

## Rule Violations (complete honesty required)
| Rule Violated | Trade | Context | Correction |
|---|---|---|---|
| | | | |

---

## Focus for Next Week
**1 thing to improve:**
**1 rule to enforce strictly:**
**1 concept to re-study:**

**Concept to Review:** [[]]
```

---

## 2.5 Dataview Queries

Paste these into your Dashboard notes to get live Dataview tables:

### Open Trades
````markdown
```dataview
TABLE ticker, direction, date, r_multiple, outcome
FROM "03 – Trade Journal"
WHERE type = "trade" AND contains(tags, "trade/open")
SORT date DESC
```
````

### All Closed Trades (This Month)
````markdown
```dataview
TABLE ticker, direction, outcome, r_multiple
FROM "03 – Trade Journal"
WHERE type = "trade" AND contains(tags, "trade/closed")
AND date >= date(today) - dur(30 days)
SORT date DESC
```
````

### Win Rate Summary
````markdown
```dataview
TABLE length(rows) as "Total Trades",
      length(filter(rows, (r) => contains(r.tags, "outcome/win"))) as "Wins",
      length(filter(rows, (r) => contains(r.tags, "outcome/loss"))) as "Losses"
FROM "03 – Trade Journal"
WHERE type = "trade"
GROUP BY true
```
````

### Phase 2 Stop Hunt Accuracy
````markdown
```dataview
TABLE date, ticker, outcome
FROM "02 – Trade Setups"
WHERE contains(tags, "setup/bullish-stop-hunt") OR contains(tags, "setup/bearish-stop-hunt")
SORT date DESC
LIMIT 20
```
````

### This Week's Pre-Market Notes
````markdown
```dataview
LIST
FROM "01 – Pre-Market"
WHERE type = "pre-market"
AND date >= date(today) - dur(7 days)
SORT date DESC
```
````

---

# SECTION 3 — P_115 KNOWLEDGE BASE: LIQUIDITY THEORY

> **File:** `05 – P_115 Knowledge Base/01 Liquidity Theory.md`
> **Links to:** [[BSL – Buy-Side Liquidity]] | [[SSL – Sell-Side Liquidity]] | [[Stop Hunt]] | [[P_115 Master Index]]

## What Is Market Liquidity?

Market liquidity is the depth of orders available at any given price level — the cumulative volume of bids and asks stacked throughout the order book. Two distinct layers exist:

| Layer | Description | Who Interacts |
|---|---|---|
| **Surface Liquidity** | Visible order book (Level 2) — displayed bid/ask volumes | Retail traders |
| **Deep Liquidity** | Hidden institutional block orders, dark pools, iceberg orders, algorithmic flow — never visible until executed | Institutions |

> [!info] Core Principle
> Price movement is not random. It is **engineered** — driven by order flow mechanics, stop placement, and the institutional need to find counterparty volume at scale.

---

## Liquidity Pools — Where the Money Lives

A **liquidity pool** is any concentration of resting orders (stop-losses, limit orders, pending orders) clustered at or near a specific price level.

| Pool Type | Location | What's Clustered There | Institutional Use |
|---|---|---|---|
| **BSL (Buy-Side Liquidity)** | ABOVE price — above swing highs, equal highs, prior H/W/M highs | Buy-stop orders + short position stop-losses | Distribution (selling) target |
| **SSL (Sell-Side Liquidity)** | BELOW price — below swing lows, equal lows, prior H/W/M lows | Sell-stop orders + long position stop-losses | Accumulation (buying) target |

---

## Why Price Hunts Liquidity Before Trending

Large institutions cannot place enormous orders at market price without moving it dramatically against themselves. They need a large pool of **counterparty orders** to fill positions efficiently.

| Scenario | What Happens | Why |
|---|---|---|
| **Before a Bullish Move** | Price drops below support, triggers retail sell-stops | Those sell orders are the counterparty for institutional long accumulation |
| **Before a Bearish Move** | Price pushes above resistance, triggers retail buy-stops | Those buy orders are the counterparty for institutional short distribution |

> [!tip] Key Insight
> **Every major trend begins with a liquidity sweep.** The sweep is not the trade — the reversal is the trade.

---

## Retail vs. Institutional Perspective

| Market Event | Retail Reads It As | Institutional Intent | Actual Outcome |
|---|---|---|---|
| Breakout above resistance | Bullish signal — buy the breakout | BSL sweep — distributing longs into retail buys | Sharp reversal below breakout level |
| Drop below support | Bearish signal — sell the breakdown | SSL sweep — accumulating longs against retail sell-stops | Strong bullish reversal begins |
| Spike to highs before reversal | FOMO entry | Final distribution at peak liquidity | Late retail buyers immediately underwater |
| False breakout and reversal | "Market is manipulated" | Planned stop-hunt — clear stops, load positions | Strong trend opposite the breakout direction |
| Equal lows tested twice | Double bottom — buy | SSL pool — third touch will sweep stops | Third touch sweeps all stops, strong reversal |

---

# SECTION 4 — P_115 KNOWLEDGE BASE: ABSORPTION MECHANICS

> **File:** `05 – P_115 Knowledge Base/02 Absorption Mechanics.md`
> **Links to:** [[Absorption]] | [[Wyckoff Model]] | [[Stop Hunt]] | [[P_115 Master Index]]

## What Is Institutional Absorption?

**Absorption** is the process by which institutions use incoming retail order flow to fill their own large positions — silently and without creating visible directional movement.

| Type | Mechanism | Signature |
|---|---|---|
| **Bullish Absorption** | Institutions absorb retail sell orders at key lows to accumulate long positions | High volume at lows + price fails to fall further |
| **Bearish Absorption** | Institutions absorb retail buy orders at key highs to build short positions | High volume at highs + price fails to rise further |

---

## The Three Phases of Absorption

> [!note] Phase 1 — ACCUMULATION: The Quiet Load
> Price consolidates in a well-defined range. Volatility decreases. Volume compresses. Institutions are quietly absorbing retail sell orders — building long inventory at favorable prices. ATR contracts. Moving averages flatten.
> **Do not trade this phase — observe it.**

> [!warning] Phase 2 — MARKUP/MANIPULATION: The Trap
> Price is engineered to move against the anticipated direction — either a false breakdown (bear trap targeting SSL) or false breakout (bull trap targeting BSL). Volume spikes sharply. The reversal candle that follows is the **most important candle in the entire cycle.**

> [!success] Phase 3 — DISTRIBUTION/EXPANSION: The Move
> Once fully loaded, institutions allow — or actively drive — price to trend strongly in their intended direction. Strong momentum candles, increasing volume, decisive structure breaks. This is the **primary entry window** for P_115 trades.

---

## Wyckoff Absorption Model (P_115 Adaptation)

| Wyckoff Term | Wyckoff Definition | P_115 Equivalent |
|---|---|---|
| Preliminary Support (PS) | First buying after extended decline | Initial demand zone — SSL approach begins |
| Selling Climax (SC) | Massive volume selling, exhaustion | Stop-hunt trigger — SSL sweep with volume spike |
| Automatic Rally (AR) | Sharp bounce from SC low | Reversal candle — Institutional Entry Zone confirmed |
| Secondary Test (ST) | Price retests SC low on lower volume | Retest of SSL — compression zone forms |
| Spring | Final push below SC low to clear stops | Liquidity Hunt — final SSL sweep before expansion |
| Sign of Strength (SOS) | Strong rally above AR high with volume | Phase 3 Expansion — P_115 primary entry confirmed |

---

## Volume Footprint of Absorption (4 Core Signatures)

1. **High volume at lows, no downward progress** → Bullish absorption. Institutions absorbing every sell order.
2. **High volume at highs, no upward progress** → Bearish absorption / distribution. Institutions selling into every buy.
3. **Low volume rallies from lows** → Institutional control of supply. Price likely to accelerate.
4. **Declining volume on new highs/lows** → Exhaustion. Phase 4 distribution. Trend near its end.

> [!success] Absorption Signal
> When price tests a key level on high volume but **fails to follow through** — that is institutional absorption. The volume = the institutional fill. Wait for the reversal candle to confirm absorption is complete.

---

## Absorption Identification Checklist

| Signal | What to Look For | Bias |
|---|---|---|
| Volume spike at key low | Above-average volume at SSL cluster; no new low on next candle | Bullish |
| Wick below support, close above | Long lower wick below support; body closes back above | Bullish |
| Consolidation near major level | Price coils at HTF support without decisively breaking | Bullish (loading) |
| Failed breakout above resistance | Price pushes above resistance then closes back below it | Bearish |
| Price compression before expansion | ATR contracts, Bollinger Bands tighten, smaller swings | Directional (confirm with structure) |
| Volume spike at key high, no progress | Above-average volume at BSL cluster; no new high on next candle | Bearish |
| Wick above resistance, close below | Long upper wick above resistance; body closes back below | Bearish |

---

# SECTION 5 — P_115 KNOWLEDGE BASE: STOP HUNT MECHANICS

> **File:** `05 – P_115 Knowledge Base/03 Stop Hunt Mechanics.md`
> **Links to:** [[Stop Hunt]] | [[BSL – Buy-Side Liquidity]] | [[SSL – Sell-Side Liquidity]] | [[Kill Zones]] | [[P_115 Master Index]]

## What Is a Stop Hunt?

A **stop hunt** is a deliberate, engineered price move that specifically targets stop-loss orders placed by retail participants at predictable levels. Not random volatility — a systematic operation to generate counterparty liquidity for institutional fills.

### Primary Stop-Hunt Target Zones
- Swing highs and swing lows
- Round numbers and psychological levels (e.g., 4,000.00, 1.2000)
- Prior day, week, and month highs/lows
- **Equal highs and equal lows** ← highest-probability targets
- VWAP extremes and moving average clusters
- Opening range extremes (first 30-minute high/low)
- Session highs/lows from the Asian session

---

## Anatomy of a Stop Hunt (4-Step Sequence)

```
Step 1 — APPROACH
Price moves toward a known liquidity level.
Retail traders place stops just beyond it.
↓
Step 2 — PENETRATION (The Sweep)
Price accelerates through the level on a sharp wick.
All stop-loss orders trigger. Volume spikes.
↓
Step 3 — IMMEDIATE REVERSAL (Institutional Entry)
Stop-out orders absorbed by institutions.
Price immediately reverses direction.
↓
Step 4 — CONFIRMATION (Close Back Above Level)
Price closes back through the swept level.
← THIS IS THE P_115 ENTRY SIGNAL
```

---

## Bullish Stop Hunt Setup

| Parameter | Detail |
|---|---|
| **Setup Condition** | Two or more lows at same level = SSL cluster below equal lows |
| **Trigger** | Price breaks below equal lows on wick/aggressive candle; volume spikes; price reverses and closes back above |
| **Entry** | Long on close of candle that recovers above swept level |
| **Stop Loss** | 1 ATR below lowest wick of stop-hunt candle |
| **Target 1** | Nearest untested BSL zone above (equal highs, prior high) |
| **Target 2** | Prior session or weekly BSL zone |
| **Minimum R:R** | 1:2 required |

---

## Bearish Stop Hunt Setup

| Parameter | Detail |
|---|---|
| **Setup Condition** | Two or more highs at same level = BSL cluster above equal highs |
| **Trigger** | Price spikes above equal highs; volume spikes; price reverses and closes back below |
| **Entry** | Short on close of candle that fails back below swept level |
| **Stop Loss** | 1 ATR above highest wick of stop-hunt candle |
| **Target 1** | Nearest untested SSL zone below (equal lows, prior low) |
| **Target 2** | Prior session or weekly SSL zone |
| **Minimum R:R** | 1:2 required |

---

## Stop Hunt vs. True Breakout — Diagnostic Table

| Characteristic | Stop Hunt | True Breakout |
|---|---|---|
| Volume on the break | High spike → immediate contraction on reversal | High → continues to expand in breakout direction |
| Candle close | Closes back inside range within 1–2 candles | Closes decisively beyond level, holds above it |
| Follow-through | Next candle moves OPPOSITE to break | Next candle continues in breakout direction |
| Market structure context | Against HTF bias; overextended; no structure confirmation | Aligns with HTF bias; prior structure supportive |
| Time of day | Kill zones (London open, NY open) | Any time — most powerful with strong catalysts |
| Wick length | Long wick beyond level; disproportionate to body | Short or no wicks; strong body closes beyond level |

---

## High-Probability Stop Hunt Zones

> [!warning] P_115 Rule
> **Equal highs and equal lows are the highest-probability stop-hunt targets.** Two touches = institutional magnet. Three touches = imminent sweep. Mark every set at session open. These are your primary watch levels.

| Zone Type | Priority | Why |
|---|---|---|
| Equal Highs / Equal Lows | ⭐⭐⭐ Highest | Most visible clustered stops; deliberate institutional magnets |
| Prior Day/Week/Month H/L | ⭐⭐⭐ Highest | Widely watched; heavily stop-clustered |
| Opening Range Extremes | ⭐⭐ High | First 30 min high/low frequently targeted before true direction |
| Kill Zone Windows | ⭐⭐ High | London Open + NY Open = highest probability stop hunt timing |

---

# SECTION 6 — P_115 KNOWLEDGE BASE: MOMENTUM PHASES

> **File:** `05 – P_115 Knowledge Base/04 Momentum Phases.md`
> **Links to:** [[Compression Phase]] | [[Expansion Phase]] | [[Stop Hunt]] | [[Kill Zones]] | [[P_115 Master Index]]

## The P_115 Four-Phase Momentum Framework

All price action moves through a **repeating four-phase cycle**. Phase identification determines when to watch, wait, enter, and exit.

| Phase | Name | ATR | Volume | Candle Structure | P_115 Action |
|---|---|---|---|---|---|
| **1** | Compression (The Coil) | Contracting | Declining / Dry | Small bodies, narrow range, inside bars | Observe. Mark SSL/BSL. Do not trade. |
| **2** | Liquidity Hunt (The Trap) | Spike (brief) | Spike on sweep | Aggressive wick or breakout candle; reversal candle immediately follows | Identify reversal candle. Prepare entry. Wait for confirmation. |
| **3** | Expansion (The Trend) | Expanding | Increasing, sustained | Large bodies, minimal wicks, consecutive closes in trend direction | Enter trade. Set stop. Target next liquidity pool. |
| **4** | Distribution/Exhaustion (The Exit) | Elevated but declining | Declining (divergence) | Long wicks, narrow bodies, doji, reversal patterns | Exit remaining position. Do not add. Await next compression. |

---

## Phase 1 — Compression (The Coil)

- Price range narrows progressively — each swing high is lower, each swing low is higher
- ATR contracts measurably
- Moving averages flatten and converge
- Volume dries up

> [!note] P_115 Action: Phase 1
> **Do NOT trade Phase 1.** Observe it. Mark the compression range boundaries. Identify SSL and BSL levels adjacent to the range. Prepare for Phase 2.

---

## Phase 2 — Liquidity Hunt (The Trap)

- Price makes a decisive move out of Phase 1 — in the **opposite** direction to the anticipated trend
- Aggressive, fast, often during kill zone windows
- Volume spikes sharply
- Move immediately stalls and reverses

> [!danger] Critical Warning: Phase 2
> Phase 2 is the most common retail trap. The fast move out of compression **looks** like a breakout. It is not. **Never enter in the direction of the Phase 2 move.** Wait for the reversal candle that confirms Phase 2 is complete.

---

## Phase 3 — Expansion (The Trend)

- Strong momentum candles with large bodies and minimal wicks
- ATR expands
- Volume increases progressively in trend direction
- Price breaks decisively out of Phase 1 compression zone in the **true direction**
- Market structure shifts: lower lows → higher lows (bullish) or higher highs → lower highs (bearish)

> [!success] P_115 Action: Phase 3
> **Enter at Phase 3 confirmation.** Stop below the Phase 2 wick. Target the next liquidity pool (BSL for bullish, SSL for bearish). This is the primary profit-generation phase.

---

## Phase 4 — Distribution / Exhaustion (The Exit)

- Price extended well beyond moving averages
- **Volume divergence** — price makes new highs/lows but volume decreases ← PRIMARY WARNING
- Candle structure degrades: large bodies → long wicks, doji, narrowing bodies
- RSI/momentum oscillator divergence appears
- Phase 1 compression patterns begin to form at the extreme

> [!danger] Exit Rule: Phase 4
> **Never hold through Phase 4 hoping for extension.** Volume divergence + wick formation + oscillator divergence = institutional distribution in progress. Exit into strength — not weakness.

---

## Full Bullish Momentum Cycle Walkthrough

```
PHASE 1 — OBSERVATION
Price ranging for hours on 1H. ATR dropped 40% from 14-period average.
Volume below 20-period average.
Two equal lows visible at range bottom → SSL cluster marked.
Nearest BSL zone above identified (equal highs from prior sessions).
↓
PHASE 2 — DECISION POINT
London Open kill zone: price drops sharply below equal lows.
Long lower wick forms. Volume spikes 2.5x average.
Strong bullish engulfing closes back above equal lows.
→ STOP HUNT CONFIRMED. TRIGGER ACTIVATED.
↓
PHASE 3 — ENTRY
Enter LONG on close of engulfing confirmation candle.
Stop: 1 ATR below stop-hunt wick.
Target 1: Range high above. Target 2: Equal highs from prior sessions.
R:R = 1:2.8 → above 1:2 minimum → TRADE IS VALID.
↓
PHASE 4 — EXIT
Price reaches Target 1 → exit 50%, move stop to breakeven.
Price continues toward Target 2.
Wicks forming + volume divergence on 15m chart.
Remaining 50% exited as price tags Target 2 BSL zone.
→ FULL CYCLE COMPLETE.
```

---

## Full Bearish Momentum Cycle Walkthrough

```
PHASE 1 — OBSERVATION
Equal highs forming visible BSL cluster above price.
ATR contracting. Volume declining.
Mark equal highs as primary stop-hunt target.
Nearest SSL zone below range identified.
↓
PHASE 2 — DECISION POINT
NY Open kill zone: price spikes sharply above equal highs.
Long upper wick forms. Volume spikes.
Strong bearish engulfing closes back below equal highs.
→ STOP HUNT CONFIRMED. TRIGGER ACTIVATED.
↓
PHASE 3 — ENTRY
Enter SHORT on close of bearish engulfing confirmation candle.
Stop: 1 ATR above stop-hunt wick.
Target 1: Bottom of range (SSL). Target 2: Prior session low.
↓
PHASE 4 — EXIT
Price reaches Target 1 → exit 50%, move stop to breakeven.
Volume divergence + long lower wicks appear at Target 2 SSL zone.
Remaining position exited into institutional buying pressure.
→ FULL CYCLE COMPLETE.
```

---

# SECTION 7 — P_115 KNOWLEDGE BASE: CYCLE INTEGRATION & MULTI-TIMEFRAME

> **File:** `05 – P_115 Knowledge Base/05 Cycle Integration.md`
> **Links to:** [[Confluence Stack]] | [[BSL – Buy-Side Liquidity]] | [[SSL – Sell-Side Liquidity]] | [[P_115 Master Index]]

## Bullish Liquidity Cycle (Full Sequence)

```
1. SSL POOL FORMATION
   Equal lows form below price → visible sell-side liquidity pool.
   More touches = more stops clustered = higher institutional interest.
   ↓
2. STOP HUNT TRIGGER
   Price breaks below SSL pool → triggers all sell stops + retail panic.
   Phase 2 liquidity hunt. Volume spikes as institutional buyers absorb.
   ↓
3. INSTITUTIONAL ABSORPTION
   Institutional reversal candle forms → strong close back above swept level.
   All targeted sell orders absorbed. Long positions loaded.
   ↓
4. PHASE 3 EXPANSION
   True directional move upward begins.
   No significant sell-side opposition remaining below.
   ↓
5. BSL TARGET
   Expansion targets nearest untested buy-side liquidity pool above.
   Price delivered to target before next distribution cycle begins.
```

## Bearish Liquidity Cycle (Full Sequence)

```
1. BSL POOL FORMATION
   Equal highs form above price → visible buy-side liquidity pool.
   Retail places buy stops above, anticipating breakout.
   ↓
2. STOP HUNT TRIGGER
   Price spikes above BSL pool → triggers all buy stops + FOMO buys.
   Phase 2 liquidity hunt. Volume spikes as institutions distribute.
   ↓
3. INSTITUTIONAL DISTRIBUTION
   Institutional reversal candle forms → strong close back below swept level.
   Distribution into BSL complete. Short positions loaded.
   ↓
4. PHASE 3 EXPANSION
   True directional move downward begins.
   No significant buy-side opposition remaining above.
   ↓
5. SSL TARGET
   Expansion targets nearest untested sell-side liquidity pool below.
   Price delivered before next accumulation cycle begins.
```

---

## Multi-Timeframe Framework

| Timeframe | Role in P_115 Framework | Primary Liquidity Tool |
|---|---|---|
| Monthly / Weekly | HTF Bias Determination — dominant directional framework | HTF SSL/BSL pool identification; major liquidity voids |
| Daily | Liquidity Hunt Identification — session-level stop-hunt zones | Prior day high/low; daily SSL/BSL clusters; session range |
| 4H / 1H | Momentum Phase Tracking — which phase is active | Phase identification; compression zone mapping; ATR monitoring |
| 15m / 5m | Entry Trigger Identification — precise reversal candle + entry confirmation | Stop-hunt reversal candle; Phase 3 breakout; entry and stop placement |
| 1m / Tick | Execution Precision — fine-tuning, real-time order flow | Order flow, tape reading, volume delta for absorption confirmation |

---

## The Confluence Stack — Highest-Probability Setup

> [!success] P_115 Confluence Stack — All Three Required
>
> **Condition 1 — HTF Directional Bias:**
> Monthly or weekly chart in bullish (or bearish) momentum phase. HTF in Phase 3 expansion, or has just completed a Phase 2 HTF stop hunt.
>
> **Condition 2 — LTF Stop Hunt:**
> On the 15m or 1H chart, a stop hunt has just completed against the LTF SSL (bullish trade) or BSL (bearish trade). Reversal candle confirmed.
>
> **Condition 3 — Phase 3 Breakout Candle:**
> The first Phase 3 expansion candle breaks the Phase 1 compression range boundary decisively on above-average volume, in the direction of the HTF bias.
>
> **When all three conditions are met: Take the trade. Size appropriately. Manage to the framework.**

---

# SECTION 8 — P_115 KNOWLEDGE BASE: EXECUTION FRAMEWORK

> **File:** `05 – P_115 Knowledge Base/06 Execution Framework.md`
> **Links to:** [[Confluence Stack]] | [[Stop Hunt]] | [[Kill Zones]] | [[P_115 Master Index]]

## Pre-Trade Checklist (8-Point Gate)

> [!danger] Any FAIL on items 1–7 = automatic no-trade.

| Step | Question | Confirmation Signal |
|---|---|---|
| 1 | HTF directional bias confirmed? | Weekly or daily in Phase 3 expansion, or clean HTF structure |
| 2 | Liquidity pool clearly identified? | Visible SSL (bullish) or BSL (bearish) cluster marked on chart |
| 3 | Stop hunt triggered and completed? | Price swept the pool AND reversal candle closed back through swept level |
| 4 | Phase 3 breakout candle confirmed? | First expansion candle broke Phase 1 boundary in HTF bias direction |
| 5 | Entry level precisely defined? | Entry price identified at close of reversal or breakout candle |
| 6 | Stop loss placed correctly? | 1 ATR beyond stop-hunt wick; not at round number; not at obvious cluster |
| 7 | Target marked and R:R ≥ 1:2? | At least one BSL/SSL target identified; R:R ≥ 1:2 confirmed |
| 8 | In kill zone or primary session? | London Open, NY Open, or other high-probability liquidity window |

---

## Three Entry Types

> [!tip] Entry Type 1 — Aggressive Entry (Earliest / Highest Reward)
> **Timing:** Close of the reversal candle — the candle that closes back through the swept level after the stop hunt.
> **Stop:** 1 ATR below wick (bullish) or above wick (bearish).
> **Use when:** High confidence in setup; Confluence Stack fully formed.

> [!info] Entry Type 2 — Conservative Entry (Tighter Risk / Higher Precision)
> **Timing:** First retest of the swept liquidity level after the initial reversal. Swept level acts as new support (bullish) or resistance (bearish).
> **Stop:** Just below (bullish) or above (bearish) the retest level.
> **Note:** Higher probability of fill; may miss if price does not retest.

> [!note] Entry Type 3 — Breakout Entry (Most Confirmation / Latest)
> **Timing:** Confirmed break of the Phase 1 compression zone boundary in the Phase 3 expansion direction, after Phase 2 is complete.
> **Stop:** Below Phase 1 zone low (bullish) or above zone high (bearish).
> **Note:** Widest stop relative to compression range. Validate R:R before taking.

---

## Stop Loss Placement Rules

| Type | Placement | Use When |
|---|---|---|
| **Structural Stop** | Beyond last swing low (bullish) or swing high (bearish) that defines the trade's thesis | Trade has clear structural invalidation point |
| **Wick-Based Stop** | 1 ATR beyond lowest wick (bullish) or highest wick (bearish) of stop-hunt candle | Accounts for secondary sweep of same level |

### Prohibited Stop Zones
- ❌ Round numbers (4,000.00, 1.2000) — these are stop-hunt targets themselves
- ❌ Entry candle high/low — inside the noise zone
- ❌ Moving average levels visible on standard charts

> [!warning] Stop Placement Rule
> **Your stop must be beyond the point that would invalidate your thesis.** Ask: "If price reaches this level, is my trade idea still valid?" If NO → that is where the stop belongs.

---

## Profit Target Framework

| Target Level | Definition | Typical R-Multiple | Action |
|---|---|---|---|
| **Target 1** | First untested liquidity pool in trade direction (nearest SSL/BSL) | 1:1 to 1:2 | Exit 50% of position. Move stop to breakeven on remainder. |
| **Target 2** | Prior session or prior day high/low (medium-term liquidity pool) | 1:2 to 1:4 | Exit additional 30–40%. Trail stop on remainder. |
| **Target 3** | Weekly or monthly liquidity zone (HTF BSL or SSL pool) | 1:4 to 1:8+ | Exit final position. Evaluate for re-entry on next compression phase. |

> [!warning] Minimum Standard
> The P_115 framework requires a **minimum 1:2 risk-reward ratio** for any trade to be taken. If the distance from entry to stop is greater than half the distance to Target 1 → do not take the trade.

---

## Trade Management Rules (6 Non-Negotiables)

1. **Move Stop to Breakeven** immediately after Target 1 is hit. No exceptions.
2. **Scale Out 50% at Target 1.** Locking in profit at T1 is a framework requirement — not optional.
3. **Hold Remainder for Target 2/3** with a trailing stop. Trail below new higher lows (bullish) or above new lower highs (bearish).
4. **Never Add to Losing Positions.** If trade moves against you, thesis may be wrong. Exit and re-evaluate.
5. **Exit Full Position on Phase 4 Signals.** Volume divergence + wick formation + oscillator divergence before T2 → exit immediately.
6. **Maximum Daily Loss Limit.** Three consecutive full stop-outs → stop trading for the session.

---

## Session Kill Zone Reference

| Session | Window (ET) | Typical Liquidity Event | P_115 Focus |
|---|---|---|---|
| Asian Session | 7:00 PM – 2:00 AM | Range building; liquidity pools form at range extremes | Mark Asian high/low. Observe Phase 1 compression forming. |
| **London Open ⭐** | 2:00 AM – 5:00 AM | First major liquidity hunt — Asian range extremes frequently swept | Highest priority stop-hunt watch window. Phase 2 → Phase 3 entry. |
| **New York Open ⭐** | 8:30 AM – 11:00 AM | Highest volume — trend establishment or second major stop hunt | Primary P_115 trade session. Phase 3 extension or new stop hunts. |
| NY Lunch ⚠️ | 11:30 AM – 1:30 PM | Liquidity thins — "lunch reversal trap" common | **Reduce size. Avoid new entries.** Often Phase 4 of AM trend. |
| NY Afternoon | 1:30 PM – 4:00 PM | Position adjustments; late-session continuation or reversal | Manage existing positions. Close intraday positions before 3:45 PM. |
| NY Close | 3:45 PM – 4:00 PM | Final institutional adjustments; range extremes revisited | Exit all intraday positions. Mark closing levels for next session. |

---

## Common Mistakes — Prevention Guide

| Mistake | Why It Happens | P_115 Correction |
|---|---|---|
| Entering before stop hunt completes | Impatience — price approaches liquidity level and "feels ready" | Wait for reversal candle that closes back through swept level. No candle = no trade. |
| Chasing Phase 3 late | FOMO — seeing strong trend, entering after 2+ expansion candles | If you missed Phase 3 entry, wait for Phase 1 to reform. Do not chase. |
| Ignoring HTF bias | Taking LTF setups without checking higher-timeframe context | Always validate HTF bias first. Perfect LTF setup against HTF = low-probability trade. |
| Placing stops at round numbers | Round numbers feel "clean" and logical | Round numbers are institutional stop-hunt targets. Place 1 ATR beyond the structural level. |
| Entering on the stop-hunt candle | Entering on Phase 2 spike rather than Phase 3 reversal candle | The spike candle is NOT the entry. The reversal candle closing back through is the entry. |
| Holding through Phase 4 | Greed — hoping for larger move after targets reached | Exit 50% at T1. Move stop to BE. Exit at first Phase 4 signal. Protect the R. |
| Overtrading NY Lunch | Boredom — taking low-quality setups to stay active | NY Lunch is a no-trade zone. Use the time to mark next session levels and review AM trades. |

---

# SECTION 9 — P_115 KNOWLEDGE BASE: QUICK REFERENCE CARD

> **File:** `05 – P_115 Knowledge Base/08 Quick Reference Card.md`
> **Links to:** [[P_115 Master Index]] | [[Stop Hunt]] | [[Kill Zones]] | [[Confluence Stack]]

## Liquidity Pool Types (Fast Reference)

| Pool | Location | Institutional Use |
|---|---|---|
| **BSL** | ABOVE price — above swing highs, equal highs, prior session highs | Distribution target (bearish); measured-move target (bullish) |
| **SSL** | BELOW price — below swing lows, equal lows, prior session lows | Accumulation target (bullish); measured-move target (bearish) |
| **Liquidity Void** | Price range with no prior significant trading volume | Price fills voids rapidly with minimal resistance during Phase 3 |

---

## Stop Hunt Rules (3 Absolutes)

> [!danger] Rule 1
> **Never enter IN the direction of the stop-hunt move.** The sweep candle is not the entry — the reversal candle is the entry.

> [!danger] Rule 2
> **A stop hunt is confirmed ONLY when price closes BACK through the swept level.** Wicks alone are not confirmation — the candle BODY close is required.

> [!danger] Rule 3
> **Equal highs and equal lows are the highest-probability targets.** Two touches = institutional magnet. Three touches = imminent sweep.

---

## Phase Quick-ID Reference

| Phase | Name | Quick Identifier | Action |
|---|---|---|---|
| 1 | Compression | ATR contracting + volume drying + flat MAs | Watch. Map levels. No trade. |
| 2 | Liquidity Hunt | Fast spike through SSL/BSL + volume spike + immediate reversal candle | Confirm reversal. Prepare entry. |
| 3 | Expansion | Strong momentum candles + ATR expanding + volume building + structure break | Enter trade. Set stop. Target liquidity pool. |
| 4 | Distribution | Long wicks + narrow bodies + volume divergence + oscillator divergence | Exit all. Do not hold. Await next Phase 1. |

---

## Full Cycle Execution Checklist

| Step | Bullish Cycle | Bearish Cycle |
|---|---|---|
| 1 | HTF bullish bias confirmed (daily/weekly) | HTF bearish bias confirmed (daily/weekly) |
| 2 | SSL cluster (equal lows) identified below price | BSL cluster (equal highs) identified above price |
| 3 | Phase 1 compression observed — ATR/volume contracting | Phase 1 compression observed — ATR/volume contracting |
| 4 | SSL sweep wick forms — stops triggered below equal lows | BSL sweep wick forms — stops triggered above equal highs |
| 5 | Bullish reversal candle closes back above swept level | Bearish reversal candle closes back below swept level |
| 6 | Enter long — stop below wick — target BSL above | Enter short — stop above wick — target SSL below |
| 7 | Exit 50% at Target 1 — move stop to breakeven | Exit 50% at Target 1 — move stop to breakeven |
| 8 | Trail stop. Exit remaining at Phase 4 signal or Target 2 | Trail stop. Exit remaining at Phase 4 signal or Target 2 |

---

## P_115 Minimum Trade Criteria (All Required)

- [ ] HTF directional bias is confirmed and aligns with trade direction
- [ ] A liquidity pool (SSL or BSL) has been clearly identified and marked
- [ ] The stop hunt has triggered AND a reversal candle has confirmed completion
- [ ] Phase 3 expansion candle has formed (or is forming) in the HTF direction
- [ ] Entry, stop, and at least one target are defined before order placement
- [ ] Minimum risk-reward ratio of 1:2 is confirmed
- [ ] Maximum daily loss limit has not been reached (3 consecutive stop-outs = no more trades)

---

# SECTION 10 — GLOSSARY (OBSIDIAN ATOMIC NOTES)

> Each term below maps to a standalone note in `06 – Concepts & Definitions/`

---

### [[ATR (Average True Range)]]
A volatility indicator measuring the average range of price movement over a specified period (typically 14 candles). In P_115: contracting ATR = Phase 1 (compression); expanding ATR = Phase 3 (expansion). Used to calibrate all stop-loss distances.

### [[Absorption]]
The process by which institutional participants use incoming retail order flow to fill their own large opposing positions at key price levels — silently, without creating visible directional movement. Signature: high volume at key level + no price follow-through in expected direction.

### [[BSL – Buy-Side Liquidity]]
Clusters of buy-stop orders and stop-losses on short positions located **ABOVE price** — typically above swing highs, equal highs, prior session highs, and round numbers. Institutional distribution targets in the bearish cycle. Measured-move targets in the bullish cycle.

### [[Compression Phase]]
Phase 1 of the P_115 momentum cycle. Contracting ATR + declining volume + flat moving averages. Represents the institutional loading period before Phase 2 stop hunt and Phase 3 expansion. **No trades are taken during Phase 1.**

### [[Confluence Stack]]
The highest-probability P_115 trade condition requiring three simultaneous alignments: (1) HTF directional bias confirmed, (2) LTF stop hunt completed with reversal candle, (3) Phase 3 breakout candle forming in HTF direction. All three must be met simultaneously.

### [[Distribution Phase]]
Phase 4 of the P_115 momentum cycle. Institutional participants exit positions into remaining retail momentum — creating volume divergence, wick formation, and oscillator divergence. Signal to exit all remaining positions immediately.

### [[Equal Highs / Equal Lows]]
Two or more candlestick highs (equal highs) or lows (equal lows) at approximately the same price level. The highest-probability stop-hunt targets in the P_115 framework. Signal a deliberate clustering of retail stop orders that institutions are likely to sweep before any major directional move.

### [[Expansion Phase]]
Phase 3 of the P_115 momentum cycle. The true directional move begins — strong momentum candles, expanding ATR, sustained volume increase, decisive structural breaks. Primary P_115 trade entry and profit-generation phase.

### [[HTF / LTF]]
Higher Timeframe / Lower Timeframe. HTF (Monthly, Weekly, Daily) = directional bias. LTF (4H, 1H, 15m, 5m) = entry precision and stop-hunt identification.

### [[Kill Zones]]
Specific high-probability session windows during which liquidity events are most consistently engineered. Primary: **London Open (2:00–5:00 AM ET)** and **New York Open (8:30–11:00 AM ET)**. Secondary: NY Afternoon (1:30–4:00 PM ET).

### [[Liquidity Pool]]
Any concentration of resting orders (stops, limit orders, pending orders) clustered at or near a specific price level. BSL pools reside above price; SSL pools reside below price. Primary targets and destinations of institutional price delivery.

### [[Liquidity Void]]
A price range where little or no trading volume occurred during prior price delivery. Price tends to move rapidly through voids during Phase 3 expansion with minimal resistance. Marks the path of least resistance for institutional delivery.

### [[Market Structure]]
Sequential pattern of swing highs and swing lows defining directional bias. Bullish = higher highs + higher lows. Bearish = lower highs + lower lows. A structural break (first lower low or higher high) signals a potential bias shift.

### [[SSL – Sell-Side Liquidity]]
Clusters of sell-stop orders and stop-losses on long positions located **BELOW price** — below swing lows, equal lows, prior session lows, and round numbers. Institutional accumulation targets in the bullish cycle. Measured-move targets in the bearish cycle.

### [[Stop Hunt]]
A deliberate, engineered price move targeting retail stop-loss orders at predictable levels. Mechanics: price sweeps through stop cluster → triggers all stops → institutions absorb triggered orders into opposing positions → price trends strongly in opposite direction.

### [[VWAP]]
Volume-Weighted Average Price — the average price of an asset weighted by volume, recalculated from the session open. A dynamic institutional reference level. Stops placed above/below VWAP are predictable and frequently targeted during kill zones.

### [[Wyckoff Model]]
Richard Wyckoff's early-20th-century framework for understanding institutional accumulation and distribution. P_115 maps Wyckoff's PS, SC, AR, ST, Spring, and SOS events directly to the P_115 compression → liquidity hunt → institutional entry → expansion cycle.

---

# APPENDIX A — P_115 MASTER INDEX

> **File:** `05 – P_115 Knowledge Base/P_115 Master Index.md`

## Knowledge Base Navigation

| Section | File | Core Concepts |
|---|---|---|
| 01 | [[01 Liquidity Theory]] | BSL, SSL, Liquidity Pools, Retail vs. Institutional |
| 02 | [[02 Absorption Mechanics]] | Absorption, Wyckoff Model, Volume Signatures |
| 03 | [[03 Stop Hunt Mechanics]] | Stop Hunt Anatomy, Bullish/Bearish Setups, Hunt vs. Breakout |
| 04 | [[04 Momentum Phases]] | 4-Phase Cycle, Phase Identification, Full Cycle Walkthroughs |
| 05 | [[05 Cycle Integration]] | Bullish/Bearish Cycle, Multi-Timeframe, Confluence Stack |
| 06 | [[06 Execution Framework]] | Pre-Trade Checklist, Entry Types, Stops, Targets, Trade Management |
| 07 | [[07 Diagram Reference]] | Visual concept index (all 9 diagrams) |
| 08 | [[08 Quick Reference Card]] | Condensed session reference |

## Playbooks Navigation

| Playbook | File | When to Use |
|---|---|---|
| Bullish Stop Hunt | [[Bullish Stop Hunt Playbook]] | SSL sweep confirmed; HTF bullish; reversal candle formed |
| Bearish Stop Hunt | [[Bearish Stop Hunt Playbook]] | BSL sweep confirmed; HTF bearish; reversal candle formed |
| Confluence Stack | [[Confluence Stack Playbook]] | All three Confluence Stack conditions met simultaneously |

---

# APPENDIX B — DAILY WORKFLOW STANDARD OPERATING PROCEDURE

## Pre-Market (Complete Before Market Open)
1. Open `01 – Pre-Market/` → create new note with Pre-Market Prep template
2. Check Weekly chart → confirm HTF bias (bullish/bearish/neutral)
3. Check Daily chart → identify prior day high/low; mark BSL/BSL
4. Identify all equal highs and equal lows on the 4H and 1H charts → mark in liquidity map
5. Assess current phase (1/2/3/4) on 1H chart
6. Set session kill zone alerts (London 2 AM, NY Open 8:30 AM)
7. List setups to watch → link to Setup templates

## During Session (Kill Zone Focus)
1. At London Open: watch for Phase 2 stop hunts on Asian range extremes
2. Complete pre-trade checklist (8-point) before any order placement
3. Enter trade → immediately link to Trade Journal template
4. Manage: T1 exit + stop to BE; trail for T2/T3

## Post-Market (Complete Within 1 Hour of Market Close)
1. Complete Trade Journal notes for all trades taken
2. Rate each trade on 6-category scoring system
3. Add reflection to Pre-Market note (end-of-day section)
4. Log R-multiple to `08 – Metrics & Stats/R-Multiple Log.md`
5. Mark any rule violations in trade journal
6. Set up next session's liquidity map (prior session high/low noted)

## End of Week
1. Open `04 – Weekly Reviews/` → create weekly review note
2. Compile all trades → fill Week at a Glance table
3. Calculate win rate and average R-multiple
4. Assess phase identification accuracy for the week
5. Identify one improvement focus for next week
6. Update HTF bias for following week

---

*P_115 Training Framework | Trading Brain Obsidian Implementation v1.0 | Confidential – Internal Use Only*
*Author: Anthony | P_115 Framework | May 2026*

4. PHASE 3 EXPANSION
   Price begins true directional move upward.
   Institutional order flow drives price with no significant sell-side opposition remaining.
   ↓
5. BSL TARGET
   Expansion targets nearest untested buy-side liquidity pool above.
   (Equal highs, prior session high, weekly BSL.)
   Price delivered to target → next distribution cycle begins.
```

---

## Bearish Liquidity Cycle (Full Sequence)

```
1. BSL POOL FORMATION
   Equal highs form above price → visible buy-side liquidity pool.
   Retail traders place buy stops above highs, anticipating breakout.
   ↓
2. STOP HUNT TRIGGER
   Price spikes above BSL pool → triggers all buy stops + FOMO buyers.
   Phase 2 liquidity hunt. Volume spikes as institutional sellers distribute.
   ↓
3. INSTITUTIONAL DISTRIBUTION
   Reversal candle forms → strong close back below swept level.
   Distribution into BSL complete. Short positions loaded.
   ↓
4. PHASE 3 EXPANSION (Down)
   Price begins true directional move downward.
   No significant buy-side opposition remaining above.
   ↓
5. SSL TARGET
   Expansion targets nearest untested sell-side liquidity pool below.
   (Equal lows, prior session low, weekly SSL.)
```

---

## Multi-Timeframe Role Assignment

| Timeframe | Role in P_115 Framework | Primary Liquidity Tool |
|---|---|---|
| Monthly / Weekly | HTF Bias Determination — establishes dominant directional framework | HTF SSL/BSL pool identification; major liquidity voids |
| Daily | Liquidity Hunt Identification — identifies session-level stop-hunt zones for the week | Prior day high/low; daily SSL/BSL clusters; session range |
| 4H / 1H | Momentum Phase Tracking — identifies which phase market is currently in | Phase identification; compression zone mapping; ATR monitoring |
| 15m / 5m | Entry Trigger Identification — precise reversal candle and entry confirmation | Stop-hunt reversal candle; Phase 3 breakout confirmation |
| 1m / Tick | Execution Precision — fine-tune entry; read real-time order flow | Order flow, tape reading, volume delta for absorption confirmation |

---

## The Confluence Stack — Highest-Probability Setup

> [!success] P_115 Confluence Stack — All Three Must Be Met
>
> **Condition 1 — HTF Directional Bias:**
> Monthly or weekly chart is in a bullish (or bearish) momentum phase. The HTF is in Phase 3 expansion, or has just completed a Phase 2 HTF stop hunt.
>
> **Condition 2 — LTF Stop Hunt:**
> On the 15m or 1H chart, a stop hunt has just completed against the LTF SSL (bullish trade) or BSL (bearish trade). The reversal candle is confirmed.
>
> **Condition 3 — Phase 3 Breakout Candle:**
> The first Phase 3 expansion candle breaks the Phase 1 compression range boundary decisively on above-average volume, in the direction of the HTF bias.
>
> **When all three conditions are met: This is the setup worth waiting for. Take the trade. Size appropriately. Manage to the framework.**

---

# SECTION 8 — P_115 KNOWLEDGE BASE: EXECUTION FRAMEWORK

> **File:** `05 – P_115 Knowledge Base/06 Execution Framework.md`
> **Links to:** [[Stop Hunt]] | [[Confluence Stack]] | [[Kill Zones]] | [[P_115 Master Index]]

## Pre-Trade Checklist (Run Before Every Trade)

| Step | Question | Confirmation Signal | Status |
|---|---|---|---|
| 1 | HTF directional bias confirmed? | Weekly or daily in Phase 3 expansion, or clean HTF structure in intended direction | Pass / Fail |
| 2 | Liquidity pool clearly identified? | Visible SSL cluster (bullish) or BSL cluster (bearish) marked on chart | Pass / Fail |
| 3 | Stop hunt triggered and completed? | Price swept liquidity pool; reversal candle closed back through swept level | Pass / Fail |
| 4 | Phase 3 breakout candle confirmed? | First expansion candle broke Phase 1 compression boundary in HTF direction | Pass / Fail |
| 5 | Entry level defined precisely? | Entry price identified at close of reversal or breakout candle | Pass / Fail |
| 6 | Stop loss placed correctly? | Stop is 1 ATR beyond stop-hunt wick; not at round number; not at obvious cluster | Pass / Fail |
| 7 | Target marked and R:R ≥ 1:2? | At least one BSL/SSL target identified; minimum 1:2 R:R confirmed | Pass / Fail |
| 8 | In kill zone or primary session? | Setup forming during London Open, NY Open, or other high-probability window | Preferred |

> [!danger] No-Trade Rule
> A **FAIL** on any of steps 1–7 is an **automatic no-trade condition**. Do not place the order. A missed trade is infinitely better than a bad trade.

---

## Entry Model — Three Entry Types

> [!success] Entry Type 1 — Aggressive Entry
> **Timing:** Enter on the close of the reversal candle — the candle that closes back through the swept level after the stop hunt. Earliest entry, highest reward potential.
> **Stop:** 1 ATR below the wick (bullish) or above the wick (bearish). Account for wider stop in position sizing.

> [!info] Entry Type 2 — Conservative Entry
> **Timing:** Enter on the first retest of the swept liquidity level after the initial reversal candle. Price pulls back to test the swept level as new support (bullish) or resistance (bearish). Tighter stop placement.
> **Risk:** Higher probability of fill but may miss if price does not retest.

> [!note] Entry Type 3 — Breakout Entry
> **Timing:** Enter on confirmed break of Phase 1 compression zone boundary in Phase 3 expansion direction — after Phase 2 stop hunt and reversal are complete. Latest and most conservative entry, most confirmation, widest stop relative to compression range.
> **Check:** Validate R:R before taking — may be tighter due to compression range width.

---

## Stop Loss Placement Rules

| Type | Placement | When to Use |
|---|---|---|
| **Structural Stop** | Beyond last swing low (bullish) or last swing high (bearish) that defines the structural thesis | Primary placement method |
| **Wick-Based Stop** | 1 ATR beyond lowest point of stop-hunt wick (bullish) or highest point (bearish) | When accounting for secondary sweeps |

**Prohibited Stop Zones:**
- ❌ Round numbers (e.g., 4,000.00) — these are institutional stop-hunt targets themselves
- ❌ Entry candle high/low — inside the noise zone
- ❌ Moving average levels visible on standard charts

> [!warning] Stop Placement Rule
> Your stop must be beyond the point that **invalidates your thesis** — not just below the entry candle. Ask: *"If price reaches this level, is my trade idea still valid?"* If no → that's where your stop belongs.

---

## Profit Target Framework

| Target Level | Definition | Typical R-Multiple | Action |
|---|---|---|---|
| **Target 1** | First untested liquidity pool in trade direction (nearest SSL/BSL — compression zone boundary or prior session extreme) | 1:1 to 1:2 | Exit 50% of position. Move stop to breakeven on remainder. |
| **Target 2** | Prior session or prior day high/low (medium-term liquidity pool) | 1:2 to 1:4 | Exit additional 30–40% of position. Trail stop on remainder. |
| **Target 3** | Weekly or monthly liquidity zone (HTF BSL or SSL pool — highest-value target) | 1:4 to 1:8+ | Exit final position. Evaluate for re-entry on next compression phase. |

> [!warning] Minimum Standard
> The P_115 framework requires a **minimum 1:2 risk-reward ratio** for any trade to be taken. If the distance from entry to stop is greater than half the distance from entry to Target 1 — **do not take the trade.**

---

## Trade Management Rules (6 Non-Negotiable Rules)

1. **Move Stop to Breakeven** immediately after Target 1 is hit. No exceptions.
2. **Scale Out 50% at Target 1.** Locking in profit at T1 is not optional — it is a framework requirement.
3. **Hold Remainder for Target 2/3** with a trailing stop. Trail below each new higher low (bullish) or above each new lower high (bearish).
4. **Never Add to Losing Positions.** Averaging down is prohibited. Exit and re-evaluate.
5. **Exit Full Position on Phase 4 Signals.** Volume divergence, wick formation, or oscillator divergence before T2 → exit immediately.
6. **Maximum Daily Loss Limit.** Three consecutive full stop-outs → stop trading the session. Preserve capital.

---

## Session Kill Zone Reference

| Session | Window (ET) | Typical Liquidity Event | P_115 Focus |
|---|---|---|---|
| Asian Session | 7:00 PM – 2:00 AM | Range building — price establishes Asian high/low; liquidity pools form at range extremes | Mark Asian high and low. Prime stop-hunt targets for London. Observe Phase 1 compression forming. |
| **London Open (Kill Zone)** | **2:00 AM – 5:00 AM** | **First major liquidity hunt — Asian range extremes frequently swept; stop hunts on prior session H/L** | **Highest priority stop-hunt watch window. Look for Phase 2 SSL/BSL sweeps and Phase 3 reversal entry.** |
| **New York Open (Kill Zone)** | **8:30 AM – 11:00 AM** | **Highest volume session — trend establishment or second major stop hunt; economic data releases** | **Primary P_115 trade session. Phase 3 extension from London, or new NY stop hunts.** |
| NY Lunch (No-Trade) | 11:30 AM – 1:30 PM | Liquidity thins — "lunch reversal trap" common; false AM reversal or Phase 1 compression | Reduce size. Watch for false reversal traps. Often Phase 4 distribution of AM trend. **Avoid new entries.** |
| NY Afternoon | 1:30 PM – 4:00 PM | Position adjustments; late-session continuation or reversal | Manage existing positions. Close intraday positions before 3:45 PM ET. |
| NY Close | 3:45 PM – 4:00 PM | Final institutional position adjustment | Exit all intraday positions. Mark closing levels for next session liquidity map. |

---

## Common Mistakes & P_115 Corrections

| Mistake | Why It Happens | P_115 Correction |
|---|---|---|
| Entering before stop hunt completes | Impatience — fear of missing the move | Wait for the reversal candle that closes back through swept level. No reversal candle = no trade. |
| Chasing Phase 3 late | FOMO — seeing a strong trend and entering after 2+ expansion candles closed | Wait for Phase 1 compression to reform. The next cycle will come. |
| Ignoring HTF bias | Taking LTF setups without checking higher-timeframe context | Always validate HTF bias before entry. A perfect LTF setup against HTF bias is a low-probability trade. |
| Stops at round numbers | Round numbers feel logical and "clean" | Round numbers are institutional stop-hunt targets. Place stops 1 ATR beyond structural level. |
| Entering on the stop-hunt candle | Entering on the spike (Phase 2 candle) rather than the confirming reversal | The stop-hunt candle is NOT the entry. The reversal candle that closes back through the level is. |
| Holding through Phase 4 | Greed — hoping for larger move; ignoring volume divergence | Exit 50% at T1. Move stop to BE. Exit remaining at first Phase 4 signal. |
| Overtrading during NY Lunch | Boredom — morning session over; taking low-quality setups | NY Lunch is a no-trade zone. Use time to mark next session liquidity levels and review morning trades. |

---

# SECTION 9 — CONCEPT ATOMIC NOTES

*These are designed to be split into individual files in `06 – Concepts & Definitions/`*

---

## BSL — Buy-Side Liquidity
**Tags:** `#liquidity/bsl`
**Links:** [[SSL – Sell-Side Liquidity]] | [[Stop Hunt]] | [[Confluence Stack]]

Clusters of buy-stop orders and stop-losses on short positions located **ABOVE price** — specifically above swing highs, equal highs, prior session/day/week/month highs, and round numbers.

- Institutional **distribution** target in bearish cycles
- Institutional **measured-move delivery target** in bullish cycles
- The bearish stop-hunt sweeps BSL to load short positions
- The bullish expansion targets BSL as the profit destination

---

## SSL — Sell-Side Liquidity
**Tags:** `#liquidity/ssl`
**Links:** [[BSL – Buy-Side Liquidity]] | [[Stop Hunt]] | [[Confluence Stack]]

Clusters of sell-stop orders and stop-losses on long positions located **BELOW price** — specifically below swing lows, equal lows, prior session/day/week/month lows, and round numbers.

- Institutional **accumulation** target in bullish cycles
- Institutional **measured-move delivery target** in bearish cycles
- The bullish stop-hunt sweeps SSL to load long positions
- The bearish expansion targets SSL as the profit destination

---

## Stop Hunt
**Tags:** `#setup/bullish-stop-hunt` or `#setup/bearish-stop-hunt`
**Links:** [[BSL – Buy-Side Liquidity]] | [[SSL – Sell-Side Liquidity]] | [[Kill Zones]] | [[Absorption]]

A deliberate, engineered price move targeting retail stop-loss orders at predictable levels. Four-step mechanics: Approach → Penetration (Sweep) → Immediate Reversal → Confirmation (Close Back Through Level).

**Confirmed by:** Candle close back through the swept level (body close — not just a wick).
**Entry signal:** Close of the confirmation reversal candle.
**Highest-probability targets:** Equal highs / equal lows.

---

## Absorption
**Tags:** `#phase/liquidity-hunt`
**Links:** [[Stop Hunt]] | [[Wyckoff Model]] | [[Compression Phase]]

The process by which institutions use incoming retail order flow to fill their own large opposing positions at key price levels — silently, without creating visible directional movement.

**Signature:** High volume at a key level without price follow-through in the expected direction.
**Bullish absorption:** Volume spike at lows with no new low formed.
**Bearish absorption:** Volume spike at highs with no new high formed.

---

## Compression Phase (Phase 1)
**Tags:** `#phase/compression`
**Links:** [[Expansion Phase]] | [[Stop Hunt]] | [[Absorption]]

Phase 1 of the P_115 momentum cycle. ATR contracting, volume declining, moving averages flat. Institutions are quietly loading positions. **Do not trade.** Mark SSL/BSL boundaries. Prepare for Phase 2.

---

## Expansion Phase (Phase 3)
**Tags:** `#phase/expansion`
**Links:** [[Compression Phase]] | [[Stop Hunt]] | [[Confluence Stack]]

Phase 3 of the P_115 momentum cycle. Strong momentum candles, expanding ATR, sustained volume increase, decisive structural breaks. The primary P_115 trade entry and profit-generation phase. Entered immediately after Phase 2 stop hunt reversal is confirmed.

---

## Kill Zones
**Tags:** `#session/london` | `#session/ny-open`
**Links:** [[Stop Hunt]] | [[Absorption]] | [[Session Kill Zone Reference]]

Specific high-probability session windows during which liquidity events are most consistently engineered.

| Kill Zone | Time (ET) |
|---|---|
| London Open | 2:00 AM – 5:00 AM |
| New York Open | 8:30 AM – 11:00 AM |
| NY Lunch (No-Trade) | 11:30 AM – 1:30 PM |

---

## Confluence Stack
**Tags:** `#setup/confluence-stack`
**Links:** [[Stop Hunt]] | [[BSL – Buy-Side Liquidity]] | [[SSL – Sell-Side Liquidity]] | [[Expansion Phase]]

The highest-probability P_115 trade condition. Requires **all three** simultaneously:
1. HTF directional bias confirmed (monthly/weekly in Phase 3 or post-Phase 2 stop hunt)
2. LTF stop hunt completed with reversal candle confirmed (15m or 1H)
3. Phase 3 breakout candle forming in HTF direction on above-average volume

---

## Liquidity Void
**Tags:** `#liquidity/void`
**Links:** [[BSL – Buy-Side Liquidity]] | [[SSL – Sell-Side Liquidity]] | [[Expansion Phase]]

A price range where little or no trading volume occurred during prior price delivery. Price tends to move rapidly through liquidity voids during Phase 3 expansion with minimal resistance — no significant resting orders exist to slow the move.

---

## Wyckoff Model (P_115 Adaptation)
**Tags:** `#phase/compression` | `#phase/liquidity-hunt`
**Links:** [[Absorption]] | [[Stop Hunt]] | [[Compression Phase]]

| Wyckoff Term | P_115 Equivalent |
|---|---|
| Preliminary Support (PS) | Initial demand zone — SSL approach begins |
| Selling Climax (SC) | Stop-hunt trigger — SSL sweep with volume spike |
| Automatic Rally (AR) | Reversal candle — Institutional Entry Zone confirmed |
| Secondary Test (ST) | Retest of SSL — compression zone forms |
| Spring | Liquidity Hunt — final SSL sweep before expansion |
| Sign of Strength (SOS) | Phase 3 Expansion — P_115 primary entry confirmed |

---

# SECTION 10 — P_115 QUICK REFERENCE CARD

> **File:** `05 – P_115 Knowledge Base/08 Quick Reference Card.md`
> **Pin this note. Open it every trading session.**

---

## Liquidity Pool Types

| Pool | Location | Institutional Use |
|---|---|---|
| **BSL** | ABOVE price — above swing highs, equal highs, prior H/W/M highs | Distribution target (bearish); Delivery target (bullish) |
| **SSL** | BELOW price — below swing lows, equal lows, prior H/W/M lows | Accumulation target (bullish); Delivery target (bearish) |
| **Liquidity Void** | Price range with no prior trading volume | Rapid price delivery zone — minimal resistance |

---

## Stop Hunt Rules (3 Core Rules)

> [!warning] Rule 1
> **Never enter IN the direction of the stop-hunt move.** The sweep candle is not the entry. The reversal candle that follows is the entry.

> [!warning] Rule 2
> **A stop hunt is confirmed only when price closes BACK through the swept level.** Wicks alone are not confirmation — the candle body close is required.

> [!warning] Rule 3
> **Equal highs and equal lows are the highest-probability targets.** Two touches = institutional magnet. Three touches = imminent sweep. Mark them at session open.

---

## Momentum Phase Quick ID

| Phase | Name | Quick Identifier | Action |
|---|---|---|---|
| 1 | Compression | ATR contracting + volume drying + flat MAs | Watch. Map levels. No trade. |
| 2 | Liquidity Hunt | Fast spike through SSL/BSL + volume spike + immediate reversal candle | Confirm reversal. Prepare entry. |
| 3 | Expansion | Strong momentum candles + ATR expanding + volume building + structure break | Enter trade. Set stop. Target liquidity pool. |
| 4 | Distribution | Long wicks + narrow bodies + volume divergence + oscillator divergence | Exit all. Do not hold. Await next Phase 1. |

---

## Full Cycle Checklist

| Step | Bullish Cycle | Bearish Cycle |
|---|---|---|
| 1 | HTF bullish bias confirmed (daily/weekly) | HTF bearish bias confirmed (daily/weekly) |
| 2 | SSL cluster (equal lows) identified below price | BSL cluster (equal highs) identified above price |
| 3 | Phase 1 compression observed — ATR/volume contracting | Phase 1 compression observed — ATR/volume contracting |
| 4 | SSL sweep wick forms — stops triggered below equal lows | BSL sweep wick forms — stops triggered above equal highs |
| 5 | Bullish reversal candle closes back above swept level | Bearish reversal candle closes back below swept level |
| 6 | Enter long — stop 1 ATR below wick — target BSL above | Enter short — stop 1 ATR above wick — target SSL below |
| 7 | Exit 50% at Target 1 — move stop to breakeven | Exit 50% at Target 1 — move stop to breakeven |
| 8 | Trail stop. Exit remaining at Phase 4 signal or Target 2/3 | Trail stop. Exit remaining at Phase 4 signal or Target 2/3 |

---

## P_115 Minimum Trade Criteria (All Must Be Met)

- [ ] HTF directional bias is confirmed and aligns with trade direction
- [ ] A liquidity pool (SSL or BSL) has been clearly identified and marked
- [ ] The stop hunt has triggered AND a reversal candle has confirmed completion
- [ ] Phase 3 expansion candle has formed (or is forming) in the HTF direction
- [ ] Entry, stop, and at least one target are defined before order placement
- [ ] Minimum risk-reward ratio of 1:2 is confirmed
- [ ] Maximum daily loss limit not reached (3 consecutive full stop-outs = done for session)

---

## Session Kill Zones (Quick Reference)

| Kill Zone | Time (ET) | Primary Liquidity Event |
|---|---|---|
| London Open ⭐ | 2:00 AM – 5:00 AM | Asian range sweep — highest probability stop hunt window |
| New York Open ⭐ | 8:30 AM – 11:00 AM | Trend establishment or second major stop hunt — primary trade session |
| NY Lunch 🚫 | 11:30 AM – 1:30 PM | False AM trend reversal trap — **no-trade zone** |
| NY Afternoon | 1:30 PM – 4:00 PM | Continuation or final distribution — manage existing positions only |

---

# APPENDIX — GLOSSARY

> **File:** `09 – Resources/Glossary.md`

| Term | Definition |
|---|---|
| **ATR** | Average True Range — volatility indicator measuring average price range over 14 candles. Used to calibrate stop distances and identify Phase 1 compression vs. Phase 3 expansion. |
| **Absorption** | Institutional use of incoming retail order flow to fill large opposing positions at key levels — without creating visible directional movement. Signature: high volume at key level with no follow-through. |
| **BSL (Buy-Side Liquidity)** | Clusters of buy-stop orders and short stop-losses located ABOVE price. Institutional distribution target (bearish cycle) and measured-move delivery target (bullish cycle). |
| **Compression Phase** | Phase 1 of the P_115 momentum cycle. Contracting ATR, declining volume, flat MAs. Institutional loading period. No trades taken during this phase. |
| **Confluence Stack** | Highest-probability P_115 setup: (1) HTF bias confirmed + (2) LTF stop hunt completed + (3) Phase 3 breakout candle forming. All three required simultaneously. |
| **Distribution Phase** | Phase 4 of the P_115 momentum cycle. Volume divergence, wick formation, oscillator divergence. Institutions exiting into retail momentum. Signal to exit all remaining positions. |
| **Equal Highs / Equal Lows** | Two or more candlestick highs or lows at approximately the same price level. Highest-probability stop-hunt targets — deliberate clustering of retail stop orders that institutions will sweep before major directional moves. |
| **Expansion Phase** | Phase 3 of the P_115 momentum cycle. Strong momentum candles, expanding ATR, sustained volume increase, decisive structure breaks. Primary trade entry and profit-generation phase. |
| **HTF / LTF** | Higher Timeframe (Monthly, Weekly, Daily) / Lower Timeframe (4H, 1H, 15m, 5m). HTF provides directional bias; LTF provides entry precision. |
| **Kill Zone** | Specific high-probability session windows: London Open (2–5 AM ET) and New York Open (8:30–11 AM ET). Liquidity events most consistently engineered during these windows. |
| **Liquidity Pool** | Any concentration of resting orders (stops, limit orders, pending orders) clustered near a specific price level. BSL pools above price; SSL pools below price. Primary targets of institutional price delivery. |
| **Liquidity Void** | Price range with no significant prior trading volume. Price moves rapidly through voids with minimal resistance during Phase 3 expansion. |
| **Market Structure** | Sequential pattern of swing highs and swing lows defining directional bias. Bullish = higher highs + higher lows. Bearish = lower highs + lower lows. |
| **SSL (Sell-Side Liquidity)** | Clusters of sell-stop orders and long stop-losses located BELOW price. Institutional accumulation target (bullish cycle) and measured-move delivery target (bearish cycle). |
| **Stop Hunt** | Deliberate, engineered price move targeting retail stop-loss orders at predictable levels. Mechanics: Approach → Sweep → Institutional Reversal → Confirmation (close back through level). |
| **VWAP** | Volume-Weighted Average Price — dynamic institutional reference level; frequently targeted for stop hunts during kill zones. |

---

*P_115 Trading Brain — Integrated Obsidian Implementation*
*Author: Anthony | P_115 Framework | v1.0 | May 2026*
*Confidential — Internal Use Only*
