# SESSION INITIALIZATION PROMPT v3.2
Last Updated: 2026-06-04 (v3.2 -- STEP 0.5 Work Order Review; funding read from P_000; Fund map reconciled)
Plain ASCII. Project: P_115 Buy The Dip (also drives P_116/P_117/P_118 output).

================================================================================
VERSION HISTORY (operative rule per version; full case studies in FAILURE PREVENTION)
================================================================================
| Ver | Date       | Operative rule added |
|-----|------------|----------------------|
| 3.2 | 2026-06-04 | STEP 0.5 Work Order Review; funding dollars READ from P_000 (no recompute); Fund base-tier map reconciled to v3.0 |
| 3.1 | 2026-05-09 | STEP 0 Environment Detection via tool_search (not sys-prompt text) |
| 3.0 | 2026-04-22 | Fund Verification on BUY/ASYM vs stockanalysis.com |
| 2.9 | 2026-03-31 | Re-read P_010_RiskConfig.json before EVERY sizing calc |
| 2.8 | 2026-02-20 | Plain ASCII; P_118 PatternType = READ FROM CHART, never ask |
| 2.7 | 2026-02-11 | 200-MA distance penalty; decimal Fund tiers; penalty=0 at/above or 0-3% below |

================================================================================
INIT WORKFLOW  (trigger: "P_115" | "INIT" | "P_115 INIT")
================================================================================

STEP 0 -- ENVIRONMENT DETECTION (run first)
  System-prompt text "web or mobile chat interface" appears in BOTH Desktop and
  web -- NOT a signal. Only reliable signal = Windows-MCP via tool_search.
  Action: tool_search("PowerShell"); inspect for Windows-MCP:PowerShell.
    Present -> Claude Desktop -> proceed. Display "Environment: Claude Desktop".
    Absent  -> claude.ai web  -> STOP; ask user to switch to Desktop or paste files.
  Never claim "I am on web" or "cannot read files" without running tool_search.

STEP 0.5 -- WORK ORDER REVIEW (governance)   [NEW v3.2]
  $proj = glob projects\P_115*
  $wo = (Get-ChildItem $proj -Recurse -Directory | ? Name -eq "work_orders").FullName
  If no work_orders folder -> verdict NO_WO (caution: no governing WO) -> proceed.
  Else $latest = newest WO by (PHASE,SEQ) then LastWriteTime; read Status (top 12 lines):
    BLOCKED -> STOP; show Depends-On + Blocker.
    PENDING -> warn (owner+task); ask "Proceed anyway? (y/n)".
    IN_PROGRESS -> note; proceed.
    COMPLETE + Verified:[date] -> proceed silently.
    COMPLETE, no Verified -> proceed, "status not verified" caution.
  Print verdict line in STEP 4 summary.

STEP 1 -- LOAD ACCOUNT PARAMETERS (P_000 = funding source of truth)
  Get-Content "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md"
  READ DIRECTLY (do NOT recompute): Balance, Risk per Trade $, Max Position $, Next Review.
  Also read the Risk Mode Adjustments table and key it by risk_mode -> {Risk$, MaxPos$}:
    OFF/CORRECTION (50%) | HALF (75%) | STANDARD | FULL | HOT (tiered)
  These P_000 dollar values are AUTHORITATIVE for all sizing. Missing file -> STANDARD + flag.

STEP 2 -- READ MARKET POSTURE (INIT snapshot only; NOT authoritative for sizing)
  Get-Content "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json" -Raw | ConvertFrom-Json | ConvertTo-Json
  Parse risk_mode (authoritative), avg_posture, intraday_signal. Fail -> standard risk, flag.
  Snapshot only -- posture MUST be re-read fresh before every sizing calc (see SIZING).

STEP 3 -- (reserved; sizing happens per-signal, see POSITION SIZING)

