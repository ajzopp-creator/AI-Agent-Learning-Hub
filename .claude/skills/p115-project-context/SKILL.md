---
name: p115-project-context
description: >
  P_115 Buy The Dip â€” project-specific operating rules, critical paths, schema
  shorthand, and anti-patterns. Load at the start of ANY session involving P_115
  work. Triggers on any reference to P_115, P_116, P_117, P_118, P_910, P_920, Buy The Dip, STEP 1/2/3, LogEntry, HybridTier,
  AsymmetricSetup, Fund Verification, PA Stop, 27-column tracker, P_920 EOD scan,
  or P_115_buyTheDipChart. Always read BEFORE writing any code or file path.
---

# P_115 Project Context

## Purpose & Pairs With

Auto-loading protection layer for P_115 â€” Buy The Dip (oversold recovery,
anticipation entries). Contains concise rules, critical paths, schema
shorthand, and anti-patterns. Full domain rules live in the SIP and
architecture doc, loaded on demand.

| File | Role |
| :---- | :---- |
| `docs/SESSION_INITIALIZATION_PROMPT.md` (v3.5) | INIT sequence â€” steps only. Read directly by path, never via project_knowledge_search (returns fragments mixed with other docs). |
| `docs/P_115_System_Architecture.v1.3.md` | Full spec, EC log, scoring detail â€” on demand |
| `docs/P_115_BuyTheDip_MasterDoc_v1_0.md` | Original strategy doc (superseded by Architecture doc for domain rules) |
| `Quick_Reference_Prompts_v9_4_1.md` | Shorthand command formats for STEP 1/2/3 + batch |
| `Tracker_Log_Schema_v9_4_0_1.md` | 27-column locked schema detail |
| `P_115_ Asset Sizing Requirements.md` | SUPERSEDED 2026-07-24 -- pointer only, sizing is P_400's job now (P_400 architecture doc Section 3.3) |
| `OPTIONS_RISK_METHODOLOGY.md` | REFERENCE ONLY 2026-07-24 -- options gates belong to P_400; never invoke in a P_115 session |
| `python-project-architecture` SKILL (Hub) | Layer Boundary Standard â€” config â†’ schemas â†’ domain â†’ infra â†’ application |
| `peh-handoff` SKILL (Hub) | 4-minute MCP timeout â†’ Claude Code handoff protocol |
| `tasks/lessons.md` | Durable trade/process lessons -- READ AT INIT STEP 0.5 (folded in 2026-08-17 after sitting orphaned since 2026-06-09 creation). APPEND new durable lessons here same session when one surfaces. |
| **THIS FILE** | Always-active protection rules |

---

## Critical Paths

| Path | Resolution |
| :---- | :---- |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| Project root | `<Hub>\projects\P_115_BuytheDipTradingSystem\` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` (shared conda env â€” never suggest a new venv) |
| Account params | `<Hub>\projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` â€” read live, never hard-code |
| Risk config | `<Hub>\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json` â€” re-read fresh before every packet emission and before writing MarketDirection, not just at INIT |
| Vault output | `<Hub>\trading_journal\TradeManagement\P115\` |
| Chaikin enrichment | `<Hub>\shared_resources\chaikin_enrichment\` (shared, P_800-owned) -- batch via Hub-root `RunChaikinBatch.ps1 -Schema P115`; real Ack 2026-07-25 (EMR/OGN/PH enriched, read back confirmed, WO-P800-E4.001) |
| Signal packets (P_400 handoff) | `<Hub>\trading_journal\TradeOrderManagement\signals\*_v2.0.json` |
| PEH verify dir | `<Hub>\Agentic-Hub-Governance\verify\` â€” write `run_this_P115_<TS>.py` + `_context.txt` here BEFORE every MCP Python call or file write (peh-handoff v1.4, timestamped names, broadened scope) |
| ThinkScript source | `P_115_buyTheDipChart_V15.ts` (current) â€” TOS custom indicator, PA Stop / HybridTier / AsymmetricSetup computed on-chart |
| Fund verification source | `stockanalysis.com/stocks/[ticker]/financials/ratios/` â€” never trust TOS Fund on BUY/ASYM without this recheck (TOS confirmed systematically inflated, AEO 4/21 fail case) |

**Signal-contract import (Hub canonical, no sys.path hack):**
`from shared_resources.python_utils.signal_schemas import SignalV2`
`from shared_resources.python_utils.vault_interface import write_to_vault`

---

## LogEntry Field Order (LOCKED â€” V110 standard)

```
Position 1: Symbol
Position 2: FundamentalsTier (ADJUSTED â€” includes 200-MA penalty)
Position 3: AnalysisTier
Position 4: CandleTier
Position 5: SetupScore
Position 6: STR flag (SellTheRip, valid range -2 to 2 â€” corrected 7/8/26, NOT 0/1 or -1 to 2)
Position 7: Verdict (BUY / ASYM / PASS)

