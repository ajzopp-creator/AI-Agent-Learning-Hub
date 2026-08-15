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
order management layer: position sizing, target/stop placement,
options/spread translation, broker-ready order formatting across
P_115/P_116/P_117/P_118/P_300. Full domain rules live in the SIP and
architecture doc, loaded on demand.

**Disk-canonical warning:** SIP/architecture doc versions on disk can lag
a Project-attached copy by weeks (confirmed 2026-07-28: attached copy was
v2.3 SIP / v2.0-labeled arch doc vs. disk v2.5/v2.3). Read fresh from disk
below before relying on STEP text — never trust an attached copy's version
number.

| File | Role |
| :---- | :---- |
| `docs\prompts\P_400_SESSION_INITIALIZATION_PROMPT_v2_0.md` (live = v2.5, file not renamed) | INIT sequence, STEP 0.7 auto Tier-1 screen, STEP 3A `dossier` command |
| `docs\P_400_TradeOrderManagement_Architecture_v2_0.md` (live = v2.3, file not renamed) | Full spec — on demand |
| `docs\P_400_TradeordermanagementGuidelines_v1.1.md` | Authority/decision-boundary rules vs P_115 |
| `docs\P_400_PositionSizing_TradeManagement_v1_0.md` | Three-gate sizing detail |
| **THIS FILE** | Always-active protection rules |

---

## Critical Paths

