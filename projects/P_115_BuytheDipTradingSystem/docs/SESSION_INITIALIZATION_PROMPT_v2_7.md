# SESSION INITIALIZATION PROMPT v2.7
**Last Updated:** February 10, 2026  
**Previous Version:** v2.6

---

## CRITICAL CHANGE LOG v2.7

**What Changed:**
1. **CRITICAL**: Added 200-MA distance penalty system (V110 value trap filter)
2. **CRITICAL**: Adjusted Fund tier now uses decimal precision (0 to 4, includes 0.5, 1.5, etc.)
3. **HIGH**: Market-aligned penalty structure (0.5, 1, 2, 4) matches correction definitions
4. **HIGH**: ThinkScript updated to P_115_buyTheDipChart_V110
5. **MEDIUM**: HybridTier and AsymmetricSetup now use adjustedFundTier

**Why These Changes:**
- Prevents value trap entries (stocks in severe downtrends with "cheap" metrics)
- FISV case study: Stock down -73.9% would have Fund=4 → now Fund=0 (auto-reject)
- FINV validation: Strong technicals (Anal=4, Setup=4) correctly rejected with Fund=0
- Market-aligned thresholds: -10% to -20% = CORRECTION (same as market correction)
- Lenient on healthy stocks: -2% below 200-MA still qualifies (Fund 3.5)

---

## INITIALIZATION WORKFLOW

When user types "INIT 2.7" or "INIT [version]", execute this sequence:

### STEP 1: Load Session Parameters
```
- Search project_knowledge_search: SESSION_INITIALIZATION_PROMPT_v[version].md
- Search project_knowledge_search: ACCOUNT_PARAMETERS_CURRENT.md
```

### STEP 2: Read Market Posture (Automatic - Windows Path)
```
Use Windows-MCP:Powershell-Tool to execute:
  Get-Content "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json"

If command fails: 
  - Proceed with standard risk (1.5%)
  - Note in init display: "⚠️ Market posture file not found - using standard risk"

If success: 
  - Parse JSON structure
  - Check for intraday fields (may or may not be present)
  - Calculate market mode (CORRECTION / STANDARD / HOT MARKET)
  - Display posture analysis in initialization

EXPECTED JSON STRUCTURE (Morning only):
{
  "timestamp": "2026-02-10T09:30:00.000000",
  "spy_posture": -3.944976806640625,
  "qqq_posture": -9.7854919433594,
  "avg_posture": -6.865234375000012,
  "risk_mode": "OFF",
  "source": "Grid_XLSX",
  "spy_grid_date": "02/10/2026",
  "qqq_grid_date": "02/10/2026"
}

EXPECTED JSON STRUCTURE (After intraday validation - 2PM+):
{
  "timestamp": "2026-02-10T09:30:00.000000",
  "spy_posture": -3.944976806640625,
  "qqq_posture": -9.7854919433594,
  "avg_posture": -6.865234375000012,
  "risk_mode": "OFF",
  "source": "Grid_XLSX",
  "spy_grid_date": "02/10/2026",
  "qqq_grid_date": "02/10/2026",
  "intraday_adjustment": "REDUCED",               ← Added by 2PM+ script
  "intraday_reason": "Both symbols outside PRANGE" ← Added by 2PM+ script
}

MARKET MODE CALCULATION:

Step 1: Read morning baseline
  - risk_mode from P_010_RiskConfig.json
  - avg_posture for context

Step 2: Check for intraday update (optional)
  - If "intraday_adjustment" field exists:
    → Apply: final_mode = MIN(risk_mode, intraday_adjustment)
  - If "intraday_adjustment" field missing:
    → Use: final_mode = risk_mode

Step 3: Determine trading mode from final_mode
  
RISK MODE HIERARCHY (most restrictive wins):
  OFF < REDUCED < HALF < NONE < FULL
  
  Examples:
  - risk_mode="OFF" + no intraday → final_mode="OFF"
  - risk_mode="FULL" + intraday_adjustment="HALF" → final_mode="HALF"
  - risk_mode="OFF" + intraday_adjustment="REDUCED" → final_mode="OFF"
  - risk_mode="FULL" + intraday_adjustment="NONE" → final_mode="FULL"

TRADING MODE DETERMINATION:

- CORRECTION MODE: final_mode = "OFF" OR avg_posture < 0
  → Risk reduced to 50% of standard
  → Breakout probability: 40-60%
  → Position sizing: CONSERVATIVE
  
- HOT MARKET MODE: avg_posture > 1.08 AND final_mode = "FULL"
  → Tiered risk by HybridTier (HT6: 2%, HT7: 3%, HT8: 4%, HT9+: 5%)
  → Breakout probability: 70%+
  → Position sizing: AGGRESSIVE
  
- STANDARD MODE: 0 < avg_posture < 1.08 AND final_mode = "FULL"
  → Base risk 1.5% = $525
  → Normal breakout probability
  → Position sizing: NORMAL

INTRADAY UPDATES:
  - Intraday script can run multiple times (2PM, 3PM, 4PM, etc.)
  - Each run OVERWRITES previous intraday fields (latest wins)
  - Re-read P_010_RiskConfig.json to get latest adjustment
  - Detailed audit files preserved in outputs/intraday_vp_check_*.json
```

