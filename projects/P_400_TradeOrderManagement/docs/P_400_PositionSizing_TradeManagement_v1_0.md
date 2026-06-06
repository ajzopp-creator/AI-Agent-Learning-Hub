# P_400 — Trade Management: Position Sizing & Target Framework
**Project ID:** P_400
**Version:** 1.0
**Created:** 2026-05-31
**Maintained By:** Anthony Zoppi
**Status:** Active — Phase 1 Foundation
**Save Path:** C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeManagementSystem\docs\P_400_PositionSizing_TradeManagement_v1_0.md

---

## PURPOSE

P_400 is the cross-system Trade Management layer for the AI-Agent-Learning-Hub trading system.
It governs position sizing, target setting, stop placement, and options translation across all
active strategies: P_115, P_116, P_117, and P_118.

This document is Phase 1. It formalizes the Three-Gate sizing system and introduces the
Confluence-Based Target Framework — the methodology for setting TP levels when a stock is
at or near all-time/multi-year highs with no visible overhead resistance.

**Applies to:** P_115 · P_116 · P_117 · P_118
**Source documents consolidated:**
- POSITION_SIZING_THREE_GATE_REFERENCE.md
- OPTIONS_RISK_METHODOLOGY.md
- ATR target logic (developed 2026-05-31, MNST case study)

---

## SECTION 1 — THREE-GATE POSITION SIZING

Every position must clear three gates. The SMALLEST gate result is the final position size.
No exceptions without explicit user override and documented justification.

### Gate 1: Risk-Based

```
Risk Capital   = Account Balance × Risk% (from P_010 risk_mode)
Stop Distance  = Entry Price − Stop Level
Ideal Shares   = Risk Capital ÷ Stop Distance
```

### Gate 2: Cash Availability

```
Max Shares (Cash) = User-Provided Cash Balance ÷ Entry Price
```

Cash Balance = per-trade buying power provided by user each session.
Do NOT subtract between trades. Do NOT equate to account balance.

### Gate 3: Concentration Cap

```
Max Shares (Concentration) = Max Position ($1,640.60) ÷ Entry Price
Options: applies to PREMIUM PAID, not notional exposure
```

### Risk Mode Adjustments (from P_010_RiskConfig.json — re-read before every STEP 2)

| risk_mode | Risk/Trade | Max Position | Notes                        |
|-----------|------------|--------------|------------------------------|
| OFF       | $246.09    | $820.30      | 50% reduction                |
| HALF      | $369.14    | $1,230.45    | 25% reduction                |
| FULL      | $492.18    | $1,640.60    | Base sizing                  |
| HOT       | Tiered     | Up to $1,640 | avg_posture > 1.08           |

**Rule:** risk_mode field in JSON is always authoritative. Re-read before every STEP 2.

### Complete Stock Sizing Example

```
Account Balance: $32,812  |  risk_mode: FULL  |  Risk Capital: $492.18
Entry: $89.95  |  Stop: $87.96  |  Stop Distance: $1.99  |  Cash: $3,294

Gate 1 (Risk):          $492.18 ÷ $1.99  = 247 shares
Gate 2 (Cash):          $3,294 ÷ $89.95  =  36 shares
Gate 3 (Concentration): $1,640.60 ÷ $89.95 = 18 shares  ← BINDS

Final Position: 18 shares  |  Capital Deployed: $1,619.10
```

### Complete Options Sizing Example

```
Premium: $2.475/share  |  Contract cost: $247.50
Gate 1: $492.18 ÷ $247.50 = 1.99 → 1 contract
Gate 2: $3,294 ÷ $247.50  = 13 contracts
Gate 3: $1,640.60 ÷ $247.50 = 6 contracts

Final: 1 contract (Gate 1 binds — risk-optimal)
```

---

## SECTION 2 — CONFLUENCE-BASED TARGET FRAMEWORK

### Problem Statement

Standard target-setting uses prior resistance levels (swing highs, consolidation zones).
When a stock is at all-time highs or multi-year highs with no overhead resistance visible,
that method fails. A systematic alternative is required.

**Trigger condition:** No visible resistance within 10–15% above entry on the daily chart.

### The Four Target Inputs

Evaluate all four inputs. The target with the highest confluence across inputs becomes T1.
A second-level target with moderate confluence becomes T2.

#### Input 1 — ATR Extension

Projects near-term price extension based on recent volatility.

```
T1 candidate = Entry + (1.5 × ATR)
T2 candidate = Entry + (3.0 × ATR)
T3 candidate = Entry + (5.0 × ATR)   [extended run / trail only]
```

ATR is the anchor. Every target must be validated against at least one other input before use.
ATR alone is insufficient — it is the starting point, not the decision.

#### Input 2 — Round Number / Psychological Level

