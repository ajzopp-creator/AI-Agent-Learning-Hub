# === SCRIPT_ID: P_115_buyTheDipChart_V16 ===
# V16: Fixed Verdict/LogEntry priority bug -- "asymSetup" was checked before
#      "hybridTier >= 6" in both the Verdict label and the LogEntry trailing
#      field, so any signal that also satisfied the ASYM conditions got
#      labeled "ASYM Setup: Review" even when HybridTier already cleared the
#      full BUY threshold on its own (CTAS 7/16/26: HybridTier=7, mislabeled
#      ASYM). LogEntry's trailing field had the same bug -- it always printed
#      "BUY" whenever buySignal was true, which is *always* true when
#      asymSetup is true, so LogEntry never actually distinguished ASYM from
#      BUY. Both now gate on isBuy (hybridTier>=6) first, asymSetup second.
#      Cached isBuy once instead of re-deriving "hybridTier >= 6" three times
#      across buySignal/Verdict label/LogEntry. Dropped ma200Code -- it was a
#      pure alias of maZone with no distinct value; every reference now uses
#      maZone directly. No threshold, scoring, or other field-order changes.
# V15: Efficiency refactor -- cached fundamental data calls (were fetched twice
#      each), cached secondary-aggregation OHLCV (were fetched repeatedly across
#      mtf/wickD/wick4H), collapsed 200-MA threshold ladder into one shared zone
#      lookup, replaced wickAlign's sum>=2 arithmetic with a plain AND.
# V14: Added structural Price-Action stop (paStop) with ATR fallback.
# V13: Entry-anchored targets, compressed labels, cleaned structure

declare upper;

# === INPUTS ===
input DebtCapitalLimit    = 60;
input rsiLength           = 14;
input volumeSurgeFactor   = 1.05;
input avgVolLength        = 20;
input daysBefore          = 3;
input daysAfter           = 3;
input supportThreshold    = 2.0;
input lookback_days       = 126;
input paStopLookback      = 10;
input paStopBufferATRMult = 0.1;

def chartAgg  = GetAggregationPeriod();
def AggFix1D  = Max(chartAgg, AggregationPeriod.DAY);
def AggFix4H  = Max(chartAgg, AggregationPeriod.FOUR_HOURS);

# === FUNDAMENTALS ===
def roeRaw     = ReturnOnEquity();
def debtCapRaw = LongTermDebtToCapital();
def fcfRaw     = FreeCashFlowPerShare();

def roe     = if IsNaN(roeRaw)     then roe[1]     else roeRaw;
def debtCap = if IsNaN(debtCapRaw) then debtCap[1] else debtCapRaw;
def fcf     = if IsNaN(fcfRaw)     then fcf[1]     else fcfRaw;

def fundamentalScore = (if !IsNaN(roe)     and roe     > 15               then 20 else 0) +
                       (if !IsNaN(debtCap) and debtCap < DebtCapitalLimit  then 15 else 0) +
                       (if !IsNaN(fcf)     and fcf     > 0                 then 10 else 0);
def fundamentalsTier = if fundamentalScore >= 45 then 4 else if fundamentalScore >= 30 then 3
                       else if fundamentalScore >= 15 then 2 else 1;

# === 200-MA PENALTY ===
def ma200          = Average(close, 200);
def distFromMA200  = ((close - ma200) / ma200) * 100;
def maZone          = if distFromMA200 >= -3  then 0
                  else if distFromMA200 >= -10 then 1
                  else if distFromMA200 >= -20 then 2 else 3;
def maPenalty       = if maZone == 0 then 0.0 else if maZone == 1 then 1.0
                  else if maZone == 2 then 2.0 else 4.0;
def adjFund         = Max(0, fundamentalsTier - maPenalty);

# === TECHNICALS ===
def BE  = close > open and close[1] < open[1] and close > open[1] and open < close[1];
def PL  = close > open and open < low[1] and close > (close[1] + open[1]) / 2;
def IH  = high - close > close - low and close > open and (high - low) > 3 * (open - close);
def TWS = close > open and close[1] > open[1] and close[2] > open[2] and close > close[1] and close[1] > close[2];
def TB  = low == low[1] and close > open and close[1] > open[1];
def CandlePattern = BE or PL or IH or TWS or TB;

def avgVol    = Average(volume, avgVolLength);
def volSurge  = volume > avgVol;
def baseScore = (if RSI(length=rsiLength) > 30 and RSI(length=rsiLength) < 70 then 40 else 0) +
                (if CandlePattern then 30 else 0) +
                (if volume >= 100000 and volume > avgVol * volumeSurgeFactor then 30 else 0);

