# CLAUDE.md -- P_300 Project Memory
# Save to: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\CLAUDE.md
# Layers ON TOP of global C:\Users\Trader\.claude\CLAUDE.md. Project-specific only.
# P_300 VantagePoint Pattern Recognition System.
# Full spec: docs\P_300_System_Architecture_v2.7.md
# Last updated: 2026-08-04 (SIP version reference corrected v3.3 -> v3.5 --
# stale since 2026-07-28's Step 0.6 addition; caught during WO-P300-E5.002/
# E5.005 independent review when this session's own INIT read a stale
# project-attached v3.3 copy instead of the live v3.5 file, M-015)

---

## Purpose

P_300 -- VantagePoint Pattern Recognition. Two pipelines:
- **Pipeline A (Add Pattern):** ingests VP XLSX history files into the catalog DB
- **Pipeline B (Daily Evaluate):** reads live VP data, queries catalog, produces BUY/WATCH/PASS signal

Tony runs the pipelines. Claude writes and debugs the Python.

---

## Folder Name -- copy verbatim, never reconstruct

RIGHT: P_300_Vantage_Point_Pattern_Recognition

---

## Running Code

Always invoke `python python\cli.py` from project root -- never from a subfolder.

All commands use p140 explicitly:

```
# Daily evaluate
C:\Users\Trader\.conda\envs\p140\python.exe python\cli.py daily-evaluate --symbol AAPL

# Add pattern
C:\Users\Trader\.conda\envs\p140\python.exe python\cli.py add-pattern --file "data\historical_patterns\Pattern_....xlsx"
```

Operator-run launchers (never invoked directly by Claude): `P_300_AddPattern.bat`,
`P_300_DailyEval_v2.bat` / `P_300_RunAllDailyEvals.ps1`, `P_300_BulkExtract.bat`,
`P_300_MinePatterns.bat` + `P_300_IngestMined.bat`, `P_300_Preflight.bat`,
`run_eval_loop.bat`.

**Never use bare `python` -- four Python installs exist on PATH; p140 must be explicit.**

Diagnostic if Python fails:
```powershell
$PROFILE                      # expect: D:\OneDrive\...\Microsoft.PowerShellISE_profile.ps1
(Get-Command python).Source   # expect: C:\Users\Trader\.conda\envs\p140\python.exe
```

---

## Canonical Paths

