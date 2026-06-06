# Price Action Edge — Summary for Trading System Enhancement
**Source:** "The Price Action Edge" by Atanas Matov (Colibri Trader)
**Purpose:** Reference for future P_115/P_118 pattern enhancements
**Created:** 2026-02-25 | **Updated:** 2026-04-12

---

## Core Philosophy
- Price action trading uses price ONLY as the indicator — no lagging indicators
- Tools used: Support/Resistance, Candlesticks, Fibonacci, Trendlines
- Clean charts preferred over indicator-cluttered charts
- Higher timeframe = more accurate signal (Daily > 4H > 1H)
- Best timeframe combination: **Daily for signal, 4H for entry refinement**
- Markets trade in ranges ~80% of the time

---

## Money Management Rules
- Never risk more than **2% per trade** (author uses 0.5%)
- Tight stop-loss is a feature, not a bug — enables high R:R ratios
- Two traders using the same system with different money management = drastically different results
- Being wrong 70% of the time is acceptable if the 30% winners are home runs
- Cut losers fast, stay in winners longer

---

## The 8 Price Action Patterns (Enhancement Candidates)

### Pattern 1 — BOSS (Bullish On Strong Support)
- Bullish engulfing candle at a **major support/demand zone**
- ANY bullish candlestick pattern can trigger (not just engulfing)
- Price should test the support level precisely or slightly below it
- **Signal:** Strong bullish reversal

### Pattern 2 — BEAR (Bearish Engulfing on Aged Resistance)
- Bearish engulfing at a **strong resistance/supply zone**
- Red candle(s) must completely encapsulate the previous green body
- Can be multi-candle engulfing
- **Signal:** Strong bearish reversal / trend change

### Pattern 3 — IBWT (Inside Bar Within a Trend)
- Inside bar forming **within an established trend** (continuation)
- Smaller red candle close very near the low of the prior green candle
- Enables **very tight stop-loss** — high R:R ratios (example showed 1:11.38)
- **Best pattern for R:R returns**

### Pattern 4 — SUP (Supply Zone Pin Bar)
- Pin bar rejecting a **major or minor supply zone/resistance level**
- Bearish continuation pattern
- Requires: (1) Supply zone present, (2) Price action rejection candle
- **Signal:** Bearish continuation, need to act fast (next candle often large bearish)

### Pattern 5 — RRR (Random Resistance Rejection)
- Pin bar rejection at **resistance-turned-support** level
- Can appear at any point — confluence of factors matters
- Higher timeframe = more accurate
- **Do NOT confuse with breakouts**

### Pattern 6 — DZC (Demand Zone Candlestick)
- Similar to BOSS but on **minor demand zones** (not major)
- Price "trapped" in demand zone — wait for candlestick confirmation
- Tight stop-loss possible
- **Powerful continuation technique**

### Pattern 7 — TVR (Theory Versus Reality)
- Contracting triangles that **break the wrong direction**
- Most traders expect upside breakout — price goes opposite
- Inside bar often precedes the decline
- **Trap pattern — use as SHORT signal when near resistance**

### Pattern 8 — TVR2 (Theory Versus Reality 2)
- Tight range with expected breakout — **retail traders get trapped**
- 3 levels where novices go long (mid-range, near resistance, at breakout)
- Closer to resistance = higher stop needed = higher chance of getting burned
- **Counter-trade:** The closer to resistance, the more ready to SHORT

---

## Key Confluence Factors (Use Multiple for Higher Probability)
1. Support/Resistance level present
2. Candlestick confirmation at the level
3. Trend direction alignment
4. Timeframe confluence (Daily + 4H)
5. Supply/Demand zones (stronger than simple S/R lines)

---

## Trend Trading Rules
1. Identify established major trend first
2. Wait for correction to prior support/resistance level
3. Get price action signal confirmation
4. Trade in direction of trend — "The trend is your friend"

---

## Instruments Applicable
- Major/Minor FOREX pairs
- US/EU Indices (Dow Jones, DAX, etc.)
- Energies (Crude Oil, Natural Gas)
- Commodities (Gold)
- Stocks (NYSE listed — pattern works on all instruments)

---

## Psychology Notes (Relevant to Discipline)
- Biggest enemy is the trader himself — fear, greed, emotions
- Wait patiently for best setups — opportunities always return
- Stick to one strategy through "the Dip" — jumping strategies = failure
- Losing streaks are normal; inability to handle them is the real problem
- Rules + discipline > strategy sophistication

---

## Implementation Status in P_115 ThinkScript (v9.4)

| Pattern Code | Pattern | Status | Notes |
|---|---|---|---|
| PA1 | BOSS | IMPLEMENTED | Bullish engulfing/piercing at 44-day low support |
| PA2 | Pin Bar | IMPLEMENTED | 60%+ lower wick ratio, <30% upper wick, at support |
| PA3 | Inside Bar | IMPLEMENTED | high < high[1] AND low > low[1] at support |
| PA4 | DZC | PLANNED | Minor demand zone candlestick — next to add |
| PA5 | RRR | PLANNED | Resistance-turned-support pin bar rejection |
| PA6 | Morning Star | PLANNED | Multi-candle bullish reversal — first 3-candle PA code |

---

## PA6 — Morning Star (Multi-Candle Bullish Reversal)

