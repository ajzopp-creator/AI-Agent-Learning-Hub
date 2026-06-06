# P_800 Obsidian Interface Layer Architecture
**Project ID:** P_800 (cross-project integration)
**Version:** 1.0
**Created:** 2026-05-22
**Owner:** Anthony Zoppi
**Status:** In Development — Phase 5

---

## 1. PURPOSE

### 1.1 What This Document Covers
The Obsidian Interface Layer is a read/write data surface that connects all
AJZ Strategies trading systems to a single queryable vault. Each upstream
project writes a normalized schema to a dedicated vault folder. Obsidian
Bases queries that data. A single Dashboard.md note is the daily entry point,
replacing the freeform daily note.

### 1.2 Scope

**In scope:**
- Vault folder structure for all five data streams (P_115, P_300, P_400, P_020, KB)
- Normalized YAML frontmatter schema per project
- Six Bases view definitions
- Dashboard.md design
- Python export layer (one writer module per project)
- Knowledge base capture and linking

**Out of scope:**
- Signal generation logic (owned by P_115, P_300, P_400)
- Trade execution (owned by P_400 → Schwab API)
- Excel tracker modification (P_020 SQLite is SoT; Obsidian is read mirror)
- P_010 market posture generation (P_800 reads only)

### 1.3 Definitions

| Term | Definition |
|------|-----------|
| Interface Layer | Obsidian vault acting as unified display/query surface fed by upstream projects |
| Base | Obsidian Bases `.base` file — defines a filtered, sorted, columnar view of notes |
| Writer Module | Python script per project that normalizes source data → YAML frontmatter `.md` |
| SoT | Source of Truth — the upstream system (Excel, SQLite, TXT) that owns the data |
| WHY code | P_020 tag identifying the trading system that generated a signal (BTD, VPT, etc.) |
| SIG code | P_020 tag for signal conviction level (A=high, B=standard, C=marginal, X=counter) |

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Data Flow

```
[P_115 Excel Tracker]──────────────┐
[P_300 TXT Reports]────────────────┤
[P_400 Lifecycle TXT]──────────────┼──► [Python Writer Modules]
[P_020 SQLite DB]──────────────────┤         │
[Web Clipper / AI Summaries]───────┘         │
                                             ▼
                              [trading_journal/TradeManagement/]
                              [trading_journal/KnowledgeBase/]
                                             │
                                             ▼
                                    [Obsidian Bases]
                                             │
                                             ▼
                                    [Dashboard.md]
                                    (daily entry point)
```

### 2.2 Vault Folder Structure

```
trading_journal/
├── Templates/
│   └── P_800_Daily_Flow.md            ← kept for manual journal use
├── Bases/
│   ├── P115_Evaluations.base
│   ├── P300_Signals.base
│   ├── P400_Trades.base
│   ├── P020_Performance.base
│   ├── Open_Positions.base
│   └── KB_Articles.base
├── TradeManagement/
│   ├── P115/                          ← one .md per evaluation
│   ├── P300/                          ← one .md per signal report
│   ├── P400/                          ← one .md per trade lifecycle
│   └── P020/                          ← one .md per closed trade
├── KnowledgeBase/                     ← articles + AI summaries
└── Dashboard.md                       ← daily entry point
```

### 2.3 File Naming Conventions

| Project | Pattern | Example |
|---------|---------|---------|
| P_115 | `TradeManagement/P115/YYYY-MM-DD_SYMBOL.md` | `P115/2026-05-22_AAPL.md` |
| P_300 | `TradeManagement/P300/YYYY-MM-DD_TICKER.md` | `P300/2026-05-20_BAC.md` |
| P_400 | `TradeManagement/P400/YYYY-MM-DD_TICKER.md` | `P400/2026-05-22_NVDA.md` |
| P_020 | `TradeManagement/P020/YYYY-MM-DD_SYMBOL_ACCT.md` | `P020/2026-05-15_AMR_AJZ6348.md` |
| KB | `KnowledgeBase/YYYY-MM-DD_SLUG.md` | `KB/2026-05-22_fed-rate-impact.md` |

---

## 3. DATA DESIGN — SCHEMAS

### 3.1 P_115 Evaluation Schema

