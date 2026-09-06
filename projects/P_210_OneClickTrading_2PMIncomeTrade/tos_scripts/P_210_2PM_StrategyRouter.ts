declare upper;

#declare upper;

# ============================================================
# 2PM STRATEGY ROUTER - QQQ-signaled / NDX-traded Income Indicator
# Determines which of the 11 validated strategy buckets is
# active for today's 2PM ET entry, with size tier.
# Run on a 5-minute chart. Bubble fires once at the 2PM bar.
# VIX/Gap/Movement math is anchored to QQQ per your confirmation
# that QQQ signals drive the NDX trades.
# ============================================================

def isNDX = GetSymbol() == "NDX";

# --- Session anchors: lock 9:30 AM ET opens for the day ---
def newDay = GetYYYYMMDD() != GetYYYYMMDD()[1];
def isFirstBar930 = SecondsFromTime(0930) >= 0 and (SecondsFromTime(0930)[1] < 0 or newDay);

def vix930Open = CompoundValue(1,
    if isFirstBar930 then open("VIX") else vix930Open[1],
    open("VIX"));

def qqq930Open = CompoundValue(1,
    if isFirstBar930 then open("QQQ") else qqq930Open[1],
    open("QQQ"));

# --- 2:00 PM ET lock: capture the EXACT 2:00:00pm tick via open() of the
# 2pm bar, not close() (which would reflect 2:05pm, after price has moved).
# This mirrors the 9:30 lock pattern above.
def isFirstBar1400 = SecondsFromTime(1400) >= 0 and SecondsFromTime(1400)[1] < 0;

def vix2pmOpen = CompoundValue(1,
    if isFirstBar1400 then open("VIX") else vix2pmOpen[1],
    Double.NaN);

def qqq2pmOpen = CompoundValue(1,
    if isFirstBar1400 then open("QQQ") else qqq2pmOpen[1],
    Double.NaN);

def vixCurrent = close("VIX");
def qqqCurrent = close("QQQ");

# --- Overnight gap: prior day's close -> today's 9:30 open (time-invariant once set) ---
def qqqClosePrev = close("QQQ", period = AggregationPeriod.DAY)[1];
def qqqGapPct = if !IsNaN(qqqClosePrev) and qqqClosePrev > 0
                then ((qqq930Open - qqqClosePrev) / qqqClosePrev) * 100
                else 0;

# --- LIVE versions (continuously update pre-2pm, for the monitoring labels only) ---
def vixPctChangeLive = if !IsNaN(vix930Open) and vix930Open > 0
                        then ((vixCurrent - vix930Open) / vix930Open) * 100
                        else 0;
def qqqIntradayPctLive = if !IsNaN(qqq930Open) and qqq930Open > 0
                          then ((qqqCurrent - qqq930Open) / qqq930Open) * 100
                          else 0;

# --- LOCKED versions (use the 2:00:00pm snapshot - these drive the actual decision) ---
def vixPctChange = if !IsNaN(vix930Open) and vix930Open > 0 and !IsNaN(vix2pmOpen)
                    then ((vix2pmOpen - vix930Open) / vix930Open) * 100
                    else 0;
def qqqIntradayPct = if !IsNaN(qqq930Open) and qqq930Open > 0 and !IsNaN(qqq2pmOpen)
                      then ((qqq2pmOpen - qqq930Open) / qqq930Open) * 100
                      else 0;

# --- Day of week ---
# CONFIRMED via live test on Aug 6, 2026 (a real Thursday): GetDayOfWeek
# returns 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat (0-indexed).
def dow = GetDayOfWeek(GetYYYYMMDD());
def isMonday    = dow == 1;
def isTuesday   = dow == 2;
def isWednesday = dow == 3;
def isThursday  = dow == 4;
def isFriday    = dow == 5;

# --- Core pass/fail conditions (decision logic - uses LOCKED 2pm values) ---
def vixDropOK = vixPctChange >= -5.0;      # VIX drop since 9:30 < 5%, AS OF 2PM
def gapUnder1 = qqqGapPct >= -1.0;         # overnight gap down < 1%
def gapOver1  = qqqGapPct <= -1.0;         # overnight gap down >= 1%

# --- Direction since open (decision logic - uses LOCKED 2pm value) ---
def isUp   = qqqIntradayPct >= 0;
def isDown = qqqIntradayPct < 0;