| What | Path |
|------|------|
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\` |
| Python layer | `python\` |
| Active catalog DB | `db_utils.get_latest_catalog()` -- glob `*catalog.db`, newest. NEVER hardcode. |
| Catalog naming | `<mmddyy>catalog.db` e.g. `061126catalog.db` |
| Temp working DB | `models\temp_working.db` -- transient write target only |
| Live XLSX input | `data\live\History Grid (<symbol>).xlsx` |
| Pattern XLSX input | `data\historical_patterns\Pattern_<start>_<end>_<symbol>.xlsx` -- NOT `data\historical\` |
| Bulk mining input | `data\bulk\mine\` (mine-patterns -> ingest-mined) -- NOT `data\historical_patterns\` |
| Posture reconstruction grids | `data\reference\10_Pattern_SPY.xlsx` / `10_Pattern_QQQ.xlsx` -- 10yr VP grids for regime reconstruction (WO-P300-E5.006); kept out of `data\bulk\mine\` so BulkAddPattern never scans them |
| IntelliScan eval-parameters grid | `data\live\P_300_HistoryGrid_IntelliscanEvalParameters.xlsx` |
| Signal output | `outputs\reports\<date>_<symbol>.txt` |
| Work order ledger | `Agentic-Hub-Governance\work_orders\` |
| Shared schema | `shared_resources\python_utils\signal_schemas.py` |
| Signal emitter | `python\infrastructure\signal_emitter.py` |
| Session working state | `tasks\todo.md` (live) + `tasks\todo_archive.md`; `tasks\lessons.md` (live) + `tasks\lessons_archive.md` |

OneDrive paths: always `Path(os.environ["OneDrive"])` -- never hardcode drive letter.

---

## Python Layer Architecture

```
python\
+-- config.py              <- ALL constants and paths -- single source of truth
+-- schemas.py             <- Pydantic models Pipeline A
+-- schemas_pipeline_b.py  <- Pydantic models Pipeline B (in-memory)
+-- schemas_preflight.py   <- Pydantic model -- preflight status artifact (WO-P000-E4.001)
+-- domain\                <- Business logic ONLY -- no I/O, no DB, no print
+-- infrastructure\        <- I/O ONLY -- files, DB, APIs
+-- application\           <- Orchestration ONLY -- calls domain + infra
+-- cli.py                 <- Entry point (thin shim; real commands in cli_commands\, WO-P300-E4.001)
+-- migrations\            <- One-shot migration scripts
```

Note: `schemas_signal_packet.py` is vestigial -- superseded by `SignalV2` in `shared_resources.python_utils.signal_schemas`. Do not import or extend it.

**Hard rules:**
- `domain\` cannot import `sqlite3`, `requests`, or anything from `infrastructure\`
- `infrastructure\` has no business logic
- `application\` has no raw logic, no direct I/O
- All paths in `config.py` only -- never hardcode elsewhere

---

## DB Write Safety -- mandatory for ALL catalog writes

1. **Check-Out:** verify catalog health before touching DB
2. Every `sqlite3.connect()` must set `PRAGMA foreign_keys = ON` immediately after -- all connections go through `python\utilities\db_connect.py`, never `sqlite3.connect()` directly
3. **Lock + Temp-DB + Atomic Move:** write to `temp_working.db`, verify, then move
4. **Check-In:** verify catalog health after write
5. Never write directly to the master catalog DB

Health check gate: `OVERALL == HEALTHY` AND `hollow == 0` before any in-session DB op.

---

## Signal Emitter

`python\infrastructure\signal_emitter.py` emits signal packets consumed by P_400.

- Schema: `SignalV2` from `shared_resources.python_utils.signal_schemas` -- import via editable install, no sys.path manipulation
- sys.path insert previously at line 57 has been removed. Do not re-introduce it. Import resolves via `hub_shared` editable install.
- WO-P000-E2.003 (PENDING as of 2026-07-22): `daily_evaluate_pipeline.py` still carries a `_HUB_ROOT` sys.path insert for the LM Studio status check -- this is the remaining scope. Blocked pending ENH-P000 (LM Studio Hub interface). Do not remove that insert until ENH-P000 ships.

**Stop fields:** emit `intelliscan_support_1`, `intelliscan_support_2`, and `atr_adjusted_stop` in every packet when the IntelliScan grid is present at eval time. P_300 does NOT decide which level clears risk -- P_400's three-gate logic does; emitting only the tighter level would force P_400 to reject setups it could accept with the wider one. All three fields are `None` (not zero, not omitted) when the grid is absent. Stop method hierarchy: chart structure (primary) > IntelliScan VP support (preferred) > ATR-based, 2x ATR below entry (fallback).

**ATR:** shared Wilder util at `shared_resources/python_utils/atr.py`, computed at eval time on bars already in memory -- never re-fetched downstream. Full True Range (max of high-low, |high-prev_close|, |low-prev_close|) + Wilder RMA smoothing, never a high-low-only or simple-average proxy.

---

## Pipeline Contracts (locked -- do not change without WO)

**Pipeline A:** XLSX -> Lock + Temp-DB + Atomic Move -> permanent rows in catalog
**Pipeline B:** Live XLSX -> in-memory normalization -> BUY/WATCH/PASS signal. READ-ONLY -- no EVAL_SET inserts (Decision E, locked Stage 6).

BUY: n>=5, win_rate>=0.70, z>0.0
WATCH: n>=3, win_rate>=0.60, z>0.0
Fail to PASS -- never silently produce a BUY.

**Target ownership:** P_300 emits a baseline only -- guideline entry/target/stop + setup context, `position_size=0` sentinel. P_400 is the single authority that resolves the broker-facing final target: validates reward-to-risk, applies sizing/stop/council rules, publishes the order-ready target. P_300 never presents its levels as execution-final; the `guideline_*` field names encode this.

**The two pipelines never merge.**

---

## Catalog Composition Target

Maintain ~70% uptrend / 30% pullback, roughly 3:1 (uptrend:pullback) on every new batch -- holds baseline win rate in the 0.65-0.72 range where BUY/WATCH gates stay meaningfully discriminating. Pullback pattern: 15-25% decline across the pre-anchor 20-bar window, 3-5 bars of tight sideways consolidation, anchor = first day of consolidation.

---

## VP License Constraints

Tony's VantagePoint subscription doesn't cover every sector browse. When a recommended symbol is unavailable, Tony names alternatives and Claude substitutes preserving the original thesis -- never silently drop the idea because the exact symbol isn't accessible.

---

## Anti-Patterns -- never introduce

1. `df.tail(N)` / `df.head(N)` in ingest -- locks window, silently drops bars
2. TEXT into INTEGER FK -- `symbol_id` is INTEGER
3. Raw dollar values in similarity matching -- use normalized `pattern_bars` columns
4. Mock data in production Pipeline B
5. Hardcoded DB paths outside `config.py`
6. Mixed layers (domain doing I/O, infrastructure doing logic)
7. Merged Pipeline A + B
8. LLM output in BUY/WATCH/PASS decision path
9. Direct write to master catalog DB
10. Skipping Check-Out / Check-In
11. Module name colliding with Python stdlib (`signal`, `csv`, `json`, etc.)
12. Unicode through Python stdout to PowerShell -- ASCII only on stdout
13. `return_pct` treated as percentage -- stored as decimal fraction (0.0672 = 6.72%); x100 at display only
14. 4x`.parent` from `python\application\` to reach Hub root -- requires 5x`.parent`
15. sys.path inserts for shared-contract imports -- use editable install

---

## Schema Quick Reference

`return_pct` is decimal fraction. Forward label horizons: 5, 7, 10, 15, 20 days.
`data_origin_type`: `PATTERN_IDENT` (permanent) or `EVAL_SET` (reserved -- never insert).

---

## Work Orders -- check before emitter or schema work

| WO | Status | Scope |
|----|--------|-------|
| WO-P115-E1.001 | CLOSED 2026-06-11 | P_115 signal emitter -- signal contract locked; P_300 ack done |
| WO-P800-E2.001 | CLOSED 2026-06-11 | Signal packet schema v2.0 -- all acks done; SignalV2 is the contract |
| WO-P000-E2.003 | PENDING | sys.path removal -- signal_emitter.py DONE; daily_evaluate_pipeline.py blocked on ENH-P000 |
| WO-P000-E8.001 | PENDING (P_300 pilot in progress) | Working-state doc retention -- this file + todo/lessons archive split |

Full P_300 WO status: `Agentic-Hub-Governance\work_orders\WO-P300-*.md` -- check before any build.

---

## INIT Execution (WO-P000-E4.001, 2026-06-18)

INIT no longer calls `python` via `windows-mcp:PowerShell` for catalog/LM-Studio checks -- that call shape reliably hits the ~4-min subprocess ceiling. Operator runs `P_300_Preflight.bat` (project root) before or during a session; it writes `P_300_preflight_status.json` (project root), which INIT reads via `windows-mcp:FileSystem` instead. Current SIP: `docs\P_300_System_Initialization_Prompt_v3_1.md` v3.5.

---

## Session / Plan Discipline

The moment a file plan gets explicit operator go-ahead, write it to `tasks\todo.md` in the same turn -- before asking "anything else" or accepting a session-end signal. A plan discussed but not written to disk is not project state; the next session's INIT reads `todo.md` directly and won't know it exists.

---

## Working-State Doc Retention (WO-P000-E8.001)

`tasks/todo.md` and `tasks/lessons.md` are live, size-capped files -- `todo.md` at ~500 lines/~100KB, `lessons.md` at ~40 entries/~70KB. When a live file crosses its cap, the oldest entries move to the matching `_archive` file (nothing deleted). This file holds standing architecture and decision facts that don't belong in either -- promote a lesson here once it's a settled decision rather than letting it accumulate indefinitely in `lessons.md` as an "active bug watch" it no longer is.

---

## Roles

- Tony: trading domain expert, runs pipelines, reviews signals, business calls
- Claude: all Python, debugging, file writes

---

## Before Touching Any Code

1. Confirm p140 is active interpreter
2. Run catalog health check if DB work involved
3. Check WO status above if touching emitter or signal schema
4. Never write to master catalog DB directly
5. If a file plan just got a go-ahead, write it to `tasks\todo.md` before doing anything else

---

## Maintenance

This file is edited in place -- unlike `tasks/todo.md`/`tasks/lessons.md`, it does not accumulate; superseded content is replaced, not appended.

**2026-08-04:** SIP version reference corrected v3.3 -> v3.5 in the INIT
Execution section -- stale since 2026-07-28 (SIP's own Step 0.6 addition).
Caught during WO-P300-E5.002/E5.005 independent review, cosmetic-drift
item flagged there, fixed here per Tony's explicit "fix these" instruction.

**2026-07-22 (WO-P000-E8.001 pilot):** Merged 8 Locked Decisions promoted
from `tasks/lessons.md` (M-012, M-023, M-025, M-033, M-049, M-050, M-052,
M-078). Two stale items corrected during the merge, both found by
cross-checking against this session's real, verified state rather than
trusted on the file's own word (M-054 discipline): (1) removed the
"MCP-safe wrappers" (`P_300_DailyEval_mcp.ps1` / `P_300_AddPattern_mcp.ps1`)
from Running Code -- both confirmed on disk, created 2026-05-29, never
modified since, and referenced nowhere else in this project's real,
active tooling (SIP, SKILL, todo.md, or any real batch run logged this
year); real launchers are the `.bat`/`.ps1` files listed above. (2)
INITIALLY (incorrectly) "corrected" a claim that the session header
has "no `--` separator as of SIP v3.3" -- that first check was made
only against the stale project-attached SIP copy from the start of
this session, not the live file (M-015: attachments lag disk -- the
exact rule being applied elsewhere all session, missed here on the
one file that mattered most for this check). Re-verified 2026-07-22,
later the same session, against the real live SIP file: it already
carries a "Header separator dropped" amendment under its own v3.3
changelog (WO-P000-E4.001 v1.1) -- the real format is
`P_300 [Day, Month DD, YYYY] [HH:MM] ET`, NO separator. The recovered
content's original claim was correct; this file's own earlier "fix"
was the actual error, reverted here.
This file itself was unknowingly overwritten and restored via
`git show` earlier the same session (see `tasks/lessons.md` M-109) --
the two corrections above were caught specifically because the restore
prompted a full re-read against current reality instead of trusting the
recovered content at face value.