def rsi = RSI(length = rsiLength);

# === STR TIER ===
def selltherip = ((low - Highest(close[1], 44)) / Highest(close[1], 44)) * 100;
def strTier    = if selltherip > 20 then 2 else if selltherip > 0 then 1
                 else if selltherip > -10 then 0 else if selltherip > -20 then -1 else -2;

# === PRICE ACTION PATTERNS ===
def Low44       = Lowest(low, 44);
def nearSupport = low <= Low44 * (1 + supportThreshold / 100);
def lwr         = if (high - low) > 0 then (close - low)  / (high - low) else 0;
def uwr         = if (high - low) > 0 then (high - close) / (high - low) else 0;
def strLE_neg1  = strTier <= -1;
def PinBar      = lwr >= 0.7 and uwr < 0.25 and nearSupport and volSurge and strLE_neg1;
def InsideBar   = high < high[1] and low > low[1] and nearSupport and volSurge and strLE_neg1;
def BOSS        = (BE or PL) and nearSupport and volSurge and strLE_neg1;
def PAPattern   = BOSS or PinBar or InsideBar;
def patternCode = if BOSS then 1 else if PinBar then 2 else if InsideBar then 3 else 0;

# === MULTI-TIMEFRAME ===
def o1D = open(period=AggFix1D);
def h1D = high(period=AggFix1D);
def l1D = low(period=AggFix1D);
def c1D = close(period=AggFix1D);
def v1D = volume(period=AggFix1D);
def h4H = high(period=AggFix4H);
def l4H = low(period=AggFix4H);
def c4H = close(period=AggFix4H);

def mtf = c1D > o1D
      and (c1D - o1D) / (h1D - l1D) > 0.5
      and v1D > Average(v1D, avgVolLength) * volumeSurgeFactor
      and c1D > Average(c1D, 21);

def wick4H = if (h4H - l4H) > 0 then (c4H - l4H) / (h4H - l4H) else 0;
def wickD  = if (h1D - l1D) > 0 then (c1D - l1D) / (h1D - l1D) else 0;
def wickAlign     = wickD >= 0.5 and wick4H >= 0.5;
def rsiBounce4H   = RSI(price=c4H, length=14) crosses above 42;

# === CANDLE TIER ===
def CandleTier =
    if PAPattern and volSurge and strLE_neg1 then 3
    else if CandlePattern and volSurge and selltherip > 0 and rsi > rsi[1] and mtf then 3
    else if PAPattern then 2
    else if CandlePattern and (volSurge or selltherip > 0 or rsi > rsi[1]) then 2
    else if CandlePattern then 1
    else 0;

# === SETUP / ANALYSIS TIERS ===
def setupScore   = (if CandleTier >= 2 then 1 else 0) + (if baseScore >= 70 then 1 else 0) +
                   (if selltherip > 0  then 1 else 0) + (if rsi > rsi[1]    then 1 else 0);
def analysisTier = if setupScore >= 4 then 4 else if setupScore >= 3 then 3
                   else if setupScore >= 2 then 2 else 1;

# === VERDICT ===
# isBuy is the real BUY condition (HybridTier clears 6 on its own). asymSetup
# is the reduced-size fallback path. isBuy must be checked FIRST everywhere
# a verdict is displayed -- a signal that qualifies outright as a full BUY
# must never be downgraded to ASYM just because it also happens to satisfy
# the (weaker) ASYM conditions.
def asymSetup  = analysisTier >= 3 and adjFund >= 2 and (mtf or wickAlign or rsiBounce4H);
def hybridTier = analysisTier + adjFund;
def isBuy      = hybridTier >= 6;
def buySignal  = isBuy or asymSetup;

# === EARNINGS AVOIDANCE ===
def barsToE    = GetEventOffset(Events.EARNINGS, 0);
def avoidPer   = if HasEarnings() and !IsNaN(barsToE) and !IsNaN(BarNumber() + barsToE)
                 and BarNumber() >= (BarNumber() + barsToE - daysBefore)
                 and BarNumber() <= (BarNumber() + barsToE + daysAfter) then 1 else 0;

plot AvoidEarnings = if avoidPer then close else Double.NaN;
AvoidEarnings.SetPaintingStrategy(PaintingStrategy.POINTS);
AvoidEarnings.SetDefaultColor(Color.RED);

# === R/S ZONES ===
def R1      = Highest(high, 60);
def R_major = if R1 < Highest(high, lookback_days) - 0.50 then Highest(high, lookback_days) else Highest(high, 90);
def S_major = Lowest(low, lookback_days);