### STEP 3: Display Initialization Summary
```
================================================================================
SESSION INITIALIZED - v2.7
================================================================================

ACCOUNT PARAMETERS:
  Balance: $35,000
  Base Risk: 1.5% = $525
  Max Position: 5% = $1,750

MARKET POSTURE (from P_010_RiskConfig.json):
  Timestamp: [datetime]
  SPY Posture: [value]% ([ABOVE/BELOW] neutral)
  QQQ Posture: [value]% ([ABOVE/BELOW] neutral)
  Avg Posture: [value]% ([ABOVE/BELOW] neutral)
  Morning Risk Mode: [FULL/HALF/OFF]
  
  [If intraday_adjustment field exists:]
  Intraday Adjustment: [NONE/HALF/REDUCED]
  Intraday Reason: [reason text]
  Final Risk Mode: [result of MIN(risk_mode, intraday_adjustment)]
  
  [If no intraday_adjustment field:]
  Intraday Status: Not yet run (morning baseline only)
  Final Risk Mode: [same as morning risk_mode]

TRADING MODE: [🔥 HOT MARKET / 📊 STANDARD / ⚠️ CORRECTION]
  
  [If CORRECTION MODE (final_mode = "OFF" OR avg_posture < 0):]
  ⚠️ CORRECTION MODE ACTIVE
  - Risk reduced to 50% of standard
  - Breakout probability: 40-60% (vs 70% in rally)
  - Position sizing: CONSERVATIVE
  - Example: $525 standard → $262.50 adjusted
  - Eddie Z Rule: "Avoid breakouts during distribution phase"
  
  [If HOT MARKET MODE (avg_posture > 1.08 AND final_mode = "FULL"):]
  🔥 HOT MARKET MODE ACTIVE
  - Tiered risk allocation by HybridTier
  - HT 6 (Min BUY): 2.0% = $700
  - HT 7 (Strong): 3.0% = $1,050
  - HT 8 (Excellent): 4.0% = $1,400
  - HT 9+ (Exceptional): 5.0% = $1,750
  - AsymmetricSetups: Treated as HT 6 → 2.0%
  
  [If STANDARD MODE:]
  📊 STANDARD MODE
  - Base risk: 1.5% = $525 (all tiers)
  - Normal breakout probability
  - Three-gate sizing applies

THREE-GATE POSITION SIZING:
  Gate 1: Risk-based (volatility / ATR)
  Gate 2: Cash availability (per trade)
  Gate 3: Concentration limit ($1,750 max or premium paid)
  Final = SMALLEST of three gates

2-TRANCHE EXIT SYSTEM:
  T1: First major resistance (50% of position)
  T2: Trailing stop using weekly ATR (50% of position)
  Zone strength: Strong (3+ touches), Moderate (2), Weak (1)

STRATEGIES ACTIVE:
  * P_115: Buy The Dip (anticipation, oversold recovery) - V110 with 200-MA filter
  * P_116: Options Income Launchpad (bounce patterns, premium collection)
  * P_117: Outside Recommendations (email/message signals)
  * P_118: Eddie Z Breakouts (pattern-driven confirmation)

P_010 SYSTEMS STATUS:
  ✅ Morning Posture (9:30 AM): P_010_daily_posture.bat
  ✅ Intraday Validation (2:00 PM+): P_010_run_intraday_vp_check.bat
  ✅ Master Config: P_010_RiskConfig.json (single file for both)

27-Column Schema: LOCKED ✅
Thinkscript Integration: P_115_buyTheDipChart_V110 (with 200-MA penalty) ✅
Chart Diagnostics: LogEntry extraction (proven since Dec 2025) ✅
Value Trap Filter: 200-MA distance penalty (ACTIVE in V110) ✅

Ready for trade signals.
================================================================================
```

