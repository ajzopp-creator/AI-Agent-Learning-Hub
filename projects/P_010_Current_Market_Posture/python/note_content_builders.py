"""
P_010 Daily Note Writer -- Content Builders
Split from P_010_write_daily_note.py (WO-P010-E1.003 housekeeping, 2026-08-10).
Suggestion logic, small formatters, and the two injected content blocks
(Section 5 VP table, Section 6 market overview table). No I/O, no external calls.
"""


def suggest_risk_level(rm, vxx):
    m = {
        ("FULL","BULLISH_CONFIRM"): ("Low",      "VP fully aligned"),
        ("FULL","NEUTRAL"):         ("Low",      "VP bullish, vol stable"),
        ("FULL","CAUTION"):         ("Moderate", "VP bullish but VXX rising"),
        ("FULL","WARNING"):         ("High",     "VP bullish but fear spike incoming"),
        ("HALF","BULLISH_CONFIRM"): ("Moderate", "Neutral posture, fear contracting"),
        ("HALF","NEUTRAL"):         ("Moderate", "Neutral environment"),
        ("HALF","CAUTION"):         ("High",     "Weak posture + rising vol"),
        ("HALF","WARNING"):         ("Extreme",  "Weak posture + fear spike"),
        ("OFF","BULLISH_CONFIRM"):  ("High",     "Bearish despite fear contracting"),
        ("OFF","NEUTRAL"):          ("Extreme",  "Bearish -- stay defensive"),
        ("OFF","CAUTION"):          ("Extreme",  "Bearish + vol expanding"),
        ("OFF","WARNING"):          ("No Trade", "OFF + fear spike -- sit in cash"),
    }
    return m.get((rm or "OFF", vxx or "NEUTRAL"), ("Moderate", "Review VP data"))


def suggest_bias(avg, vxx):
    if avg is None: return "Neutral", "No VP data"
    if avg <= -2.0 and vxx == "WARNING": return "Strongly Bearish", "Deep negative + fear spike"
    if avg < -1.0:  return "Bearish",         "Negative posture"
    if avg < 0.0:   return "Bearish",         "Below-zero posture"
    if avg < 0.5:   return "Neutral",         "Low positive -- no clear trend"
    if avg < 1.0:   return "Neutral",         "Modest positive -- wait for confirmation"
    if avg >= 1.0 and vxx == "BULLISH_CONFIRM": return "Bullish", "FULL + fear contracting"
    if avg >= 1.5:  return "Strongly Bullish", "Strong positive posture"
    return "Bullish", "Positive posture"


def fp(v): return f"${v:.2f}" if v is not None else "--"
def fc(v): return f"{v:.4f}" if v is not None else "--"


def build_section5_block(cfg, now):
    """Full VP posture table + Your Assessment checkboxes."""
    rm     = cfg.get("risk_mode",    "N/A")
    avgp   = cfg.get("avg_posture")
    spyp   = cfg.get("spy_posture")
    qqqp   = cfg.get("qqq_posture")
    vxxs   = cfg.get("vxx_signal")
    vxxn   = cfg.get("vxx_note",     "")
    vxxp   = cfg.get("vxx_posture")
    cfg_ts = cfg.get("timestamp",    "N/A")
    sz     = {"FULL":"100%","HALF":"50%","OFF":"0%"}.get(rm, "N/A")
    ve     = {"BULLISH_CONFIRM":"[+]","NEUTRAL":"[=]",
              "CAUTION":"[!]","WARNING":"[!!]"}.get(vxxs or "", "[=]")
    sr, srn = suggest_risk_level(rm, vxxs)
    sb, sbn = suggest_bias(avgp, vxxs)

    return f"""### VantagePoint P_010 -- Morning Assessment
*Auto-generated: {cfg_ts}*

| Field | Value |
|-------|-------|
| **VP Risk Mode** | **{rm}** |
| **Position Sizing** | **{sz}** |
| **Avg Posture** | {fc(avgp)} |
| **SPY Posture** | {fc(spyp)} |
| **QQQ Posture** | {fc(qqqp)} |
| **VXX Posture** | {fc(vxxp)} *(inverted -- negative = bullish)* |
| **VXX Signal** | {ve} **{vxxs or "N/A"}** |
| **VXX Note** | {vxxn} |

### Your Assessment

**Market Bias:**
Suggested: **{sb}** -- {sbn}
- [ ] Strongly Bullish  - [ ] Bullish  - [ ] Neutral  - [ ] Bearish  - [ ] Strongly Bearish

**Market Regime:**
- [ ] Trending Up  - [ ] Trending Down  - [ ] Range-Bound  - [ ] Volatile  - [ ] Breakout Mode

**Risk Level:**
Suggested: **{sr}** -- {srn}
- [ ] No Trade  - [ ] Extreme  - [ ] High  - [ ] Moderate  - [ ] Low

**Key Setups / Notes:**
> *(Your stock-specific observations)*"""


def build_market_overview(cfg, snap):
    """Pre-market table for Section 6."""
    sc  = snap.get("spy", {}).get("close");     sph = snap.get("spy", {}).get("pred_high")
    spl = snap.get("spy", {}).get("pred_low");  qc  = snap.get("qqq", {}).get("close")
    qph = snap.get("qqq", {}).get("pred_high"); qpl = snap.get("qqq", {}).get("pred_low")
    vxxc  = cfg.get("vxx_close");   vxxph = cfg.get("vxx_pred_high")
    vxxpl = cfg.get("vxx_pred_low")
    spyd  = cfg.get("spy_grid_date","N/A")
    qqqd  = cfg.get("qqq_grid_date","N/A")
    vxxd  = cfg.get("vxx_grid_date","N/A")
    spr = fp((sph - spl) if sph and spl else None)
    qr  = fp((qph - qpl) if qph and qpl else None)

    return f"""| Symbol | Close | Pred High | Pred Low | PRANGE | Grid Date |
|--------|-------|-----------|----------|--------|-----------|
| SPY | {fp(sc)} | {fp(sph)} | {fp(spl)} | {spr} | {spyd} |
| QQQ | {fp(qc)} | {fp(qph)} | {fp(qpl)} | {qr} | {qqqd} |
| VXX | {fp(vxxc)} | {fp(vxxph)} | {fp(vxxpl)} | -- | {vxxd} |"""