Markets cluster institutional orders at round numbers. After calculating ATR extensions,
identify the nearest clean round number at or above the ATR target.

```
Scan levels: $X0.00, $X5.00, $X2.50 (in descending order of significance)
```

**Confluence signal:** ATR target lands within $1.00–$2.00 of a round number → elevated
probability target. Use the round number as the stated target.

#### Input 3 — Measured Move (Base Depth Projection)

Requires a clearly identifiable consolidation base on the daily chart.
Do not estimate or approximate — base must be visually confirmed before using this input.

```
Base Depth   = Breakout Point − Base Low
Measured Move Target = Entry + Base Depth
```

This produces the highest-confidence stretch target when the base is clean.
Use as T2 or T3 only. Do not use as T1 unless ATR and round number also converge at same level.

#### Input 4 — Prior Structure (When Available)

If any prior swing high, gap fill level, or consolidation zone exists within the target range,
treat it as a resistance cluster. Downgrade targets that sit directly below prior structure.
Upgrade targets where prior structure has been cleared and price is extended above it.

### Confluence Decision Engine

Confluence — not ATR alone — governs target selection.

```
STRONG CONFLUENCE (use as T1):
  ATR extension + Round Number within $1–2  →  High probability target
  Example: ATR T1 = $92.94, Round Number = $95.00 → use $95.00 as T1

MODERATE CONFLUENCE (use as T2):
  Measured Move + Round Number alignment
  Example: Measured Move = $106, Round Number = $105 → use $105 as T2

WEAK / SINGLE INPUT (do not use alone):
  ATR only, no round number, no base depth → insufficient
  Round number only, no ATR support → insufficient
```

### Target Hierarchy Rules

1. T1 must produce R:R ≥ 2:1 from entry. If T1 fails this test, there is no valid setup.
2. T2 is the primary execution target when T1 R:R < 2:1.
3. After price reaches T1, move stop to breakeven and trail for T2.
4. Measured move targets are valid only when base is visually confirmed on chart.
5. Never fabricate a target to satisfy the 2:1 requirement — if no valid target exists, log PASS.

### MNST Case Study (2026-05-31)

```
Ticker: MNST  |  Entry: $89.95  |  ATR: $1.99  |  3-year high — no overhead resistance

Input 1 (ATR):
  T1 = $89.95 + (1.5 × $1.99) = $92.94
  T2 = $89.95 + (3.0 × $1.99) = $95.92

Input 2 (Round Numbers):
  $92.50 — minor
  $95.00 — major  ← ATR T2 ($95.92) within $0.92 → CONFLUENCE
  $100.00 — major stretch

Input 3 (Measured Move):
  Base low ~$72–74, depth ~$16
  Measured move = $89.95 + $16 = ~$106  ← valid only if base confirmed on chart
  $105.00 round number nearby → moderate confluence at T3

Input 4 (Prior Structure): None within target range — price at 3-year high

RESULT:
  T1 = $95.00  (ATR T2 + round number confluence)
  T2 = $100.00 (round number stretch, no ATR anchor — single input, use as secondary)
  T3 = $105.00 (measured move + round number — requires base confirmation)

  Stop = $89.95 − $1.99 = $87.96
  R:R to T1 = ($95.00 − $89.95) ÷ ($89.95 − $87.96) = $5.05 ÷ $1.99 = 2.54:1  ✅
```

### Stop Placement

Primary: 1× ATR below entry (standard)
Secondary: Below nearest technical level (support, base low, handle low)
Use whichever is more conservative (wider stop) unless pattern structure dictates otherwise.

```
ATR Stop  = Entry − (1 × ATR)
Chart Stop = Entry − distance to nearest support
Final Stop = MAX(ATR Stop distance, Chart Stop distance) from entry
```

---

## SECTION 3 — INTEGRATION WITH P_115 BUYING LOGIC

The Confluence-Based Target Framework is now part of P_115 STEP 2 logic under the
following condition:

**Trigger:** No visible overhead resistance within 10–15% of entry on daily chart
(typically occurs when stock is at 52-week high, multi-year high, or all-time high)

**STEP 2 workflow change:**

```
STANDARD (resistance visible):
  T1 = prior swing high or resistance level
  T2 = next resistance level above T1

PRICE DISCOVERY ZONE (no resistance):
  STEP 1: Calculate ATR extensions (1.5×, 3.0×)
  STEP 2: Identify round numbers at or near each ATR level
  STEP 3: Identify base depth if clean base exists on chart (confirm visually)
  STEP 4: Select T1 = highest confluence target that produces R:R ≥ 2:1
  STEP 5: Select T2 = next confluence level above T1
  STEP 6: Note "Price Discovery Zone — ATR/Confluence targets" in Comments
```

This logic applies equally to P_116, P_117, and P_118 when the same condition is met.

---

## SECTION 4 — OPTIONS TRANSLATION

