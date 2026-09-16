---
name: python-project-architecture
description: >
  Enforces Tony's Python coding standards and project architecture rules for the
  AI-Agent-Learning-Hub. Use this skill BEFORE writing any Python code — even a
  single function. Triggers whenever the user asks to create, extend, refactor, or
  review any Python code, script, or project. Never skip this skill when Python is involved.
---

# Python Project Architecture — AI-Agent-Learning-Hub Standard

## ⛔ APPROVAL GATE — NON-NEGOTIABLE
Before writing ANY file or code: present the complete file plan (files, line counts, save paths) + what/why, then STOP for explicit approval ("go ahead"/"yes"/"proceed"). Diagnosis is not permission.

## Step 0 — Pre-Code Checklist
| # | Check | Rule |
|---|---|---|
| 1 | Approval | Explicit "go ahead" received — if not, STOP |
| 2 | Environment | `p140` conda env → `C:\Users\Trader\.conda\envs\p140\python.exe` |
| 3 | File plan | All files + line counts BEFORE any code |
| 4 | File size | Hard 300 lines; split at 250 |
| 5 | Function size | Hard 50 lines |
| 6 | Layer separation | No mixed layers (see Layer Rules) |
| 7 | Process boundary | One reason to change per module; `application/` = orchestration only |
| 8 | One file/block | Never combine files in one code block |
| 9 | No monoliths | Never put everything in `main.py` |
| 10 | Regression gate | File has `tests/test_<module>.py`? Run it first via PEH before the new change — a failure means a past fix just broke |

## Folder Structure
```
projects/P_XXX_ProjectName/python/
├── config.py           ← constants, paths, thresholds
├── schemas.py          ← Pydantic models, all non-temp file I/O
├── domain/             ← logic only, no I/O
├── infrastructure/     ← I/O only, no logic
├── application/        ← orchestration only
├── tests/              ← test_<module>.py per file with a real bug fix — permanent, accreting
├── cli.py              ← entry point
├── launcher.bat
└── requirements.txt
```
Shared utilities → `shared_resources/python_utils/`

## Layer Rules
| Layer | Owns | Forbidden |
|---|---|---|
| `domain/` | Pure logic, fully testable | File/API/DB/print |
| `infrastructure/` | Reads/writes/API/DB/network | Business logic |
| `application/` | Calls domain + infra in sequence | Raw logic, direct I/O, service checks, output suppression |
| `config.py` | Constants, paths, env vars, thresholds | Hardcoded values elsewhere |

## Process Boundary Standard
| Rule | Statement |
|---|---|
| One reason to change | Two reasons = two modules |
| Function soft limit | ~5 public functions/module |
| Application purity | Status checks / I-O suppression / service connections → `infrastructure/`, never `application/` |
| Swap test | Can this module be replaced without touching another layer? No → it owns too much |
| Violation direction | Infra change must never force an application change |

Example (P_300): LM Studio status check lived in `daily_evaluate_pipeline.py` (application) — wrong layer when it started emitting console noise. Fix: `infrastructure/lm_studio_status.py`; application just calls `lms_status.check()`.