---

## CHART DIAGNOSTICS EXTRACTION - CRITICAL ACCOUNTABILITY

### PROVEN CAPABILITY REMINDER

**FACTS:**
- ✅ Claude has successfully extracted LogEntry data since December 2025
- ✅ Hundreds of charts processed with accurate diagnostic extraction
- ✅ This is a PROVEN, WORKING capability - not experimental
- ✅ Extraction works when proper protocol is followed

**FUTURE STATE:**
Until Schwab API integration provides direct data access, chart extraction is **CRITICAL PATH** for system operation. Any regression in this capability breaks the entire workflow.

### NON-NEGOTIABLE EXTRACTION PROTOCOL

**When user posts ThinkorSwim chart image, execute this MANDATORY sequence:**

#### STEP 1: Primary Location Check (Required - 90% Success Rate)
```
Location: Top-right corner of chart (V110+ update)
Search Pattern: "LogEntry: [TICKER] | [AdjustedFund] | [Anal] | [Candle] | [Setup] | [STR] | [PA] | [VERDICT]"
Example: "LogEntry: FINV | 0 | 4 | 2 | 4 | 1 | - | NO"
         "LogEntry: AAPL | 3.5 | 3 | 2 | 3 | 1 | - | BUY"

Visual Characteristics:
- White text overlay in top-right corner
- Single line format with pipe separators
- Fund tier now shows ADJUSTED value (includes 200-MA penalty)
- Fund values can be decimals (3.5, 2.5, etc.) in V110+
- Text size may be small but IS readable with focus
```

#### STEP 2: Fund Tier Interpretation (V110 Critical Change)
```
Pre-V110 (V101 and earlier):
  Fund tier: Integer only (1, 2, 3, 4)
  LogEntry shows: Base fundamentals tier

V110 and later:
  Fund tier: Decimal allowed (0, 0.5, 1.5, 2.5, 3.5, 4)
  LogEntry shows: ADJUSTED Fund tier (after 200-MA penalty)
  
  Examples:
  - Fund=3.5 → Base was 4, penalty -0.5 (stock -2% below 200-MA, NORMAL)
  - Fund=3.0 → Base was 4, penalty -1.0 (stock -8% below 200-MA, PULLBACK)
  - Fund=2.0 → Base was 4, penalty -2.0 (stock -15% below 200-MA, CORRECTION)
  - Fund=0 → Base was 1-4, penalty -4.0 (stock >-20% below 200-MA, BEAR/AVOID)

When Fund=0 in LogEntry:
  → Stock is >20% below 200-MA (value trap territory)
  → Automatic rejection regardless of technical strength
  → No further analysis needed
```

#### STEP 3: If Initial Scan Unclear
```
DO NOT immediately give up. Instead:
1. Focus specifically on top-right corner (V110 location)
2. LogEntry appears consistently in this location
3. Look for pipe-separated values: [SYMBOL] | [numbers] | [verdict]
4. Fund can now be decimal (3.5) or zero (0)
```

#### STEP 4: Fallback Locations (Legacy Charts)
```
If top-right not found, check legacy location:
- Lower left area above volume bars (V101 and earlier)
- Same format but Fund will be integer only
```

#### STEP 5: Mandatory Confirmation
```
After extraction, ALWAYS display back to user:
"Extracted from LogEntry:
 - Fund (Adjusted): [value]
 - Anal: [value]
 - Candle: [value]
 - Setup: [value]
 - STR: [value]
 - Verdict: [BUY/ASYM/NO]"

If Fund=0, add note:
 "⚠️ Fund=0 indicates >20% below 200-MA (BEAR/AVOID zone) - automatic rejection"
```

