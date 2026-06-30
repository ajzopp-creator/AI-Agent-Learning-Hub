# === SCRIPT_ID: P_115_buyTheDipChart_V14 ===
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
def roe     = if IsNaN(ReturnOnEquity())          then roe[1]     else ReturnOnEquity();
def debtCap = if IsNaN(LongTermDebtToCapital())   then debtCap[1] else LongTermDebtToCapital();
def fcf     = if IsNaN(FreeCashFlowPerShare())     then fcf[1]     else FreeCashFlowPerShare();

def fundamentalScore = (if !IsNaN(roe)     and roe     > 15               then 20 else 0) +
                       (if !IsNaN(debtCap) and debtCap < DebtCapitalLimit  then 15 else 0) +
                       (if !IsNaN(fcf)     and fcf     > 0                 then 10 else 0);
def fundamentalsTier = if fundamentalScore >= 45 then 4 else if fundamentalScore >= 30 then 3
                       else if fundamentalScore >= 15 then 2 else 1;

# === 200-MA PENALTY ===
def ma200          = Average(close, 200);
def distFromMA200  = ((close - ma200) / ma200) * 100;
def maPenalty      = if distFromMA200 >= -3  then 0.0
                else if distFromMA200 >= -10 then 1.0
                else if distFromMA200 >= -20 then 2.0 else 4.0;
def adjFund        = Max(0, fundamentalsTier - maPenalty);
def ma200Code      = if distFromMA200 >= -3 then 0 else if distFromMA200 > -10 then 1
                     else if distFromMA200 > -20 then 2 else 3;

# === TECHNICALS ===
def BE  = close > open and close[1] < open[1] and close > open[1] and open < close[1];
def PL  = close > open and open < low[1] and close > (close[1] + open[1]) / 2;
def IH  = high - close > close - low and close > open and (high - low) > 3 * (open - close);
def TWS = close > open and close[1] > open[1] and close[2] > open[2] and close > close[1] and close[1] > close[2];
def TB  = low == low[1] and close > open and close[1] > open[1];
def CandlePattern = BE or PL or IH or TWS or TB;

def avgVol    = Average(volume, avgVolLength);
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
def PinBar      = lwr >= 0.7 and uwr < 0.25 and nearSupport and volume > avgVol and strTier <= -1;
def InsideBar   = high < high[1] and low > low[1] and nearSupport and volume > avgVol and strTier <= -1;
def BOSS        = (BE or PL) and nearSupport and volume > avgVol and strTier <= -1;
def PAPattern   = BOSS or PinBar or InsideBar;
def patternCode = if BOSS then 1 else if PinBar then 2 else if InsideBar then 3 else 0;

# === MULTI-TIMEFRAME ===
def mtf = close(period=AggFix1D) > open(period=AggFix1D)
      and (close(period=AggFix1D) - open(period=AggFix1D)) / (high(period=AggFix1D) - low(period=AggFix1D)) > 0.5
      and volume(period=AggFix1D) > Average(volume(period=AggFix1D), avgVolLength) * volumeSurgeFactor
      and close(period=AggFix1D) > Average(close(period=AggFix1D), 21);

def wick4H   = if (high(period=AggFix4H) - low(period=AggFix4H)) > 0
               then (close(period=AggFix4H) - low(period=AggFix4H)) / (high(period=AggFix4H) - low(period=AggFix4H)) else 0;
def wickD    = if (high(period=AggFix1D)  - low(period=AggFix1D))  > 0
               then (close(period=AggFix1D)  - low(period=AggFix1D))  / (high(period=AggFix1D)  - low(period=AggFix1D))  else 0;
def wickAlign     = (if wickD >= 0.5 then 1 else 0) + (if wick4H >= 0.5 then 1 else 0) >= 2;
def rsiBounce4H   = RSI(price=close(period=AggFix4H), length=14) crosses above 42;