# --- VIX bands, evaluated against the LOCKED 2pm VIX (half-open intervals) ---
def vix1819 = vix2pmOpen >= 18 and vix2pmOpen < 19;
def vix1920 = vix2pmOpen >= 19 and vix2pmOpen < 20;
def vix20p  = vix2pmOpen >= 20;
def vix1618 = vix2pmOpen >= 16 and vix2pmOpen < 18;
def vixU16  = vix2pmOpen < 16;
def vix18p  = vix2pmOpen >= 18;

# ============================================================
# DOWN SINCE OPEN cascade
# ============================================================
def downCode =
    if isDown and vix1819 then 1                                              # Bear Call | 4
    else if isDown and vix1920 and gapUnder1 then 2                           # Bull Put  | 1
    else if isDown and vix20p then 3                                          # Bear Call | 2
    else if isDown and vix1618 and gapOver1 then 6                            # Bear Call | 1  (new gap override)
    else if isDown and vix1618 and isTuesday and gapUnder1 then 5             # Bear Call | 1  (Tuesday flip - corrected)
    else if isDown and vix1618 and !isTuesday and gapUnder1 then 4            # Bull Put  | 1  (base bucket - corrected)
    else if isDown and vixU16 and !isTuesday and qqqIntradayPct > -0.5 then 7 # Bear Call | 2
    else 0;

# ============================================================
# UP SINCE OPEN cascade
# ============================================================
def upCode =
    if isUp and vix18p and gapOver1 then 10                                              # Bonus Butterfly | 4
    else if isUp and vix18p and vixDropOK and gapUnder1 and !isMonday then 8             # Bull Put  | 8
    else if isUp and vix18p and vixDropOK and gapUnder1 and isMonday then 9              # Bear Call | 2  (new Monday flip)
    else if isUp and vix1618 and gapOver1 then 14                                        # Bear Call | 1  (catch-all, Mid VIX)
    else if isUp and vix1618 and vixDropOK and gapUnder1 then 11                         # Bull Put  | 4
    else if isUp and vixU16 and vixDropOK and (isTuesday or isThursday) then 12          # Bull Put  | 8  (gap filter removed per request)
    else if isUp and vixU16 and vixDropOK and (isWednesday or isFriday) then 13          # Bear Call | 2  (gap filter removed per request)
    else if isUp and vixU16 and gapOver1 then 14                                         # Bear Call | 1  (catch-all: Monday, or VIX drop >=5% on other days)
    else 0;                                                                              # Monday @ VIX<16, VIX-drop failures fall here -> SKIP

def ruleCode = if isDown then downCode else upCode;

# ============================================================
# LIVE PREVIEW cascade - same logic, but using continuously-
# updating values instead of the 2pm lock. This lets the team
# see a running projection ahead of 2pm so they can prep the
# trade in advance. IT CAN CHANGE before the 2pm lock fires -
# treat it as a heads-up, not a confirmed signal.
# ============================================================
def vixDropOKLive = vixPctChangeLive >= -5.0;
def isUpLive   = qqqIntradayPctLive >= 0;
def isDownLive = qqqIntradayPctLive < 0;

def vix1819Live = vixCurrent >= 18 and vixCurrent < 19;
def vix1920Live = vixCurrent >= 19 and vixCurrent < 20;
def vix20pLive  = vixCurrent >= 20;
def vix1618Live = vixCurrent >= 16 and vixCurrent < 18;
def vixU16Live  = vixCurrent < 16;
def vix18pLive  = vixCurrent >= 18;

def downCodeLive =
    if isDownLive and vix1819Live then 1
    else if isDownLive and vix1920Live and gapUnder1 then 2
    else if isDownLive and vix20pLive then 3
    else if isDownLive and vix1618Live and gapOver1 then 6
    else if isDownLive and vix1618Live and isTuesday and gapUnder1 then 5
    else if isDownLive and vix1618Live and !isTuesday and gapUnder1 then 4
    else if isDownLive and vixU16Live and !isTuesday and qqqIntradayPctLive > -0.5 then 7
    else 0;

def upCodeLive =
    if isUpLive and vix18pLive and gapOver1 then 10
    else if isUpLive and vix18pLive and vixDropOKLive and gapUnder1 and !isMonday then 8
    else if isUpLive and vix18pLive and vixDropOKLive and gapUnder1 and isMonday then 9
    else if isUpLive and vix1618Live and gapOver1 then 14
    else if isUpLive and vix1618Live and vixDropOKLive and gapUnder1 then 11
    else if isUpLive and vixU16Live and vixDropOKLive and (isTuesday or isThursday) then 12
    else if isUpLive and vixU16Live and vixDropOKLive and (isWednesday or isFriday) then 13
    else if isUpLive and vixU16Live and gapOver1 then 14
    else 0;

