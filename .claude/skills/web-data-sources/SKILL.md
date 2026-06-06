---
name: web-data-sources
description: >
  Verified working web data sources for trading workflows. Load this skill whenever
  Claude needs to look up option chain data (bid, ask, open interest, delta, last
  price, spread), company fundamentals (ROE, debt-to-capital, free cash flow, V110.2
  Fund verification), or live stock price quotes. Triggers on option contract symbols
  like CRML260618C12.5 or TWLO260116C145, references to "option chain", "bid/ask",
  "OI", "delta", "spread %", "live quote", "current price", "fundamentals lookup",
  "Fund verify", "ROE check", or mentions of stockanalysis.com, ChartExchange, or
  Yahoo Finance v8 API. Also triggers when the user mentions Yahoo Finance or
  Barchart as option chain sources, so Claude redirects to a source that actually
  works via web_fetch. Use this BEFORE attempting any web_fetch on financial data.
---

# web-data-sources
## AI-Agent-Learning-Hub Edition

---

## Purpose

Document the small set of URLs that actually return usable data through `web_fetch`,
and the set that does not, so Claude stops wasting cycles on JavaScript-rendered
pages. Built after a May 14, 2026 session where Yahoo and Barchart returned page
shells but Perplexity found CRML option data on ChartExchange in seconds.

The rule: try the verified source first. If the request maps to a documented
endpoint below, build the URL and fetch it directly — do not search-then-fetch.

---

## When to Trigger

Load this skill before any of the following:

- User pastes an option contract symbol (pattern: `TICKER + YYMMDD + C/P + strike`)
- User asks for bid/ask, OI, delta, last price, or spread on an option
- User requests Fund verification per V110.2 (BUY or ASYM signal with claimed Fund >= 2)
- User asks for live ROE, debt/capital, FCF, or any financial ratio
- User asks for live or recent stock quote outside of TOS
- Claude is about to call `web_fetch` on a finance.yahoo.com or barchart.com options URL

---

## Source 1 — ChartExchange (Option Chains)

**URL pattern:**
```
https://chartexchange.com/symbol/nasdaq-{TICKER}/optionchain/?date={YYYYMMDD}
```

For NYSE-listed names, try `nyse-{TICKER}` if the nasdaq path 404s.

**What it returns via web_fetch:**
Plain HTML tables, server-rendered. Both Calls and Puts in separate tables, ITM
and OTM sections, sorted by strike. Fields per row:
- Strike, Price (last), Change %, Volume, Open Interest, Last trade date, Contract Name

**What it does NOT include:**
- Bid / Ask quotes (need supplementary source — see Source 1b)
- Delta and other greeks
- Real-time updates (15 min delay typical)

**Example — CRML June 18, 2026:**
```
https://chartexchange.com/symbol/nasdaq-crml/optionchain/?date=20260618
```
Returns the full chain with OI 7,966 on the C12.50 strike, last price 1.60.

---

## Source 1b — Supplementary Bid/Ask/Delta

ChartExchange does not show bid/ask or delta in the basic chain view. When those
fields are required (any options viability check needs all three gates), request
the values from the user via TOS paste in this format:

```
__.{CONTRACT_SYMBOL} B/A:{BID}/{ASK} OI:{OI} Delta:{DELTA}__
```

The OI from ChartExchange is usually sufficient to skip asking for that field —
only request bid/ask and delta.

If the user already has a Perplexity quote handy for bid/ask, that is also acceptable.

---

## Source 2 — stockanalysis.com (Fundamentals / V110.2 Fund Verification)

**URL pattern:**
```
https://stockanalysis.com/stocks/{ticker}/financials/ratios/
https://stockanalysis.com/stocks/{ticker}/statistics/
```

Lowercase ticker. Statistics page often loads faster than ratios page and contains
the same ROE, debt/equity, and FCF data needed for V110 Fund recompute.

**What to extract:**
- ROE (percent)
- Debt / Equity or Debt / Capital (percent)
- Free Cash Flow (positive or negative)

**V110 Fund recompute rules:**
| Metric | Threshold | Points |
|--------|-----------|--------|
| ROE | > 15% | 20 |
| Debt / Capital | < 60% | 15 |
| FCF | > 0 | 10 |

Tier mapping: 40-45 = 4 | 30-39 = 3 | 20-29 = 2 | 10-19 = 1 | 0-9 = 0

**Apply 200-MA penalty if known:**
- 0-3% below 200-MA: no penalty
- 3-10% below: -1.0
- 10-20% below: -2.0
- > 20% below: Fund forced to 0 (BEAR/AVOID zone)

