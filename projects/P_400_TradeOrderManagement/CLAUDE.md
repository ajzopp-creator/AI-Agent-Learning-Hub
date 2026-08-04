# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

P_400 Trade Order Management. Consumes trade signals from upstream strategy projects (P_115, P_300) and produces order tickets for Tony to review and submit. Tony reviews and submits every order — P_400 never auto-submits.

## Running Code

All commands run from `python\` with the p140 env:

```
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python

# Signal inbox summary
C:\Users\Trader\.conda\envs\p140\python.exe cli.py

# Tier-1 screen of all inbox signals
C:\Users\Trader\.conda\envs\p140\python.exe cli.py screen-all

# Full evaluation of one signal
C:\Users\Trader\.conda\envs\p140\python.exe cli.py evaluate SYMBOL --snapshot snapshot_SYMBOL.json --cash 50000

# Build order spec (evaluated + formatted for submission)
C:\Users\Trader\.conda\envs\p140\python.exe cli.py spec SYMBOL --snapshot snapshot_SYMBOL.json --cash 50000

# Stock vs option vehicle comparison
C:\Users\Trader\.conda\envs\p140\python.exe cli.py compare SYMBOL --snapshot snapshot_SYMBOL.json --chain chain_SYMBOL.json --cash 50000

# Paper session (same sizing logic; records to paper book dir)
C:\Users\Trader\.conda\envs\p140\python.exe cli.py --paper-session evaluate SYMBOL --snapshot snapshot_SYMBOL.json --cash 50000
```

Additional CLI flags for `evaluate` and `spec`: `--target PRICE` (override signal target), `--pre-market` (forces market_open=True), `--qty-override N` (bypasses share sizing post-council), `--drop-reason REASON` (archive without trading).

Run a single test file:
```
C:\Users\Trader\.conda\envs\p140\python.exe -m pytest python\test_sizing.py -v
```

All test files are in `python\` and named `test_*.py`. Tests run standalone (no fixtures needed).

## Architecture

Python code lives in `python\` with strict layer separation:

**Config / Schema**
- `config.py` — all paths, thresholds, and constants. Risk-mode multipliers, sizing constants, and option viability gates live here.
- `schemas.py` — re-exports `SignalV2` and `AssetClass` from the shared contract; defines P_400-owned schemas: `BookRecord`, `PostureSnapshot`, `AccountParams`, `SnapshotDict`, `OptionChainInput`.

**Domain (pure logic, no I/O)**
- `domain/packet_classifier.py` — classifies signal filenames as `V2`, `LEGACY`, or `UNKNOWN`
- `domain/sizing.py` — three-gate stock sizer; returns `SizingResult` with share count, dollar risk, winning gate, and R:R
- `domain/council.py` — five-role deterministic block checks (QUANT, RISK, MACRO, TAPE, BEHAVIORAL); returns `CouncilResult` with verdict `APPROVED | APPROVED_WITH_CAUTION | BLOCKED`
- `domain/council_codes.py` — reason code constants (e.g. `RC_HEAT_BREACH`)
- `domain/screen.py` — Tier-1 lightweight screen across all inbox signals; returns pass/flag per signal without full evaluation
- `domain/portfolio.py` — builds `PortfolioState` (heat, open counts, sector exposure, realized day loss) from a list of `BookRecord`
- `domain/options_sizer.py` — two option sizing methods: chart-based and risk-budget-first; viability gates from config
- `domain/options_council.py` — option-specific block checks (OI, spread pct, IV rank)
- `domain/spread_sizer.py` — debit/credit spread sizing
- `domain/vehicle_selector.py` — compares stock vs option R:R; returns `VehicleComparison` with recommendation

**Infrastructure (I/O only)**
- `infrastructure/signal_loader.py` — scans `SIGNALS_DIR`, validates JSON against `SignalV2`; rejects bad packets, never repairs
- `infrastructure/book_loader.py` — reads `*.md` files from `BOOK_DIR`, extracts YAML frontmatter, validates as `BookRecord`; CLOSED records included for daily-loss calculation
- `infrastructure/params_reader.py` — parses `P_000_Account_Parameters_Current.md` for live account balance and risk sizing
- `infrastructure/posture_reader.py` — glob-discovers `P_010_RiskConfig.json` and returns `PostureSnapshot` with risk_mode
- `infrastructure/signal_archiver.py` — appends processed JSON packets to monthly zip in `SIGNALS_PROCESSED_DIR`, then deletes from inbox
- `infrastructure/chain_loader.py` — reads `chain_SYMBOL.json` and validates as `OptionChainInput`
- `infrastructure/record_writer.py` — writes `*_P400.md` trade records to `BOOK_DIR`

**Application (orchestration only)**
- `application/read_signals.py` — calls infra + domain; returns `ReadResult` with valid count, rejected list, legacy count
- `application/evaluate_signal.py` — full pipeline: reads posture + params + book fresh, reconciles entry drift, sizes, runs Council, returns `EvaluationResult`
- `application/build_order_spec.py` — formats `EvaluationResult` into a human-readable order spec block
- `application/drop_signal.py` — archives a signal without trading (writes REVIEWED_NO_TRADE record)
- `application/compare_vehicles.py` — loads snapshot + chain, runs both sizing paths, calls `vehicle_selector`
- `application/build_spread_spec.py` — builds spread order spec

## Full Evaluation Pipeline

`cli.py evaluate SYMBOL` → `evaluate_signal()`:
1. Validate `SnapshotDict` (live market data Tony provides as JSON)
2. Read posture from P_010 RiskConfig, account params from P_000 markdown, book records from BOOK_DIR
3. Compute entry drift (`(live_price - guideline_entry) / guideline_entry * 100`)
4. If adverse drift > `ENTRY_DRIFT_THRESHOLD_PCT` (1.5%) and R:R collapses below minimum → auto-BLOCK with `RC_ADVERSE_DRIFT`
5. Three-gate stock sizer (risk gate → position gate → cash gate); active gate determines share count
6. Five Council votes → `APPROVED | APPROVED_WITH_CAUTION | BLOCKED`
7. Archive signal packet to monthly zip; write evaluation result

## Signal Contract

`SignalV2` is canonical schema owned by P_800, shared via `shared_resources\python_utils\signal_schemas.py`. P_400 re-exports it from `schemas.py` — **never import from P_800 internals directly**.

Signal files: `<date>_<SYMBOL>_v2.0.json` in `SIGNALS_DIR`. Legacy packets (`*_signal.json`) are counted but not parsed while `TOLERATE_LEGACY = True` in config.

Snapshot files (`snapshot_SYMBOL.json`) are assembled by Tony/Claude from live market data and handed to the pipeline at eval time. Required fields defined in `SnapshotDict` schema.

Option chain files (`chain_SYMBOL.json`) are required for `compare` and spread paths. Required fields defined in `OptionChainInput` schema. Source priority: TOS → ChartExchange → Yahoo → Barchart.

## Vault Write Schema

`P400Record` (obsidian_writers\domain\vault_schemas.py, P_800-owned -- P_800 validates
all P_400 vault writes against this model) gained a `source` field and six
spread-specific fields (`spread_long_strike`, `spread_short_strike`, `spread_debit`,
`spread_max_profit`, `spread_max_loss`, `spread_breakeven`) under WO-P400-E3.004.
`extra="forbid"` on this model briefly broke every P400 write (2026-06-30, narrow
window, caught same-session) when `write_handler.py` injects an unmodeled `source`
key -- fixed by adding `source: Optional[str] = None` to the model. P_800
acknowledged 2026-07-21. A second schema key, `"P400_PAPER"`, was added
2026-07-21 for paper-trade routing (WO-P400-E2.019) -- see Paper book note below.

## Key Paths

- Signals inbox: `trading_journal\TradeOrderManagement\signals\`
- Processed signals archive: `signals\processed\YYMM_ProcessedJson.zip`
- Open-position book: `trading_journal\TradeManagement\P400\` (`.md` files with YAML frontmatter)
- Paper book: `trading_journal\TradeManagement\P400\paper\` (fixed WO-P400-E2.019, 2026-07-21 -- was TradeOrderManagement, stale since E2.012 moved BOOK_DIR's root)
- Account params: `projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md`
- P_010 posture: glob-discovered at `**/P_010_RiskConfig.json`

## Locked Decisions

- Bad signal packets are **rejected and logged, never repaired** (E2 decision #3)
- `BOOK_DIR` points to `TradeManagement\P400` (not `TradeOrderManagement`) — this was fixed in WO-P400-E2.012 and must not be reverted
- Risk parameter values must be read live from `P_000_Account_Parameters_Current.md`; never hardcode them in config or domain
- Paper records write to a separate P_800 schema key, `"P400_PAPER"` (obsidian_writers\schemas.py), not a folder override on the `"P400"` schema -- `write_to_vault()` has no folder parameter (WO-P400-E2.019)

## Open Work Orders

Check `Agentic-Hub-Governance\work_orders\` before signal-ingest or schema work:
- `WO-P800-E2.001` — signal packet schema v2.0 adoption (affects P_115/P_300/P_400)
- `WO-P115-E1.001` — P_115 signal emitter feeding P_400


## Known Gaps (not yet formal WOs)

- **2026-07-28 — `defined_risk_confirmed` never wired end-to-end.** `domain\council.py`'s
  `macro_vote()` accepts a `defined_risk_confirmed: bool = False` param that converts an
  `EARNINGS_IN_WINDOW` MACRO block to CAUTION, per architecture doc Section 3.4/4.4's
  "Confirm defined-risk to convert to CAUTION" language and the BLOCK message printed
  by the CLI itself. Grepped the whole `application\` layer and `cli.py` -- the param is
  referenced nowhere outside `council.py`'s own signature and `test_council.py`'s unit
  tests. No CLI flag exists to set it (confirmed via `cli.py evaluate --help`); `--options`
  does not set it either. Net effect: any earnings-in-window MACRO block is currently
  un-convertible from the CLI -- the documented escape hatch is dead code. Found live on
  CCEP (2026-07-28), same day NBIX hit the identical block with no attempt to work around
  it. Needs a real WO: either wire a `--defined-risk-confirmed` flag (and decide what
  evidence justifies setting it -- an options `--chain` present? an explicit flag?) or a
  reduced-size equivalent if Tony wants that path added, since today only defined-risk
  exists in the domain layer at all, and even that isn't reachable from the CLI.