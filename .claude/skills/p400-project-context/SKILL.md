---
name: p400-project-context
description: >
  P_400 Trade Order Management — project-specific operating rules, critical
  paths, council roles, and known bugs. Load at the start of ANY session
  involving P_400 work. Triggers on any reference to P_400, TradeOrderManagement,
  council verdict, three-gate sizing, QUANT/RISK/MACRO/TAPE/BEHAVIORAL roles,
  spread council, screen-all, or Tier-1/Tier-2 signal packets. Always read
  BEFORE writing any code or file path.
---

# P_400 Project Context

## Purpose & Pairs With

Auto-loading protection layer for P_400 — the Hub's authoritative trade
order management layer. Governs position sizing, target setting, stop
placement, options/spread translation, and broker-ready order formatting
across P_115/P_116/P_117/P_118/P_300. Full domain rules live in the SIP
and architecture doc, loaded on demand.

| File | Role |
| :---- | :---- |
| `docs\prompts\P_400_SESSION_INITIALIZATION_PROMPT_v2_0.md` (live content is v2.3 — file not renamed) | INIT sequence, STEP 0.7 auto Tier-1 screen |
| `docs\P_400_TradeOrderManagement_Architecture_v2_0.md` | Full spec — on demand |
| `docs\P_400_TradeordermanagementGuidelines_v1.1.md` | Authority/decision-boundary rules vs P_115 |
| `docs\P_400_PositionSizing_TradeManagement_v1_0.md` | Three-gate sizing detail |
| **THIS FILE** | Always-active protection rules |

---

## Critical Paths