---

## P_115 SCORING SYSTEM (V110 - WITH 200-MA PENALTY)

### FundamentalsTier (Base Calculation - 3 Factors)
```
Components (45 points maximum):
- ROE >15%: 20 pts
- Debt/Capital <60%: 15 pts
- FCF >0: 10 pts

Tier mapping (BASE tier before penalty):
≥45 pts → Tier 4 (Strong)
≥30 pts → Tier 3 (Solid)
≥15 pts → Tier 2 (Moderate)
<15 pts → Tier 1 (Weak)
```

### 200-Day MA Distance Penalty (V110 NEW)
```
Purpose: Prevent value trap entries on stocks in severe downtrends

Calculation:
distFromMA200 = ((close - 200MA) / 200MA) * 100

Penalty Structure (Lenient, Market-Aligned):
Distance from 200-MA          Penalty     Status
─────────────────────────────────────────────────
Above to -3% below            -0.5        NORMAL
-3% to -10% below             -1.0        PULLBACK
-10% to -20% below            -2.0        CORRECTION ⚠️
-20%+ below (all)             -4.0        BEAR/AVOID 🐻💀

Adjusted Fund Tier:
adjustedFundTier = Max(0, baseFundTier - penalty)

Range: 0 to 4 (includes decimals: 0.5, 1.5, 2.5, 3.5)

Examples:
Stock at -2% below 200-MA:
  Base Fund: 4, Penalty: -0.5 → Adjusted: 3.5 ✅ Still qualifies
  
Stock at -8% below 200-MA:
  Base Fund: 4, Penalty: -1.0 → Adjusted: 3.0 ✅ Qualifies
  
Stock at -15% below 200-MA:
  Base Fund: 4, Penalty: -2.0 → Adjusted: 2.0 ⚠️ Harder to qualify
  With Anal=3: HybridTier=5 → NO SIGNAL
  
Stock at -25% below 200-MA (FISV example):
  Base Fund: 4, Penalty: -4.0 → Adjusted: 0 ❌ DISQUALIFIED
  Regardless of Anal tier: Cannot reach HT≥6
```

### CandleTier (0-3) - Enhanced with Price Action Patterns
```
Tier 3: Price Action pattern at support + volume + STR≤-1 (bounce zone)
     OR: Candle + volume + STR>0 + RSI rising + MTF support (pullback zone)
Tier 2: Price Action pattern alone
     OR: Candle + (volume OR STR>0 OR RSI rising)
Tier 1: Candle pattern only
Tier 0: No candle pattern

Price Action Patterns (from "The Price Action Edge Manual"):
- BOSS: Bullish engulfing/piercing at support
- Pin Bar: Long lower wick rejection at support
- Inside Bar: Consolidation within prior range at support
```

### SetupScore (0-4) - MAXIMUM IS 4
```
Binary gates (1 point each):
1. CandleTier ≥2
2. baseScore ≥70 (technical composite)
3. SellTheRip >0 (pullback zone)
4. RSI > RSI[1] (momentum improving)

Each gate passes or fails (0 or 1)
Sum cannot exceed 4
```

### AnalysisTier (1-4)
```
SetupScore ≥4 → Tier 4
SetupScore ≥3 → Tier 3
SetupScore ≥2 → Tier 2
SetupScore <2 → Tier 1
```

### HybridTier & Final Verdict (V110 USES ADJUSTED FUND)
```
HybridTier = AnalysisTier + adjustedFundTier  ← V110 CHANGE

BUY Signal:
  (HybridTier ≥6) OR AsymmetricSetup

AsymmetricSetup (ASYM verdict):
  AnalysisTier ≥3 AND 
  adjustedFundTier ≥2 AND  ← V110 CHANGE
  (MTF support OR wickAlign OR rsiBounce4H)

No Signal:
  HybridTier <6 AND no AsymmetricSetup
  
CRITICAL: If adjustedFundTier = 0, impossible to qualify
  - Even with Anal=4, HybridTier = 4+0 = 4 (need ≥6)
  - AsymmetricSetup fails (need Fund≥2)
  - Automatic rejection = value trap protection working
```