**Added:** 4/12/2026 | **PA Code:** PA6 | **Type:** Multi-Candle (3-Bar Pattern)

### Why It Fits P_115
The Morning Star is a natural P_115 convergence signal. P_115 already hunts oversold stocks pulling back to support showing buyer re-entry. A Morning Star IS the visual confirmation that the bounce has begun. When the scan surfaces a ticker AND that ticker prints a Morning Star at the 44-day low support zone, two independent systems are pointing at the same entry simultaneously — the highest-conviction P_115 setup possible.

### Three-Candle Structure

| Candle | Requirement | Role |
|--------|-------------|------|
| Candle 1 | Strong bearish body > 0.6x ATR | Downtrend continuation — sellers in control |
| Candle 2 | Small body < 0.3x C1 body (any color or doji) | Indecision — selling pressure slowing |
| Candle 3 | Bullish, closes above midpoint of C1 body | Buyer takeover confirmed |

### Context Requirements (P_115 Application)
- Clear downtrend preceding the pattern (not sideways/choppy markets)
- Price within 2% of 44-day low (nearSupport zone active)
- RSI oversold or positive divergence strengthens the signal
- Rising volume on Candle 3 = institutional participation (upgrade to T3)

### Scoring Integration
```
CandleTier = T2   (pattern present, no volume surge on C3)
CandleTier = T3   (pattern present + C3 volume > 125% of 20-day avg)
SetupScore: +1 for CandleTier >= 2 (existing rule — no new rule needed)
HybridTier: Indirect benefit via CandleTier elevation
FundamentalsTier: No impact (purely technical pattern)
```

### Entry, Stop, and Target

| Parameter | Value |
|-----------|-------|
| Entry (standard) | Close of Candle 3 |
| Entry (best R:R) | Pullback into Candle 3 body after close |
| Entry (60-min confirm) | Mini cup-and-handle forming after C3 prints |
| Stop (tight) | Below Candle 2 low — ideal at major support |
| Stop (standard) | Below Candle 3 low — most common |
| Stop (wide) | Below pattern low — for volatile/wide-range candles |
| Minimum R:R | 2:1 required; trail via moving average if new uptrend develops |

### Log Entry Format (27-Column Schema)
```
Comments:         PA6 – Morning Star at 44-day low. C3 closed above C1 midpoint. Vol [surge/normal].
SimulationNotes:  Morning Star confirmed at [support level] — [date]
CandleTier:       [2 or 3 depending on volume]
SLLevel:          Below C2 low [tight] or C3 low [standard]
```

### ThinkScript Detection Logic (Future — implement after PA4 and PA5)
```thinkscript
# Morning Star Pattern Detection
def c1_bearish  = close[2] < open[2] and (open[2] - close[2]) > 0.6 * ATR(14)[2];
def c2_small    = AbsValue(close[1] - open[1]) < 0.3 * AbsValue(open[2] - close[2]);
def c1_midpoint = close[2] + (open[2] - close[2]) / 2;
def c3_bullish  = close > open and close > c1_midpoint;
def nearSupport = close <= Lowest(low, 44)[1] * 1.02;
def morningStar = c1_bearish and c2_small and c3_bullish and nearSupport;
def volSurge    = volume > Average(volume, 20) * 1.25;
# CandleTier result: T3 if morningStar AND volSurge; T2 if morningStar only
```

### PA Code Series Architecture

| Range | Type | Patterns |
|-------|------|----------|
| PA1–PA3 | Single-candle BULLISH (live) | BOSS, Pin Bar, Inside Bar |
| PA4–PA5 | Single-candle expansion (planned) | DZC, RRR |
| PA6 | Multi-candle BULLISH (planned) | Morning Star |
| PA7 | Multi-candle BEARISH (future) | Evening Star |
| PA8 | Multi-candle continuation (future) | Three White Soldiers |

---

## CandleTier Boost Logic (Current)
```
Tier 3: PA Pattern + volume surge + STR <= -1 (bounce zone)
Tier 2: PA Pattern alone (no volume/STR confirmation)
Tier 1: Candle pattern only (no PA pattern)
Tier 0: No pattern
```

## Support Zone Definition
- Uses **44-day low** as support reference
- Default threshold: **2% within 44-day low** triggers nearSupport
- Adjustable via input parameter (tighter = 1%, looser = 3-5%)

---

## Patterns Ranked by P_115/P_118 Relevance

| Pattern | PA Code | Relevance | Status |
|---------|---------|-----------|--------|
| BOSS | PA1 | High — core bounce confirmation at major support | Live |
| Pin Bar | PA2 | High — rejection candle at support, tight stop | Live |
| Inside Bar | PA3 | High — continuation/consolidation at support | Live |
| DZC | PA4 | High — next to implement for minor zone entries | Planned Q3 |
| RRR | PA5 | Medium — resistance-turned-support plays | Planned Q3 |
| Morning Star | PA6 | High — first multi-candle code; P_115 convergence signal | Planned Q3 |
| BEAR / TVR / TVR2 | Future | Short-side and trap avoidance | Post-2026 |

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.1 | 4/12/2026 | Added PA6 Morning Star section — first multi-candle PA code; ThinkScript logic, P_115 integration, PA series architecture table |
| 1.0 | 2/25/2026 | Initial document created from The Price Action Edge (Colibri Trader) |

---

*PDF source can be removed from project — all actionable content captured above*