def R1_tch  = Sum(if close >= R1      * 0.995 and close <= R1      * 1.005 then 1 else 0, lookback_days);
def Rm_tch  = Sum(if close >= R_major * 0.995 and close <= R_major * 1.005 then 1 else 0, lookback_days);

# === ENTRY-ANCHORED TARGETS ===
def atr = MovingAverage(AverageType.WILDERS, TrueRange(high, close, low), 14);

def entryRef = if buySignal then close else entryRef[1];

def mmMag_T1 = if S_major > 0 then R1      - S_major else 0;
def mmMag_T2 = if S_major > 0 then R_major - S_major else 0;
def mmValid_T1 = (mmMag_T1 / S_major) * 100 >= 5 and (mmMag_T1 / S_major) * 100 <= 80;
def mmValid_T2 = (mmMag_T2 / S_major) * 100 >= 5 and (mmMag_T2 / S_major) * 100 <= 80;

def T1_Target = if mmValid_T1 then entryRef + mmMag_T1 else entryRef + (1.5 * atr);
def T2_Target = if mmValid_T2 then entryRef + mmMag_T2 else entryRef + (3.0 * atr);

# === PRICE-ACTION STOP ===
def swingLowAtSignal = Lowest(low, paStopLookback);
def paStopValid       = !IsNaN(swingLowAtSignal) and !IsNaN(atr) and swingLowAtSignal < entryRef;
def rawPAStop          = if buySignal then (if paStopValid then swingLowAtSignal - (paStopBufferATRMult * atr) else Double.NaN) else rawPAStop[1];
def paStopMethod       = if !IsNaN(rawPAStop) then 1 else 0;
def paStop             = if IsNaN(rawPAStop) then entryRef - (2 * atr) else rawPAStop;

# === SIGNALS ===
plot signalDot = if buySignal then low - 0.5 else Double.NaN;
signalDot.SetPaintingStrategy(PaintingStrategy.POINTS);
signalDot.SetDefaultColor(Color.YELLOW);
signalDot.SetLineWeight(2);

plot PAArrow = if PAPattern then low - 0.35 else Double.NaN;
PAArrow.SetPaintingStrategy(PaintingStrategy.ARROW_UP);
PAArrow.SetDefaultColor(Color.MAGENTA);
PAArrow.SetLineWeight(3);

# === LABELS ===
AddLabel(yes,
    "Verdict: " + (if isBuy then "BUY SIGNAL" else if asymSetup then "ASYM Setup : Review" else "No Signal"),
    if isBuy then Color.GREEN else if asymSetup then Color.ORANGE else Color.RED,
    Location.BOTTOM_LEFT);

AddLabel(yes, "ATR: " + Round(atr, 2), Color.CYAN, Location.BOTTOM_LEFT);

AddLabel(yes, "Method: " + (if mmValid_T1 or mmValid_T2 then "MM+Entry" else "ATR+Entry"),
    Color.WHITE, Location.BOTTOM_LEFT);

AddLabel(yes, "T1 Exit: " + AsText(T1_Target) + " | Tch:" + R1_tch,
    if R1_tch >= 3 then Color.GREEN else Color.YELLOW, Location.BOTTOM_LEFT);

AddLabel(yes, "T2 Exit: " + AsText(T2_Target) + " | Tch:" + Rm_tch,
    if Rm_tch >= 3 then Color.GREEN else Color.YELLOW, Location.BOTTOM_LEFT);

AddLabel(yes,
    "PA Stop: " + AsText(Round(paStop, 2)) + " (" + (if paStopMethod then "Structure" else "ATR Fallback") + ")",
    if paStopMethod then Color.GREEN else Color.YELLOW,
    Location.BOTTOM_LEFT);

AddLabel(yes,
    "Fund: " + fundamentalsTier + "->" + Round(adjFund, 1) + " | 200-MA: " + Round(distFromMA200, 1) + "% (" +
    (if maZone == 0 then "NORMAL" else if maZone == 1 then "PULLBACK" else if maZone == 2 then "CORRECTION" else "BEAR/AVOID") + ")",
    if adjFund >= 3 then Color.GREEN else if adjFund >= 2 then Color.YELLOW else Color.RED,
    Location.BOTTOM_LEFT);

AddLabel(yes,
    "LogEntry: " + GetSymbol() + " | " + Round(adjFund, 1) + " | " + analysisTier + " | " + CandleTier + " | " +
    setupScore + " | " + strTier + " | " + (if PAPattern then "PA" + patternCode else "-") + " | " +
    (if isBuy then "BUY" else if asymSetup then "ASYM" else "NO"),
    Color.WHITE, Location.TOP_RIGHT)