| Path | Resolution |
| :---- | :---- |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| Project root | `<Hub>\projects\P_400_TradeOrderManagement\` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` (never suggest new venv) |
| Signal inbox | `VAULT_ROOT\TradeOrderManagement\signals\` — P_800 writes `*_v2.0.json` packets here |
| Signal archive | `...\signals\processed\` — monthly zip, source JSON deleted after evaluate |
| Open-position book (WO-P400-E2.012) | `VAULT_ROOT\TradeManagement\P400\` — **not** `TradeOrderManagement\P400`; that was the E2.012 bug |
| Paper book dir | `VAULT_ROOT\TradeManagement\P400\paper\` — WO-P400-E2.019 (closed 2026-07-21, P_800-Acked): `record_writer.py` routes PAPER trades to schema `P400_PAPER`; confirmed working live 2026-07-24 |
| Cross-project params | `projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` |
| Risk config | glob `**/P_010_RiskConfig.json` — folder name drifts, always glob-discover, never hardcode |

**VAULT_ROOT** = `<Hub>\trading_journal\`. All vault paths above hang off this.

---

## Council Roles & Decision Codes

Five roles vote per evaluate: **QUANT** (R:R, stop tightness), **RISK**
(portfolio heat/position count/daily loss/sector), **MACRO** (earnings/binary
events), **TAPE** (price freshness, market hours, adverse drift), **BEHAVIORAL**
(annotate-only, `can_block=False` always — revenge-trade, overtrading, streak-chasing).

Verdict assembly: any BLOCK from a blocking role → `BLOCKED`. No blocks but
a CAUTION → `APPROVED_WITH_CAUTION`. Otherwise `APPROVED`.

Reason codes live in `domain\council_codes.py` as string constants — never
inline a literal reason string in a new role function; import from there.

---

## Three-Gate Sizing

Every position sizes against three gates; the **smallest** result wins:
1. Risk-based (account risk % → dollar risk → shares/contracts)
2. Cash availability
3. Concentration cap (posture-multiplier-adjusted — see E2.014 below)

Options use premium paid, not notional exposure, for gate 3.

Risk mode multipliers (read live from `P_010_RiskConfig.json`, never assume):
OFF/CORRECTION 0.50x, HALF 0.75x, STANDARD/FULL/HOT 1.00x.

---

## Snapshot Data Source Rule (LOCKED — 2026-07-10, no exceptions, no interpretation)

Every snapshot dict field falls into exactly one of two buckets. There is no
judgment call at build time — the field name alone decides the source.

**Bucket A — live-quote fields. TOS ONLY. Never web search/fetch, ever.**
`price`, `bid`, `ask`, `atr_14`, `today_volume`, `avg_volume_20d`,
`market_open`. These move every second and web sources are stale, ticker-
confused across share classes, or missing bid/ask and ATR entirely. If Tony
has not pasted a TOS screenshot with these fields, they do not exist yet —
ask for the screenshot. Do not estimate, do not carry over a prior session's
number.

**Bucket B — static/scheduled fields. Claude searches automatically,
unprompted, every time. Never leave `null` without having searched first.**
`next_earnings_date`, `sector`, `binary_events`. These are calendar facts,
not live quotes — a `web_search` for "`{TICKER}` next earnings date" is the
correct and required step for every Tier-2A or Tier-2B symbol, run before
the snapshot JSON is written, not offered as an optional extra. If sources
conflict by more than a few days, use the source explicitly marked
"Confirmed" over one marked "estimated/projected"; note the conflict in the
chat response so the MACRO role narrative can flag it.

**Violation on record:** 2026-07-09 session correctly searched earnings
dates for BP/SHEL. 2026-07-10 session (same day as this rule was written)
built six Tier-2B snapshots with `next_earnings_date: null` on all six and
told Tony "I don't look up earnings data" — a false statement that
contradicted the prior session's own behavior. Two of the six (SONO, WYNN)
turned out to have confirmed earnings dates 19-25 days out. Root cause: no
written rule existed, so each session re-decided the split from scratch.
This section exists so that never happens again — the split above is not
Claude's judgment call, it is fixed.

---

## Bugs Already Fixed

One test candidate per row — see `test_p400_known_bugs.py` (build alongside
or immediately after this skill, same session, per the Hub-wide rule in
`WO_COMPLETION_GATE.md`).

| WO | Bug | Fix |
| :---- | :---- | :---- |
| E2.007 | `quant_vote()` used strict `<` on stop-vs-ATR; float rounding on exactly-1xATR stops caused false `STOP_TOO_TIGHT` BLOCK | `STOP_ATR_TOLERANCE = 0.005` added to `config.py`; council.py compares against it, not a hardcoded `-0.01` |
| E2.012 | `BOOK_DIR` pointed at `TradeOrderManagement\P400` (dead folder); real records land in `TradeManagement\P400`. Risk gates read an empty book for ~6 trading days, 13 real records invisible. Second layer: reader expected `symbol`/`status`, writer produces `ticker`/`lifecycle_status` | `config.py` BOOK_DIR corrected; `book_loader.py` glob fixed (`*_P400.md` → `*.md`); field remap added at the read boundary only, no schema change |
| E2.013 | `tape_vote()` BLOCKed on `RC_ADVERSE_DRIFT` when `quant_vote()` already BLOCKs on the same underlying R:R failure — duplicate noise, no added protection | TAPE's adverse-drift branch changed BLOCK → CAUTION; QUANT still owns the hard block |
| E2.014 | Gate 3 (Concentration) sized against unreduced STANDARD/FULL `max_position$` regardless of live `risk_mode` — 33% oversized at HALF, 100% oversized at OFF/CORRECTION | `three_gate_size()` now multiplies Gate 3's cap by the same `posture_multiplier(risk_mode)` Gate 1 already used |
| E2.018 | Tier-1 FAIL packets had no automated disposal — inbox accumulated indefinitely, required manual ad hoc batch drops every session | `dispose_failed()` wired into `cmd_screen_all()`; every FAIL gets a real `REVIEWED_NO_TRADE` vault record and archive, same session, no manual step |
| E3.005 | Vertical spread legs had no viability gate — a leg that would BLOCK outright on the single-leg options path (spread_pct_of_mid=11.9%, above 10% threshold) sized and rendered cleanly as part of a spread | New `domain\spread_council.py`; both legs checked independently; either leg failing OI/spread thresholds is a hard BLOCK, same severity as single-leg |

---

## Layer Architecture (Hub Standard)

```
python/
├── config.py              ← All constants and paths, no logic
├── schemas.py              ← Pydantic models (BookRecord, etc.)
├── domain/                ← Business logic ONLY — council, sizing, screen,
│                              spread_council, packet_classifier, portfolio
├── infrastructure/         ← All I/O ONLY — book_loader, chain_loader,
│                              signal_loader, signal_archiver, record_writer
├── application/            ← Orchestration ONLY — evaluate_signal,
│                              evaluate_options, evaluate_spread, commands
├── cli.py                  ← Entry points
└── test_*.py                ← One test file per domain/application module
```

**Hard rules:** `domain/` cannot import `sqlite3` (P_400 uses Obsidian
vault + JSON, not a catalog DB) or reach into `infrastructure/`.
`infrastructure/` has no business logic — `chain_loader.py`'s
`_warn_liquidity()` logging a warning without blocking sizing (the root
cause of E3.005) is the worked cautionary example: a log line is not a
council verdict.

---

## AI Behavioral Rules

**Must:**
1. Read `P_010_RiskConfig.json` live before every evaluate — never assume a
   fixed risk_mode from memory or an older session.
2. Apply the posture multiplier to every gate that has a dollar cap, not
   just Gate 1 (E2.014 is the exact bug this prevents).
3. Keep BEHAVIORAL role annotate-only — `can_block` stays `False` always.
4. Route new council reason codes through `council_codes.py`, never an
   inline string literal.
5. Plan all files with line counts BEFORE writing code; one file per block.
6. State the full Windows save path with every file delivered.
7. When Tony reports an order_id for STEP 7 (record), confirm the actual
   executed quantity against the specced position_size before writing
   SUBMITTED -- TOS defaults its Qty field to 10 regardless of the spec,
   and it's easy to submit that default without noticing. Ask if they
   differ; do not assume the specced size was what actually filled
   (2026-07-24, MRCY: specced 7, filled 10, Tony confirmed "got lazy,
   TOS defaults to QTY 10").
7. For every Tier-2A/2B snapshot, web-search `next_earnings_date` and
   `sector` automatically before writing the JSON — see "Snapshot Data
   Source Rule" above. Do not ask Tony first, do not leave null by default.

**Must Not:**
1. Hardcode a risk_mode, account balance, or position cap that should be
   read live from P_000/P_010 config.
2. Add a new BLOCK-capable check anywhere without a corresponding entry in
   `council_codes.py` and a `test_council.py`/`test_spread_council.py` case.
3. Let a liquidity or viability check exist only as a `logger.warning()`
   line — if it should affect sizing or the printed spec, it must be a
   council vote, not a log side effect (E3.005 pattern).
4. Treat `TradeOrderManagement\P400` and `TradeManagement\P400` as
   interchangeable — the first is signal-packet inbox only, the second is
   the real lifecycle-record book.
5. Claim "I don't look up earnings data" or otherwise imply Bucket B fields
   are out of scope for web search — they are in scope, always, per the
   Snapshot Data Source Rule. Only Bucket A (live quotes) is TOS-only.

---

## Session-Start Checklist

- [ ] Call `tool_search` first — never assume ephemeral
- [ ] If INIT not yet run, prompt: "Type `INIT` to load working state"
- [ ] Confirm current `risk_mode` from `P_010_RiskConfig.json` before any
      sizing or council work
- [ ] STEP 0.7 (auto Tier-1 screen, per WO-P400-E3.007) runs before symbol
      selection — don't re-run screen-all manually if INIT already did

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (drafting)
- **Update trigger:** New WO fixing a bug in this project — add a row to
  Bugs Already Fixed and a matching test in the same session (Hub-wide
  rule, WO_COMPLETION_GATE.md, 2026-07-06)

## Changelog

### 2026-07-10
- Added "Snapshot Data Source Rule" section (locked, no interpretation) after
  Tony caught an inconsistency: 2026-07-09 session correctly web-searched
  earnings dates for BP/SHEL; 2026-07-10 session (same day) built six
  snapshots with earnings null and falsely told Tony earnings lookup wasn't
  something Claude does. Rule fixes the field-by-field source split as a
  written standard instead of a per-session judgment call. AI Behavioral
  Rules Must #7 and Must Not #5 added to match.

### 2026-07-06
- Initial build. Created under WO-P000-E6.001 (Gap 3 of the 2026-07-06
  context-engineering KB review — P_400 was the most active project
  running every session with no project-context layer). Bugs Already
  Fixed table seeded from 6 CLOSED WOs found in the Hub ledger (E2.007,
  E2.012, E2.013, E2.014, E2.018, E3.005). E2.017 (test_screen.py hardcoded
  dates) is still OPEN, not fixed -- correctly excluded from this table.

---

**End of P_400 Project Context SKILL**