def ruleCodeLive = if isDownLive then downCodeLive else upCodeLive;

# ============================================================
# Map ruleCode -> size tier / bubble color
# ============================================================
def sizeTier =
    if ruleCode == 1 then 4
    else if ruleCode == 2 then 1
    else if ruleCode == 3 then 2
    else if ruleCode == 4 then 1
    else if ruleCode == 5 then 1
    else if ruleCode == 6 then 1
    else if ruleCode == 7 then 2
    else if ruleCode == 8 then 8
    else if ruleCode == 9 then 2
    else if ruleCode == 10 then 4
    else if ruleCode == 11 then 4
    else if ruleCode == 12 then 8
    else if ruleCode == 13 then 2
    else if ruleCode == 14 then 1
    else 0;

# NOTE: thinkScript's def can only hold numeric values - strings and Colors
# cannot be pre-declared as reusable defs. The bucket text and color logic
# below is inlined directly into each function call that needs it (this is
# why the same if/else chain appears more than once in this file).

# ============================================================
# 2:00 PM ET bubble - fires once per day (trigger defined earlier, near the 2pm lock)
# ============================================================
AddChartBubble(isNDX and isFirstBar1400, high,
    if ruleCode == 1 then "DN/HIGH1 BEAR CALL (4)"
    else if ruleCode == 2 then "DN/HIGH2 BULL PUT (1)"
    else if ruleCode == 3 then "DN/HIGH3 BEAR CALL (2)"
    else if ruleCode == 4 then "DN/MID BULL PUT (1)"
    else if ruleCode == 5 then "DN/MID-TUE BEAR CALL (1)"
    else if ruleCode == 6 then "DN/MID-GAP BEAR CALL (1)"
    else if ruleCode == 7 then "DN/LOW BEAR CALL (2)"
    else if ruleCode == 8 then "UP/HIGH BULL PUT (8)"
    else if ruleCode == 9 then "UP/HIGH-MON BEAR CALL (2)"
    else if ruleCode == 10 then "BONUS BUTTERFLY (4)"
    else if ruleCode == 11 then "UP/MID BULL PUT (4)"
    else if ruleCode == 12 then "UP/LOW T-TH BULL PUT (8)"
    else if ruleCode == 13 then "UP/LOW W-F BEAR CALL (2)"
    else if ruleCode == 14 then "UP-GAP BEAR CALL (1)"
    else "SKIP",
    if ruleCode == 1 then CreateColor(255, 60, 60)    # Bear Call, size 4 (brightest red)
    else if ruleCode == 2 then CreateColor(0, 90, 0)  # Bull Put, size 1 (darkest green)
    else if ruleCode == 3 then CreateColor(180, 0, 0) # Bear Call, size 2 (medium red)
    else if ruleCode == 4 then CreateColor(0, 90, 0)  # Bull Put, size 1 (darkest green)
    else if ruleCode == 5 then CreateColor(100, 0, 0) # Bear Call, size 1 (dark red)
    else if ruleCode == 6 then CreateColor(100, 0, 0) # Bear Call, size 1 (dark red)
    else if ruleCode == 7 then CreateColor(180, 0, 0) # Bear Call, size 2 (medium red)
    else if ruleCode == 8 then CreateColor(50, 230, 50)  # Bull Put, size 8 (brightest green)
    else if ruleCode == 9 then CreateColor(180, 0, 0) # Bear Call, size 2 (medium red)
    else if ruleCode == 10 then CreateColor(255, 210, 0) # Bonus Butterfly, size 4 (gold)
    else if ruleCode == 11 then CreateColor(0, 160, 0)   # Bull Put, size 4 (medium green)
    else if ruleCode == 12 then CreateColor(50, 230, 50) # Bull Put, size 8 (brightest green)
    else if ruleCode == 13 then CreateColor(180, 0, 0)   # Bear Call, size 2 (medium red)
    else if ruleCode == 14 then CreateColor(100, 0, 0)   # Bear Call, size 1 (dark red)
    else CreateColor(120, 120, 120),                     # SKIP (gray)
    yes);