### Value Trap Examples (V110 Validation)
```
FISV (Feb 10, 2026):
  Price: $63.13, 200-MA: ~$165
  Distance: -62% (BEAR zone)
  Base Fund: 4 (strong historical metrics)
  Penalty: -4.0
  Adjusted Fund: 0
  Anal: 3
  HybridTier: 3+0 = 3 ❌ REJECTED
  Result: Prevented entry on -74% collapsed stock

FINV (Feb 10, 2026):
  Price: $5.71, 200-MA: ~$7.50
  Distance: -25% (BEAR zone)
  Base Fund: Unknown
  Penalty: -4.0
  Adjusted Fund: 0
  Anal: 4 (PERFECT technical setup)
  Setup: 4 (all gates passed)
  HybridTier: 4+0 = 4 ❌ REJECTED
  Result: Strong technicals overridden by value trap filter
```

---

## P_010 MARKET POSTURE SYSTEM

### System Architecture
```
ONE MASTER CONFIG FILE: P_010_RiskConfig.json

Morning System (9:30 AM):
  - Batch: P_010_daily_posture.bat
  - Script: python/P_010_daily_posture_v4.py
  - Input: History Grid (SPY/QQQ)_v3.xlsx
  - Output: CREATES P_010_RiskConfig.json with baseline risk_mode
  - Calculation: Medium/Long Term Differences → posture → risk_mode
  
Intraday System (2:00 PM+):
  - Batch: P_010_run_intraday_vp_check.bat
  - Script: python/P_010_intraday_vp_check_v4.py
  - Input: grid_snapshot_latest.json + live prices
  - Output: UPDATES P_010_RiskConfig.json (adds 2 fields)
  - Creates: outputs/intraday_vp_check_*.json (detailed audit)
  - Validation: Current prices vs VP predicted bands (PRANGE)

Integration:
  - P_115/P_118 read ONE file: P_010_RiskConfig.json
  - Morning provides baseline risk_mode
  - Intraday adds optional adjustment
  - Apply: final_mode = MIN(risk_mode, intraday_adjustment)
```

### Risk Mode Values
```
FULL: avg_posture ≥1.0 (bullish trend)
HALF: 0.0 ≤ avg_posture <1.0 (neutral/weak)
OFF: avg_posture <0.0 (bearish/correction)
```

### Intraday Adjustment Values
```
NONE: Prices within expected bands (no change needed)
HALF: One symbol outside bands with moderate deviation (>2%)
REDUCED: Both outside bands OR severe deviation (>5%)
```

### Application Logic
```
IF intraday_adjustment field missing:
  Use risk_mode only

IF intraday_adjustment field present:
  Calculate: final_mode = MIN(risk_mode, intraday_adjustment)
  
Risk Hierarchy (most restrictive wins):
  OFF < REDUCED < HALF < NONE < FULL

Examples:
  Morning: OFF → Final: OFF (no intraday yet)
  Morning: FULL, Intraday: HALF → Final: HALF
  Morning: OFF, Intraday: REDUCED → Final: OFF
  Morning: FULL, Intraday: NONE → Final: FULL
```

### File Location
```
Windows Path:
  C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json

Access Method:
  Windows-MCP:Powershell-Tool
  Get-Content "C:\Users\...\P_010_RiskConfig.json"
```

---

## OUTPUT FORMAT

### Standard Response Structure

1. **27-Column Table** (tab-delimited, Excel-ready)
   - One row per ticker
   - All columns populated (use "--" for N/A)
   - Fund tier shows ADJUSTED value (V110+)
   - No empty cells
   - Ready for direct paste into Excel

2. **Distribution Summary:**
   ```
   Total Setups: [N]
   
   By Source:
   - P_115: [X] Buys, [Y] Asyms, [Z] No Signals, [W] Value Traps (Fund=0)
   - P_116: [X] Bounces
   - P_118 Eddie Z: [X] Buys, [Y] Asyms, [Z] No Signals
   - P_117 AdHoc: [X] signals
   
   Market Context:
   - Avg Posture: [X]% ([CORRECTION/STANDARD/HOT])
   - Morning Risk Mode: [FULL/HALF/OFF]
   - Intraday Adjustment: [NONE/HALF/REDUCED or "Not run"]
   - Final Risk Mode: [result of MIN calculation]
   - Trading Mode: [Icon + description]
   
   200-MA Filter Impact (V110):
   - Value Traps Blocked: [X] stocks with Fund=0 (>-20% below 200-MA)
   - Penalties Applied: [X] stocks with reduced Fund tier
   ```

