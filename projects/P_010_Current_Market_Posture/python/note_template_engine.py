"""
P_010 Daily Note Writer -- Template Engine
Split from P_010_write_daily_note.py (WO-P010-E1.003 housekeeping, 2026-08-10).
Template discovery, Templater-tag substitution, and the hardcoded fallback note
used when no P_010_TemplateSchema_v*.md is found.
"""

import re
from pathlib import Path

from note_content_builders import (
    suggest_risk_level, suggest_bias, fc,
    build_section5_block, build_market_overview,
)

# -- Paths ---------------------------------------------------------------------
VAULT_PATH = Path(r"C:\Users\Trader\Documents\AJZStrategies_TradingJournal\Trading Journal")
TEMPLATES  = VAULT_PATH / "TradingJournal" / "Templates"


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


def build_fallback_note(now, cfg, snap, scripture, quote, joke):
    """Used when no P_010_TemplateSchema_v*.md is found in Templates/."""
    rm     = cfg.get("risk_mode",    "N/A")
    avgp   = cfg.get("avg_posture")
    vxxs   = cfg.get("vxx_signal")
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