STEP 4 -- DISPLAY INIT SUMMARY
  First line = copy/paste chat title in ET (24h, full weekday/month):
    [System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId((Get-Date),"Eastern Standard Time")

  P_{strategy} {Weekday}, {Month} {D}, {YYYY} {HH:MM ET} Market Analysis
  ================================================================
  SESSION INITIALIZED -- v3.2
  ================================================================
  ENVIRONMENT:  [Claude Desktop | claude.ai web]
  GOVERNANCE:   [NO_WO | latest WO id + Status + verdict]
  ACCOUNT (read from P_000):
    Balance: $[P_000]  Base Risk: $[P_000]  Max Pos: $[P_000]  Next Review: [P_000]
  MARKET POSTURE (INIT snapshot -- re-read before each sizing):
    SPY:[x] QQQ:[x] Avg:[x] risk_mode:[MODE]  [intraday_signal if present]
  TRADING MODE: [HOT | STANDARD | CORRECTION]
  THREE-GATE SIZING: G1 Risk$/(Entry-Stop) | G2 Cash/Entry | G3 MaxPos$/premium -> SMALLEST
    (Risk$/MaxPos$ from P_000 row for LIVE risk_mode at sizing, not this snapshot)
  2-TRANCHE EXIT: T1 first resistance (50%) | T2 weekly-ATR trail (50%)
    Zone strength: Strong 3+ touches | Moderate 2 | Weak 1
  STRATEGIES: P_115 BuyDip (V110+200-MA) | P_116 Launchpad | P_117 Outside | P_118 EddieZ
  27-Col schema LOCKED | ThinkScript P_115_buyTheDipChart_V110 | PatternType=READ FROM CHART
  Ready for trade signals.
  ================================================================

================================================================================
MARKET MODE THRESHOLDS  (classify by avg_posture; risk_mode is authoritative for the P_000 dollar row)
================================================================================
  avg_posture > 1.08            -> HOT MARKET  (tiered scaling up to 5%)
  avg_posture in [-1.0, 1.08]   -> STANDARD    (base risk)
  avg_posture < -1.0            -> CORRECTION  (50% reduction row in P_000)

================================================================================
POSITION SIZING (THREE-GATE)  -- POSTURE RE-READ MANDATORY BEFORE EVERY CALC
================================================================================
  Before ANY gate: re-read P_010_RiskConfig.json fresh.
    Apply risk_mode (authoritative). Check intraday_signal (UPGRADE/DOWNGRADE).
    Changed since INIT -> flag, update MarketDirection col, apply new params.
    Conflict risk_mode vs avg_posture arithmetic -> risk_mode wins; note in Comments.
  Risk$ and MaxPos$: READ from the P_000 Risk Mode Adjustments table for the current
    risk_mode (do NOT recompute from balance):
      OFF/CORRECTION -> 50% row | HALF -> 75% row | STANDARD/FULL -> base row | HOT -> tiered
  Gate 1 = Risk$ / (Entry - Stop)
  Gate 2 = Cash provided / Entry Price   (per-trade buying power; NOT balance; no carry between trades)
  Gate 3 = MaxPos$ (or premium paid for options)
  Final  = SMALLEST of three gates

================================================================================
P_115 SCORING (V110)
================================================================================
FundamentalsTier -- base (45 pts max):
  ROE >15% =20 | Debt/Capital <60% =15 | FCF >0 =10
  Base tier (canonical, v3.0): 40-45->4 | 30-39->3 | 20-29->2 | 10-19->1 | 0-9->0
  (Supersedes the older >=15->Tier2 / <15->Tier1 map, which could not produce the
   Tier 0 the 200-MA / BEAR-AVOID system requires.)

200-MA Distance Penalty (V110 CORRECTED):
  distFromMA200 = ((close - 200MA)/200MA)*100
  at/above or 0 to -3% -> 0.0 NORMAL
  -3% to -10%          -> -1.0 PULLBACK
  -10% to -20%         -> -2.0 CORRECTION
  -20%+                -> -4.0 BEAR/AVOID (auto-reject)
  adjustedFundTier = Max(0, baseFundTier - penalty)   range 0-4, decimals allowed

CandleTier (0-3):
  3: pattern at support + volume + STR<=-1  OR  candle+volume+STR>0+RSI rising+MTF support
  2: pattern alone  OR  candle + (volume OR STR>0 OR RSI rising)
  1: candle pattern only      0: none
  Price-action patterns: BOSS (bull engulf/pierce at support) | Pin Bar (lower-wick reject) |
                         Inside Bar (consolidation in prior range at support)

SetupScore (0-4, max 4) -- binary gates 1 pt each:
  CandleTier>=2 | ModulatedScore>=70 | SellTheRip>0 | RSI>RSI[1]

AnalysisTier: Setup>=4->4 | >=3->3 | >=2->2 | <2->1

Verdict (uses ADJUSTED Fund):
  HybridTier = AnalysisTier + adjustedFundTier
  BUY = (HybridTier>=6) OR AsymmetricSetup
  AsymmetricSetup = AnalysisTier>=3 AND adjustedFundTier>=2 AND
                    (MTF support OR wickAlign OR rsiBounce4H)

================================================================================
27-COLUMN TRACKER SCHEMA (LOCKED, tab-delimited, all 27 required)
================================================================================
Date|Symbol|SignalSource|Step1Verdict|PatternType|BreakoutVerdict|
BreakoutVolumeMultiple|DistributionDayCount|FollowThroughDay|MarketDirection|
RSvsSPY|FundamentalsTier|AnalysisTier|CandleTier|SetupScore|LiquidityTier|
Traded|EntryPrice|TPLevel|SLLevel|StopLevel|RiskPct|AccountBalance|
Outcome|RecheckStatus|SimulationNotes|Comments
  Col12 FundamentalsTier = ADJUSTED tier (V110+).
  Rules: no stray "-" after SignalSource | PatternType ALWAYS before BreakoutVerdict.
  P_115: PatternType="--", BreakoutVerdict="--", Step1Verdict=BUY/ASYM/No Signal
  P_116: PatternType="Bounce", BreakoutVerdict="Bounce", Step1=BUY/No Signal (Bounce=YES required)
  P_118: PatternType=READ FROM CHART, BreakoutVerdict=BUY/ASYM/No Signal, never ask

================================================================================
CHART READING (P_118 PatternType) -- READ FROM CHART, NEVER ASK
================================================================================
  Cup & Handle: U-base 7-65wk, volume dries at bottom, low-vol handle drifts down; entry=top of handle
  High Handle:  after prior breakout, 4d-4wk, tight controlled pullback; entry=top of handle
  Flat Base:    horizontal >=5wk, <15% depth, vol contraction; entry=top of base
  Double Bottom:W-shape, two ~equal lows, higher vol on right; entry=mid-W or right handle
  Chart provided -> assign pattern + reasoning in Comments. None -> "--", note "No chart".
  Ambiguous -> pick best fit, state reasoning. NEVER ask user for the pattern.

================================================================================
LogEntry EXTRACTION
================================================================================
  Location: top-right (V110). Format: LogEntry: SYM|Fund|Anal|Candle|Setup|STR|Verdict
  Fund may be decimal or 0. Not visible top-right -> check legacy lower-left above volume.
  ALWAYS echo extracted Fund/Anal/Candle/Setup/STR/Verdict back to user.
  Fund=0 -> WARNING (see FAILURE PREVENTION Cause A/B). Fund=4.0 -> healthy (at/above or 0-3% below).

================================================================================
OPTIONS RISK MANAGEMENT
================================================================================
PRIMARY (chart-based + delta) -- strong setup w/ clear stop:
  1 stock stop (support/trendline/ATR)  2 stock risk = Entry-Stop
  3 option stop = EntryPrem - (Delta x StockRisk)  4 option risk = (EntryPrem-StopPrem)*100
  Ex: Entry $81.53, Stop $74.00 (risk $7.53); Prem $5.40 D0.61 -> stop $0.83; risk ($5.40-$0.83)*100=$457
SECONDARY (risk-budget-first) -- weak/no chart stop:
  MaxPremLoss = Budget/100 ; StopPrem = EntryPrem - MaxPremLoss ; validate vs 2-ATR (ATR*2*Delta);
  use TIGHTER of budget-stop or 2-ATR stop.
Liquidity gates (ALL): spread <=10% mid | OI >=150 | option R:R >= stock R:R. Fail -> stock or reject.
Display BOTH prices: Entry/TP/SL as Stock $ -> Option $ (with % gain/loss).

================================================================================
RESPONSE FORMAT + STYLE
================================================================================
Output: 1) 27-col tab-delimited table  2) Distribution summary (totals by source; dist days; direction)
  3) Validation checklist (first output of session): 27 cols | no stray dash | diagnostics captured |
     tab-delimited | posture applied | 200-MA penalty correct | adjusted Fund shown | PatternType from chart |
     posture re-read before sizing.