**V110.2 verification gate:**
- If recomputed Fund is more than 1 tier below user-submitted value → STOP, flag
  before STEP 2 output, wait for user resolution
- If within 1 tier → proceed normally

**Financial sector tickers (banks, brokers, insurers):**
Structurally carry higher leverage. Note balance-sheet caveat when applying the
standard debt/capital threshold. Borderline discrepancies within V110.2 tolerance
are usually expected for this sector.

---

## Source 3 — Yahoo Finance v8 API (Live Stock Price)

**URL pattern:**
```
https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?interval=1d&range=5d
```

Use `range=5d` for daily data. Do NOT use `range=1d` for daily change calculations —
the intraday `chartPreviousClose` field returns stale values.

**PowerShell parse template:**
```powershell
$r = Invoke-RestMethod "https://query1.finance.yahoo.com/v8/finance/chart/$ticker?interval=1d&range=5d"
$meta = $r.chart.result[0].meta
$q = $r.chart.result[0].indicators.quote[0]
# Available fields: $meta.regularMarketPrice, $meta.previousClose, $q.open, $q.high, $q.low, $q.close, $q.volume
```

Returns numeric data without HTML parsing required.

---

## Sources That FAIL (Skip These)

Do not waste a web_fetch call on these for option or quote data — they return
JavaScript-rendered shells with empty tables:

| Source | Reason |
|--------|--------|
| finance.yahoo.com/quote/.../options | JS-rendered table, returns empty shell |
| www.barchart.com/stocks/quotes/.../options | JS-rendered, full navigation menu only |
| www.nasdaq.com/market-activity/stocks/.../option-chain | JS-rendered, unverified but assumed broken |
| investing.com options pages | JS-rendered, login-walled for full data |
| public.com options pages | Marketing copy only, no live data in HTML |

If the user explicitly mentions one of these, redirect to ChartExchange.

---

## Workflow — Parse an Option Contract Symbol

Given `CRML260618C12.5`:

| Component | Value |
|-----------|-------|
| Ticker | CRML |
| Year | 2026 |
| Month | 06 |
| Day | 18 |
| Type | C (call) — P would be put |
| Strike | 12.5 |

Build the ChartExchange URL:
```
https://chartexchange.com/symbol/nasdaq-crml/optionchain/?date=20260618
```

Call web_fetch. Find the row in the Calls table where Strike = `12.50 C`. Read
Price, Volume, OI, Last date. Report the values.

If bid/ask/delta are needed, request from user (Source 1b format).

---

## Workflow — V110.2 Fund Verification (Fast Path)

Triggered by: P_115, P_116, P_117, or P_118 BUY or ASYM verdict with claimed
Fund >= 2.

1. Build URL: `https://stockanalysis.com/stocks/{ticker}/statistics/`
2. Call web_fetch
3. Extract ROE, Debt/Equity, FCF from page content
4. Score per V110 thresholds (table above)
5. Apply 200-MA penalty if known
6. Compare recomputed Fund vs user-submitted Fund
7. If more than 1 tier below submitted → FLAG before STEP 2, wait for resolution
8. If within 1 tier → proceed normally to STEP 2

Note ROE percent and FCF sign in the SimulationNotes column for audit.

---

## Edge Cases

| Situation | Action |
|-----------|--------|
| ChartExchange returns 404 on nasdaq path | Retry with nyse path |
| Both nasdaq and nyse paths 404 | Note in response, request TOS paste |
| Strike not listed on chain | Note as illiquid, recommend stock-only |
| stockanalysis.com page blocked or empty | Use web_search with site:stockanalysis.com prefix |
| Ticker is a recent IPO | Fundamentals may be unavailable — note and ask user |
| Crypto or international ticker | These endpoints US-equity only — skip skill |
| Yahoo v8 API rate limited | Wait or fall back to web_search with ticker name |

---

## What This Skill Does NOT Do

- Does NOT replace TOS as the primary execution data source
- Does NOT provide real-time tick-level quotes (15 min delay typical on free sources)
- Does NOT cover futures, forex, or options on indices
- Does NOT replace user-provided bid/ask data when accuracy is critical

---

## Last Updated

May 14, 2026 — Created after Yahoo/Barchart web_fetch failures on CRML option
chain lookup. Perplexity surfaced ChartExchange as a reliable alternative. Locked
in URL patterns for the three verified sources and the list of broken ones to
skip.
