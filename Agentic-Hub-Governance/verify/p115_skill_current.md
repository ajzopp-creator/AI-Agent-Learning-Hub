---
name: p115-project-context
description: >
  P_115 Buy The Dip — project-specific operating rules, critical paths, schema
  shorthand, and anti-patterns. Load at the start of ANY session involving P_115
  work. Triggers on any reference to P_115, P_116, P_117, P_118, P_910, P_920, Buy The Dip, STEP 1/2/3, LogEntry, HybridTier,
  AsymmetricSetup, Fund Verification, PA Stop, 27-column tracker, P_920 EOD scan,
  or P_115_buyTheDipChart. Always read BEFORE writing any code or file path.
---

# P_115 Project Context

## Purpose & Pairs With

Auto-loading protection layer for P_115 — Buy The Dip (oversold recovery,
anticipation entries). Contains concise rules, critical paths, schema
shorthand, and anti-patterns. Full domain rules live in the SIP and
architecture doc, loaded on demand.

| File | Role |
| :---- | :---- |
| `docs/SESSION_INITIALIZATION_PROMPT.md` (v3.5) | INIT sequence — steps only. Read directly by path, never via project_knowledge_search (returns fragments mixed with other docs). |
| `docs/P_115_System_Architecture.v1.0.md` | Full spec, EC log, scoring detail — on demand |
| `docs/P_115_BuyTheDip_MasterDoc_v1_0.md` | Original strategy doc (superseded by Architecture doc for domain rules) |
| `Quick_Reference_Prompts_v9_4_1.md` | Shorthand command formats for STEP 1/2/3 + batch |
| `Tracker_Log_Schema_v9_4_0_1.md` | 27-column locked schema detail |
| `P_115_ Asset Sizing Requirements.md` | SUPERSEDED 2026-07-24 -- pointer only, sizing is P_400's job now (P_400 architecture doc Section 3.3) |
| `OPTIONS_RISK_METHODOLOGY.md` | REFERENCE ONLY 2026-07-24 -- options gates belong to P_400; never invoke in a P_115 session |
| `python-project-architecture` SKILL (Hub) | Layer Boundary Standard — config → schemas → domain → infra → application |
| `peh-handoff` SKILL (Hub) | 4-minute MCP timeout → Claude Code handoff protocol |
| **THIS FILE** | Always-active protection rules |

---

## Critical Paths

| Path | Resolution |
| :---- | :---- |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| Project root | `<Hub>\projects\P_115_BuytheDipTradingSystem\` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` (shared conda env — never suggest a new venv) |
| Account params | `<Hub>\projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` — read live, never hard-code |
| Risk config | `<Hub>\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json` — re-read fresh before every packet emission and before writing MarketDirection, not just at INIT |
| Vault output | `<Hub>\trading_journal\TradeManagement\P115\` |
| Signal packets (P_400 handoff) | `<Hub>\trading_journal\TradeOrderManagement\signals\*_v2.0.json` |
| PEH verify dir | `<Hub>\Agentic-Hub-Governance\verify\` — write `run_this_P115_<TS>.py` + `_context.txt` here BEFORE every MCP Python call or file write (peh-handoff v1.4, timestamped names, broadened scope) |
| ThinkScript source | `P_115_buyTheDipChart_V15.ts` (current) — TOS custom indicator, PA Stop / HybridTier / AsymmetricSetup computed on-chart |
| Fund verification source | `stockanalysis.com/stocks/[ticker]/financials/ratios/` — never trust TOS Fund on BUY/ASYM without this recheck (TOS confirmed systematically inflated, AEO 4/21 fail case) |

**Signal-contract import (Hub canonical, no sys.path hack):**
`from shared_resources.python_utils.signal_schemas import SignalV2`
`from shared_resources.python_utils.vault_interface import write_to_vault`

---

## LogEntry Field Order (LOCKED — V110 standard)

```
Position 1: Symbol
Position 2: FundamentalsTier (ADJUSTED — includes 200-MA penalty)
Position 3: AnalysisTier
Position 4: CandleTier
Position 5: SetupScore
Position 6: STR flag (SellTheRip, valid range -2 to 2 — corrected 7/8/26, NOT 0/1 or -1 to 2)
Position 7: Verdict (BUY / ASYM / PASS)

