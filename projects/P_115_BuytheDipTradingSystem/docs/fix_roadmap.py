import re

roadmap_path = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\docs\FEATURES_ROADMAP_2026.md'
pa_path = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\docs\Price_Action_Edge_Summary.md'

# ── Read current roadmap ──────────────────────────────────────────────────────
with open(roadmap_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ── STEP 1: Remove the orphan Morning Star block (appended at bottom after
#            Quarterly Review and before Version History) ─────────────────────
#  The block starts with a lone "---\n\n### Feature 8: Morning Star" and ends
#  just before "## Version History"
pattern = r'\n---\n\n### Feature 8: Morning Star Pattern — PA6 Integration.*?(?=\n## Version History)'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# ── STEP 2: Remove duplicate Feature 9 blocks (keep only the last/fullest one)
# There are 3 copies; keep the third (most complete) and remove first two ─────
feature9_block = r'### Feature 9: Schwab API Auto-Log \(PRIORITY 2 - Q4\).*?---\n'
matches = list(re.finditer(feature9_block, content, flags=re.DOTALL))
if len(matches) >= 3:
    # Remove first two matches (keep last)
    for m in reversed(matches[:-1]):
        content = content[:m.start()] + content[m.end():]

# ── STEP 3: Fix duplicate v1.2 — rename April 12 entry to v1.3 ───────────────
content = content.replace(
    '### v1.2 - April 12, 2026\n- Added Feature 8: Morning Star Pattern PA6 Integration',
    '### v1.3 - April 12, 2026\n- Added Feature 8 (Q3): Morning Star Pattern PA6 Integration'
)

# ── STEP 4: Insert Morning Star as Feature 5 in Q3 section ───────────────────
#  Insert after the Z-Score Feature 4 block (before "## Q4 2026")
morning_star_block = '''
---

### Feature 5: Morning Star Pattern — PA6 Integration (PRIORITY 5)

**Status:** Proposed Q3 2026 — PA Pattern Code Expansion Series

**Rationale:**
- First multi-candle PA code — extends pattern library beyond single-candle reversals
- Natural P_115 convergence signal: oversold + support + three-candle buyer confirmation = highest-probability bounce setup
- Visible without indicators — pure price action, no data dependency
- Directly boosts CandleTier and SetupScore when confirmed at 44-day low support zone
- Strongest P_115 signal when Morning Star appears ON the day the scan surfaces the ticker

**PA Code:** PA6 = Morning Star (Multi-Candle Bullish Reversal)

**What Is It:**
The Morning Star is a three-candle bullish reversal that signals a shift from downtrend to uptrend:
- Candle 1: Strong bearish candle — sellers in control, continues the downtrend
- Candle 2: Small body (bullish, bearish, or doji) — indecision; selling pressure slowing
- Candle 3: Strong bullish candle — closes above the midpoint of Candle 1 body; buyers in control

**Scoring Impact:**
- CandleTier: T2 minimum on pattern alone; T3 with volume surge on Candle 3 (>125% of 20-day avg)
- SetupScore: +1 for CandleTier >= 2 (existing rule — no schema change required)
- FundamentalsTier: No impact (purely technical pattern)
- HybridTier: Benefits indirectly via CandleTier elevation

**Detection Criteria (ThinkScript — future automation):**
```
Candle 1: bearish body > 0.6x daily ATR
Candle 2: body < 0.3x Candle 1 body (indecision)
Candle 3: bullish, closes above midpoint of Candle 1 body
           + price within 2% of 44-day low (nearSupport zone)
Optional boost: Candle 3 volume > 125% of 20-day avg volume
```

**Workflow Integration:**

STEP 1 — Detection:
- When Morning Star identified on chart: CandleTier = T2 min (T3 if C3 volume surge)
- Log PA6 in Comments: "PA6 – Morning Star at 44-day low. C3 closed above C1 midpoint. Vol [surge/normal]"
- SimulationNotes: "Morning Star at [support level]"

STEP 2 — Position Sizing:
- Stop placed below Candle 2 low (tight) OR Candle 3 low (standard) — document in SLLevel
- No sizing bonus beyond standard three-gate system

**Entry Method Alignment with P_115:**
- Close of C3 = standard close-of-signal-day entry
- 60-min mini-handle forming after C3 = highest confirmation (synergy with Feature 2)
- Pullback into C3 body after close = best R:R entry

**Stop-Loss Options:**
- Below Candle 2 low: tightest (ideal at major support)
- Below Candle 3 low: standard (most common)
- Below pattern low: widest (volatile or wide-range candles)

**Relationship to Existing PA Codes:**
- PA1–PA5: Single-candle patterns
- PA6+: Multi-candle patterns (Morning Star opens new sub-series)
- Future: PA7 = Evening Star (bearish mirror), PA8 = Three White Soldiers

**Prerequisites:**
- PA4 (DZC) and PA5 (RRR) implemented first — sequential PA code build
- 5+ Morning Star setups documented manually before ThinkScript automation
- No 27-column schema changes required (Comments field absorbs PA6)

**Priority:** Q3 2026 — after PA4/PA5; no dependency on validation phase completion

**Success Metrics:**
- PA6 signals achieve R:R >= 2:1 baseline
- T3 CandleTier (volume surge C3) shows higher win rate than T2 alone
- ThinkScript detection fires correctly on known historical examples

'''

insert_marker = '\n## Q4 2026: Automation & Scale (FUTURE)'
if insert_marker in content:
    content = content.replace(insert_marker, morning_star_block + insert_marker)
    print('Morning Star block inserted in Q3 section.')
else:
    print('WARNING: Q4 marker not found — Morning Star block not inserted.')

# ── STEP 5: Write updated roadmap ─────────────────────────────────────────────
with open(roadmap_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'FEATURES_ROADMAP_2026.md updated. Chars: {len(content)}')

# ── STEP 6: Write Price_Action_Edge_Summary.md ────────────────────────────────
pa_content = '''# Price Action Edge — Summary for Trading System Enhancement
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
- Enables **very tight stop-loss** → high R:R ratios (example showed 1:11.38)
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
- Price "trapped" in demand zone → wait for candlestick confirmation
- Tight stop-loss possible
- **Powerful continuation technique**

### Pattern 7 — TVR (Theory Versus Reality)
- Contracting triangles that **break the wrong direction**
- Most traders expect upside breakout → price goes opposite
- Inside bar often precedes the decline
- **Trap pattern — use as SHORT signal when near resistance**

### Pattern 8 — TVR2 (Theory Versus Reality 2)
- Tight range with expected breakout → **retail traders get trapped**
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
| PA1 | BOSS | ✅ IMPLEMENTED | Bullish engulfing/piercing at 44-day low support |
| PA2 | Pin Bar | ✅ IMPLEMENTED | 60%+ lower wick ratio, <30% upper wick, at support |
| PA3 | Inside Bar | ✅ IMPLEMENTED | high < high[1] AND low > low[1] at support |
| PA4 | DZC | 🔲 PLANNED | Minor demand zone candlestick — next to add |
| PA5 | RRR | 🔲 PLANNED | Resistance-turned-support pin bar rejection |
| PA6 | Morning Star | 🔲 PLANNED | Multi-candle bullish reversal — first 3-candle PA code |

---

## PA6 — Morning Star (Multi-Candle Bullish Reversal)

**Added:** 4/12/2026 | **PA Code:** PA6 | **Type:** Multi-Candle (3-Bar Pattern)

### Structure
| Candle | Requirement | Role |
|--------|-------------|------|
| Candle 1 | Strong bearish body > 0.6x ATR | Downtrend continuation — sellers in control |
| Candle 2 | Small body < 0.3x C1 body (any color or doji) | Indecision — selling pressure slowing |
| Candle 3 | Bullish, closes above midpoint of C1 body | Buyer takeover confirmed |

### Context Requirements (P_115 Application)
- Clear downtrend preceding the pattern (not sideways/choppy)
- Price within 2% of 44-day low (nearSupport zone)
- RSI oversold OR positive divergence strengthens the signal
- Rising volume on Candle 3 = institutional participation (upgrade to T3)

### Scoring Integration
```
CandleTier = T2 (pattern present, no volume surge)
CandleTier = T3 (pattern present + C3 volume > 125% of 20-day avg)
SetupScore: +1 for CandleTier >= 2 (existing rule — no new rule needed)
HybridTier: Indirect benefit via CandleTier elevation
```

### Entry, Stop, Target
| Parameter | Value |
|-----------|-------|
| Entry | Close of C3 (standard) OR pullback into C3 body (best R:R) |
| 60-min Confirm | Mini cup-and-handle forming after C3 = highest conviction |
| Stop (tight) | Below Candle 2 low — ideal at major support |
| Stop (standard) | Below Candle 3 low — most common |
| Stop (wide) | Below pattern low — volatile/wide-range candles |
| Target | 2:1 R:R minimum; trail via moving average if new uptrend develops |

### Log Entry Format
```
Comments: PA6 – Morning Star at 44-day low. C3 closed above C1 midpoint. Vol [surge/normal].
SimulationNotes: Morning Star confirmed at [support level] — [date]
```

### ThinkScript Detection Criteria (Future Automation — after PA4/PA5)
```thinkscript
def c1_bearish = close[2] < open[2] and (open[2] - close[2]) > 0.6 * ATR(14)[2];
def c2_small   = AbsValue(close[1] - open[1]) < 0.3 * AbsValue(open[2] - close[2]);
def c1_mid     = close[2] + (open[2] - close[2]) / 2;
def c3_bullish = close > open and close > c1_mid;
def nearSupport = close <= Lowest(low, 44)[1] * 1.02;
def morningStar = c1_bearish and c2_small and c3_bullish and nearSupport;
def volSurge    = volume > Average(volume, 20) * 1.25;
# CandleTier: T3 if morningStar AND volSurge; T2 if morningStar only
```

### Relationship to PA Code Series
- **PA1–PA5:** Single-candle patterns (BOSS, Pin Bar, Inside Bar, DZC, RRR)
- **PA6+:** Multi-candle patterns — new sub-series
- **PA7 (planned):** Evening Star — bearish mirror of PA6
- **PA8 (planned):** Three White Soldiers — bullish continuation multi-candle

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

## Patterns Most Relevant to Existing P_115/P_118 System
| Pattern | PA Code | Relevance |
|---------|---------|-----------|
| BOSS | PA1 | High — core bounce confirmation at major support |
| Pin Bar | PA2 | High — rejection candle at support, tight stop-loss |
| Inside Bar | PA3 | High — continuation/consolidation at support |
| DZC | PA4 | High — NEXT TO IMPLEMENT for minor zone entries |
| RRR | PA5 | Medium — PLANNED for resistance-turned-support plays |
| Morning Star | PA6 | High — first multi-candle code; ideal P_115 convergence signal |
| BEAR / TVR / TVR2 | Future | Future — short-side and trap avoidance signals |

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.1 | 4/12/2026 | Added PA6 Morning Star — first multi-candle PA code; ThinkScript detection criteria; P_115 integration details |
| 1.0 | 2/25/2026 | Initial document created from Price Action Edge (Colibri Trader) |

---

*PDF can be removed from project — all actionable content captured above*
*Continuation prompts file (Price_Action_Continuation_Prompts.md) can also be replaced with this summary*
'''

with open(pa_path, 'w', encoding='utf-8') as f:
    f.write(pa_content)
print(f'Price_Action_Edge_Summary.md written. Chars: {len(pa_content)}')
print('All updates complete.')