# === CANDLE TIER ===
def CandleTier =
    if PAPattern and volume > avgVol and strTier <= -1 then 3
    else if CandlePattern and volume > avgVol and selltherip > 0 and rsi > rsi[1] and mtf then 3
    else if PAPattern then 2
    else if CandlePattern and (volume > avgVol or selltherip > 0 or rsi > rsi[1]) then 2
    else if CandlePattern then 1
    else 0;

# === SETUP / ANALYSIS TIERS ===
def setupScore   = (if CandleTier >= 2 then 1 else 0) + (if baseScore >= 70 then 1 else 0) +
                   (if selltherip > 0  then 1 else 0) + (if rsi > rsi[1]    then 1 else 0);
def analysisTier = if setupScore >= 4 then 4 else if setupScore >= 3 then 3
                   else if setupScore >= 2 then 2 else 1;

# === VERDICT ===
def asymSetup  = analysisTier >= 3 and adjFund >= 2 and (mtf or wickAlign or rsiBounce4H);
def hybridTier = analysisTier + adjFund;
def buySignal  = hybridTier >= 6 or asymSetup;

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

# === ENTRY-ANCHORED TARGETS (V13 CORE CHANGE) ===
def atr = MovingAverage(AverageType.WILDERS, TrueRange(high, close, low), 14);

# Persist entry price from the signal bar forward
def entryRef = if buySignal then close else entryRef[1];

# MM magnitude validation (5%-80% move from support to resistance)
def mmMag_T1 = if S_major > 0 then R1      - S_major else 0;
def mmMag_T2 = if S_major > 0 then R_major - S_major else 0;
def mmValid_T1 = (mmMag_T1 / S_major) * 100 >= 5 and (mmMag_T1 / S_major) * 100 <= 80;
def mmValid_T2 = (mmMag_T2 / S_major) * 100 >= 5 and (mmMag_T2 / S_major) * 100 <= 80;

# Targets anchored to entry — MM magnitude OR ATR fallback
def T1_Target = if mmValid_T1 then entryRef + mmMag_T1 else entryRef + (1.5 * atr);
def T2_Target = if mmValid_T2 then entryRef + mmMag_T2 else entryRef + (3.0 * atr);

# === PRICE-ACTION STOP (V14) ===
# Structural stop: swing low over paStopLookback bars up to/including signal bar,
# minus a small ATR buffer for noise. Persists forward from signal bar like entryRef.
# Falls back to Entry - 2*ATR if structure is invalid or sits above entry.
def swingLowAtSignal = Lowest(low, paStopLookback);
def paStopValid       = !IsNaN(swingLowAtSignal) and !IsNaN(atr) and swingLowAtSignal < entryRef;
def rawPAStop          = if buySignal then (if paStopValid then swingLowAtSignal - (paStopBufferATRMult * atr) else Double.NaN) else rawPAStop[1];
def paStopMethod       = if !IsNaN(rawPAStop) then 1 else 0;  # 1=Structure, 0=ATR Fallback
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
    "Verdict: " + (if buySignal and asymSetup then "ASYM Setup : Review" else if buySignal then "BUY SIGNAL" else "No Signal"),
    if buySignal and asymSetup then Color.ORANGE else if buySignal then Color.GREEN else Color.RED,
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
    (if ma200Code == 0 then "NORMAL" else if ma200Code == 1 then "PULLBACK" else if ma200Code == 2 then "CORRECTION" else "BEAR/AVOID") + ")",
    if adjFund >= 3 then Color.GREEN else if adjFund >= 2 then Color.YELLOW else Color.RED,
    Location.BOTTOM_LEFT);

AddLabel(yes,
    "LogEntry: " + GetSymbol() + " | " + Round(adjFund, 1) + " | " + analysisTier + " | " + CandleTier + " | " +
    setupScore + " | " + strTier + " | " + (if PAPattern then "PA" + patternCode else "-") + " | " +
    (if buySignal then "BUY" else if asymSetup then "ASYM" else "NO"),
    Color.WHITE, Location.TOP_RIGHT);