Source: Excel tracker (27 LOCKED columns → snake_case YAML)
Writer: `p115_writer.py`

```yaml
---
source: P_115
date: 2026-05-22
symbol: AAPL
signal_source: P_115
step1_verdict: BUY           # BUY | ASYM | PASS
pattern_type: "--"
breakout_verdict: "--"
breakout_volume_multiple: null
distribution_day_count: null
follow_through_day: null
market_direction: STANDARD
rs_vs_spy: null
fundamentals_tier: 3
analysis_tier: 3
candle_tier: 2
setup_score: 5
liquidity_tier: null
traded: N                    # Y | N
entry_price: null
tp_level: null
sl_level: null
stop_level: null
risk_pct: null
account_balance: 32812
outcome: null                # TP Hit | SL Hit | Manual | null
recheck_status: null
simulation_notes: ""
comments: ""
why_code: BTD                # P_020 WHY vocabulary (added at trade entry)
sig_code: null               # P_020 SIG vocabulary (added at trade entry)
---
```

### 3.2 P_300 Signal Schema

Source: TXT report files
Writer: `p300_writer.py`

```yaml
---
source: P_300
date: 2026-05-20
ticker: BAC
anchor_date: 2026-05-20
signal: PASS                 # BUY | SELL | PASS
signal_horizon: 5            # horizon where signal fires
generated_dt: "2026-05-20 22:39"
h5_win_rate: 0.600
h5_mean_ret: 2.07
h5_z_score: 0.000
h5_class: PASS
h7_win_rate: 0.600
h7_mean_ret: 2.69
h7_z_score: 0.000
h7_class: PASS
h10_win_rate: 0.600
h10_mean_ret: 1.52
h10_z_score: 0.000
h10_class: PASS
h15_win_rate: 0.550
h15_mean_ret: 2.43
h15_z_score: -0.090
h15_class: PASS
h20_win_rate: 0.600
h20_mean_ret: 3.32
h20_z_score: 0.000
h20_class: PASS
top_analog_1: SPY
top_analog_2: DE
top_analog_3: GS
top_comp_dist_1: 10.314
n_matches: 20
---
```

Body: full TXT narrative block (preserved as-is below frontmatter)

### 3.3 P_400 Trade Lifecycle Schema

Source: TXT trade input + council output
Writer: `p400_writer.py`
Status: schema v0.1 — evolves as P_400 is built

```yaml
---
source: P_400
date: 2026-05-22
ticker: NVDA
account_id: AJZ6348
council_verdict: Approve     # Approve | Approve with Caution | Block | Override Required
risk_mode: FULL
entry_price: null
stop_price: null
target_1: null
target_2: null
position_size: null          # contracts or shares
order_type: null             # Limit | Market
lifecycle_status: PENDING    # PENDING | OPEN | PARTIAL | CLOSED
entry_date: null
close_date: null
realized_pnl: null
why_code: BTD
sig_code: B
p115_linked: true            # cross-reference to P_115 note
p300_linked: false
---
```

Body: TOS narrative block + Schwab payload reference

### 3.4 P_020 Performance Schema

Source: SQLite `v_trade_summary` view
Writer: `p020_writer.py`

```yaml
---
source: P_020
date: 2026-05-15
symbol: AMR
account_id: AJZ6348
system: P_115
why_code: BTD
sig_code: A
open_date: 2026-05-10
close_date: 2026-05-15
entry_price: 42.30
exit_price: 45.10
qty: 100
realized_pnl: 280.00
realized_R: 1.87
risk_amount: 150.00
outcome: TP Hit              # TP Hit | SL Hit | Manual
days_held: 5
signal_strength: A
---
```

### 3.5 Knowledge Base Schema

Source: Web Clipper, PDF upload, AI summary paste
Writer: manual (Templater template) or Claude MCP injection

```yaml
---
source: KB
date: 2026-05-22
title: "Fed Rate Impact on Regional Banks"
kb_type: Article             # Article | AI Summary | Research | Transcript
origin: Web Clipper          # Web Clipper | PDF | AI Summary | Manual
ai_summarized: true
tags: [macro, banking, rates]
ticker_relevance: [BAC, JPM]
sector: Financials
market_regime: null
linked_trades: []
---
```

---


---
*Continued in: P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md*
