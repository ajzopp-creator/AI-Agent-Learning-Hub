---
name: python-project-architecture
description: >
  Enforces Tony's Python coding standards and project architecture rules for the
  AI-Agent-Learning-Hub. Use this skill BEFORE writing any Python code — even a
  single function. Triggers whenever the user asks to create, extend, refactor, or
  review any Python code, script, or project. Never skip this skill when Python is involved.
---

# Python Project Architecture — AI-Agent-Learning-Hub Standard

---

## ⛔ APPROVAL GATE — NON-NEGOTIABLE

Before writing ANY file or code, Claude MUST:
1. Present the complete file plan (all files, estimated line counts, save paths)
2. State what will be changed and why
3. STOP and wait for explicit approval ("go ahead", "yes", "proceed")

Diagnosis is not permission. Understanding the problem is not permission.
Only Tony's explicit confirmation is permission.

---

## Step 0 — Pre-Code Checklist

| # | Check | Rule |
|---|-------|------|
| 1 | Approval | Tony has explicitly approved — if not, STOP |
| 2 | Environment | `p140` conda env → `C:\Users\Trader\.conda\envs\p140\python.exe` |
| 3 | File plan | List ALL files + line counts BEFORE writing any code |
| 4 | File size | Hard limit 300 lines. Begin splitting at 250 |
| 5 | Function size | Hard limit 50 lines |
| 6 | Layer separation | No mixed layers — see Layer Rules |
| 7 | Process boundary | One reason to change per module. `application/` = orchestration only |
| 8 | One file per block | Never combine multiple files into one code block |
| 9 | No monoliths | Never put everything in `main.py` |

---

## Project Folder Structure

```
projects/P_XXX_ProjectName/python/
├── config.py              ← All constants, paths, thresholds
├── schemas.py             ← Pydantic models for all non-temporary file I/O
├── domain/                ← Business logic ONLY (no I/O)
├── infrastructure/        ← All I/O ONLY (files, APIs, DB, network)
├── application/           ← Orchestration ONLY (calls domain + infra)
├── cli.py                 ← Entry point
├── launcher.bat           ← Windows batch launcher
└── requirements.txt
```

Shared utilities across projects → `shared_resources/python_utils/`

---

## Layer Rules

### `domain/` — Logic only
Pure functions and classes. No file reads, no API calls, no DB, no print. Fully testable without external dependencies.

### `infrastructure/` — I/O only
All file reads/writes, API calls, DB queries, network requests. No business logic — fetch, send, load, save only. Returns raw data to application layer.

### `application/` — Orchestration only
Calls domain and infrastructure in sequence. No raw logic, no direct I/O, no external-service checks, no output suppression. If application code reaches into system internals, that code belongs in `infrastructure/`.

### `config.py` — Configuration only
All constants, paths, env vars, thresholds. Never hardcode values in other layers.

---

## Process Boundary Standard

A **process** is a group of modules within a layer that share one reason to change. Rules:

| Rule | Statement |
|------|-----------|
| One reason to change | Two reasons = two modules |
| Function soft limit | ~5 public functions per module — more is an awareness trigger |
| Application purity | `application/` orchestrates only. Status checks, I/O suppression, and service connections belong in `infrastructure/` |
| Swap test | Can you replace this module without touching any other layer? If no — it owns too much |
| Violation direction | Infrastructure change must never require an application change. If it does, the boundary is wrong |

**Example (P_300):** LM Studio status check lived in `daily_evaluate_pipeline.py` (application). When LMS started emitting console noise, the fix landed in application — wrong layer. Correct location: `infrastructure/lm_studio_status.py`. Application calls `lms_status.check()` and knows nothing else.

---

## File Delivery Rules

| Rule | Detail |
|------|--------|
| One file per block | Never combine files |
| Completion marker | `✅ FILE COMPLETE: filename.py (N lines)` after every file |
| Incomplete file | Stop, output `⏸ PAUSING — filename.py next. Type "continue".` Never deliver partial files |
| Delivery order | config → schemas → domain → infrastructure → application → cli → .bat → requirements |
| Save path | Every file includes `📁 Save to: <full Windows path>` |

---

## Python Style Standards

- PEP 8 · type hints on all signatures · Google-style docstrings
- Imports: stdlib → third-party → local (blank line between groups)
- `ALL_CAPS` constants in `config.py`
- `try/except` in infrastructure · `raise` in domain
- `logging` module — never bare `print()` in production
- f-strings for formatting

---

## Schema Rules

Any file read from or written to disk on a non-temporary basis **must** have a Pydantic schema before the read/write code is written. Schema location: `python/schemas.py`. Add `schemas.py` to the file plan whenever persistent file I/O is involved.

---

## Cross-Project File Access

Never assume or guess a path owned by another project.
1. Search the owning project's docs first
2. If not found, ask Tony — state what you need and wait
3. Never hardcode a drive letter — use `Path(os.environ["OneDrive"])` or `HUB_ROOT`
4. Document the confirmed path in `config.py`

| Project | Primary file |
|---------|-------------|
| P_010 | `P_010_RiskConfig.json` — read via Hub path |
| P_115 | `P_115_118_TrackerDashboard_V2.xlsx` — lives in OneDrive |
| P_020 | SQLite DB — confirm path from P_020 docs |

---

## Common Mistakes

| Mistake | Correct approach |
|---------|-----------------|
| Writing files without approval | Present plan → wait for "go ahead" |
| Logic in `main.py` | Split across domain / infra / application |
| Hardcoded paths | All paths in `config.py` |
| Guessing cross-project paths | Search owning project's docs — ask if not found |
| Mixing I/O with logic | Separate into domain vs infrastructure |
| Functions over 50 lines | Break into smaller functions |
| Files without save paths | Always include `📁 Save to:` |
| Infrastructure concerns in `application/` | Move to `infrastructure/` — keep application as pure orchestration |
| Module with two reasons to change | Split into two modules — one reason each |

---

## Quick Reference

```
APPROVAL GATE:        Present plan → wait for "go ahead" → write files
BEFORE CODING:        List all files + line counts
ENVIRONMENT:          p140 conda env always
LAYER ORDER:          config → schemas → domain → infra → application → cli → .bat
FILE LIMIT:           300 lines hard / 250 lines split trigger
FUNCTION LIMIT:       50 lines hard
PROCESS BOUNDARY:     One reason to change · ≤5 fns soft · application = orchestration only
SCHEMAS:              Required for ALL non-temporary file reads and writes
CROSS-PROJECT FILES:  Search owning project's docs first — never guess
ONE FILE PER BLOCK:   Always
COMPLETION MARKER:    ✅ FILE COMPLETE: name.py (N lines)
PAUSE IF NEEDED:      ⏸ PAUSING — type "continue" to proceed
```

---

## Environment Reference

| Item | Value |
|------|-------|
| Conda env | `p140` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| LLM preference | Local LM Studio → Claude API (fallback) |

---

## Last Updated
2026-05-30 — Process Boundary Standard added (Layer → Process → Module → Functions hierarchy). Mirrors P_300 refactor plan. Full SKILL rewritten and compressed (~40% token reduction). Infrastructure-in-application anti-pattern added to Common Mistakes. Process boundary check added to Step 0.
