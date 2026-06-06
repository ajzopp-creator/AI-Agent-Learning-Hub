import re, sys, json, urllib.request
from pathlib import Path
from datetime import datetime

# -- Paths ---------------------------------------------------------------------
VAULT_PATH   = Path(r"C:\Users\Trader\Documents\AJZStrategies_TradingJournal\Trading Journal")
TEMPLATES    = VAULT_PATH / "TradingJournal" / "Templates"
NOTES_FOLDER = VAULT_PATH / "TradingJournal"
PROJECT_ROOT = Path(__file__).parent.parent
RISK_CONFIG  = PROJECT_ROOT / "P_010_RiskConfig.json"
SNAPSHOT     = PROJECT_ROOT / "grid_snapshot_latest.json"
SKIP_FLAG    = PROJECT_ROOT / "SKIP_TODAY.flag"
DATE_FORMAT  = "%m-%d-%Y"

# -- Template selection --------------------------------------------------------
def find_latest_template():
    """Search Templates/ for P_800_Daily_Flow*.md -- auto-picks highest version."""
    matches = sorted(TEMPLATES.glob("P_800_Daily_Flow*.md"))
    if not matches:
        return None, None
    latest = matches[-1]
    # Extract version number if present (e.g. v2), otherwise default to 1
    m = re.search(r'v(\d+)', latest.stem, re.IGNORECASE)
    version = int(m.group(1)) if m else 1
    return latest, version

# -- Suggestion logic ----------------------------------------------------------
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

# -- API fetches ---------------------------------------------------------------
def fetch_scripture():
    try:
        req = urllib.request.Request(
            "https://labs.bible.org/api/?passage=random&type=json",
            headers={"User-Agent": "P_010"})
        with urllib.request.urlopen(req, timeout=5) as r:
            v = json.loads(r.read().decode())[0]
            return f'> *{v["bookname"]} {v["chapter"]}:{v["verse"]}*\n> "{v["text"]}"'
    except Exception as e:
        return f"> *Scripture unavailable -- check connection ({e})*"

def fetch_quote():
    try:
        req = urllib.request.Request(
            "https://zenquotes.io/api/random",
            headers={"User-Agent": "P_010"})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read().decode())
            return f'> "{d[0]["q"]}" -- *{d[0]["a"]}*'
    except Exception as e:
        return f"> *Quote unavailable -- check connection ({e})*"

def fetch_joke():
    try:
        url = "https://v2.jokeapi.dev/joke/Any?safe-mode&type=single&blacklistFlags=nsfw,racist,sexist,explicit"
        req = urllib.request.Request(url, headers={"User-Agent": "P_010"})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read().decode())
            return f'> {d["joke"]}'
    except Exception as e:
        return f"> *Humor unavailable -- check connection ({e})*"

# -- Data loaders --------------------------------------------------------------
def load_risk_config():
    if not RISK_CONFIG.exists():
        print(f"  WARNING: {RISK_CONFIG.name} not found -- posture fields will show N/A")
        return {}
    with open(RISK_CONFIG) as f:
        return json.load(f)

def load_snapshot():
    if not SNAPSHOT.exists():
        print(f"  WARNING: {SNAPSHOT.name} not found -- price table will show --")
        return {}
    with open(SNAPSHOT) as f:
        return json.load(f)

# -- Injection blocks ----------------------------------------------------------
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

