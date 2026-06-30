# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Python Environment

All code runs under the shared conda environment — never create a venv.

```
C:\Users\Trader\.conda\envs\p140\python.exe
```

Run any script directly by full path; no activation needed:
```powershell
"C:\Users\Trader\.conda\envs\p140\python.exe" "python\your_script.py"
```

Install packages into p140:
```powershell
"C:\Users\Trader\.conda\envs\p140\python.exe" -m pip install <package>
```

Run a single test file:
```powershell
"C:\Users\Trader\.conda\envs\p140\python.exe" -m pytest projects\P_800_Automation_Note_Taking\python\tests\test_signal_v2_e2e.py -v
```

## Hub Architecture

The hub is a mono-repo containing multiple numbered trading projects. Two things are hub-wide (used by all projects):

**`hub_lib/`** — model-routing facade. Projects call `ModelManager.generate(task, prompt)` without knowing the underlying provider. Task→provider routing is defined in `hub_lib/model_manager.py` (`MODEL_MAP`). Providers: `lmstudio` (local, default), `anthropic`, `google`. Override a route at runtime via env var: `HUBLIB_TASK_<TASKNAME_UPPER>=provider:model_id`.

**`shared_resources/`** — shared signal contract and utilities (XML parser for TOS History Grid exports, etc.). Both `hub_lib` and `shared_resources` are installed as the editable package `hub_shared` (`pyproject.toml`).

## Project Structure

Each project lives under `projects/P_XXX_ProjectName/python/` and follows strict layer separation:

```
python/
├── config.py          # all constants, paths, thresholds
├── schemas.py         # Pydantic models for every file read/write
├── domain/            # pure logic, no I/O, no print
├── infrastructure/    # all file/API/DB I/O, no business logic
├── application/       # orchestration — calls domain + infra in sequence
├── cli.py             # entry point
└── launcher.bat       # calls p140 python directly by full path
```

Never mix layers. Domain code must never import from infrastructure or application. Infrastructure must never contain business logic.

## File and Path Rules

- OneDrive: `Path(os.environ["OneDrive"])` — never hardcode drive letter
- Hub root: `HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")` is the one allowed hardcoded path
- Any non-temporary file read or write needs a Pydantic schema in `schemas.py` first
- Max 300 lines per file, 50 lines per function. Start splitting at 250 lines.

## Git Workflow

Commit message format: `WO-[ID] - [brief] - YYYY-MM-DD`

Push immediately after every commit (`git push`). Main branch only — no feature branches.

Do NOT commit: `logs/`, `*.log`, `__pycache__/`, `.env`, `data/xml_exports/`, `data/historical/`, `venv/`, `.vscode/` local settings.

## Work Orders

Active project work is tracked in `Agentic-Hub-Governance/work_orders/`. Each file is named `WO-P[XXX]-E[N].[NNN].md` and carries a `Status:` field (`PENDING`, `BLOCKED`, `IN_PROGRESS`, `OWNER_DONE`, `CLOSED`). `OWNER_DONE` means the owner finished but a downstream project's Ack is still pending; `CLOSED` means all Acks are in. Check the relevant WO before starting project work.

## LM Studio

LM Studio must be running locally at `http://localhost:1234/v1` for `local_fast` and `local_smart` tasks. Run a health check at session start:

```python
from hub_lib import verify_health
verify_health(["local_fast"])   # only check what you plan to use
```

Do NOT call `check_provider()` per-request — rate limits on Gemini's free tier exhaust quickly.
