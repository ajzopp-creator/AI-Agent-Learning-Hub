# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

P_400 Trade Order Management. Consumes trade signals from upstream strategy projects (P_115, P_300) and produces order tickets for Tony to review and submit. Tony reviews and submits every order — P_400 never auto-submits.

## Running Code

All commands run from `python\` with the p140 env:

```
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python
C:\Users\Trader\.conda\envs\p140\python.exe cli.py
```

Run tests (no pytest required):
```
C:\Users\Trader\.conda\envs\p140\python.exe test_read_signals.py
```

## Architecture

Python code lives in `python\` with strict layer separation:

- `config.py` — all paths and constants; `SIGNALS_DIR` points to the live signals folder
- `schemas.py` — re-exports `SignalV2` and `AssetClass` from the shared contract at `shared_resources.python_utils.signal_schemas`; P_400 never imports from P_800 internals
- `domain/packet_classifier.py` — pure logic; classifies signal filenames as `V2`, `LEGACY`, or `UNKNOWN`
- `infrastructure/signal_loader.py` — I/O only; scans `SIGNALS_DIR`, reads JSON, validates against `SignalV2`; bad packets are rejected and logged, never repaired (locked E2 decision #3)
- `application/read_signals.py` — orchestration; calls infra and domain, assembles `ReadResult`
- `cli.py` — CLI entry point; prints a summary table
- `test_read_signals.py` — standalone tests against live folder + temp dir

Signal files follow the naming convention `<date>_<SYMBOL>_v2.0.json`. Legacy packets (`*_signal.json`) are counted but not parsed during the dual-read compat window (`TOLERATE_LEGACY = True` in config).

## Signal Contract

P_400 is a signal consumer. `SignalV2` is the canonical schema (owned by P_800, shared via `04-Shared-Resources\python_utils\signal_schemas.py`). Key fields used by P_400: `symbol`, `asset_class`, `guideline_entry`, `guideline_stop`, `signal_source`.

## Shared Resources

- Signal schema: `C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\python_utils\signal_schemas.py`
- Account parameters (risk sizing rules, read live, never hardcode): `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md`
- Schwab Token Manager: `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\schwab_api\`
- Work order ledger: `C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\work_orders\`

## Risk Rules

Standing gates (read live from account params file; never hardcode values):
- Normal mode: 1.5% risk/trade, max 5% single position, min 2:1 R:R, max 3 open trades
- Correction mode: 0.75% risk/trade, max 2 open trades

## Open Work Orders

Check these before any signal-ingest or schema work:
- `WO-P800-E2.001` — signal packet schema v2.0 adoption (affects P_115/P_300/P_400)
- `WO-P115-E1.001` — P_115 signal emitter feeding P_400