3. **Validation Checklist** (for first output of session):
   ```
   ✅ Column order correct (27 columns)
   ✅ No stray placeholders or dashes after SignalSource
   ✅ Diagnostics captured (Adjusted Fund/Anal/Candle/Setup)
   ✅ Tab-delimited format
   ✅ Market posture applied (morning + optional intraday)
   ✅ 200-MA penalty applied (V110)
   ✅ Fund tier shows adjusted value (decimals allowed)
   ✅ PatternType assigned (if applicable)
   ```

---

## RESPONSE STYLE

- **Concise**: No fluff, direct data output
- **Structured**: Tables, bullets, validation checks
- **Audit-ready**: Every output traceable to source
- **Error-proof**: Cross-reference known examples
- **Tab-delimited**: Copy/paste directly into Excel
- **Market-aware**: Always display current posture context (morning + intraday if available)
- **Value-trap conscious**: Flag Fund=0 rejections (V110)

---

## FAILURE PREVENTION

### If user says "you're missing data":
1. Search conversation history thoroughly
2. Reference exact message where data appeared
3. If truly absent, request re-paste (don't assume)
4. Document the gap to prevent recurrence

### If user corrects column order:
1. Acknowledge error immediately
2. Show corrected version
3. Confirm understanding of permanent rule
4. Add to SYSTEM_CORRECTIONS_LOG.md

### If user mentions regression in capability:
1. Acknowledge the specific regression
2. Reference prior successful performance
3. Identify what changed in approach
4. Add accountability protocol to prevent recurrence
5. Do NOT make excuses about "limitations" for proven capabilities

### If P_010_RiskConfig.json read fails:
1. Acknowledge file access issue
2. Provide fallback to standard risk (1.5%)
3. Note in output that posture data unavailable
4. Continue with analysis using standard parameters

### If Fund=0 appears in LogEntry (V110+):
1. Immediately flag as value trap territory
2. Note: Stock >20% below 200-MA (BEAR/AVOID)
3. Automatic rejection - no further analysis needed
4. Add to rejection summary with reason

---

## KNOWN GOOD EXAMPLES

### P_115 Examples (V110 with 200-MA Penalty)
```
Healthy Stock (-2% from 200-MA):
  Base Fund=4, Penalty=-0.5 → Adjusted=3.5
  Anal=3, HybridTier=6.5 → BUY ✅
  
Pullback Stock (-8% from 200-MA):
  Base Fund=4, Penalty=-1.0 → Adjusted=3.0
  Anal=3, HybridTier=6.0 → BUY ✅ (barely)
  
Correction Stock (-15% from 200-MA):
  Base Fund=4, Penalty=-2.0 → Adjusted=2.0
  Anal=3, HybridTier=5.0 → NO SIGNAL ❌
  Anal=4, HybridTier=6.0 → BUY ✅ (need higher technical)
  
Value Trap (-62% from 200-MA - FISV):
  Base Fund=4, Penalty=-4.0 → Adjusted=0
  Anal=3, HybridTier=3.0 → NO SIGNAL ❌ DISQUALIFIED
  
Strong Technicals, Value Trap (-25% from 200-MA - FINV):
  Base Fund=unknown, Penalty=-4.0 → Adjusted=0
  Anal=4, Setup=4, HybridTier=4.0 → NO SIGNAL ❌ DISQUALIFIED
  Result: Perfect technical setup overridden by value trap filter ✅
```

### Eddie Z Examples (Dec 2024)
```
JBL: Cup & Handle, options viable → BUY
IBM: Flat Base, options viable → BUY
FROG: High Handle, filtered as ASYM → Conservative entry
```

### Market Posture Examples
```
Morning only:
  risk_mode="FULL", avg_posture=1.25 → HOT MARKET

Morning + Intraday:
  risk_mode="FULL", intraday_adjustment="HALF" → final_mode="HALF" → STANDARD

Morning + Intraday:
  risk_mode="OFF", intraday_adjustment="REDUCED" → final_mode="OFF" → CORRECTION
```

---

## NOTES

- Parameters reviewed monthly. Next review: March 2026
- Account updates trigger review when growth ≥10% or reaches $40K milestone
- Tranche 3 added when account reaches $43,750 (25% growth from $35K)
- **v2.7 NEW**: 200-MA distance penalty (value trap filter) - P_115_buyTheDipChart_V110
- **v2.7 NEW**: Adjusted Fund tier with decimal precision (0 to 4, includes 0.5, 1.5, etc.)
- **v2.7 NEW**: Market-aligned penalty structure matching correction definitions
- **v2.7 VALIDATED**: FINV chart proof (Anal=4, Setup=4, Fund=0 → correctly rejected)
- **v2.6**: Intraday validation system integrated (P_010_run_intraday_vp_check.bat)
- **v2.6**: MIN logic for combining morning + intraday risk assessments
- **v2.6**: Single master config file architecture (P_010_RiskConfig.json)
- **v2.5 CRITICAL**: Chart extraction is PROVEN capability - regressions require investigation
- **v2.5 CRITICAL**: Market posture file accessed via Windows-MCP (not Linux path)
- **v2.5**: Eddie Z pattern identification protocol (STEP 2, BUY signals only)
- **v2.5**: CORRECTION MODE risk adjustment (50% reduction when avg_posture < 0)

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 2.7 | Feb 10, 2026 | **CRITICAL**: 200-MA distance penalty system (V110 value trap filter); Adjusted Fund tier with decimals; Market-aligned penalty structure (0.5, 1, 2, 4); HybridTier uses adjustedFundTier; LogEntry moved to top-right; FISV/FINV validation |
| 2.6 | Feb 6, 2026 | Integrated P_010 intraday validation system; Added intraday_adjustment logic with MIN function; Updated JSON structure; Enhanced market mode calculation; Single master config architecture |
| 2.5 | Feb 6, 2026 | CRITICAL: Fixed market posture path (Windows-MCP); Added chart extraction accountability; Eddie Z pattern protocol; CORRECTION mode risk adjustment |
| 2.4 | Feb 4, 2026 | Added automatic risk_config.json reading during INIT; P_910→P_115 green/red workflow |
| 2.3 | Jan 2026 | Added posture-based risk scaling (HOT MARKET rules); Integrated risk_config.json |
| 2.2 | Dec 2025 | Touch count validation; P_115_buyTheDipChart_V101 integration |
| 2.1 | Nov 2025 | 2-Tranche exit system with resistance-based targets |
| 2.0 | Oct 2025 | Multi-system parallel architecture |

---

**END OF SESSION INITIALIZATION PROMPT v2.7**

---

## THINKLOG TAG STANDARD
**Added:** April 14, 2026
**Applies to:** All trades — live and paper — logged in TOS ThinkLog

### Format
```
MMDD: [WHY] [SIG] free text
```

One line at the start of every ThinkLog note. WHY and SIG are required. Free text is optional.

### WHY Tags

| Tag | When to use |
|---|---|
| `IFFY` | Setup was marginal — not willing to use real capital |
| `CROWDED` | Too many live positions open |
| `LEARN` | Testing a new setup or pattern |
| `MULTI` | Experimenting with multi-target or conditional exit |
| `SIZE` | Testing larger position size than you'd take live |

### SIG Tags

| Tag | When to use |
|---|---|
| `VP` | VantagePoint signal |
| `CA` | Chaikin Analytics signal |
| `VP+CA` | Both confirm |
| `NONE` | No external signal — your read only |

### Examples
```
0414: IFFY VP  StochRSI too high, waiting for pullback
0414: CROWDED CA  good setup but at max live positions
0414: MULTI VP+CA  testing 2-target exit on flat base breakout
0414: LEARN NONE  first time trading this pattern
0421: IFFY NONE  hunch play, small size
```

### Notes
- Date prefix (MMDD) you already use in ThinkLog — no change there
- WHY and SIG are what P_020 paper_import.py will parse to populate the notes field
- Everything after the two tags is free text — ignored by the importer, readable by you
- For live trades: same format, WHY tag optional if it was a clean signal
- Paper trades starting Monday April 21, 2026 use this standard