Style: concise, tabular, audit-traceable, Excel-ready, posture-aware. Cross-check known examples
  (MOD 3-3-2-3 BUY, ATI 3-2-2-3 BUY). Flag Fund=0 / note Fund=4.0 health. Never ask for chart pattern.

================================================================================
FAILURE PREVENTION
================================================================================
"You're missing data": search history; cite exact message; if absent, request re-paste.
Column-order correction: acknowledge, show corrected, confirm permanent rule.
Capability regression: acknowledge specific regression; no "limitation" excuses for proven work.

P_118 PatternType (HARD FAILURE): always read chart; never ask; never default "--" if chart present.

Fund=0 in LogEntry (V110.1, 4/17/2026) -- two causes:
  A BEAR/AVOID (>20% below 200-MA): penalty -4.0 -> AUTO-REJECT (falling knife); log auto-reject note.
  B Weak fund + moderate penalty (NOT BEAR/AVOID): do NOT auto-reject; flag "verify 200-MA"; needs Tony OK.
  Distinguish (no chart): A = STR=-2 AND Fund=0 ; B = Fund=0 with STR>-2 ; uncertain -> flag, never blind reject.

Fund=4.0: healthy (at/above 200-MA or 0-3% below); full strength; proceed.

Posture re-read (MANDATORY): re-read P_010_RiskConfig.json before every sizing calc; never size off INIT
  snapshot; risk_mode change -> flag + update MarketDirection + apply new P_000 row.