Format: LogEntry: [SYMBOL] | [Fund] | [Anal] | [Candle] | [Setup] | [STR] | [Verdict]
Example: LogEntry: CYTK | 2 | 3 | 2 | 3 | 0 | BUY
```
State the field-position parse explicitly before scoring ("Symbol=X, Fund=Y,
Anal=Z, Candle=W, Setup=V, STR=U") â€” EC-011 (MRAM/POET/AAOI 5/27/26) was a
silent misread of position 2 as STR, wrongly auto-rejecting three BUY-quality
tickers as Fund=0 value traps. LogEntry is authoritative over the chart's
Final Verdict display bar if the two conflict â€” flag, don't silently pick one.

---

## Scoring Chain (V110 â†’ V111)

```
FundamentalsTier (0-4, ADJUSTED)
  ROE>15%=20pts | Debt/Cap<60%=15pts | FCF>0=10pts
  200-MA penalty: 0-3% below=0 | 3-10%=-1 | 10-20%=-2 | >20%=Fund forced to 0 (auto-reject, value trap)

CandleTier (0-3)
  T3=candle+vol+STR+RSI+MTF | T2=candle+(vol OR STR OR RSI) | T1=candle only | T0=none

SetupScore (0-4)
  CandleTier>=2 | ModScore>=70 | STR>0 | RSI>RSI[1]

AnalysisTier (1-4) â€” mapped from SetupScore (>=4=T4, >=3=T3, >=2=T2, else T1)

HybridTier = AnalysisTier + FundamentalsTier
  >=6 -> BUY
  AsymmetricSetup (Anal>=3 AND Fund>=2 AND MTF/wickAlign/rsiBounce4H) -> ASYM
  neither -> PASS
