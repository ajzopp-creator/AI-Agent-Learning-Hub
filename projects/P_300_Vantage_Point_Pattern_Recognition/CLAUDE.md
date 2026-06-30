# CLAUDE.md — P_300 Project Memory
# Save to: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\CLAUDE.md
# Layers ON TOP of global C:\Users\Trader\.claude\CLAUDE.md. Project-specific only.
# P_300 VantagePoint Pattern Recognition System.
# Full spec: docs\P_300_System_Architecture_v2.7.md
# Last updated: 2026-06-18

---

## Purpose

P_300 — VantagePoint Pattern Recognition. Two pipelines:
- **Pipeline A (Add Pattern):** ingests VP XLSX history files into the catalog DB
- **Pipeline B (Daily Evaluate):** reads live VP data, queries catalog, produces BUY/WATCH/PASS signal

Tony runs the pipelines. Claude writes and debugs the Python.

---

## Folder Name — copy verbatim, never reconstruct

RIGHT: P_300_Vantage_Point_Pattern_Recognition

---

## Running Code

All commands use p140 explicitly:

```
# Daily evaluate
C:\Users\Trader\.conda\envs\p140\python.exe python\cli.py daily-evaluate --symbol AAPL

# Add pattern
C:\Users\Trader\.conda\envs\p140\python.exe python\cli.py add-pattern --file "data\historical_patterns\Pattern_....xlsx"

# MCP-safe wrappers (use these from Desktop, not the .bat files)
P_300_DailyEval_mcp.ps1 -Symbol AAPL
P_300_AddPattern_mcp.ps1 -XlsxPath "..."
```