## Regression Test Governance — NON-NEGOTIABLE
Work-order governance tracks project scope, not function-level invariants — a fix recorded only in lessons.md must be *remembered* on every future touch. (Origin: WO-P300-E3.002 — M-082's capped-window fix was silently lost 3 versions later in an unrelated rewrite; nothing forced a check against it.)

**Rule:** every `domain/` / `infrastructure/` / `application/` file with a real (post-build) bug fix gets a permanent `tests/test_<module>.py` — never deleted, only grows, one assertion per fix.

| Rule | Statement |
|---|---|
| One assertion/fix | Verified fix → one test encoding the invariant, not just a lessons.md paragraph |
| Permanent | Test file never shrinks; lessons.md keeps the why, the test file keeps the guarantee |
| Gate before rewrite | Run the file's test suite first (its own PEH step) before modifying — pre-existing failure = stop |
| Disposable vs. permanent | Ad-hoc PEH scripts stay one-and-done; `tests/test_<module>.py` is reused every future touch |
| Hub-wide | Same convention, every project (P_010/020/115/300/400/800/etc.) |
| Rewrites especially | A full rewrite is exactly when a prior invariant silently drops — gate matters more, not less |

Shape: `tests/test_pattern_miner.py` for a 3-fix `domain/pattern_miner.py` = 3 tests minimum, named after the guarantee (e.g. `test_dedup_window_capped_at_max_forward_horizon`), smallest input that proves it — not a full end-to-end (that's PEH's job).

## File Delivery Rules
| Rule | Detail |
|---|---|
| One file/block | Never combine |
| Completion marker | `✅ FILE COMPLETE: filename.py (N lines)` |
| Incomplete file | `⏸ PAUSING — filename.py next. Type "continue".` Never partial |
| Delivery order | config → schemas → domain → infrastructure → application → cli → .bat → requirements |
| Save path | Every file: `📁 Save to: <full Windows path>` |

## Python Style
PEP 8 · type hints all signatures · Google-style docstrings · imports stdlib→third-party→local (blank line between) · `ALL_CAPS` constants in `config.py` · `try/except` in infrastructure, `raise` in domain · `logging`, never bare `print()` · f-strings

## Schema Rules
Any file read/written on a non-temporary basis needs a Pydantic schema in `python/schemas.py` before the read/write code — add `schemas.py` to the file plan whenever persistent I/O is involved.

## Cross-Project File Access
Never guess a path owned by another project: (1) search the owning project's docs, (2) if not found, ask Tony and wait, (3) never hardcode a drive letter — use `Path(os.environ["OneDrive"])` or `HUB_ROOT`, (4) document the confirmed path in `config.py`.

| Project | Primary file |
|---|---|
| P_010 | `P_010_RiskConfig.json` — read via Hub path |
| P_115 | `P_115_118_TrackerDashboard_V2.xlsx` — OneDrive |
| P_020 | SQLite DB — confirm path from P_020 docs |

## Cross-Project Bridge Imports
Any module that reaches into another project's folder via `sys.path.insert` (e.g. `p020_order_writer.py` bridging into P_020's `database\` folder) must load the foreign module under a private alias with `importlib.util`, never a bare `import`:

```python
import importlib.util

spec = importlib.util.spec_from_file_location("p020_schemas", target_path)
foreign_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foreign_mod)
# foreign_mod.Exit, foreign_mod.Order, foreign_mod.Trade
```

**Never** `sys.path.insert` + bare `import name`. The bare name lands in `sys.modules` globally — if the calling project has ANY same-named top-level module (its own `schemas.py`, `config.py`, etc.), Python returns the cached one silently instead of re-resolving via the inserted path, and the failure surfaces as a missing-attribute error pointing at the wrong file. Root cause: the target folder (e.g. P_020's `database\`) isn't an installed/namespaced package — it's sys.path-inserted directly, so every module inside it lives at the bare top level of `sys.modules`, exposed to collision with any same-named module anywhere else in the Hub.

Confirmed live 3x, same root cause, different name each time: `infrastructure`/`domain` (WO-P400-E6.001, 2026-09-07), `config` (2026-09-09), `schemas` (2026-09-11) — each fixed reactively by adding the name to an allowlist tuple (`_COLLIDING_PACKAGES`) in the bridge module, which only protects names already caught in production. `importlib.util` with a private alias avoids the whole class permanently — write every **new** bridge module this way from the start. Existing allowlist-based bridges aren't required to be rewritten unless touched for another reason anyway.

**Related pitfalls, same root cause (flat sys.path, no real packages):**

| Pitfall | Guard |
|---|---|
| Import side effects | A bridged module that configures logging or a singleton client on import silently no-ops on its 2nd load in the same process (Python thinks it's already loaded) — don't rely on import-time side effects in any module reachable via a bridge |
| Stale `__pycache__` | Python invalidates by mtime+size, normally safe — but a copy tool that doesn't preserve mtime can leave a stale `.pyc` shadowing a real edit; clear `__pycache__` if an edited bridge file doesn't seem to take effect |
| Direct-run vs. import path | Running `python cli.py` vs. importing `cli` as a module gives a different `sys.path[0]` — never `import` another project's `cli.py`; always invoke it as `python cli.py` from its own directory (already standard practice Hub-wide — this is why) |

## Common Mistakes
| Mistake | Correct approach |
|---|---|
| Writing without approval | Present plan → wait for "go ahead" |
| Logic in `main.py` | Split domain / infra / application |
| Hardcoded paths | All paths in `config.py` |
| Guessing cross-project paths | Search owning project's docs — ask if not found |
| Mixing I/O with logic | Separate domain vs infrastructure |
| Functions over 50 lines | Break into smaller functions |
| Files without save paths | Always include `📁 Save to:` |
| Infra concerns in `application/` | Move to `infrastructure/` |
| Module with two reasons to change | Split into two, one reason each |
| Rewriting without checking test file | Run `tests/test_<module>.py` first — a rewrite can silently drop a prior fix (M-082, WO-P300-E3.002) |
| Bridging into another project via `sys.path.insert` + bare `import` | Use `importlib.util.spec_from_file_location` with a private alias (see Cross-Project Bridge Imports) |

## Quick Reference
```
APPROVAL GATE:        Present plan → wait for "go ahead" → write files
BEFORE CODING:        List all files + line counts
ENVIRONMENT:           p140 conda env always
LAYER ORDER:           config → schemas → domain → infra → application → cli → .bat
FILE LIMIT:            300 hard / 250 split trigger
FUNCTION LIMIT:        50 lines hard
PROCESS BOUNDARY:      One reason to change · ≤5 fns soft · application = orchestration only
SCHEMAS:               Required for ALL non-temp file reads/writes
REGRESSION TESTS:      tests/test_<module>.py per fixed file — run before rewriting, never delete
CROSS-PROJECT FILES:   Search owning project's docs first — never guess
CROSS-PROJECT IMPORTS: importlib.util private alias for bridge modules — never sys.path.insert + bare import
ONE FILE/BLOCK:        Always
COMPLETION MARKER:     ✅ FILE COMPLETE: name.py (N lines)
PAUSE IF NEEDED:       ⏸ PAUSING — type "continue" to proceed
```

## Environment Reference
| Item | Value |
|---|---|
| Conda env | `p140` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| LLM preference | Local LM Studio → Claude API (fallback) |

## Last Updated
2026-09-11 — Cross-Project Bridge Imports section added: `importlib.util.spec_from_file_location` with a private alias required for all new sys.path-bridge modules, replacing the reactive `_COLLIDING_PACKAGES` allowlist pattern. Common Mistakes +1 row, Quick Reference +1 line. Origin: `p020_order_writer.py` — same `sys.modules` bare-name collision hit `infrastructure`/`domain` (2026-09-07), `config` (2026-09-09), and `schemas` (2026-09-11), three live incidents, same root cause, each patched reactively. Related-pitfalls table added (import side effects, `__pycache__` staleness, direct-run vs. import `sys.path[0]`) — same root cause, not yet hit live, flagged proactively.
2026-07-12 — Compression pass: layer/mistake sections converted to tables, prose trimmed throughout; no rule, path, or condition removed. Regression Test Governance added same day (Hub-wide, non-negotiable) — Step 0 +item 10, folder +tests/, Common Mistakes +1 row, Quick Reference +1 line. Origin: WO-P300-E3.002, M-082 fixed then silently lost 3 versions later in a rewrite.
2026-05-30 — Process Boundary Standard added (Layer → Process → Module → Functions). Full rewrite/compression (~40% token reduction). Infra-in-application anti-pattern + Step 0 process-boundary check added.