Format: LogEntry: [SYMBOL] | [Fund] | [Anal] | [Candle] | [Setup] | [STR] | [Verdict]
Example: LogEntry: CYTK | 2 | 3 | 2 | 3 | 0 | BUY
```
State the field-position parse explicitly before scoring ("Symbol=X, Fund=Y,
Anal=Z, Candle=W, Setup=V, STR=U") — EC-011 (MRAM/POET/AAOI 5/27/26) was a
silent misread of position 2 as STR, wrongly auto-rejecting three BUY-quality
tickers as Fund=0 value traps. LogEntry is authoritative over the chart's
Final Verdict display bar if the two conflict — flag, don't silently pick one.

---

## Scoring Chain (V110 → V111)

```
FundamentalsTier (0-4, ADJUSTED)
  ROE>15%=20pts | Debt/Cap<60%=15pts | FCF>0=10pts
  200-MA penalty: 0-3% below=0 | 3-10%=-1 | 10-20%=-2 | >20%=Fund forced to 0 (auto-reject, value trap)

CandleTier (0-3)
  T3=candle+vol+STR+RSI+MTF | T2=candle+(vol OR STR OR RSI) | T1=candle only | T0=none

SetupScore (0-4)
  CandleTier>=2 | ModScore>=70 | STR>0 | RSI>RSI[1]

AnalysisTier (1-4) — mapped from SetupScore (>=4=T4, >=3=T3, >=2=T2, else T1)

HybridTier = AnalysisTier + FundamentalsTier
  >=6 -> BUY
  AsymmetricSetup (Anal>=3 AND Fund>=2 AND MTF/wickAlign/rsiBounce4H) -> ASYM
  neither -> PASS