| Path | Resolution |
| :---- | :---- |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| Project root | `<Hub>\projects\P_400_TradeOrderManagement\` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` (never a new venv) |
| Signal inbox | `VAULT_ROOT\TradeOrderManagement\signals\` — P_800 writes `*_v2.0.json` here |
| Signal archive | `...\signals\processed\` — monthly zip, source JSON deleted after evaluate |
| Open-position book | `VAULT_ROOT\TradeOrderManagement\P400\` — **not** `TradeManagement\P400`. WO-P800-E3.003 (2026-07-25) renamed the vault namespace hub-wide, reversing E2.012's (2026-06-17) opposite conclusion. Live, PEH-verified (191 records on disk 2026-07-25). |
| Paper book dir | `VAULT_ROOT\TradeOrderManagement\P400\paper\` — `record_writer.py` routes PAPER trades to schema `P400_PAPER` (WO-P400-E2.019, closed 2026-07-21); path matches the E3.003 rename. |
| Cross-project params | `projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` |
| Risk config | glob `**/P_010_RiskConfig.json` — folder name drifts, always glob-discover, never hardcode |
| Schwab credentials (app_key/app_secret) | `projects\P_020_AJZStrategies_PerformanceAnalysisSystem\config\P_020_schwab_config.json` — cross-project by design (WO-P400-E4.001, 2026-07-24): one credential, one rotation point. P_400's own `config\P_400_schwab_config.json` placeholder is dead/unreferenced. |
| Schwab token (P_400's own) | `projects\P_400_TradeOrderManagement\config\P_400_schwab_token.json` — never shared with P_020's token (schwab-py rewrites on refresh; separate tokens avoid a race). Confirmed empirically (2026-07-26): P_400/P_020 hold independent concurrent grants under the shared app_key, no collision. |
| P_020 auth issuance | `projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database\cli.py auth --project P_400` — the ONLY way to re-grant P_400's token (WO-P020-E1.010, IN_PROGRESS; see Auth troubleshooting below). |

**VAULT_ROOT** = `<Hub>\trading_journal\`. All vault paths above hang off this.

---

## Council Roles & Decision Codes

Five roles vote per evaluate: **QUANT** (R:R, stop tightness), **RISK**
(portfolio heat/position count/daily loss/sector — downgraded, see below),
**MACRO** (earnings/binary events), **TAPE** (price freshness, market
hours, adverse drift), **BEHAVIORAL** (annotate-only, `can_block=False`
always — revenge-trade, overtrading, streak-chasing).

**RISK never blocks** (Architecture v2.2 / SIP v2.4, 2026-07-20, Tony
directive — supersedes the "RISK BLOCK" narrative templates and the
`risk_can_block = true` line still shown in arch doc §8.1, which is
stale): heat/position-count/daily-loss/sector checks produce
`APPROVED_WITH_SEVERE_WARNING` instead, with the open-position list
attached. New `CASH_BELOW_RISK` check added same change. Tier-1 mirror:
HEAT_BREACH/POSITION_COUNT downgraded FAIL→WARN in `screen.py`. SIP STEP 5
has a dedicated `APPROVED_WITH_SEVERE_WARNING` branch (state each warning
+ open-position list, wait for confirm, then STEP 6).

**Verdict assembly:** any BLOCK from QUANT/MACRO/TAPE (RISK can't block)
→ `BLOCKED`. No blocks, a SEVERE_WARNING → `APPROVED_WITH_SEVERE_WARNING`.
No blocks/severe-warnings, a CAUTION → `APPROVED_WITH_CAUTION`. Otherwise
`APPROVED`.

**TAPE and market hours (WO-P400-E5.005, 2026-08-10):** outside 9:30-16:00
ET no longer hard-BLOCKs. `fetch_snapshot.py` prices off the last
completed daily bar's close instead of a live quote, with bid/ask
reconstructed from the symbol's last observed LIVE half-spread
(`infrastructure\last_spread_cache.py`, updated on every market-open
fetch — real friction, not a synthetic zero). `tape_vote()` reads this as
`price_basis` ("live" | "close"): closed + `price_basis=="close"` →
CAUTION (`RC_USING_CLOSE_DATA`), not BLOCK. No cached spread for a symbol
yet (never fetched live before) → `fetch_snapshot.py` fails loud, no file
written — fetch that symbol live during market hours first. The old
`pre_market_flag` param is gone (was dead — hardcoded `False`, never
wired to anything).

Reason codes live in `domain\council_codes.py` as string constants — never
inline a literal reason string in a new role function; import from there.

---

## Three-Gate Sizing

Every position sizes against three gates; the **smallest** wins:
1. Risk-based (account risk % → dollar risk → shares/contracts)
2. Cash availability
3. Concentration cap (posture-multiplier-adjusted, E2.014 below)

Options use premium paid, not notional exposure, for gate 3.

Risk mode multipliers (read live from `P_010_RiskConfig.json`, never
assume): OFF/CORRECTION 0.50x, HALF 0.75x, STANDARD/FULL/HOT 1.00x.

---

## Live Data & Dossier Automation (Schwab API — WO-P400-E4.001/E4.002/E4.003, all CLOSED 2026-07-24)

Replaces the TOS-screenshot workflow described in the v2.0/v2.1 arch doc
and pre-v2.5 SIP. If either still shows the old screenshot flow, that's a
stale/attached copy, not disk.

**Snapshot (Bucket A — Schwab-API-first, TOS is fallback-only):**
```
cli.py fetch-snapshot SYMBOL [--earnings-date DATE] [--sector SECTOR]
```
Pulls `price`/`bid`/`ask`/`atr_14` (via `compute_atr_wilder()` on real
bars)/`avg_volume_20d`/`today_volume`/`market_open` live from Schwab,
writes `snapshot_SYMBOL.json` (`data_source="schwab_api"`).
`next_earnings_date`/`sector` stay web-search-sourced (Tony's call
2026-07-21 — Schwab's fundamentals data isn't reliably populated for
earnings) — search first, pass as the flags above. TOS is fallback only:
if `fetch-snapshot` errors, it writes nothing; fall back to manual TOS
transcription + `data_source="manual"` at that point, not before.

**Bucket B (earnings/sector/binary events) — always Claude's job, always
web-search, unprompted, before every snapshot.** Never leave `null`
without having searched first. Two violations on record for claiming
otherwise (2026-07-10: told Tony "I don't look up earnings data" — false;
2026-07-28: asked for a TOS screenshot instead of using the by-then-live
Schwab command). Third instance of this gap-class would need a structural
fix, not another changelog line.

**batch-2b's earnings source is different from the manual flow above --
read this before offering batch-2b (WO-P400-E5.002, 2026-08-08; found live
2026-08-11 on HAL/VKTX).** `batch-2b` does NOT use Bucket B web-search or
the old manual `earnings_YYYY-MM-DD.json` bridge file -- that file is dead
code for batch-2b as of E5.002 (`infrastructure/earnings_file.py`, still on
disk, called by nothing). `application/earnings_lookup.py` reads
`earnings_calendar_cache.json` exclusively (Nasdaq public calendar,
refreshed via `cli.py refresh-earnings-calendar`). A PASS symbol missing
from that cache -- e.g. a real, liquid, well-known ticker whose next-earnings
date simply isn't officially confirmed by Nasdaq yet -- hard-fails the
WHOLE batch (`EarningsDataMissing`, no per-symbol skip/override exists).
Running `refresh-earnings-calendar` will NOT help if Nasdaq itself hasn't
posted a date yet -- confirmed live: HAL/VKTX still absent after a fresh
pull. The only way through today is the manual per-symbol
`fetch-snapshot`/`fetch-chain`/`compare` flow (Bucket B web-search-sourced
earnings), which does not touch the cache at all.

**Chain data (options):**
```
cli.py fetch-chain SYMBOL --type call|put [--strike X] [--expiration DATE]
```
Auto-selects closest-to-0.50-delta in the 21-45 DTE window when no
`--strike`/`--expiration` given (`domain\chain_selector.py`); explicit
values override and skip selection. **Known UX gap, not a bug:** the
auto-selected contract isn't guaranteed liquid — `options_council.py`'s
OI/spread gates run downstream and can still BLOCK it (observed on MRCY:
110C 2026-08-21 delta 0.470, OI=78/spread=19.2%, both fail).

**Tier-2A dossier (arch §4.2 items 1-8):**
```
cli.py dossier SYMBOL
```
Computes trend/S-R/MAs/RSI/MACD/BB/volume/Fibonacci live from Schwab bars
(`domain\moving_averages.py`, `oscillators.py`, `levels.py`,
`shared_resources\python_utils\swing_detector.py`). Fib swing detection =
simple rolling max(high)/min(low), not a pivot-window algorithm — matches
Tony's TOS ThinkScript exactly (verified against MRCY, all 5 levels
exact). **Item 9 (chart pattern) is never computed** — geometric shape ID
is a judgment call (Tony confirmed 2026-07-21); Claude narrates it over
the printed table in STEP 3A, no screenshot.

**Record trade_mode (WO-P400-E5.001, 2026-07-29):** `record` accepts
`--paper` independently of what `evaluate`/`spec` cached. Fill-time is
often when Tony actually knows paper-vs-real -- use `record SYMBOL
--order-id ID --paper` (or omit for real) at that point; never require a
prior `--paper` on evaluate/spec first. See Bugs Already Fixed below.

**Auth troubleshooting:** `OAuthError "unsupported_token_type"` on
`fetch-snapshot`/`fetch-chain` → get a fresh grant via **P_020**, not
P_400. WO-P020-E1.010 removed P_400's own `cli.py schwab-auth`
subcommand (2026-07-26) — it is gone, not a fallback. Remedy:
```
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database
C:\Users\Trader\.conda\envs\p140\python.exe cli.py auth --project P_400
```
Writes straight to P_400's own token path; nothing else in P_400 changes.
Root cause of `unsupported_token_type` itself never diagnosed, but
re-granting has resolved it every time observed (2026-07-25/26, 2026-08-04).
Full incident + why the skill missed this for 9 days: WO-P020-E1.010's
"FOUND LIVE" section.

---

## Bugs Already Fixed

One test candidate per row — see `test_p400_known_bugs.py` (build
alongside or immediately after this skill, same session, per
`WO_COMPLETION_GATE.md`).

| WO | Bug | Fix |
| :---- | :---- | :---- |
| E2.007 | `quant_vote()` strict `<` on stop-vs-ATR; float rounding on exactly-1xATR stops caused false `STOP_TOO_TIGHT` BLOCK | `STOP_ATR_TOLERANCE = 0.005` in `config.py`, council.py compares against it |
| E2.012 | `BOOK_DIR` pointed at the then-dead `TradeOrderManagement\P400`; real records landed in `TradeManagement\P400`. Risk gates read an empty book ~6 days, 13 records invisible. Reader also expected `symbol`/`status`, writer produced `ticker`/`lifecycle_status` | `config.py` corrected, `book_loader.py` glob fixed, field remap at read boundary. **SUPERSEDED 2026-07-25 by WO-P800-E3.003** — vault namespace renamed, reversing this. See Critical Paths. |
| E2.013 | `tape_vote()` BLOCKed on `RC_ADVERSE_DRIFT` when `quant_vote()` already BLOCKs same R:R failure — duplicate noise | TAPE's adverse-drift branch BLOCK→CAUTION; QUANT owns the hard block |
| E2.014 | Gate 3 sized against unreduced STANDARD/FULL cap regardless of live `risk_mode` — 33% oversized at HALF, 100% at OFF/CORRECTION | `three_gate_size()` multiplies Gate 3's cap by the same `posture_multiplier(risk_mode)` Gate 1 uses |
| E2.018 | Tier-1 FAIL packets had no automated disposal — inbox grew indefinitely | `dispose_failed()` wired into `cmd_screen_all()`; every FAIL gets a `REVIEWED_NO_TRADE` record + archive, same session |
| E3.005 | Vertical spread legs had no viability gate — a leg that would BLOCK single-leg sized cleanly inside a spread | New `domain\spread_council.py`; either leg failing OI/spread thresholds is a hard BLOCK |
| E3.010/E3.011 (4th recurrence) | New verdict tier `APPROVED_WITH_SEVERE_WARNING` (2026-07-20) missing from spec-cache gate, `record_commands.py` allow-list, `obsidian_writers\config.py` `VERDICT_MAP` (defaulted PASS instead of BUY), and a test allowlist — same root cause, 4 spots | Each fixed individually; `VERDICT_MAP` P_800-Acked 2026-07-24. **Unfixed structural gap:** no single source of truth enumerates all verdict-tier consumers. |
| E4.005 | `is_market_open_now()` was Mon-Fri 9:30-16:00 wall-clock only, no holiday check — `market_open: true` on holidays | Fixed with E4.006 (same root gap) |
| E4.006 | `_sessions_since_earnings()` weekday-count had no holiday awareness — miscounted the `POST_EARNINGS_STABILIZATION_SESSIONS` window by one per holiday | New `domain\market_holidays.py` (rule-based, verified vs. NYSE 2026-2028 calendar); consumed by `market_hours.py` and `evaluate_signal.py`. Also fixed: `test_schwab_market_data.py` mock (`get_quotes` plural for slash-symbols); a weekday-dependent test fixture. |
| E2.016 | quant_vote()'s RC_RR_BELOW_MIN `reason_detail` stated R:R (spread-adjusted, from `evaluate_signal.py`) and needs >= (clean entry/stop) on the same line with no basis label — read as self-contradictory though the BLOCK itself was always correct | Relabeled both figures in place: (realistic-fill, spread-adjusted) / (clean/guideline basis). No parameter or behavior change. Test: `test_council.py::test_quant_blocks_rr_below_min` asserts both labels present. |
| E5.001 | `record` couldn't set `trade_mode` -- `evaluate`/`spec` cache it early, but Tony often decides paper-vs-real at fill, not eval time (CPAY, 2026-07-29: workaround was re-running `spec --paper` just to overwrite the cache before `record`). | `record` gained `--paper`; `cmd_record_submit()` builds a call-scoped override to `PAPER` before `write_p400_record()` -- `eval_cache` file itself never mutated. Tony: "Paper is a decision I make when I go to BUY." Test: `test_record_commands.py` (override-sets-PAPER / no-override-keeps-cached / override-doesn't-mutate-cache). |
| E5.005 | `tape_vote()` hard-BLOCKed every evaluate outside 9:30-16:00 ET via `RC_MARKET_CLOSED` unless `pre_market_flag=True` -- hardcoded `False` in `evaluate_signal.py`, never wired anywhere, so it was a 100% block with a dead escape hatch | Replaced `pre_market_flag` with `price_basis` ("live"/"close"). Closed-market path prices off the last daily bar's close (`fetch_snapshot.py`) with bid/ask reconstructed from the symbol's last observed LIVE half-spread (`infrastructure\last_spread_cache.py`, real friction, not synthetic zero) -- CAUTIONs (`RC_USING_CLOSE_DATA`) instead of BLOCKing. No cached spread yet -> fails loud, no file written. Tests: `test_tape_price_basis.py`, `test_fetch_snapshot.py`, `test_last_spread_cache.py`. |
| E6.001 | `Bases/P400_Trades.base` filtered on `TradeManagement/P400` -- renamed to `TradeOrderManagement/P400` by WO-P800-E3.003 (2026-07-25); dead path returned zero rows silently for 17 days. Also sorted on a `date` field that does not exist in the P400 note schema | Path corrected to `TradeOrderManagement/P400`; sort field corrected to `run_date`. See WO-P400-E6.001 -- also found P_400 order notes never close the lifecycle loop (entry_date/close_date/realized_pnl stay null forever), reconciliation design pending |
| E5.006 | `cmd_compare()` had zero disposition wiring on any outcome -- a `NEITHER` recommendation (both vehicles fail R:R/viability) printed the comparison table and returned, leaving the packet in the live inbox indefinitely -- no archive, no record, re-fetched (re-billed against live Schwab) every session. Found live 2026-08-11 on HAL and VKTX after a `batch-2b` earnings-cache hard-fail forced the manual `compare` fallback. | `run_comparison()` (`compare_vehicles.py`) gained a `trade_mode` param and a new `_dispose_if_neither()` helper -- on `NEITHER`, calls the existing `drop_signal()` (`drop_reason="RR_INVALID"`), archiving the packet and writing a REVIEWED_NO_TRADE record, mirroring the ENTRY_MISSED path `cmd_evaluate()` already used. Tony's directive (2026-08-11): once a signal reaches P_400 it is either a trade or it is not -- no hold-and-recheck; re-qualification is the trade-selector projects' job (P_115/P_300/P_118), not Order Management's. Test: `test_run_comparison_neither_disposes_packet`. Live-verified same session: inbox count 16 -> 0. |
---

## Layer Architecture (Hub Standard)

```
python/
├── config.py              ← All constants and paths, no logic
├── schemas.py              ← Pydantic models (BookRecord, etc.)
├── domain/                ← Business logic ONLY — council, sizing, screen,
│                              spread_council, packet_classifier, portfolio,
│                              chain_selector, moving_averages, oscillators,
│                              levels, market_holidays, market_hours
├── infrastructure/         ← All I/O ONLY — book_loader, chain_loader,
│                              signal_loader, signal_archiver, record_writer,
│                              schwab_market_data
├── application/            ← Orchestration ONLY — evaluate_signal,
│                              evaluate_options, evaluate_spread, commands,
│                              schwab_commands, fetch_snapshot, fetch_chain,
│                              build_dossier
├── cli.py                  ← Entry points (fetch-snapshot, fetch-chain,
│                              dossier — schwab-auth removed 2026-07-26,
│                              see Auth troubleshooting)
└── test_*.py                ← One test file per domain/application module
```

**Shared (Hub root, not P_400-local):** `shared_resources\python_utils\`
has `schwab_auth.py`/`schwab_client.py` (WO-P400-E4.001 — generalized from
P_020's original, both projects call the same module with different
config/token paths) and `swing_detector.py` (WO-P400-E4.003 — Fib
swing-high/low, simple rolling max/min).

**Hard rules:** `domain/` cannot import `sqlite3` (P_400 uses Obsidian
vault + JSON, no catalog DB) or reach into `infrastructure/`.
`infrastructure/` has no business logic — `chain_loader.py`'s
`_warn_liquidity()` logging without blocking sizing (E3.005's root cause)
is the cautionary example: a log line is not a council verdict.

---

## AI Behavioral Rules

**Must:**
1. Read `P_010_RiskConfig.json` live before every evaluate — never assume
   a fixed risk_mode from memory or an older session.
2. Apply the posture multiplier to every gate with a dollar cap, not just
   Gate 1 (E2.014 is the bug this prevents).
3. Keep BEHAVIORAL role annotate-only — `can_block` stays `False` always.
4. Route new council reason codes through `council_codes.py`, never an
   inline string literal.
5. Plan all files with line counts BEFORE writing code; one file per
   block.
6. State the full Windows save path with every file delivered.
7. When Tony reports an order_id for STEP 7, confirm executed quantity
   against specced position_size before writing SUBMITTED — TOS defaults
   Qty to 10 regardless of spec; ask if they differ, don't assume a match
   (2026-07-24, MRCY: specced 7, filled 10 — TOS default, unnoticed).
8. For every Tier-2A/2B snapshot, run `fetch-snapshot SYMBOL` first
   (Schwab API); web-search `next_earnings_date`/`sector` before writing
   the command, pass as flags. Don't ask for a TOS screenshot unless
   `fetch-snapshot` actually errors.
9. For Tier-2A, run `dossier SYMBOL` for items 1-8, then narrate item 9
   (pattern ID) over the printed table — never ask for a screenshot or
   compute item 9 yourself.
10. Before trusting SIP/architecture-doc wording on a versioned section,
    check whether a Project-attached copy might be stale — read disk
    (paths above) when stakes are non-trivial. Confirmed 2026-07-28: an
    attached copy can lag disk 2+ weeks / 2 SIP minor versions unnoticed.
11. Before running evaluate, cross-check the symbol against
    `port_state.open_symbols` (visible in Council's RISK line every run),
    not just on SEVERE_WARNING. `has_duplicate()` exists
    (`domain\portfolio.py`) but is deliberately never auto-BLOCK-wired
    (Tony's call, 2026-07-28) — scale-in/replace/skip is discretionary,
    not Council's math to decide. This is a Claude-side habit, not a code
    guarantee: a quiet PASS never narrates open_symbols on its own (a real
    open SEIC position nearly went unnoticed this way — turned out to be
    paper, not a real duplicate, but the miss itself was real). If found,
    surface shares/cost-basis/P&L and ask scale-in/replace/skip (arch doc
    §2.5 item 1) — never decide it silently.
12. Before offering to run Tier-2B on a symbol, check its earnings date
    against `EARNINGS_WINDOW_FORWARD_DAYS` (config.py, currently 3) as
    soon as known — for a stock, earnings inside that window means MACRO
    BLOCKs by default (`council.py` `macro_vote()`, RC_EARNINGS_IN_WINDOW;
    no `defined_risk_confirmed` path on a plain stock trade). State a
    near-certain BLOCK as its own line, not folded into a general "risk"
    flag alongside unrelated concerns (e.g. market-hours timing) — a
    skimmed multi-part warning can get "run anyway" picked without the
    dead-end branch registering. Recommend PASS/skip explicitly, don't
    offer it as one neutral choice among several (2026-08-04, EXEL:
    next-day after-close earnings inside the 3-day window; presented as an
    unweighted 3-way pick, Tony picked "run anyway," burned a live pull +
    an auth re-grant, caught his own call as wrong before evaluate ran).
13. Vehicle selection is options-first (WO-P400-E5.003, 2026-08-07, Tony
    confirmed applies to both the manual flow and batch-2b) -- no longer
    gated behind stock-sizes-to-0 / R:R<2:1 / Tony-request. For every
    approved stock-based (asset_class="stock") signal, run compare
    (calls domain.vehicle_selector.compare_vehicles()) before evaluate and
    follow its recommended field -- STOCK, OPTION, SPREAD,
    OPTION_OVERRIDE_ONLY, or NEITHER -- into the matching command. SIP
    v2.6 Step 2/4c carries the full branch table. batch-2b's internal
    vehicle selection (application/batch_2b_scoring.py) reuses
    compare_vehicles() directly rather than the manual compare CLI path,
    but the same options-first policy governs both.
14. Trade mode (paper vs. real) is set at `record` time via `--paper`
    (WO-P400-E5.001) -- do not ask Tony to resolve it as an open question
    if he's already stated it; do not require `--paper` on an earlier
    `evaluate`/`spec` call. Fill-time is the correct decision point.

**Must Not:**
1. Hardcode a risk_mode, account balance, or position cap that should be
   read live from P_000/P_010 config.
2. Add a new BLOCK-capable check without a `council_codes.py` entry and a
   `test_council.py`/`test_spread_council.py` case.
3. Let a liquidity/viability check exist only as a `logger.warning()` line
   — if it affects sizing or the printed spec, it must be a council vote
   (E3.005 pattern).
4. Assume the older of `TradeOrderManagement\P400` / `TradeManagement\P400`
   is correct without checking this file's date against the Hub ledger.
   Since WO-P800-E3.003 (2026-07-25), `TradeOrderManagement\P400` is live;
   `TradeManagement\P400` is a retired empty shell — do not write there.
5. Claim "I don't look up earnings data" or imply Bucket B is out of
   scope for web search — it's always in scope. Only Bucket A (live
   quotes) had a source restriction, and since 2026-07-24 that's
   Schwab-API-first/TOS-fallback, not TOS-only or web-search.
6. Ask for a TOS screenshot as the first move for snapshot/dossier data —
   `fetch-snapshot`/`fetch-chain`/`dossier` are first since 2026-07-24;
   screenshot is fallback after an actual API failure.
7. Add a new Council verdict tier without checking every downstream
   verdict-string consumer (spec cache, record allow-lists, `VERDICT_MAP`,
   test allowlists) in the same session — this gap has recurred 4 times
   (E3.010/E3.011 row above).

---

## Session-Start Checklist

- [ ] Call `tool_search` first — never assume ephemeral
- [ ] If INIT not yet run, prompt: "Type `INIT` to load working state"
- [ ] Confirm current `risk_mode` from `P_010_RiskConfig.json` before any
      sizing or council work
- [ ] STEP 0.7 (auto Tier-1 screen, WO-P400-E3.007) runs before symbol
      selection — don't re-run screen-all manually if INIT already did
- [ ] For any Tier-2A/2B symbol, use `fetch-snapshot`/`fetch-chain`/
      `dossier` (Schwab API) before considering a TOS screenshot ask

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (drafting)
- **Write safety (added WO-P400-E5.005, 2026-08-10):** any PowerShell
  write to THIS file must use a single-quoted here-string (`@'...'@`),
  never double-quoted (`@"..."@` or `"..."`). This file's own prose uses
  markdown backtick-code-formatting constantly (`` `reason_detail` ``,
  `` `evaluate_signal.py` ``, etc.) -- in a double-quoted string,
  PowerShell reads backtick+letter as an escape sequence (`` `r ``->CR,
  `` `e ``->ESC, `` `n ``->LF, `` `t ``->TAB), silently eating the first
  letter after the backtick and inserting a control character instead.
  The E2.016 Bugs-table row corrupted this way sat wrong for 5 days,
  unnoticed, before this WO found and fixed it. A single-quoted
  here-string is fully literal -- no escape interpretation at all -- so
  this class of bug can't recur regardless of how much backtick-code
  formatting the new content contains.
- **Update trigger:** any WO that fixes a bug here (add a Bugs Already
  Fixed row + matching test, same session, per `WO_COMPLETION_GATE.md`)
  OR any WO that renames, moves, redefines, or automates a path/config/
  data-source value this file documents — even when P_400 is only an
  `Affects:` consumer, not the Owner. This file's own last-updated date
  is not evidence its content is current: check the WO ledger, not just
  this changelog, before trusting a Bucket-A/B or path rule. Three
  confirmed multi-day gaps on record (WO-P800-E3.003 vault rename sat
  unreflected 2 days; WO-P400-E4.001-E4.003 Schwab automation sat
  unreflected 4 days; WO-P400-E5.001 sat unreflected 14 days) plus the
  2026-08-04 auth-command gap (9 days) — same failure shape each time:
  "P_400 already knows this happened, the skill file just wasn't told."

## Changelog

### 2026-08-12
- WO-P400-E5.001 (OWNER_DONE 2026-07-29, 11/11 live-verified) never got
  its Bugs-table row -- 14 days undocumented, only surfaced this session
  via chat-history search after Tony flagged it. Added Bugs row, Live
  Data section note, and Must #14. Same failure shape as the other
  doc-sync gaps logged below.

### 2026-08-11
- WO-P400-E5.006: Bugs Already Fixed row added -- `cmd_compare()` had no
  disposition wiring on any outcome; NEITHER left packets stuck in the
  inbox indefinitely. Fixed via `_dispose_if_neither()` in
  `compare_vehicles.py`, reusing the existing `drop_signal()` path.
  Tony's directive: once a signal reaches P_400 it is either a trade or
  it is not -- no hold-and-recheck state anywhere in this project.
- Same session, unrelated: added a note under Live Data & Dossier
  Automation describing batch-2b's earnings source (WO-P400-E5.002,
  Nasdaq calendar cache only, no per-symbol override, old manual bridge
  file now dead code) -- found live when batch-2b hard-failed on HAL/VKTX
  despite both being real, liquid tickers with simply-unconfirmed dates.
  No code defect, documentation gap only.

- WO-P400-E6.001: `Bases/P400_Trades.base` found pointing at the dead
  `TradeManagement/P400` path (renamed by WO-P800-E3.003, 2026-07-25) --
  zero rows returned silently for 17 days. Fixed, plus a sort-field bug
  (`date` does not exist in this schema; corrected to `run_date`). Same
  investigation found P_400 order notes never close the lifecycle loop --
  `entry_date`/`close_date`/`realized_pnl` stay null forever, no
  reconciliation step exists. Reconciliation design recommended (extend
  P_020's SQLite-as-source-of-truth pattern) but not yet approved/built.

### 2026-08-10
- WO-P400-E5.005: Council Roles section updated -- TAPE no longer
  hard-BLOCKs outside market hours; describes price_basis and the new
  last_spread_cache.json mechanism. Added Bugs Already Fixed row.
- Same session, unrelated: found and fixed byte-level corruption in the
  E2.016 Bugs table row (sitting since ~2026-08-05) -- a prior session's
  PowerShell write used a double-quoted string containing markdown
  backtick-code-formatting; PowerShell interpreted backtick+letter as
  escape sequences, eating the first letter of several words and
  inserting a control character in its place. Purely cosmetic (didn't
  break table syntax) but silently wrong for 5 days, unnoticed. Root
  cause is generic to any future skill-file edit containing markdown
  backtick-code spans -- single-quoted here-strings (fully literal, no
  escape interpretation) are the safe pattern; used one for both fixes.

### 2026-08-07
- Added Must #13: vehicle selection is options-first (WO-P400-E5.003) --
  compare runs before every stock-based evaluate now, both in the manual
  flow and in the new batch-2b CLI runner. Replaces the old
  stock-sizes-to-0/R:R<2:1/Tony-request fork description. SIP updated to
  v2.6 same session (Scope 7 of WO-P400-E5.003 -- doc-sync required before
  that WO can move past IN_PROGRESS).

### 2026-08-05
- Added Bugs Already Fixed row for WO-P400-E2.016 (OWNER_DONE, pending Independent Review) — RC_RR_BELOW_MIN message-text relabel, no behavior change. Matching test added same session per this file's own Update trigger.

### 2026-08-04
- Added Must #12 (earnings-window pre-check before offering Tier-2B) and
  corrected Auth troubleshooting (dead `cli.py schwab-auth` → `P_020 cli.py
  auth --project P_400`). Both are documentation-sync gaps: the underlying
  WOs (forward-earnings-window check; WO-P020-E1.010's subcommand removal)
  shipped without this file being updated. WO-P020-E1.010 corrected in
  place with a FOUND LIVE section + new acceptance item (no new WO opened,
  per Tony). Full incident detail lives in that WO and in this file's own
  Must #12 / Auth troubleshooting entries above, not duplicated here.
- **Whole file compressed 2026-08-04** (Tony's request) — narrative
  padding and repeated context cut throughout; every path, WO ID, config
  value, function/module name, and threshold preserved. ~32.7KB → ~22.6KB
  (~31% reduction), 512 lines → ~388.

### 2026-07-28 (two updates same day)
- Major update after WO-P400-E4.001-E4.006 (Schwab API automation) sat
  unreflected 4 days: added Live Data & Dossier Automation section,
  RISK-never-blocks correction, Schwab paths, E4.005/E4.006/E3.010-E3.011
  bug rows, Must #8-10, Must Not #6-7, disk-vs-attached version-drift
  caution. Trigger: a session asked Tony for a TOS screenshot twice after
  automation had replaced that flow.
- Added Must #11 (cross-check `open_symbols` before every evaluate, not
  just on SEVERE_WARNING) after a real open SEIC paper position nearly
  went unnoticed mid-session (turned out to be paper, not a true
  duplicate — the miss itself was real). `has_duplicate()` exists but is
  deliberately not auto-BLOCK-wired (Tony's call); fix is a standing
  Claude-side habit.

### 2026-07-27
- Corrected Critical Paths (open-position/paper book dirs) and Must Not #4
  for WO-P800-E3.003's vault rename, which this file had backwards for 2
  days (nearly caused a live session to revert `obsidian_writers/config.py`
  and move 190+ records to the retired path). Root cause: two gaps —
  `WO_COMPLETION_GATE.md`'s checklist never named skill files as a sync
  target, and this file's Update trigger was worded around bug-fixes only,
  not renames. Both fixed same session.

### 2026-07-10
- Added (now-superseded) Snapshot Data Source Rule after a same-day
  contradiction: 2026-07-09 correctly web-searched earnings for BP/SHEL;
  2026-07-10 built six snapshots with earnings null and told Tony earnings
  lookup "isn't something Claude does" — false. Must #7 / Must Not #5
  added to lock the Bucket A/B split as written policy, not a per-session
  judgment call.

### 2026-07-06
- Initial build (WO-P000-E6.001, Gap 3 of the context-engineering KB
  review — P_400 was the most active project with no project-context
  layer). Bugs table seeded from 6 CLOSED WOs (E2.007, E2.012, E2.013,
  E2.014, E2.018, E3.005). E2.017 (hardcoded test dates) correctly
  excluded — still OPEN, not fixed.

---

**End of P_400 Project Context SKILL**
