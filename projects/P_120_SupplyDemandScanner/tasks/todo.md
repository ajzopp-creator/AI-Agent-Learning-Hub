# P_120 Supply & Demand Scanner — Task Queue

Project root: `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_120_SupplyDemandScanner\`

---

## Current State — 2026-08-03

**Status:** Architecture converted from source PDF. Folder tree created. Phase 1 planned, NOT written. No code exists yet.

### Decisions locked

| # | Decision | Rationale |
|---|---|---|
| D-001 | Project ID is **P_120**, not P300 | Source PDF self-brands as "P300"; P_300 is VantagePoint Pattern Recognition. All references scrubbed, including DB name `p300_trading.db` -> `P_120_scanner.db` |
| D-002 | **4H timeframe dropped** | Schwab has no native 4H; would require resampling 30-min bars. Source lessons state the method is timeframe-agnostic |
| D-003 | **Weekly = market structure; Daily = zones, entry, stop, target** | Weekly carries HH/HL vs LH/LL for the Part 1 failure filter. Daily carries everything else |
| D-004 | 30-min bars, if ever added, are **execution-time only** — never a scan timeframe | Keeps candle cache small and the scan deterministic |
| D-005 | Batch runs **after the close**, orders placed next morning | Source PDF said 30 min before close; the current daily candle is not closed at that time |
| D-006 | Demand-zone top is a config toggle, not a constant | Source lesson allows wick-top or body-top; PDF hard-coded wick-top. `DEMAND_TOP_MODE = "wick" \| "body"` |
| D-007 | No project `secrets\` folder | Hub convention keeps credentials in hub-root `.env`. Schwab refresh-token cache lives in `data\cache\` and must be gitignored |

### Folder tree — CREATED 2026-08-03

```
P_120_SupplyDemandScanner\
├── config\                    <- parameter docs (.md), not Python
├── data\
│   ├── cache\                 <- P_120_scanner.db, candle cache, token cache
│   └── processed\
├── docs\
│   ├── notes\
│   └── processes\             <- run_daily_scan.md, refresh_schwab_token.md
├── logs\
├── outputs\
│   ├── alerts\
│   └── reports\
├── python\
│   ├── application\__init__.py
│   ├── domain\__init__.py
│   ├── infrastructure\__init__.py
│   └── tests\
├── tasks\
└── tos_scripts\
```

### Phase 1 file plan — APPROVED, NOT YET WRITTEN

Target: `...\P_120_SupplyDemandScanner\python\`

| File | Subfolder | Lines |
|---|---|---|
| `config.py` | — | 95 |
| `schemas.py` | — | 185 |
| `schwab_auth.py` | `infrastructure\` | 160 |
| `schwab_client.py` | `infrastructure\` | 220 |
| `price_history_repo.py` | `infrastructure\` | 185 |
| `universe_repo.py` | `infrastructure\` | 90 |
| `fetch_candles_pipeline.py` | `application\` | 125 |
| `cli.py` | — | 130 |
| `requirements.txt` | — | 12 |
| `P_120_DailyScan.bat` | — | 15 |
| `P_120_DailyScan_mcp.ps1` | — | 25 |

11 files, 1,242 lines. All under the 300-line ceiling.

### Next actions (in order)

1. Add `.gitignore` entry for `data\cache\` before any token is written.
2. Register the Schwab developer app; put client ID + secret in hub-root `.env`.
3. Write Phase 1 in delivery order: config -> schemas -> infrastructure -> application -> cli -> .bat -> .ps1 -> requirements.
4. First live call: `pricehistory` for one symbol, daily, to confirm the OAuth round-trip before building the universe loop.

### Open questions — answer before Phase 2

- **Q-001** — Ticker universe source and size for the daily scan. S&P 500 was assumed from the source PDF but never confirmed.
- **Q-002** — Retest dwell-time threshold (see L-001 item 2). Source lesson gives direction only ("longer = worse"), no number.
- **Q-003** — Whether zone status history is retained indefinitely or pruned after N days.

---

## Phase Roadmap

| Phase | Scope | Status |
|---|---|---|
| 1 | Schwab OAuth, REST client, candle cache, universe | Planned, not written |
| 2 | Zone detection, structure, scoring, risk levels | Corrections logged in `lessons.md` L-001 |
| 3 | LangGraph nodes + graph wiring | Not started |
| 4 | Backtest, rate-limit resilience, live batch | Viable on Daily/Weekly only (see L-003) |