**Never use bare `python` — four Python installs exist on PATH; p140 must be explicit.**

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
| Active catalog DB | `db_utils.get_latest_catalog()` — glob `*catalog.db`, newest. NEVER hardcode. |
| Catalog naming | `<mmddyy>catalog.db` e.g. `061126catalog.db` |
| Temp working DB | `models\temp_working.db` — transient write target only |
| Live XLSX input | `data\live\History Grid (<symbol>).xlsx` |
| Pattern XLSX input | `data\historical_patterns\Pattern_<start>_<end>_<symbol>.xlsx` |
| Signal output | `outputs\reports\<date>_<symbol>.txt` |
| Work order ledger | `Agentic-Hub-Governance\work_orders\` |
| Shared schema | `shared_resources\python_utils\signal_schemas.py` |
| Signal emitter | `python\infrastructure\signal_emitter.py` |

OneDrive paths: always `Path(os.environ["OneDrive"])` — never hardcode drive letter.

---

## Python Layer Architecture

```
python\
├── config.py              ← ALL constants and paths — single source of truth
├── schemas.py             ← Pydantic models Pipeline A
├── schemas_pipeline_b.py  ← Pydantic models Pipeline B (in-memory)
├── schemas_preflight.py   ← Pydantic model — preflight status artifact (WO-P000-E4.001)
├── domain\                ← Business logic ONLY — no I/O, no DB, no print
├── infrastructure\        ← I/O ONLY — files, DB, APIs
├── application\           ← Orchestration ONLY — calls domain + infra
├── cli.py                 ← Entry point
└── migrations\            ← One-shot migration scripts
```

Note: `schemas_signal_packet.py` is vestigial — superseded by `SignalV2` in `shared_resources.python_utils.signal_schemas`. Do not import or extend it.

**Hard rules:**
- `domain\` cannot import `sqlite3`, `requests`, or anything from `infrastructure\`
- `infrastructure\` has no business logic
- `application\` has no raw logic, no direct I/O
- All paths in `config.py` only — never hardcode elsewhere

---

## DB Write Safety — mandatory for ALL catalog writes

1. **Check-Out:** verify catalog health before touching DB
2. **Lock + Temp-DB + Atomic Move:** write to `temp_working.db`, verify, then move
3. **Check-In:** verify catalog health after write
4. Never write directly to the master catalog DB

Health check gate: `OVERALL == HEALTHY` AND `hollow == 0` before any in-session DB op.

---

## Signal Emitter

`python\infrastructure\signal_emitter.py` emits signal packets consumed by P_400.

- Schema: `SignalV2` from `shared_resources.python_utils.signal_schemas` — import via editable install, no sys.path manipulation
- sys.path insert previously at line 57 has been removed. Do not re-introduce it. Import resolves via `hub_shared` editable install.
- WO-P000-E2.003 (PENDING): `daily_evaluate_pipeline.py` still carries a `_HUB_ROOT` sys.path insert for the LM Studio status check — this is the remaining scope. Blocked pending ENH-P000 (LM Studio Hub interface). Do not remove that insert until ENH-P000 ships.

---

## Pipeline Contracts (locked — do not change without WO)

**Pipeline A:** XLSX → Lock + Temp-DB + Atomic Move → permanent rows in catalog
**Pipeline B:** Live XLSX → in-memory normalization → BUY/WATCH/PASS signal. READ-ONLY — no EVAL_SET inserts (Decision E, locked Stage 6).

BUY: n≥5, win_rate≥0.70, z>0.0
WATCH: n≥3, win_rate≥0.60, z>0.0
Fail to PASS — never silently produce a BUY.

**The two pipelines never merge.**

---

## Anti-Patterns — never introduce

1. `df.tail(N)` / `df.head(N)` in ingest — locks window, silently drops bars
2. TEXT into INTEGER FK — `symbol_id` is INTEGER
3. Raw dollar values in similarity matching — use normalized `pattern_bars` columns
4. Mock data in production Pipeline B
5. Hardcoded DB paths outside `config.py`
6. Mixed layers (domain doing I/O, infrastructure doing logic)
7. Merged Pipeline A + B
8. LLM output in BUY/WATCH/PASS decision path
9. Direct write to master catalog DB
10. Skipping Check-Out / Check-In
11. Module name colliding with Python stdlib (`signal`, `csv`, `json`, etc.)
12. Unicode through Python stdout to PowerShell — ASCII only on stdout
13. `return_pct` treated as percentage — stored as decimal fraction (0.0672 = 6.72%); ×100 at display only
14. 4×`.parent` from `python\application\` to reach Hub root — requires 5×`.parent`
15. sys.path inserts for shared-contract imports — use editable install

---

## Schema Quick Reference

`return_pct` is decimal fraction. Forward label horizons: 5, 7, 10, 15, 20 days.
`data_origin_type`: `PATTERN_IDENT` (permanent) or `EVAL_SET` (reserved — never insert).

---

## Work Orders — check before emitter or schema work

| WO | Status | Scope |
|----|--------|-------|
| WO-P115-E1.001 | CLOSED 2026-06-11 | P_115 signal emitter — signal contract locked; P_300 ack done |
| WO-P800-E2.001 | CLOSED 2026-06-11 | Signal packet schema v2.0 — all acks done; SignalV2 is the contract |
| WO-P000-E2.003 | PENDING | sys.path removal — signal_emitter.py DONE; daily_evaluate_pipeline.py blocked on ENH-P000 |

---

## INIT Execution (WO-P000-E4.001, 2026-06-18)

INIT no longer calls `python` via `windows-mcp:PowerShell` for catalog/LM-Studio checks — that call shape reliably hit the ~4-min subprocess ceiling. Operator runs `P_300_Preflight.bat` (project root) before or during a session; it writes `P_300_preflight_status.json` (project root), which INIT reads via `windows-mcp:FileSystem` instead. Session header format: `P_300 [Day, Month DD, YYYY] [HH:MM] ET` (no `--` separator as of SIP v3.3). Current SIP: `docs\P_300_System_Initialization_Prompt_v3_1.md` v3.3.

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