# -- Template processor --------------------------------------------------------
def process_template(template_text, now, cfg, snap, scripture, quote, joke):
    """
    Replace all Templater tags in the template with real values.
    Uses markers to locate and replace whole blocks (Section 5, Section 6).
    Falls back gracefully with <!-- P_010 INJECT FAILED --> on any block error.
    """
    text = template_text

    # -- 1. Frontmatter date tags ----------------------------------------------
    text = re.sub(r'<%[^%]*tp\.date\.now\("YYYY-MM-DD"\)[^%]*%>',
                  now.strftime("%Y-%m-%d"), text)
    text = re.sub(r'<%[^%]*tp\.date\.now\("dddd"\)[^%]*%>',
                  now.strftime("%A"), text)
    text = re.sub(r'<%[^%]*tp\.date\.now\("\[Week\] WW"\)[^%]*%>',
                  f"Week {now.strftime('%W')}", text)
    text = re.sub(r'<%[^%]*tp\.date\.now\("dddd, MMMM D, YYYY"\)[^%]*%>',
                  now.strftime("%A, %B") + f" {now.day}, " + now.strftime("%Y"), text)
    text = re.sub(r'<%[^%]*tp\.date\.now\("dddd MMMM D"\)[^%]*%>',
                  now.strftime("%A %B") + f" {now.day}", text)
    text = re.sub(r'<%[^%]*tp\.date\.now\("h:mm A"\)[^%]*%>',
                  now.strftime("%I:%M %p").lstrip("0"), text)
    text = re.sub(r'<%[^%]*tp\.date\.now\("YYYY-MM-DD \[at\] h:mm A"\)[^%]*%>',
                  now.strftime("%Y-%m-%d at %I:%M %p").lstrip("0"), text)

    # -- 2. Add P_010 frontmatter fields (after tags: line) -------------------
    text = text.replace("tags: daily-flow",
        f"tags: daily-flow\np010_risk_mode: {cfg.get('risk_mode','N/A')}\n"
        f"p010_avg_posture: {fc(cfg.get('avg_posture'))}\n"
        f"p010_vxx_signal: {cfg.get('vxx_signal','N/A')}")

    # -- 3. Scripture block (multi-line <%* ... %> JS block) ------------------
    try:
        text = re.sub(r'<%\*.*?fetch\(.*?bible\.org.*?%>', scripture,
                      text, flags=re.DOTALL)
    except Exception as e:
        text = text.replace("<%*", f"<!-- P_010 INJECT FAILED: scripture ({e}) -->", 1)

    # -- 4. Quote of the Day ---------------------------------------------------
    try:
        text = re.sub(r'<%[^%]*tp\.web\.daily_quote\(\)[^%]*%>', quote, text)
    except Exception as e:
        text = text.replace("<% tp.web.daily_quote() %>",
                            f"<!-- P_010 INJECT FAILED: quote ({e}) -->")

    # -- 5. Joke / Humor block -------------------------------------------------
    try:
        text = re.sub(r'<%\*.*?jokeapi\.dev.*?%>', joke,
                      text, flags=re.DOTALL)
    except Exception as e:
        text = re.sub(r'<%\*.*?jokeapi.*?%>',
                      f"<!-- P_010 INJECT FAILED: joke ({e}) -->",
                      text, flags=re.DOTALL)

    # -- 6. Replace Section 5 body (JSON stub -> VP data table) ---------------
    try:
        sec5_block = build_section5_block(cfg, now)
        # Replace from "### ?? Bias" header through the Posture Summary cursor
        text = re.sub(
            r'### .{0,5} Bias & Regime.*?### .{0,5} Posture Summary Notes\s*<%[^%]*tp\.file\.cursor\(\d+\)[^%]*%>',
            sec5_block,
            text, flags=re.DOTALL)
    except Exception as e:
        print(f"  WARNING: Section 5 inject failed ({e})")
        text = text.replace("### ?? Bias & Regime",
                            f"<!-- P_010 INJECT FAILED: section5 ({e}) -->\n### Bias & Regime")

    # -- 7. Replace Section 6 Market Overview lines ---------------------------
    try:
        overview_table = build_market_overview(cfg, snap)
        # Replace the blank SPY/QQQ/VIX bullet lines with the full table
        text = re.sub(
            r'\*\*Market Overview\*\*\s*\n- SPY:.*?\n- QQQ:.*?\n- VIX:.*?\n',
            f"**Market Overview**\n{overview_table}\n",
            text, flags=re.DOTALL)
    except Exception as e:
        print(f"  WARNING: Section 6 market overview inject failed ({e})")

    # -- 8. Clean up remaining cursor tags and any leftover Templater tags -----
    text = re.sub(r'<%[^%]*tp\.file\.cursor\(\d+\)[^%]*%>', '', text)
    text = re.sub(r'<%\*.*?%>', '', text, flags=re.DOTALL)
    text = re.sub(r'<%.*?%>', '', text)

    return text

