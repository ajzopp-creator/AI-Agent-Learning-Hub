# P_020 Future Enhancements

**Project:** P_020 AJZ Strategies Performance Analysis System
**Owner:** Anthony Zoppi (AJZ Strategies LLC)
**Last Updated:** 2026-09-02

---

## Status Legend

- ✅ **DONE** — Implemented and validated
- 🔵 **NEXT** — Top of the queue, ready to start
- 📋 **BACKLOG** — Approved, awaits scheduling
- 💭 **IDEA** — Captured, not yet scoped

---

## Recently Completed

| ID | Description | Completed |
|---|---|---|
| ✅ | SQLite schema + `reason` / `signal_strength` columns + indexes | 2026-04-21 |
| ✅ | `domain/thinklog_parser.py` — open-vocabulary `[WHY] [SIG]` parser | 2026-04-21 |
| ✅ | `infrastructure/thinklog_reader.py` — TOS ThinkLog CSV record-format reader with same-day concat and ±3-day auto-filter | 2026-04-28 |
| ✅ | `application/paper_import.py` — Symbol+Date join from TOS Account Statement → ThinkLog CSV → DB | 2026-04-28 |
| ✅ | Extended `_apply_stop_prices()` (`application/ingest_pipeline.py`) to all accounts except IRA9885 — live AJZ trades previously never got a stop_price at all, gate was hard-coded to PAPER only. 5 new regression tests, 75/75 passing. No WO filed. | 2026-09-02 |
| ✅ | SKILL.md v1.5 — locks in the dual-CSV (Account Statement + ThinkLog) flow | 2026-04-28 |
| ✅ | End-to-end round-trip test (AMR test trade 2026-04-28) | 2026-04-28 |

---

## 🔵 NEXT — Ready to Pick Up Next Session

### NEXT-1: Lock in WHY and SIG vocabularies
**Priority:** High — blocks tag emitter and analytical filtering
**Estimate:** 30 minutes (no code, just decision + documentation)

The parser is open-vocabulary by design, but Tony needs to commit to a finite
list of WHY codes (one per trading system + situational tags) and SIG codes
(signal strength A/B/C/X with definitions) so:

1. ThinkLog entries are consistent week to week
2. The future tag emitter knows what to emit
3. SQL filtering by `reason` returns meaningful groups

**Deliverable:** `SESSION_INITIALIZATION_PROMPT_v2_7.md` updated with:
- WHY codes table — code → trading system / situation it represents
- SIG codes table — A/B/C/X with one-line definitions of what each means to Tony
- Worked example: `0428: [BTD] [A] tight bounce off 50DMA, RSI 28, 3:1 R:R`

**Starter draft Tony reviews and edits:**

| WHY | Maps to | Use when... |
|---|---|---|
| BTD | P_115 Buy The Dip | Standard BTD scan signal |
| OIL | P_116 Options Income Launchpad | OIL-style credit/income setup |
| EXT | P_117 External recommendations | Anyone else's trade idea (newsletter, email, friend) |
| EZB | P_118 Eddie Z Breakouts | Eddie Z breakout signal |
| VPT | P_300 VantagePoint | VP signal triggered |
| SNT | Sunday Night Trader (BigTrends) | Weekly BigTrends pick |
| DAY | Day trades | Intraday only, flat by close |
| IFFY | Situational | Setup didn't fully trigger but you took it |
| LEARN | Situational | Educational trade — testing a theory |
| CROWDED | Situational | Everyone else is in this |
| FOMO | Situational | Be honest with yourself |
| REVENGE | Situational | Trying to make back a loss — review these brutally |

| SIG | Meaning |
|---|---|
| A | High conviction — all signals aligned, prefers entry |
| B | Standard — system fired, no obvious red flags |
| C | Marginal — system fired but something feels off |
| X | Counter-signal — taking it anyway, flag for review |

---

### NEXT-2: Update `v_trade_summary` view to expose tag columns
**Priority:** Medium — needed before any analytical SQL works
**Estimate:** 15 minutes

The view currently aggregates trades + exits but doesn't expose `reason` or
`signal_strength`. After NEXT-1 locks in vocabulary, the view needs both
columns added so dashboards and ad-hoc queries can filter on them.

**Deliverable:** Migration script `migration_view_add_tag_cols.py` that
DROPs and CREATEs `v_trade_summary` with `reason` and `signal_strength`
selected from the trades table.

**SQL to add:**
```sql
SELECT t.reason, t.signal_strength, ...
```