### Viability Gates (ALL must pass)

1. Bid-ask spread ≤ 10% of mid price
2. Open interest ≥ 150 contracts
3. Option R:R ≥ Stock R:R

Spread % = (Ask − Bid) ÷ Mid × 100

If any gate fails → fallback to stock. Document which gate failed in SimulationNotes.

### Delta Translation (Primary Method)

```
Option Entry  = market mid price
Option Stop   = Entry Premium + (Delta × Stock Stop Movement)   [movement is negative]
Option Target = Entry Premium + (Delta × Stock Target Movement)
Risk/Contract = (Entry Premium − Stop Premium) × 100
```

### Options Position Sizing (Three Gates)

Gate 1: Risk Capital ÷ Risk/Contract
Gate 2: Cash Balance ÷ (Entry Premium × 100)
Gate 3: Max Position ($1,640.60) ÷ (Entry Premium × 100)   ← premium paid, not notional

Smallest gate binds.

### Options Display Format (Required on Every STEP 2)

```
Entry:       Stock $XX.XX  →  Option $X.XX
Take Profit: Stock $XX.XX  →  Option ~$X.XX  (+XX% gain)
Stop Loss:   Stock $XX.XX  →  Option ~$X.XX  (-XX% loss)
```

### Override Protocol

When gate math produces 0 contracts but setup has strong confluence:
- Override to 1 contract requires explicit user instruction
- Document in SimulationNotes: method, calculated risk, budget, overshoot %, justification

---

## SECTION 5 — OUTPUT REQUIREMENTS

All STEP 2 outputs must include:

- [ ] All three gates calculated and shown
- [ ] Binding gate identified
- [ ] Final share/contract count stated
- [ ] Capital deployed calculated
- [ ] T1 and T2 with target method noted (resistance / ATR+confluence / measured move)
- [ ] Stop level stated
- [ ] R:R to T1 calculated and validated ≥ 2:1
- [ ] Options: both stock price AND option price shown at each level
- [ ] Price Discovery Zone notation when applicable
- [ ] Comments field updated with sizing method and target basis

---

## SECTION 6 — APPLIES-TO MATRIX

| Strategy | Sizing Method         | Target Method                     | Stop Method          |
|----------|-----------------------|-----------------------------------|----------------------|
| P_115    | Three-Gate            | Resistance / Confluence-ATR       | Chart support / ATR  |
| P_116    | Three-Gate (premium)  | Bounce targets / prior resistance | Bounce failure level |
| P_117    | Three-Gate            | Source-provided / Confluence-ATR  | Chart / ATR          |
| P_118    | Three-Gate            | Pattern target / Confluence-ATR   | Handle low / ATR     |

---

## SECTION 7 — DOCUMENT REFERENCES

| Document                                  | Location         | Purpose                          |
|-------------------------------------------|------------------|----------------------------------|
| P_000_Account_Parameters_Current.md       | Local config     | Account balance, risk parameters |
| P_010_RiskConfig.json                     | Local config     | risk_mode (authoritative)        |
| POSITION_SIZING_THREE_GATE_REFERENCE.md   | Project Knowledge| Source: sizing gates             |
| OPTIONS_RISK_METHODOLOGY.md               | Project Knowledge| Source: options translation      |
| P_115_BuyTheDip_MasterDoc_v1_0.md        | Project Knowledge| P_115 strategy integration       |
| P_118_EddieZ_Guide.md                     | Project Knowledge| P_118 strategy integration       |

---

## SECTION 8 — CHANGE LOG

| Version | Date       | Author         | Change                                           |
|---------|------------|----------------|--------------------------------------------------|
| 1.0     | 2026-05-31 | Anthony Zoppi  | Initial document — Three-Gate + Confluence-ATR   |
|         |            |                | target framework. MNST case study validated.     |
|         |            |                | Consolidated from THREE_GATE_REFERENCE and       |
|         |            |                | OPTIONS_RISK_METHODOLOGY source documents.       |

---

## SECTION 9 — P_400 ROADMAP (FUTURE PHASES)

This document is Phase 1. Planned future phases:

| Phase | Scope                                                           | Target     |
|-------|-----------------------------------------------------------------|------------|
| 1     | Position sizing + target framework (THIS DOCUMENT)             | 2026-05-31 |
| 2     | Trade lifecycle tracking (open → partial close → exit)         | Q3 2026    |
| 3     | Position adjustment rules (add-to, reduce, trail stop logic)   | Q3 2026    |
| 4     | Cross-strategy exposure management (total portfolio view)      | Q4 2026    |
| 5     | Integration with P_020 performance analytics                   | Q4 2026    |

---

**Document Classification:** Internal
**Document Owner:** Anthony Zoppi
**System Version:** V110.2
**Next Review:** June 2026

---
*END OF DOCUMENT*