# -- Hardcoded fallback --------------------------------------------------------
def build_fallback_note(now, cfg, snap, scripture, quote, joke):
    """Used when no P_010_TemplateSchema_v*.md is found in Templates/."""
    rm     = cfg.get("risk_mode",    "N/A")
    avgp   = cfg.get("avg_posture")
    spyp   = cfg.get("spy_posture")
    qqqp   = cfg.get("qqq_posture")
    vxxs   = cfg.get("vxx_signal")
    vxxp   = cfg.get("vxx_posture")
    vxxn   = cfg.get("vxx_note",    "")
    cfg_ts = cfg.get("timestamp",   "N/A")
    sz     = {"FULL":"100%","HALF":"50%","OFF":"0%"}.get(rm,"N/A")
    ve     = {"BULLISH_CONFIRM":"[+]","NEUTRAL":"[=]",
              "CAUTION":"[!]","WARNING":"[!!]"}.get(vxxs or "","[=]")
    sr,srn = suggest_risk_level(rm,vxxs)
    sb,sbn = suggest_bias(avgp,vxxs)
    sc5    = build_section5_block(cfg, now)
    ov     = build_market_overview(cfg, snap)
    ds     = now.strftime("%Y-%m-%d")
    day    = now.strftime("%A")
    mn     = now.strftime("%B") + " " + str(now.day)

    return f"""---
date: {ds}
day: {day}
week: Week {now.strftime('%W')}
tags: daily-flow
p010_risk_mode: {rm}
p010_avg_posture: {fc(avgp)}
p010_vxx_signal: {vxxs or "N/A"}
---

# Daily Flow -- {day}, {mn}, {now.strftime("%Y")}

> [!warning] Template not found
> No P_010_TemplateSchema_v*.md found in Templates/ -- using built-in fallback layout.
> Add template to restore full formatting.

**Energy Level Today:** (1-5 stars)

---

## 1 -- Inspiration & Warmup

### Daily Prayer & Scripture
{scripture}

### Quote of the Day
{quote}

### Humor of the Day
{joke}

---

## 5 -- Market Posture -- {ds}

{sc5}

---

## 6 -- TOS + VantagePoint Analysis

### Pre-Market Overview -- {now.strftime("%I:%M %p")}

{ov}

**VantagePoint Watchlist Signals**

| Ticker | VP Signal | Pred High | Pred Low | My Read |
|--------|-----------|-----------|----------|---------|
|        |           |           |          |         |
|        |           |           |          |         |

---

## 7 -- Trade Execution Log

| Time | Ticker | Direction | Entry | Stop | Exit | P&L | Notes |
|------|--------|-----------|-------|------|------|-----|-------|
|      |        |           |       |      |      |     |       |

---

## Daily Rollover / Review

**Wins Today** --

**Improve Tomorrow** --

**Tasks Carried Forward**
- [ ]

---
*Auto-generated (fallback) by P_010 v5.0 at {now.strftime("%Y-%m-%d %H:%M")}*
"""

# -- Main ----------------------------------------------------------------------
def main():
    now = datetime.now()
    print("=" * 70)
    print("P_010 DAILY NOTE WRITER v2.0 -- Template-Driven")
    print("=" * 70)
    print(f"Time  : {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Guards
    if SKIP_FLAG.exists():
        print("SKIP_TODAY.flag found -- skipping note creation"); return 0
    if now.weekday() >= 5:
        print(f"Today is {now.strftime('%A')} -- markets closed, skipping"); return 0

    # Load data
    cfg  = load_risk_config()
    snap = load_snapshot()
    print(f"  Risk Mode  : {cfg.get('risk_mode','N/A')}")
    print(f"  Avg Posture: {cfg.get('avg_posture','N/A')}")
    print(f"  VXX Signal : {cfg.get('vxx_signal','N/A')}")
    print()

    # Fetch live content
    print("  Fetching scripture..."); scripture = fetch_scripture()
    print("  Fetching quote...");     quote     = fetch_quote()
    print("  Fetching humor...");     joke      = fetch_joke()
    print()

    # Find template
    template_path, version = find_latest_template()
    if template_path:
        print(f"  Template   : {template_path.name} (v{version})")
        template_text = template_path.read_text(encoding="utf-8")
        note = process_template(template_text, now, cfg, snap, scripture, quote, joke)
        source = f"template {template_path.name}"
    else:
        print("  WARNING: No P_010_TemplateSchema_v*.md found -- using hardcoded fallback")
        note = build_fallback_note(now, cfg, snap, scripture, quote, joke)
        source = "hardcoded fallback"

    # Write note
    NOTES_FOLDER.mkdir(parents=True, exist_ok=True)
    fn = now.strftime(DATE_FORMAT) + ".md"
    tf = NOTES_FOLDER / fn

    if tf.exists():
        print()
        print("=" * 70)
        print(f"  NOTE ALREADY EXISTS -- SKIPPING")
        print(f"  File   : {tf}")
        print(f"  Action : Note will NOT be overwritten")
        print(f"  To regenerate: delete {fn} from TradingJournal/ and re-run morning batch")
        print("=" * 70)
        return 0

    tf.write_text(note, encoding="utf-8")

    print()
    print("=" * 70)
    print("DAILY NOTE CREATED")
    print("=" * 70)
    print(f"  File   : {tf}")
    print(f"  Size   : {tf.stat().st_size} bytes")
    print(f"  Source : {source}")
    print(f"  Open Obsidian -- note ready in TradingJournal/")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())