# ============================================================
# Live status labels (continuous, for monitoring pre-2PM)
# ============================================================
AddLabel(isNDX,
    "Direction (live): " + (if qqqIntradayPctLive >= 0 then "UP" else "DOWN") + "  Move: " + AsText(qqqIntradayPctLive, "%10.2f") + "%",
    Color.WHITE);

AddLabel(isNDX,
    "VIX (live): " + AsText(vixCurrent, "%10.2f") + "  VIX drop: " + AsText(vixPctChangeLive, "%10.2f") + "%",
    Color.WHITE);

AddLabel(isNDX,
    "Gap: " + AsText(qqqGapPct, "%10.2f") + "%",
    Color.WHITE);

AddLabel(isNDX,
    "2PM LOCKED -> VIX: " + AsText(vix2pmOpen, "%10.2f") + "  Move: " + AsText(qqqIntradayPct, "%10.2f") + "%",
    Color.CYAN);

AddLabel(isNDX,
    "Day# (0=Sun..6=Sat): " + dow + " -> " +
    (if isMonday then "MON" else if isTuesday then "TUE" else if isWednesday then "WED"
     else if isThursday then "THU" else if isFriday then "FRI" else "WEEKEND"),
    Color.GRAY);

def isLiveWindow = SecondsFromTime(0930) >= 0 and SecondsFromTime(1400) < 0;

AddLabel(isNDX and isLiveWindow,
    "LIVE PROJECTION (subject to change until 2PM lock): " +
    (if ruleCodeLive == 1 then "DN/HIGH1 BEAR CALL (4)"
     else if ruleCodeLive == 2 then "DN/HIGH2 BULL PUT (1)"
     else if ruleCodeLive == 3 then "DN/HIGH3 BEAR CALL (2)"
     else if ruleCodeLive == 4 then "DN/MID BULL PUT (1)"
     else if ruleCodeLive == 5 then "DN/MID-TUE BEAR CALL (1)"
     else if ruleCodeLive == 6 then "DN/MID-GAP BEAR CALL (1)"
     else if ruleCodeLive == 7 then "DN/LOW BEAR CALL (2)"
     else if ruleCodeLive == 8 then "UP/HIGH BULL PUT (8)"
     else if ruleCodeLive == 9 then "UP/HIGH-MON BEAR CALL (2)"
     else if ruleCodeLive == 10 then "BONUS BUTTERFLY (4)"
     else if ruleCodeLive == 11 then "UP/MID BULL PUT (4)"
     else if ruleCodeLive == 12 then "UP/LOW T-TH BULL PUT (8)"
     else if ruleCodeLive == 13 then "UP/LOW W-F BEAR CALL (2)"
     else if ruleCodeLive == 14 then "UP-GAP BEAR CALL (1)"
     else "SKIP (as of right now)"),
    Color.ORANGE);

AddLabel(isNDX and !isLiveWindow,
    "LIVE PROJECTION: inactive outside 9:30AM-2PM window - see CURRENT BUCKET below",
    Color.GRAY);

AddLabel(isNDX,
    "CURRENT BUCKET: " +
    (if ruleCode == 1 then "DN/HIGH1 BEAR CALL (4)"
     else if ruleCode == 2 then "DN/HIGH2 BULL PUT (1)"
     else if ruleCode == 3 then "DN/HIGH3 BEAR CALL (2)"
     else if ruleCode == 4 then "DN/MID BULL PUT (1)"
     else if ruleCode == 5 then "DN/MID-TUE BEAR CALL (1)"
     else if ruleCode == 6 then "DN/MID-GAP BEAR CALL (1)"
     else if ruleCode == 7 then "DN/LOW BEAR CALL (2)"
     else if ruleCode == 8 then "UP/HIGH BULL PUT (8)"
     else if ruleCode == 9 then "UP/HIGH-MON BEAR CALL (2)"
     else if ruleCode == 10 then "BONUS BUTTERFLY (4)"
     else if ruleCode == 11 then "UP/MID BULL PUT (4)"
     else if ruleCode == 12 then "UP/LOW T-TH BULL PUT (8)"
     else if ruleCode == 13 then "UP/LOW W-F BEAR CALL (2)"
     else if ruleCode == 14 then "UP-GAP BEAR CALL (1)"
     else "SKIP"),
    if ruleCode == 0 then Color.RED else Color.GREEN);