**Acceptance:**
```sql
SELECT system, reason, COUNT(*), AVG(realized_pnl)
FROM v_trade_summary
WHERE account_id = 'PAPER' AND reason IS NOT NULL
GROUP BY system, reason;
```
returns rows once paper trades with tags exist in the DB.

---

## 📋 BACKLOG — Approved, Not Scheduled

### BACKLOG-1: System-Generated Tag Emitter
**Captured:** 2026-04-26
**Estimate:** 90 minutes
**Affects:** P_115, P_116, P_117, P_118, P_300, SNT, Day projects

When any trading system project fires a BUY or PAPER TRADE signal, it should
emit a ready-to-paste tag string in the canonical ThinkLog format. Tony copies,
pastes into the TOS ThinkLog entry, places the trade. Zero typing, zero
remembering vocabulary.

**Architecture:**
- Shared helper at `C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\python\tag_emitter.py`
- Each system project imports `emit_tag(why, sig, free_text)` and calls it from its alert/output stage
- Each project owns its WHY constant (P_115 → `BTD`, P_116 → `OIL`, etc.)
- Optional: auto-copy to Windows clipboard via `pyperclip` so Tony just Ctrl-V into TOS

**Depends on:** NEXT-1 (vocabulary locked)

**Why not scheduled yet:**
- Crosses project boundaries (P_115 → shared_resources → P_020)
- Requires reading P_115 code I haven't seen yet
- Vocabulary needs to be locked first

---

### BACKLOG-2: SNVXX Filter in Schwab Ingest
**Priority:** Low
**Affects:** Schwab API ingest pipeline (live account)

Money market sweeps (SNVXX) are inserting as trades in the live ingest. They
should be filtered out at the parsing stage.

---

### BACKLOG-3: Token Expiry Detection in `P_020_Weekly_Update.bat`
**Priority:** Low

Current batch silently fails when Schwab token has expired. Add a pre-flight
check that probes the token and prompts for re-auth if expired, before
running the full pipeline.

---

### BACKLOG-4: HTML Performance Dashboard Auto-Regenerate
**Status:** HTML generator exists; not yet wired to `analyze` command

Wire the existing HTML dashboard generator into the weekly `analyze` step
so it regenerates automatically on every weekly update.

---

### BACKLOG-5: Phase 2C — `schwab_positions.py`
**Priority:** Medium

Open positions + balance snapshot puller. Outputs current portfolio state
to a CSV for the dashboard.

---

### BACKLOG-6: Phase 3D — Excel Power Query View Layer
**Priority:** Low

Lets Tony view DB content in Excel without exporting CSVs.

---

### BACKLOG-7: Phase 3E — AI Review Stats Exports
Six CSVs for AI-assisted weekly review:
- `summary_by_system.csv`
- `equity_curve.csv`
- `r_distribution.csv`
- `monthly_summary.csv`
- `open_positions.csv`
- `drawdown.csv`

---

### BACKLOG-8: Live Account ThinkLog Tagging
**Priority:** Low (after paper validates)

Currently tag parsing only runs in `paper_import.py`. Once Tony is happy with
how tags work on paper, extend the same logic to live account ingestion.
The `account_id contains '6348'` check in `paper_import.py` would relax;
Schwab live ingest would gain a ThinkLog join step.

---

## 💭 IDEAS — Captured, Not Vetted

- **Auto-categorize untagged historical trades** — train a small classifier on tagged trades, suggest tags for the 324 pre-2026 TOS_Import rows
- **Tag drift report** — weekly check that vocabulary used in ThinkLog matches the locked vocabulary in `SESSION_INITIALIZATION_PROMPT_v2_7.md`
- **Mobile capture** — quick tag-string generator on phone for trades placed away from desk
- **TOS Watchlist column that emits tag string** — instead of a separate Python project, a TOS thinkscript column that generates the WHY+SIG string from scan conditions

---

## How This Document Is Used

- Read this file at the start of any P_020 session before deciding what to work on
- "NEXT" items are the ones to pick first
- BACKLOG items are committed work waiting for time
- IDEAS are unvetted — promote to BACKLOG only after a quick scope check
- Move completed items up to "Recently Completed" with date and link to the artifact

---

*Last session: 2026-09-02 — closed 12 pre-2026 legacy trades; fixed live-account stop_price gap (see Recently Completed); see `tasks\todo.md` for full session history since 4/28 (WO ledger and todo.md have been the primary tracking since, this file lagged)*