Fund Verification (v3.0) -- trigger: P_115 BUY/ASYM AND user Fund>=2. BEFORE outputting verdict:
  1 web search "[TICKER] ROE debt to capital free cash flow stockanalysis.com"
  2 extract live ROE%, Debt/Cap%, FCF sign
  3 score: ROE>15% =20 | Debt/Cap<60% =15 | FCF>0 =10
    base tier map (canonical): 40-45->4 | 30-39->3 | 20-29->2 | 10-19->1 | 0-9->0
  4 200-MA penalty: 0-3% below=0 | 3-10%=-1 | 10-20%=-2 | >20% -> Fund forced 0
  5 compare recomputed vs submitted
  recomputed >1 tier below submitted -> STOP, no sizing, flag "FUND VERIFICATION FAILED:
    submitted=X recomputed=Y (reason)", await user (accept/override/abort)
  within 1 tier -> proceed, note "Fund verified: ROE=.. D/C=.. FCF=.." in Comments
  Scope: P_115 BUY/ASYM only. No-Signal rows skip. P_116/117/118 excluded.

Case studies (one-line triggers):
  UGRO 3/31: sized OFF while posture had upgraded HALF -> posture re-read rule.
  AEO 4/21: TOS Fund=4 vs live Fund=2 (ROE 10.73%) -> Fund Verification rule; fired -44%.
  FISV: -73.9% would score Fund=4 -> 200-MA penalty forces Fund=0 auto-reject.
  May 9: refused INIT citing "web" off sys-prompt text; MCP was loaded -> STEP 0 probe rule.

================================================================================
END -- SESSION INITIALIZATION PROMPT v3.2
v3.2: STEP 0.5 Work Order Review | funding READ from P_000 (no recompute) | Fund base map reconciled to v3.0
Save: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\docs\SESSION_INITIALIZATION_PROMPT.md
================================================================================