```

**Fund Verification (V110.2 -> V111):** recompute Fund via stockanalysis.com
ROE/Debt-Cap/FCF on any Fund>=2 BUY/ASYM. Flag if recomputed value sits
>1 tier below submitted.
- V110.2 (4/22/26): P_115 BUY/ASYM â€” mandatory
- V111 (6/18/26): extended to P_118 BUY/ASYM (mandatory, via P_115 recheck) and
  P_117 BUY/ASYM (only when an optional P_115 recheck was actually performed)
- P_920 BUY/ASYM: applies per V111 logic, **not yet consistently enforced** â€”
  open gap, first BVS signal (7/6/26) logged without the recheck
- Post-Earnings Auto-Flag (V110.3) applies to ALL four strategies, checks
  earnings date only (not Fund tier) â€” do not conflate with V110.2/V111
- No re-verify on PASS rows

**PA Stop (v1.2, `P_115_buyTheDipChart_V14.ts`, `def paStop`):** primary =
swing low over 10-bar lookback minus 0.1x ATR buffer; fallback = Entry - 2xATR
when structure low is NaN or above entry. Always use the chart's displayed
PA Stop label â€” never recompute independently.

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
(FULL/HALF/OFF â€” HOT is a derived session state, never persisted, never
written here); PatternType/BreakoutVerdict = `--` for P_115 (belongs to
P_118); Step1Verdict vocabulary is BUY/ASYM/PASS ("No Signal" deprecated,
grandfathered pre-5/23/2026 rows only).

---

## Anti-Patterns (Forbidden by Construction)

Full incident narratives for all of these live in the architecture doc's EC log (see "When to Consult" below) -- this list is rule + reference only.

1. **LogEntry position 2 = FundamentalsTier, not STR.** State the parse explicitly before scoring. (EC-011)
2. **PascalCase vault-write dict keys** -- Pydantic silently drops them; can return True/PASS on an empty record. snake_case only.
3. **`traded` as Python bool** -- must be string `"Y"`/`"N"`; bool raises a Pydantic error.
4. **Numeric optionals as `'--'`** -- must be `None`, not the tracker placeholder string.
5. **Trusting `write_to_vault()`'s True/PASS return as proof** -- always read the file back to confirm fields landed.
6. **Wrong-case/missing Symbol on vault write** -- drives the filename; silently writes `UNKNOWN`, still returns PASS.
7. **Treating a same-day `write_to_vault(overwrite=False)` False return as failure** -- usually means the file already exists (idempotent); verify content before calling it an error.
8. **Trusting TOS Fund tier without the stockanalysis.com recheck** -- TOS is systematically inflated (AEO 4/21: TOS=4 vs actual=2).
9. **Using an INIT-snapshot risk_mode on any output** -- re-read `P_010_RiskConfig.json` fresh before every packet emission and MarketDirection write. P_115 doesn't size; sizing-time posture is P_400's concern.
10. **Reclassifying a P_910-sourced signal as SignalSource=P_117** -- P_910 logs `SignalSource=P_910` directly (fixed 7/6/26).
11. **Treating a mid-session LogEntry/chart mismatch as a data-entry error** -- classify as "Flipped" during market hours.
12. **Treating a uniform batch-wide STR=-2 as N individual errors** -- it's a regime signal, not per-ticker noise. Same for a P_920 scanner output.
13. **Producing any P_115 STEP 2 sizing block** -- STEP 2 is emission only (v1.3, 2026-07-24): build and emit SIGNAL_V2, nothing else. No sizing, R:R, options gates, TP/SL, or premium math -- all P_400's. STEP 3 stays in the locked compact block format, never prose.
14. **Asking the user for P_118 PatternType** -- read from chart LogEntry or image; never ask, never default `--` on BUY/ASYM.
15. **Waiting past 4 minutes on a stalled `windows-mcp:PowerShell` Python call** -- hand off to Claude Code immediately per `peh-handoff`; never retry MCP or substitute inline PowerShell.
16. **Building a vault-write dict from only the deprecated `date` field** -- `P115Record` needs `signal_date`/`run_date`/`run_ts`/`written_by` (convention `"P_11X/session"`); `date` alone fails Pydantic validation.
17. **Delivering a BUY/ASYM verdict without the 27-column tracker row** -- owed immediately alongside the vault write, every time, even single-ticker flows (missed live on ANET, 2026-07-08).
---

## Layer Architecture (Hub Standard)

```
python/
â”œâ”€â”€ config.py                  â† All constants and paths, no logic
â”œâ”€â”€ schemas.py                 â† Pydantic models â€” non-temporary file I/O
â”œâ”€â”€ domain/
â”‚   â””â”€â”€ signal_builder.py      â† build_record(), scoring/sizing logic â€” no I/O
â”œâ”€â”€ infrastructure/
â”‚   â””â”€â”€ tracker_writer.py      â† sys.path-clean since WO-P000-E2.003 (2026-06-09)
â”œâ”€â”€ application/
â”‚   â””â”€â”€ emit_signal.py         â† orchestration: computes atr_adjusted_stop,
â”‚                                  calls signal_builder + write_to_vault
â”œâ”€â”€ cli.py
â””â”€â”€ launcher.bat
```

Imports resolve through the `hub_shared` editable install
(`shared_resources`, `hub_lib`, `obsidian_writers` all real installed
packages as of WO-P000-E2.002/E2.003) â€” no sys.path side-channel inserts
remain in P_115's own files. Never reintroduce one.

---

## AI Behavioral Rules

**Must:**
1. State the explicit LogEntry field-position parse before applying any
   scoring logic (EC-011 guard).
2. Capture Fund/Anal/Candle/Setup/STR/Verdict the instant they're pasted â€”
   never claim missing data that exists earlier in the current conversation.
3. Re-read `P_010_RiskConfig.json` fresh before every packet emission and before writing MarketDirection -- never carry the INIT snapshot forward.
4. Trigger the stockanalysis.com Fund recheck on every Fund>=2 BUY/ASYM per
   the active V110.2/V111 scope table.
5. Read the vault file back after any `write_to_vault()` call to confirm
   fields actually landed â€” a True/PASS return alone is not proof.
6. Use snake_case for every vault-write dict key; `traded` as string
   `"Y"`/`"N"`; numeric optionals as `None` not `'--'`.
7. Write `run_this_P115_<TS>.py` + `_context.txt` (timestamped, peh-handoff v1.4)
   to the PEH verify dir before any MCP Python call or file write; hand off to
   Claude Code on a 4-minute timeout.
8. STEP 2 = emit the SIGNAL_V2 packet, full stop (architecture v1.3, 2026-07-24). Output STEP 3 in the locked compact labeled block format -- never prose.
9. Chart Final Verdict overrides LogEntry BUY/ASYM if they conflict during
   market hours â€” but flag the divergence, don't silently resolve it.

**Must Not:**
1. Ask the user for P_118 PatternType â€” read it from the chart.
2. Assume STR range is 0/1 or -1 to 2 â€” valid range is -2 to 2 (corrected 7/8/26; -2 is a legitimate falling-knife/regime reading, not out of range).
3. Perform ANY sizing, R:R validation, options-gate check, options chain
   lookup, or premium-cap calculation inside a P_115 session -- every one of
   those is P_400's as of 2026-07-24 (architecture v1.3). This includes the
   5%-cap-applies-to-premium-not-notional rule, which is now P_400's to apply.
   If a P_115 surface still instructs otherwise, that surface is stale --
   flag it, do not obey it.
4. Persist `HOT` to `MarketDirection` in a vault write or tracker row â€” HOT
   is a derived session state, never a JSON-persisted risk_mode value.
5. Treat a batch-wide uniform STR=-2 as individual ticker misreads.
6. Skip the Fund Verification recheck on a P_920 BUY/ASYM signal â€” this is a
   currently-open enforcement gap (flagged for retroactive correction), not a
   sanctioned exception.
7. Retry a stalled `windows-mcp:PowerShell` Python call past ~4 minutes â€”
   hand off immediately.

---

## Signal Source Quick Reference

**SignalSource is set by the message's BATCH HEADER, never by the chart.**
A "P_118 STEP 1 [...]" header governs every ticker in that batch, including
trailing "STEPS 1-2 [TICKER EP:x]" entries with no new header of their own --
even when the chart shown is running the P_115_BuyTheDipChart indicator.
P_118 candidates are REQUIRED to run the P_115 recheck engine (V111), so
seeing that chart/indicator on a P_118 ticker is expected, not a signal the
ticker is P_115-sourced. Repeated twice same session 2026-08-20 (CDNA, V),
corrected in-session but never written durably, then repeated again in a new
session 2026-08-21 (INCY, MA, V) -- see lessons.md 2026-08-21 entry. If the
batch-header scope is genuinely ambiguous, ask; do not infer SignalSource
from the chart.

| Source | PatternType | BreakoutVerdict | Step1Verdict |
| :---- | :---- | :---- | :---- |
| P_115 | `--` | `--` | BUY / ASYM / PASS |
| P_116 | `Bounce` | `Bounce` | BUY / PASS |
| P_118 | READ FROM CHART | BUY / ASYM / PASS | BUY / ASYM / PASS |
| P_910 (scan) | logs `SignalSource=P_910` directly | â€” | â€” |
| P_920 (EOD scan) | feeds P_115 pre-market workflow; carries real P_115-style diagnostics | â€” | â€” |

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
   `work_orders\*.md`, combined with a `tasks\lessons.md` read in the SAME
   PowerShell call (2026-08-17: lessons.md now wired into Step 0.5 -- do
   not split into a separate round trip), not a directory listing plus
   individual reads.
4. Steps 1-3 (ET time, account params, posture) = one combined PowerShell
   call -- already the working pattern, keep it.
5. Ping (`Write-Output "ping"`) before any call expected to run long; if
   ping itself doesn't return in a few seconds, stop and report relay-down
   rather than let the real call run to the 4-min ceiling.
6. Read `tasks/lessons.md` once at INIT -- small local read, fold into the
   item 4 combined call, no added round trip.

## Session-Start Checklist

- [ ] Call `tool_search` for PowerShell/Windows-MCP first (SIP STEP 0) â€”
      never claim web/Desktop status before this check
- [ ] Run the full SIP v3.4+ 7-step sequence â€” never the condensed 3-step
      summary in `P_115_System_Architecture.v1.3.md` Section 3.3 (stale)
- [ ] Steps 0.5 through 6 are one uninterruptible block â€” no file writes,
      lesson logs, or actions between them
- [ ] Confirm current `risk_mode` from `P_010_RiskConfig.json` is re-read
      live before any packet emission, not carried over from INIT
- [ ] On any LogEntry paste: state the field-position parse explicitly
      before scoring
- [ ] Follow INIT Fast Path above -- target 2 Windows-MCP calls, not 8+
- [ ] Read `tasks/lessons.md` at INIT -- apply any durable lesson logged there to this session
- [ ] Confirm `tasks/lessons.md` was read in the Step 0.5 call and any 14-day-recent entries surfaced in the Step 4 summary

---

## When to Consult the Full Architecture Doc

Load `docs/P_115_System_Architecture.v1.3.md` for:
- Full EC-001 through EC-011+ log with root-cause detail
- Section 8 workflows (STEP 1/2/3) in full prose
- Section 9.3/9.4 complete schema + data-integrity rule set
- Section 10 known-good reference examples + backtesting thresholds
- Appendix F full configuration reference (thresholds, gate constants)

Do NOT load reflexively â€” this SKILL covers routine STEP 1/2/3 operation.

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (drafting)
- **Update trigger:** New EC-XXX entry in the architecture doc, a schema/
  scoring version bump (V110.x, V111+), or a vault-write lesson discovered
  in a live session (add here same session, per Hub-wide rule in
  `WO_COMPLETION_GATE.md`)

## Changelog

### 2026-08-24
- **Chaikin Power Gauge batch path added (Completion Gate skill-file gap from WO-P800-E4.001).** P_115 ran a real Chaikin enrichment Ack on 2026-07-25 (EMR/OGN/PH via `RunChaikinBatch.ps1 -Schema P115`) but this skill never referenced it -- WO-P800-E4.001 sat OWNER_DONE with that Completion Gate item unsatisfied for P_115 specifically (P_300's skill file was already correct). Fix: Critical Paths row added. Also merged two duplicate `tasks/lessons.md` file-table rows into one (compression pass).

### 2026-08-17
- **`tasks/lessons.md` wired into INIT (orphaned mechanism fix).** File existed,
  self-described "Read at every INIT STEP 3," but was never in this skill's
  file table or Session-Start Checklist -- nothing actually read it. Same
  failure shape as the 2026-08-03 changelog-vs-rule gap. Fix: added to file
  table, added INIT Fast Path item 6, added checklist bullet.

### 2026-08-17
- **`tasks/lessons.md` wired into Step 0.5, file table row added.** File
  existed since 2026-06-09 with its own header saying "read at every INIT"
  -- nothing ever did. Root cause: same class of gap as the 8/3 Anti-Pattern
  sweep (a written instruction is not an executed step until it's in the
  operative Musts/steps, not just documented). Trigger: two live process
  failures same session that a maintained lessons file exists specifically
  to prevent -- (1) used a stale tracker Excel path instead of verifying
  the canonical one with Tony, producing a false "tracker abandoned since
  Feb 2026" conclusion; (2) declared the STEP2 SIGNAL_V2 emitter "never
  worked" without opening an already-noticed archive zip that held 16+ of
  the 44 flagged signals, and without checking past chat history that
  showed the emitter working on 7/28 and 7/30. Both lessons appended to
  `tasks/lessons.md` same session. SIP bumped to v3.6 (Step 0.5 renamed
  "Work Order + Lessons Review", Step 4 summary gained a `Lessons:` line,
  INIT Fast Path point 3 updated to combine the lessons read into the
  existing WO-grep call).

### 2026-08-06
- **INIT Fast Path added; changelog archived (Tony directive, live session).**
  INIT was taking 8+ round trips before a relay stall made it worse -- see
  INIT Fast Path section above for root cause + fix. Same session: changelog
  entries before 2026-08-03 moved to CHANGELOG_ARCHIVE.md, and Anti-Patterns
  compressed to rule + reference (full incident detail already lives in the
  architecture doc's EC log) -- cuts load size, drops zero rules.

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

*Entries before 2026-08-03 archived verbatim to `p115-project-context_CHANGELOG_ARCHIVE.md`.*

---

**End of P_115 Project Context SKILL**