```

**Fund Verification (V110.2 -> V111):** recompute Fund via stockanalysis.com
ROE/Debt-Cap/FCF on any Fund>=2 BUY/ASYM. Flag if recomputed value sits
>1 tier below submitted.
- V110.2 (4/22/26): P_115 BUY/ASYM — mandatory
- V111 (6/18/26): extended to P_118 BUY/ASYM (mandatory, via P_115 recheck) and
  P_117 BUY/ASYM (only when an optional P_115 recheck was actually performed)
- P_920 BUY/ASYM: applies per V111 logic, **not yet consistently enforced** —
  open gap, first BVS signal (7/6/26) logged without the recheck
- Post-Earnings Auto-Flag (V110.3) applies to ALL four strategies, checks
  earnings date only (not Fund tier) — do not conflate with V110.2/V111
- No re-verify on PASS rows

**PA Stop (v1.2, `P_115_buyTheDipChart_V14.ts`, `def paStop`):** primary =
swing low over 10-bar lookback minus 0.1x ATR buffer; fallback = Entry - 2xATR
when structure low is NaN or above entry. Always use the chart's displayed
PA Stop label — never recompute independently.

---

## 27-Column Tracker Schema (LOCKED)

```
Date | Symbol | SignalSource | Step1Verdict | PatternType | BreakoutVerdict |
BreakoutVolumeMultiple | DistributionDayCount | FollowThroughDay | MarketDirection |
RSvsSPY | FundamentalsTier | AnalysisTier | CandleTier | SetupScore | LiquidityTier |
Traded | EntryPrice | TPLevel | SLLevel | StopLevel | RiskPct | AccountBalance |
Outcome | RecheckStatus | SimulationNotes | Comments
```

Rules: column order never reorders; all 27 required on every row including
PASS; Symbol = ticker only, never expand with company name (breaks P_020 join
keys); Date = M/D/YYYY; MarketDirection = risk_mode value from P_010 JSON only
(FULL/HALF/OFF — HOT is a derived session state, never persisted, never
written here); PatternType/BreakoutVerdict = `--` for P_115 (belongs to
P_118); Step1Verdict vocabulary is BUY/ASYM/PASS ("No Signal" deprecated,
grandfathered pre-5/23/2026 rows only).

---

## Anti-Patterns (Forbidden by Construction)

1. **Misreading LogEntry field position 2 as STR** — it's FundamentalsTier.
   State the explicit parse before scoring. EC-011.
2. **PascalCase vault-write dict keys** — silently dropped by Pydantic; can
   return True/PASS with an empty record. All keys snake_case.
3. **`traded` field as Python bool** — must be the string `"Y"`/`"N"`; bool
   raises a Pydantic validation error.
4. **Numeric optional fields as `'--'`** — must be `None`, not the string
   placeholder used in the human-facing tracker.
5. **Trusting `write_to_vault()`'s True/PASS return as proof of a real write**
   — a structurally empty record can still return True/PASS. Always read the
   written file back to confirm fields landed.
6. **Wrong-case or missing Symbol on vault write** — drives the filename;
   silently writes as `UNKNOWN` and still returns PASS, no error.
7. **Treating a same-day `write_to_vault(..., overwrite=False)` False return
   as failure** — `overwrite=False` is the default; False on a re-run usually
   means the file already exists (idempotent protection). Verify file content
   directly before treating it as an error.
8. **Trusting TOS Fund tier on a BUY/ASYM without the stockanalysis.com
   recheck** — TOS Fund is systematically inflated (AEO 4/21 confirmed fail,
   TOS=4 vs actual=2).
9. **Using an INIT-snapshot risk_mode on any P_115 output** -- posture must be
   re-read fresh from `P_010_RiskConfig.json` before every packet emission and
   before writing MarketDirection to a tracker row, not just once at INIT.
   P_115 does not size; sizing-time posture is P_400's concern.
10. **Reclassifying a P_910-sourced signal as SignalSource=P_117** — P_910
    signals log `SignalSource=P_910` directly (fixed in spreadsheet 7/6/26).
11. **Treating a mid-session LogEntry/chart mismatch as a data-entry error**
    during market hours — classify as "Flipped" (live intraday change)
    instead.
12. **Treating a uniform STR=-2 across an entire batch as N individual ticker
    errors** — that pattern is a regime signal (falling knife / deep bounce),
    not per-ticker noise. Same logic applies to a P_920 scanner output that
    comes back systematically STR=-2.
13. **Producing a P_115 STEP 2 sizing block at all** -- as of 2026-07-24
    (architecture v1.3) P_115 STEP 2 is signal emission ONLY: build and emit
    the SIGNAL_V2 packet, nothing else. No three-gate sizing, no R:R
    validation, no options viability gates, no TP/SL rendering, no options
    chain lookup, no premium-cap math. All of it is P_400's (P_400
    architecture doc Section 3.1). STEP 3 output stays in the locked compact
    labeled block format -- never prose.
14. **Asking the user for P_118 PatternType** — read from chart LogEntry or
    chart image; never ask, never default to `--` on a BUY/ASYM row.
15. **Calling `windows-mcp:PowerShell` for Python and waiting past 4 minutes**
    — on timeout, hand off to Claude Code immediately per `peh-handoff` SKILL;
    do not retry MCP, do not write inline PowerShell as a substitute.
16. **Building a vault-write data dict from only the deprecated `date` field**
    — `P115Record` requires `signal_date`, `run_date`, `run_ts`, and
    `written_by` (convention: `"P_11X/session"`, matching prior records like
    `2026-07-06_JPM.md`). A dict with only `date` will fail Pydantic
    validation on write. Include all four on every vault-write script, not
    just the display-facing tracker fields.

17. **Delivering a single-ticker BUY/ASYM verdict without the 27-column
    tab-delimited tracker row** -- happened on ANET (P_118, 2026-07-08): the
    vault write went out but the Excel-ready row was never output, caught
    only when Tony asked for it after the fact. The tab-delimited row is
    owed immediately alongside the vault write on every BUY/ASYM, not just
    on batch STEP 1 runs -- a single-ticker STEP 1->2->3 flow does not
    exempt it.
---

## Layer Architecture (Hub Standard)

```
python/
├── config.py                  ← All constants and paths, no logic
├── schemas.py                 ← Pydantic models — non-temporary file I/O
├── domain/
│   └── signal_builder.py      ← build_record(), scoring/sizing logic — no I/O
├── infrastructure/
│   └── tracker_writer.py      ← sys.path-clean since WO-P000-E2.003 (2026-06-09)
├── application/
│   └── emit_signal.py         ← orchestration: computes atr_adjusted_stop,
│                                  calls signal_builder + write_to_vault
├── cli.py
└── launcher.bat
```

Imports resolve through the `hub_shared` editable install
(`shared_resources`, `hub_lib`, `obsidian_writers` all real installed
packages as of WO-P000-E2.002/E2.003) — no sys.path side-channel inserts
remain in P_115's own files. Never reintroduce one.

---

## AI Behavioral Rules

**Must:**
1. State the explicit LogEntry field-position parse before applying any
   scoring logic (EC-011 guard).
2. Capture Fund/Anal/Candle/Setup/STR/Verdict the instant they're pasted —
   never claim missing data that exists earlier in the current conversation.
3. Re-read `P_010_RiskConfig.json` fresh before every packet emission and before writing MarketDirection -- never carry the INIT snapshot forward.
4. Trigger the stockanalysis.com Fund recheck on every Fund>=2 BUY/ASYM per
   the active V110.2/V111 scope table.
5. Read the vault file back after any `write_to_vault()` call to confirm
   fields actually landed — a True/PASS return alone is not proof.
6. Use snake_case for every vault-write dict key; `traded` as string
   `"Y"`/`"N"`; numeric optionals as `None` not `'--'`.
7. Write `run_this_P115_<TS>.py` + `_context.txt` (timestamped, peh-handoff v1.4)
   to the PEH verify dir before any MCP Python call or file write; hand off to
   Claude Code on a 4-minute timeout.
8. STEP 2 = emit the SIGNAL_V2 packet, full stop (architecture v1.3, 2026-07-24). Output STEP 3 in the locked compact labeled block format -- never prose.
9. Chart Final Verdict overrides LogEntry BUY/ASYM if they conflict during
   market hours — but flag the divergence, don't silently resolve it.

**Must Not:**
1. Ask the user for P_118 PatternType — read it from the chart.
2. Assume STR range is 0/1 or -1 to 2 — valid range is -2 to 2 (corrected 7/8/26; -2 is a legitimate falling-knife/regime reading, not out of range).
3. Perform ANY sizing, R:R validation, options-gate check, options chain
   lookup, or premium-cap calculation inside a P_115 session -- every one of
   those is P_400's as of 2026-07-24 (architecture v1.3). This includes the
   5%-cap-applies-to-premium-not-notional rule, which is now P_400's to apply.
   If a P_115 surface still instructs otherwise, that surface is stale --
   flag it, do not obey it.
4. Persist `HOT` to `MarketDirection` in a vault write or tracker row — HOT
   is a derived session state, never a JSON-persisted risk_mode value.
5. Treat a batch-wide uniform STR=-2 as individual ticker misreads.
6. Skip the Fund Verification recheck on a P_920 BUY/ASYM signal — this is a
   currently-open enforcement gap (flagged for retroactive correction), not a
   sanctioned exception.
7. Retry a stalled `windows-mcp:PowerShell` Python call past ~4 minutes —
   hand off immediately.

---

## Signal Source Quick Reference

| Source | PatternType | BreakoutVerdict | Step1Verdict |
| :---- | :---- | :---- | :---- |
| P_115 | `--` | `--` | BUY / ASYM / PASS |
| P_116 | `Bounce` | `Bounce` | BUY / PASS |
| P_118 | READ FROM CHART | BUY / ASYM / PASS | BUY / ASYM / PASS |
| P_910 (scan) | logs `SignalSource=P_910` directly | — | — |
| P_920 (EOD scan) | feeds P_115 pre-market workflow; carries real P_115-style diagnostics | — | — |

---

## INIT Fast Path (target: 2 Windows-MCP calls)

Root cause of slow INIT (2026-08-06): system-doc-initializer's Hub-wide
P_000_SYSTEM_DOCUMENTATION.md pull was running on every P_115 INIT with
nothing P_115-specific in it; SIP was fetched via project_knowledge_search
then re-read directly because search returned fragments mixed with other
docs; WO review was a directory listing + 6 individual file reads instead
of one grep. 8+ round trips before a relay stall made it worse.

1. Skip the Hub-wide P_000_SYSTEM_DOCUMENTATION.md pull on routine P_115
   trade sessions -- p115-project-context already carries what matters.
   Only pull it for explicit cross-project/governance work.
2. Read `docs/SESSION_INITIALIZATION_PROMPT.md` directly by path -- never
   project_knowledge_search it first.
3. WO review (Step 0.5) = one `Select-String -Pattern "P_115"` pass across
   `work_orders\*.md`, not a directory listing plus individual reads.
4. Steps 1-3 (ET time, account params, posture) = one combined PowerShell
   call -- already the working pattern, keep it.
5. Ping (`Write-Output "ping"`) before any call expected to run long; if
   ping itself doesn't return in a few seconds, stop and report relay-down
   rather than let the real call run to the 4-min ceiling.
## Session-Start Checklist

- [ ] Call `tool_search` for PowerShell/Windows-MCP first (SIP STEP 0) —
      never claim web/Desktop status before this check
- [ ] Run the full SIP v3.4+ 7-step sequence — never the condensed 3-step
      summary in `P_115_System_Architecture.v1.0.md` Section 3.3 (stale)
- [ ] Steps 0.5 through 6 are one uninterruptible block — no file writes,
      lesson logs, or actions between them
- [ ] Confirm current `risk_mode` from `P_010_RiskConfig.json` is re-read
      live before any packet emission, not carried over from INIT
- [ ] On any LogEntry paste: state the field-position parse explicitly
      before scoring
- [ ] Follow INIT Fast Path above -- target 2 Windows-MCP calls, not 8+

---

## When to Consult the Full Architecture Doc

Load `docs/P_115_System_Architecture.v1.0.md` for:
- Full EC-001 through EC-011+ log with root-cause detail
- Section 8 workflows (STEP 1/2/3) in full prose
- Section 9.3/9.4 complete schema + data-integrity rule set
- Section 10 known-good reference examples + backtesting thresholds
- Appendix F full configuration reference (thresholds, gate constants)

Do NOT load reflexively — this SKILL covers routine STEP 1/2/3 operation.

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (drafting)
- **Update trigger:** New EC-XXX entry in the architecture doc, a schema/
  scoring version bump (V110.x, V111+), or a vault-write lesson discovered
  in a live session (add here same session, per Hub-wide rule in
  `WO_COMPLETION_GATE.md`)

## Changelog

### 2026-08-06
- **INIT Fast Path added (Tony directive, live session).** INIT was taking
  8+ Windows-MCP-adjacent round trips: Hub-wide P_000_SYSTEM_DOCUMENTATION.md
  pull (nothing P_115-specific in it), SIP fetched via project_knowledge_search
  then re-read directly (search returned fragments mixed with other docs), WO
  review as a directory listing + 6 file reads instead of one grep. A relay
  stall (3 x 4-min timeouts) piled on top. Fix: routine P_115 sessions skip
  the Hub-wide pull, read SIP directly by path, one grep pass for WO review.
  Target 2 Windows-MCP calls total. See INIT Fast Path section above.

### 2026-08-03
- **Imperative sweep for architecture v1.3/v1.4 (Tony directive).** The
  7/24 removal of P_115 order management had been recorded in this file's
  changelog and file table but never propagated into the operative rules.
  Five live instructions (file-table options row, Anti-Pattern 9, 13, 17,
  Must 3, Must 8, Must Not 3, session checklist) still directed P_115 to
  size positions and run options gates. Missed live on ZION 8/3/26: a full
  three-gate block, a 7.09:1 R:R, and an options-chain request were all
  produced in a P_115-engine session. Root cause recorded as: a changelog
  entry is a record, not a rule -- version changes must be swept into
  Musts, Must Nots, anti-patterns, and workflow command lines, not just
  logged. Rule added: STEP 2 = emit only.

### 2026-07-24
- P_115 Order Management removed (Tony directive). Architecture doc
  Section 8.2 changed from Position Sizing to Signal Emission -- P_400
  owns all sizing/R:R/stop/target/order-formatting decisions now
  (P_400 architecture doc Section 3.1), confirmed P_400's screen-all is
  fully source-agnostic (no P_400-side change needed for P_116/P_118/
  P_910/P_920 packets). schemas.py archived (dead code, unused
  VALID_SOURCES gate that would've blocked non-P_115/P_300 source tags
  if ever reconnected). File table row above corrected -- it pointed at
  POSITION_SIZING_THREE_GATE_REFERENCE.md, a file that never existed
  on disk; actual file is P_115_ Asset Sizing Requirements.md, now
  marked superseded. Note: found but did NOT fix -- LogEntry Field Order
  section below still says STR valid range is -1 to 2, but the 2026-07-08
  (update 4) entry below corrected it to -2 to 2; out of scope for this
  session's task, flagged for a future pass.

### 2026-07-24 (correction, same day)
- v1.3's Section 8.2 Step 3 wrongly had signal_source varying by
  P_115/P_116/P_118/P_910/P_920 (Tony caught this). Corrected in the
  architecture doc (v1.4): P_115 is the analytical process (V110 scoring
  engine) -- P_116/P_118/P_910/P_920 are scan sources / chart-pattern
  variants that feed candidates INTO P_115's analysis, not separate
  emitters. signal_source is always P_115 in the P_400 packet. strategy
  still carries the setup-type distinction (dip_buy/breakout/
  mean_reversion/support_bounce); scan/variant provenance is a
  27-column-tracker-level detail only. The schemas.py archival itself
  still stands (genuinely dead code either way) but the "would block
  P_116/P_118/P_910/P_920 tags" rationale in the entry below is wrong --
  those tags should never have gone in signal_source to begin with.
### 2026-07-08 (update 4)
- STR valid range corrected again: -2 to 2, not -1 to 2 as the 7/6/26
  correction had it. -2 is a legitimate falling-knife/regime reading, not
  out of range -- confirmed by repeated live LogEntry data across multiple
  tickers (WYFI, ANET-batch PASS rows) and the architecture doc's own
  FISV-style Cause A worked example, which uses STR=-2 as the falling-knife
  trigger alongside Fund=0. LogEntry Field Order section and Must-Not #2
  both updated.
### 2026-07-08 (update 3)
- Anti-pattern #17 added: the 27-column tab-delimited tracker row is owed
  on every BUY/ASYM immediately alongside the vault write, even on a
  single-ticker STEP 1->2->3 flow -- not just on batch STEP 1 runs. Missed
  live on ANET (P_118 BUY, 2026-07-08); vault write landed clean but the
  Excel row was never output until Tony asked for it retroactively.
### 2026-07-08 (update 2)
- Anti-pattern #16 added: `P115Record` requires `signal_date`/`run_date`/
  `run_ts`/`written_by` -- the deprecated `date` field alone fails Pydantic
  validation. Discovered live via PEH handoff on the ANET P_118 BUY write
  (2026-07-08_ANET.md, version 1, confirmed clean via readback -- no
  double-write despite an earlier MCP 4-minute timeout on the same script).
  Claude Code fixed the missing fields using the `P_118/session`
  `written_by` convention already established in `2026-07-06_JPM.md`.

### 2026-07-08- Initial build. Created under WO-P000-E6.001 (Gap 3 of the 2026-07-06
  context-engineering KB review — P_115 was one of three active projects
  with no project-context layer). Content sourced from
  `SESSION_INITIALIZATION_PROMPT.md` v3.4, `P_115_System_Architecture.v1.0.md`
  (EC log, scoring chain, schema), and accumulated session memory (vault-write
  lessons, STR range correction 7/6/26, P_910 SignalSource fix, P_920 Fund
  Verification gap).

---

**End of P_115 Project Context SKILL**
