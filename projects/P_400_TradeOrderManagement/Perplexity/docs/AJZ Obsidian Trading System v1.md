# AJZ Obsidian Trading Journal & Signal System — v1.4

Companion to `AJZ-Strategies-Trading-Plan-2026-V2` and the P_300 Trade Management Framework / Council Review process. This document reviews the layout Copilot proposed, then delivers a revised, ready-to-drop-in vault structure that wires your P_115 / P_300 / P_400 signal chain directly into the journal, plus a Daily Report that pulls both automatically.

**v1.4 update:** P_920 ("Buyers-in-Control EOD scan") is now folded in the same way as P_117/P_118 — new folder, template, Daily Report/Daily Review sections, and `new_signal_note.py --type p920` support. Same caveat as the other two: placeholder pending a real generated note, confirmed so far only from one P_115 rationale mention.

**v1.3 update:** you confirmed you want P_117 and P_118 folded in, and said you're not yet sure whether the HybridTier-scoring P_115 is the same system as the ThinkScript "Regime Council" indicator. P_117 and P_118 now have their own vault folders, templates, and Daily Report sections (all placeholders — see Section 0c), and the P_115 template now carries both possible field sets side by side until you confirm which applies.

**v1.2 update:** you shared two real generated notes (`TradeOrderManagement/P400/2026-09-03_CRUS.md` and `TradeOrderManagement/P300/2026-09-03_CRUS.md`) plus the `2609_ProcessedJson.zip` signal archive. This confirms the *exact* frontmatter schema for both folders, and reveals P_115 is also a live automated signal source (not chart-only) — see Section 0.

**v1.1 update:** you shared a real `P400_2026-09-04.log` and a real `batch2b_2026-09-03_20260903_154518.json` from your live P_400 pipeline, and confirmed the vault path is `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal`.

---

## 0. What Your Real Log/JSON Changed

The log and JSON you shared aren't a P_300 Pipeline B pattern report — they're artifacts from your **P_400** pipeline (`AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement`), and they show it's considerably more built-out than the design assumed:

- **P_400 already writes directly into your Obsidian vault, automatically.** The log shows a working `obsidian_writers` package (`application.write_handler` → `domain.validator` → `domain.filename_builder` → `infrastructure.vault_writer`) that already writes one note per symbol to:
  `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\P400\<date>_<TICKER>.md`
  So the vault root is `trading_journal` itself (not a `Trading\` subfolder as v1.0 assumed) — **all folder paths below have been corrected to drop that extra layer.**
- **P_400 has its own live council + Schwab integration.** `options_council` issues real `BLOCK` verdicts (`SPREAD_TOO_WIDE`, `RR_BELOW_MIN`, `RR_INVALID`, `ADVERSE_DRIFT`), pulled from live Schwab quotes/chains (`api.schwabapi.com`), and every signal gets archived to a zip (`signal_archiver` → `2609_ProcessedJson.zip`) before being written or dropped (`drop_signal` / `dispose_failed`).
- **There's a daily batch-screening step** (`batch2b_<session_date>_<run_timestamp>.json`) that runs before per-symbol evaluation — confirmed fields: `run_timestamp`, `session_date`, `cash_available`, `posture` (saw value `HALF` — confirm the full enum, likely alongside FULL/OFF), `screened_count`, `passed_tier1`, `evaluated`, `candidates`, `skipped` (list of `{symbol, reason}`, reason format `verdict=BLOCKED (<CODE>)`), `cumulative_risk_if_all_taken`, `heat_cap`, `heat_warning`. This is your Council Role 01 (portfolio heat) and Role 02 (posture) check, already running automatically — it just wasn't reaching the vault yet, so I added a folder + sync script for it (`TradeOrderManagement/P400-Batch/`, Section 7).

**What this means for the design:** since P_400 already auto-writes its own notes, you generally won't hand-fill the P_400 template — it's now documented as a schema reference / manual fallback only (see the updated template). What's still missing is confirmation of the *exact* frontmatter `vault_writer` puts in those already-written `.md` files — the log only proves the file gets written, not what's inside it. **If you can paste one real generated file from `TradeOrderManagement\P400\`, I'll lock in the Dataview field names instead of guessing from the log.** Until then, the P_400 dashboard queries use best-guess field names (`council_verdict`, `write_route`, `drop_reason`) built from the log's own vocabulary.

Open question worth a quick answer: does **P_300** (VantagePoint) or **P_115** (Regime Council) have a similar automated `obsidian_writers`-style module already, or are they still chat/screenshot-only for now? If either already auto-writes, tell me its output path the same way and I'll fold it in the same way I just did for P_400.

---

## 0b. v1.2 — Confirmed Real Schema (from your actual generated notes)

You shared a real `TradeOrderManagement/P400/2026-09-03_CRUS.md`, a real `TradeOrderManagement/P300/2026-09-03_CRUS.md`, and the `2609_ProcessedJson.zip` signal archive. This resolves most of Section 0's open questions and changes a few things again:

- **Folder name correction:** the real P_300 folder is `TradeOrderManagement/P300/` — not `P300-Pattern` as v1.1 guessed. Confirmed directly from a signal envelope's `signal_metadata.signal_source_link: "trading_journal/TradeOrderManagement/P300/2026-09-03_CRUS.md"`. All folders/scripts/templates below have been renamed to match.
- **P_300 is also fully automated** — `written_by: P_300/daily_evaluate_pipeline` writes complete notes (per-horizon stats, narrative, Chaikin Power Gauge) directly to the vault, same as P_400. `sync_p300_pattern_reports.py` is now a low-priority legacy fallback, not part of the main flow — see Section 7.
- **P_115 is also live and automated, and is not the ThinkScript regime indicator I assumed.** The archive contains real P_115-sourced signal envelopes (`signal_id: "P115-2026-09-02-HNGE-001"`, etc.) with `strategy` values `breakout`, `dip_buy`, and even `pattern_analog`. Its `signal_rationale` shows an internal scoring system — component scores (Fund/Anal/Candle/Setup/STR) rolling into a `HybridTier`, plus fundamental verification (ROE, Debt/Equity, FCF via stockanalysis.com), a 200-MA regime check, and an earnings-proximity check. This is a materially different (and more built-out) P_115 than the VWAP_Z/OBV_Z/sumZZ chart indicator the `regime-council-chart-analysis` skill describes — worth a quick clarification on your end (see Section 9) about whether those are the same system, a renamed successor, or two separate things you use in parallel.
- **Two more upstream sources surfaced: P_117 and P_118.** Several P_115 rationale strings reference `P_117/CEG_2026-09-02` and `P_118_STEP1/HNGE_2026-09-02_reemit` as the origin of the candidate before P_115's "recheck." I have not built anything for these — flagging only so nothing surprises you later; tell me if you want them folded in too.
- **The shared signal-envelope schema** used by both P_115 and P_300 before they reach P_400: `signal_id, signal_timestamp, signal_source, strategy, symbol, asset_class, guideline_entry, guideline_stop, guideline_target, signal_horizon, confidence_level, position_size, strike_price, underlying_price, option_type, expiration_date, atr_adjusted_stop, intelliscan_support_1, intelliscan_support_2, target_source, context: {close_at_signal, trailing_volume_30d, signal_rationale, atm_at_signal}, signal_metadata: {session_date, chart_timeframe, signal_source_link}`. This lives in the archived JSON, one level below the vault notes — useful if you ever want richer dashboards than the markdown frontmatter alone supports.
- **P_400 already tracks the signal chain itself** via `p115_linked` / `p300_linked` booleans and a `why_code` field (e.g. `P_300`) right on the P_400 note. I updated the Daily Report to query these directly instead of relying on manual backlinks — the automation already does what I was trying to build by hand.
- **Confirmed P_400 fields** (from the real note): `source, schema_version, signal_date, run_date, run_ts, ticker, write_route, written_by, note_version, write_route_history, account_id, council_verdict, risk_mode, entry_price, stop_price, target_1, target_2, position_size, order_type, order_id, lifecycle_status, entry_date, close_date, realized_pnl, why_code, sig_code, p115_linked, p300_linked, drop_reason`, plus a full options/spread block (`option_method, option_structure, option_contract, option_entry_premium, option_stop_premium, option_target_premium, option_contracts, option_override, option_override_justification, iv_rank, spread_long_strike, spread_short_strike, spread_debit, spread_max_profit, spread_max_loss, spread_breakeven`).
- **Confirmed P_300 fields** (from the real note): `source, schema_version, signal_date, run_date, run_ts, ticker, write_route, written_by, note_version, write_route_history, signal, signal_horizon, generated_dt`, plus five parallel horizon blocks `h5_win_rate/h5_mean_ret/h5_z_score/h5_class` through `h20_*`, and `top_analog_1-3, top_comp_dist_1, n_matches`.
- **Still unconfirmed:** P_115's own vault-write path and exact frontmatter. The archive proves P_115 signals exist and get processed, but I don't yet have a real `TradeOrderManagement/P115/` note to copy from. Templates and dashboard queries for P_115 remain placeholders using the same shared-schema pattern as P_300/P_400 until you share one.

---

## 0c. v1.3/v1.4 — Folding In P_117 / P_118 / P_920

What the signal archive actually showed about these two, all from real `signal_rationale` text (not guesses):

- **P_117 = an external/outside recommendation source.** The only sample seen: `"P_117 outside rec (info@lockandloadfinance.com); P_115 recheck BUY..."` — i.e. a tip from an outside email newsletter that P_115 then independently re-verifies (fundamentals, 200-MA, earnings) before deciding whether to pass it through.
- **P_118 = your own internal chart-pattern scanner.** Multiple samples: `"P_118 High Handle candidate; P_115 recheck ASYM..."`, `"P_118 Cup and Handle breakout, ASYM via P_115 recheck..."`, and a `signal_metadata.signal_source_link` value of `"P_118_STEP1/HNGE_2026-09-02_reemit"` — suggesting a multi-stage scan (`STEP1`) that can re-emit a candidate later with corrected levels.
- **Neither has a confirmed vault-write path of its own.** Their `signal_source_link` values (`"P_117/CEG_2026-09-02"`, `"P_118_STEP1/HNGE_2026-09-02_reemit"`) don't look like vault-relative paths the way P_300's did (`"trading_journal/TradeOrderManagement/P300/..."`) — they read more like internal identifiers or references to something outside the vault. So for now these are placeholders you can fill manually (or point a future writer at) rather than confirmed live folders.
- **P_115 itself got richer fields** from this same evidence: component scores `Fund/Anal/Candle/Setup/STR` rolling into a `HybridTier`, a fundamental pass/fail (ROE, Debt/Cap or Debt/Equity, FCF), a 200-MA regime check, an earnings-proximity check, and for breakout strategies a `BreakoutVerdict` (TrueBounce PASS/FAIL). The P_115 template now has this as "Block A" alongside the original ThinkScript Z-stack assumption as "Block B" — use whichever turns out to be the real live system once you confirm, or keep both if you actually run them in parallel.
- **P_920 = an end-of-day "Buyers-in-Control" scan** — another upstream source feeding P_115, same pattern as P_117/P_118. Only sample seen: `"P_920 Buyers-in-Control EOD scan, P_115 BUY signal (HybridTier=8, Fund 4/4 verified clean...)"`. Folded in at your request (v1.4) with the same placeholder caveat as P_117/P_118.
- **Added to the vault:** `TradeOrderManagement/P117/`, `TradeOrderManagement/P118/`, `TradeOrderManagement/P920/`, `Templates/Signal - P117.md`, `Templates/Signal - P118.md`, `Templates/Signal - P920.md`, plus corresponding Daily Report/Daily Review sections and `new_signal_note.py` support (`--type p117` / `--type p118` / `--type p920`).

---

## 1. Review of the Copilot Layout

What Copilot got right:
- Separating **Journal** (what you did) from **Analysis** (what you observed) is the correct base split, and bidirectional linking is the right mechanism.
- Trade Entry / Trade Exit / Daily Review as three note types is a sound minimum viable journal.

What was missing — and why it matters for you specifically:
1. **No home for signals.** Your actual pipeline is `P_115 (chart regime read) → P_300 (pattern signal + Council Review) → P_400 (TOS order ticket)`. None of that has a folder in Copilot's layout, so today it either lives only in chat history or gets summarized by hand into the Trade Entry note — you lose the audit trail the Council process is supposed to produce.
2. **No Council Status field anywhere.** Your project instructions are explicit that a trade shouldn't proceed without Approve / Approve with Caution / Block / Override Required from the five council roles. That status needs to be a queryable field, not prose buried in a thesis paragraph.
3. **"Daily Report" wasn't actually built.** Copilot's Daily Review template only has blank prose sections — it doesn't pull anything from your day's signals or trades. A daily report that requires you to manually recall and retype what happened isn't a report, it's still a blank journal page.
4. **Risk fields don't match your actual plan.** Your Trading Plan V2 uses 1.5% normal / 0.75% CORRECTION risk, a 3-gate sizing method, and a hard pre-trade checklist (§3.4). The Copilot template's generic `risk:` field doesn't capture mode or gate-pass status.
5. **P_115 has no file-based feed.** It's a ThinkScript chart study (Regime Council indicator: VWAP_Z, VOL_Z, OBV_Z, CMF_Z, RSI_Z, MACD_Z, PCT_GAIN_Z, sumZZ) — nothing writes it to disk automatically. Any design needs an explicit manual-capture step for this one, unlike P_300 which already emits `outputs/reports/<date>_<symbol>.txt` from Pipeline B.
6. **Signal vs. execution roles need to be kept distinct.** P_115 is signal-only now — it emits the entry read that feeds P_400, but no longer performs any order management itself. P_400 owns 100% of order construction and execution formatting. The vault structure needs to make that division obvious so a P_115 note never looks like it's carrying order-management responsibility.

The rest of this doc fixes all six.

---

## 2. Signal Sources — What Each One Actually Emits

| Source | What it is | What it emits | How it reaches the vault |
|---|---|---|---|
| **P_115** | Regime Council ThinkScript indicator (chart-only). **Signal-only role** — emits the entry read that feeds P_400; performs no order management itself | Plain-English regime/action/strength/volume tags + Z-stack (VWAP_Z, VOL_Z, OBV_Z, CMF_Z, RSI_Z, MACD_Z, PCT_GAIN_Z, sumZZ) | Manual: screenshot the chart, drop it in a `Signal - P115 Regime` note (Perplexity/Claude can read the screenshot and fill the fields for you via the regime-council-chart-analysis workflow) |
| **P_300 (Pattern)** | VantagePoint pattern-matching engine, Pipeline B | BUY / WATCH / PASS classification + n, win rate, composite Z | File: `outputs/reports/<date>_<symbol>.txt` → sync script converts to a vault note (parser is still a stub — see Section 9) |
| **P_300 (Council)** | Council Input Form → Council Review Response workflow (the trigger doc in this project) | Validation, calculated stop/limit inputs, Council Status (Approve / Approve with Caution / Block / Override Required), which role blocked it | Manual paste: copy the chat response into a `Signal - P300 Council` note |
| **P_400 (Batch Screen)** | Confirmed live: daily Tier-1 screening step, JSON output (`batch2b_<date>_<run_timestamp>.json`) | `cash_available`, `posture`, `screened_count`, `passed_tier1`, `evaluated`, `candidates`, `skipped` (symbol+reason), `cumulative_risk_if_all_taken`, `heat_cap`, `heat_warning` | **Automated via new script:** `sync_p400_batch_json.py` converts the JSON into a `TradeOrderManagement/P400-Batch/<date>.md` note |
| **P_400 (Per-Symbol)** | Confirmed live: `obsidian_writers` already writes one note per symbol automatically | Council verdict, write route, drop reason, archived signal JSON reference; live Schwab quote/chain data for options | **Already automated** — `vault_writer` writes straight to `TradeOrderManagement/P400/<date>_<TICKER>.md`. Exact frontmatter fields still need confirming against one real file (Section 9). |

Confirmed division of labor: P_400 replaced P_115's *order-management* function only — P_115 is still a live signal source, it just no longer touches execution. P_300 (Pattern + Council) validates and gates; P_400 is the sole order-management/execution layer, and — as of the log/JSON you shared — already handles its own batch screening, council verdicts, live Schwab pricing, and vault writing end-to-end. The `Feeds Into` link on every P_115 note points at `TradeOrderManagement/P400/`, in addition to `TradeOrderManagement/P300/`, to make that direct signal-to-execution path visible in the vault graph.

---

## 3. Vault Folder Structure

Vault root = `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal` (confirmed). `TradeOrderManagement/P400/` already exists and is already being written to by your live pipeline — nothing here should be renamed or moved on disk; the zip just adds the folders/files around it.

```
trading_journal/                    (vault root)
├── TradeOrderManagement/
│   ├── P115/                ← HybridTier scoring + optional ThinkScript read (both unconfirmed path)
│   ├── P117/                ← NEW — outside/external recommendations (placeholder, unconfirmed path)
│   ├── P118/                ← internal chart-pattern scanner candidates (placeholder, unconfirmed path)
│   ├── P920/                ← NEW — Buyers-in-Control EOD scan candidates (placeholder, unconfirmed path)
│   ├── P300/                ← BUY/WATCH/PASS pattern signals (fully automated, confirmed schema)
│   ├── P300-Council/        ← Council Input Form + Review Response
│   ├── P400/                ← ALREADY LIVE — written automatically by obsidian_writers
│   └── P400-Batch/          ← daily Tier-1 screening summary (posture/heat/cash)
├── Journal/
│   ├── Daily Reviews/       ← one note per day = your Daily Report
│   ├── Trade Entries/
│   ├── Trade Exits/
│   ├── Patterns/
│   ├── Mistakes/
│   └── Wins/
├── Analysis/
│   ├── Market Intel/
│   ├── Sector Rotation/
│   └── Macro Notes/
├── Dashboards/
│   ├── Daily Report (Live).md   ← always shows *today*, no new note needed
│   ├── Pattern Library.md
│   ├── Mistake Tracker.md
│   └── Performance Heatmap.md
├── Templates/
│   ├── Trade Entry.md
│   ├── Trade Exit.md
│   ├── Daily Review.md
│   ├── Signal - P115 Regime.md
│   ├── Signal - P117.md
│   ├── Signal - P118.md
│   ├── Signal - P920.md
│   ├── Signal - P300.md
│   ├── Signal - P300 Council.md
│   ├── Signal - P400 Order.md
│   └── Signal - P400 Batch Screen.md
└── scripts/
    ├── new_signal_note.py
    ├── sync_p300_pattern_reports.py
    └── sync_p400_batch_json.py
```

This exact structure is included as ready-to-drop-in files in the accompanying zip. Since `TradeOrderManagement/P400/` already exists in your real vault, extract the zip's contents *into* `trading_journal\` (not as a subfolder) so it merges with what's already there instead of creating a duplicate.

---

## 4. Unified Frontmatter Schema

Every note carries a `type`, `date`, and `ticker` (where applicable) so Dataview can query across all of them consistently:

| type | Folder | Key fields |
|---|---|---|
| `signal_p115` | TradeOrderManagement/P115 | regime, action, strength, sumzz, vwap_z...pct_gain_z |
| P_300 note (`source: P300`) | TradeOrderManagement/P300 | signal, signal_horizon, h5/h7/h10/h15/h20_win_rate, _mean_ret, _z_score, _class, n_matches |
| `signal_p300_council` | TradeOrderManagement/P300-Council | council_status, blocking_role, framework_mode, conditional_trigger |
| `signal_p400` | TradeOrderManagement/P400 | **already live** — confirmed vocabulary: council_verdict, write_route, drop_reason; exact frontmatter keys still TBD (Section 9) |
| `signal_p400_batch` | TradeOrderManagement/P400-Batch | cash_available, posture, screened_count, passed_tier1, evaluated, heat_cap, cumulative_risk_if_all_taken, heat_warning |
| `trade_entry` | Journal/Trade Entries | risk_pct, mode, council_status, links to all signal types |
| `trade_exit` | Journal/Trade Exits | result, r_multiple, outcome, entry_ref |
| `daily_review` | Journal/Daily Reviews | date only — everything else is pulled live via Dataview |

File naming convention throughout: `<date>_<ticker>.md` (e.g. `2026-09-04_BAC.md`), so every signal, entry, and exit for the same trade sorts together and is trivially cross-referenced.

---

## 5. The Daily Report (the actual ask)

Two versions, same queries, different purpose:

- **`Dashboards/Daily Report (Live).md`** — a single fixed note you open every evening. Its Dataview queries use `date(today)`, so it always reflects the current day with zero setup.
- **`Journal/Daily Reviews/<date>.md`** — created fresh each day from the `Daily Review` template. Its queries use `date = this.date`, referencing that note's own frontmatter date, so once written it becomes a permanent, accurate snapshot of that specific day (unlike the Live dashboard, which always jumps to "today").

Both pull the same eight tables, now built on the confirmed real schema rather than guessed field names:

1. **P_300 Pattern Signals** — ticker, signal, WR/Z at h5 and h10, n_matches (sorted by h5 Z-score, strongest first).
2. **P_115 Signals** — placeholder until a real note confirms its schema.
3. **P_400 — Approved / Trade-Worthy** — only rows where `write_route` is BUY or TRADE: ticker, entry, stop, T1, T2, size, risk mode.
4. **P_400 — Passed / Blocked** — everything else: ticker, route, council verdict, drop reason, origin (`why_code`).
5. **Signal Chain** — uses the real `p115_linked`/`p300_linked`/`why_code`/`lifecycle_status` fields to show exactly which upstream signal produced each P_400 record, with no manual linking required.
6. **Open Positions** (Live dashboard only) — every P_400 note with `lifecycle_status = OPEN`, so you can see what's still live at a glance.
7. **Trades Entered / Exited** — your own journal notes.
8. **P_400 Batch Screen** — posture, cash, heat cap, cumulative risk, warnings.

Splitting P_400 into "Approved/Trade-Worthy" vs. "Passed/Blocked" (tables 3 and 4) instead of one flat table makes the report read like an actual desk briefing — what's live/tradeable jumps out instead of being buried among the (usually much more numerous) REVIEWED_NO_TRADE rows. The Daily Review version additionally has prose sections for market summary, the Behavioral Judge check ("did I force any trades"), portfolio-heat check, and lessons, matching Council Roles 01 and 05 directly.

**Requires the Dataview community plugin** (Settings → Community Plugins → Browse → "Dataview" → Install → Enable). Templater is optional but recommended so `{{date}}` auto-fills when you create a note from a template — install "Templater" and point its template folder at `Templates/`.

---

## 6. Daily Workflow

0. **Pre-market batch screen (already automated):** P_400's Tier-1 screen runs and produces `batch2b_<date>_<run_timestamp>.json`. Run `sync_p400_batch_json.py` on it to get the day's posture/cash/heat into `TradeOrderManagement/P400-Batch/<date>.md`.
1. **Pre-market:** capture any P_115 chart reads for tickers on your radar → `TradeOrderManagement/P115/<date>_<ticker>.md`. This is signal only — P_115 does not manage the order.
2. **Signal check (already automated):** P_300 writes its own note straight to `TradeOrderManagement/P300/<date>_<ticker>.md` — nothing to do here manually.
3. **Council Review:** run the Council Input Form, paste the response → `TradeOrderManagement/P300-Council/<date>_<ticker>.md`. If Council Status isn't Approve or Approve with Caution, stop here — no order, no entry.
4. **Order generation (already automated):** P_400 writes its own verdict/order note straight to `TradeOrderManagement/P400/<date>_<ticker>.md` — nothing to do here manually unless you're logging a manual override.
5. **Log the trade:** create `Journal/Trade Entries/<date>_<ticker>.md` from the template, link back to the relevant signal notes, complete the §3.4 pre-trade checklist.
6. **On exit:** create `Journal/Trade Exits/<date>_<ticker>.md`, compute realized R using the *original* stop (Plan §5.2), log mistakes/improvements.
7. **End of day:** open `Dashboards/Daily Report (Live).md` for the desk check, then create today's `Journal/Daily Reviews/<date>.md` from the Daily Review template to lock in the permanent record.
8. **Weekly:** review `Dashboards/Mistake Tracker.md` and `Pattern Library.md`.

---

## 7. Automation Included (starter-level)

- `scripts/new_signal_note.py` — CLI that writes a correctly-formatted note into the right TradeOrderManagement/Journal folder from a paste (chat response, clipboard, or `--body` text), so you're not hand-typing frontmatter for every Council Review. Example:
  ```powershell
  Get-Clipboard | python new_signal_note.py --vault "C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal" `
      --type p300-council --ticker BAC --date 2026-09-04 `
      --field council_status="Approve with Caution"
  ```
- `scripts/sync_p300_pattern_reports.py` — **now a legacy fallback only.** A real sample confirmed P_300 already writes its own notes directly (same pattern as P_400), so this script is no longer part of the main flow. Kept only in case you ever need to backfill from an old-style Pipeline B `outputs/reports/<date>_<symbol>.txt` file that predates the automated writer.
- `scripts/sync_p400_batch_json.py` — **new, tested against your real `batch2b_2026-09-03_20260903_154518.json`.** Converts the daily Tier-1 screening JSON into `TradeOrderManagement/P400-Batch/<date>.md`, capturing posture, cash available, heat cap, cumulative risk, and every skipped symbol with its block reason. This is the one piece of your existing pipeline that wasn't reaching the vault yet.

All three are plain Python, no dependencies beyond the standard library, matching your existing Hub environment. Note that `TradeOrderManagement/P400/` itself needs **no sync script** — your `obsidian_writers` module already writes there directly.

---

## 8. Setup Steps (PowerShell)

This extracts *into* your existing `trading_journal` vault, merging with the live `TradeOrderManagement\P400\` folder that's already there — it will not overwrite any file P_400 has already written.

```powershell
# 1. Extract the starter package directly into your existing vault root
Expand-Archive -Path "AJZ-Obsidian-Trading-Vault-Starter.zip" -DestinationPath "C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal" -Force

# 2. Open C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal as an Obsidian vault (if not already)

# 3. In Obsidian: Settings -> Community plugins -> Browse -> install "Dataview" -> Enable
#    Optional: install "Templater" -> set template folder to Templates/

# 4. Confirm the dashboards render (open Dashboards/Daily Report (Live).md)
#    It should already show any P_400 activity from today, since that folder is live.

# 5. Convert today's batch screen JSON into the vault
cd "C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\scripts"
python sync_p400_batch_json.py --batch-file "<path to today's batch2b_*.json>" --vault "C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal"

# 6. Test the CLI helper
python new_signal_note.py --vault "C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal" --type p300-council --ticker TEST --date 2026-09-04 --body "test paste"
```

---

## 9. Open Items for You to Confirm

- **Resolved:** P_115 is a live signal source that feeds P_400 directly; P_400 owns all order management.
- **Resolved:** vault root is `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal`, confirmed live.
- **Resolved:** P_400 per-symbol frontmatter — confirmed against a real note, full field list in Section 0b and Section 4.
- **Resolved:** P_300 also has an automated vault writer — confirmed against a real note, full field list in Section 0b and Section 4. `TradeOrderManagement/P300/` is the correct folder (not `P300-Pattern`).
- **Still open — P_115's own vault-write path/frontmatter:** the signal archive proves P_115 signals exist and flow through the same envelope schema as P_300, but I don't have a real generated `TradeOrderManagement/P115/<date>_<ticker>.md` note to confirm its exact frontmatter. If P_115 writes one, paste a real example the same way you did for P_400/P_300.
- **Still open — HybridTier vs. ThinkScript Regime Council:** you said not sure yet. The P_115 template now carries both field sets ("Block A" HybridTier, "Block B" ThinkScript Z-stack) side by side so nothing is lost either way — resolve whenever you're ready, no rush.
- **Resolved:** P_117 and P_118 are folded in — new folders, templates, and Daily Report sections added (Section 0c). Both are placeholders since neither has a confirmed vault-write path yet; paste a real sample if either ever writes one.
- **Resolved:** P_920 ("Buyers-in-Control EOD scan") is now folded in the same way as P_117/P_118 (v1.4) — folder, template, Daily Report/Daily Review sections, and `new_signal_note.py --type p920`. Same placeholder caveat: no confirmed vault-write path yet, just the one rationale mention.
