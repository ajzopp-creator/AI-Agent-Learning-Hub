---
name: python-project-architecture
description: >
  Enforces Tony's Python coding standards and project architecture rules for the
  AI-Agent-Learning-Hub. Use this skill BEFORE writing any Python code — even a
  single function. Triggers whenever the user asks to create, extend, refactor, or
  review any Python code, script, or project. Also triggers when the user says things
  like "write me a Python script", "add a function", "build a module", "start a new
  project", or "help me code this in Python". Never skip this skill when Python is involved.
---

# Python Project Architecture
## AI-Agent-Learning-Hub Standard

---

## Purpose

Enforce consistent Python architecture rules across all Hub projects so that:
- Code stays modular, readable, and maintainable
- Files never grow into unmanageable monoliths
- The correct Python environment is always used
- Every file Claude delivers is complete and immediately usable

---

## Step 0: Pre-Code Checklist (ALWAYS run before writing any Python)

Before writing a single line of Python, confirm ALL of the following:

| # | Check | Rule |
|---|-------|------|
| 1 | **Environment** | Always use the `p140` conda env -> `C:\Users\Trader\.conda\envs\p140\python.exe` |
| 2 | **LLM preference** | Local LM Studio first -- Claude API only when local is insufficient |
| 3 | **File plan** | List ALL files with estimated line counts BEFORE writing any code |
| 4 | **File size** | Hard limit: 300 lines per file. Begin splitting at 250 lines |
| 5 | **Function size** | Hard limit: 50 lines per function |
| 6 | **Layer separation** | See Layer Rules below -- never mix layers |
| 7 | **One file per block** | Never combine multiple Python files into one code block |
| 8 | **No monoliths** | Never put everything into a single `main.py` |

**Output the file plan to Tony BEFORE writing any code.** Wait for approval if the plan
involves more than 3 files or significant structural decisions.

---

## Project Folder Structure

Every Hub Python project follows this layout:

```
projects/
L P_XXX_ProjectName/
    L python/
        - config.py              <- All constants, paths, thresholds
        - schemas.py             <- Pydantic models for all non-temporary file I/O
        - domain/                <- Business logic ONLY (no I/O)
        -   L *.py
        - infrastructure/        <- All I/O ONLY (files, APIs, DB, network)
        -   L *.py
        - application/           <- Orchestration ONLY (calls domain + infra)
        -   L *.py
        - cli.py                 <- Entry point / command-line interface
        - launcher.bat           <- Windows batch launcher
        L requirements.txt       <- Project dependencies
```

**Shared utilities** that work across multiple projects go here:
```
shared_resources/
L python_utils/
    L *.py
```

---

## Layer Rules

### `domain/` -- Logic Only
- Pure Python functions and classes
- NO file reads, NO API calls, NO database access, NO print statements
- Takes data as input, returns data as output
- Fully testable without any external dependencies

### `infrastructure/` -- I/O Only
- ALL file reads/writes, API calls, database queries, network requests
- NO business logic -- just fetch, send, load, save
- Returns raw data to the application layer

### `application/` -- Orchestration Only
- Calls domain functions and infrastructure functions in sequence
- Contains the "workflow" -- what happens in what order
- NO raw business logic, NO direct I/O

### `config.py` -- Configuration Only
- All constants, file paths, environment variables, thresholds
- Imported by any layer that needs a value
- Never hardcode values inside domain/, infrastructure/, or application/

#### Path Rules -- OneDrive vs Non-OneDrive

| Path Type | Method | Example |
|---|---|---|
| **OneDrive paths** | `os.environ["OneDrive"]` | `Path(os.environ["OneDrive"]) / "Documents" / "AJZStrategiesLLC"` |
| **Non-OneDrive paths** (AI-Hub, C: tools) | Constant in `config.py` | `HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")` |

**Why %OneDrive%?** The OneDrive folder location can change (drive letter reassignment,
migration to a different drive). Using the environment variable means all scripts survive
any future move without code changes -- just update the env variable once.

**Standard pattern for every config.py that touches OneDrive paths:**
```python
import os
from pathlib import Path

# PATH CONFIGURATION
# OneDrive root -- reads from Windows environment variable.
# Survives OneDrive folder moves without code changes.
ONEDRIVE = Path(os.environ["OneDrive"])

# Project-specific paths built from ONEDRIVE root
AJZ_ROOT       = ONEDRIVE / "Documents" / "AJZStrategiesLLC"
OPERATIONS_DIR = AJZ_ROOT / "2026_Operations"

# Non-OneDrive paths -- hardcode only Hub root (it never moves)
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
```

**For .bat / PowerShell scripts:**
```powershell
# PowerShell
$OneDrive = $env:OneDrive
$AJZ_ROOT = "$OneDrive\Documents\AJZStrategiesLLC"
```
```batch
REM Batch
SET AJZ_ROOT=%OneDrive%\Documents\AJZStrategiesLLC
```

---

## File Delivery Rules

### Rule 1 -- One file per code block
Never combine two Python files into a single code block.
Each file gets its own clearly labeled block.

### Rule 2 -- Completion marker
After every file, output:
```
FILE COMPLETE: filename.py (N lines)
```

### Rule 3 -- Incomplete file handling
If a file cannot fit in the current response:
- Stop before starting it
- Output: PAUSING -- filename.py will be in the next response. Type "continue" to proceed.
- Never deliver a partial file

### Rule 4 -- Delivery order (multi-file sessions)
Always deliver files in this order:
1. config.py
2. schemas.py (if any persistent file I/O is involved)
3. domain/ files
4. infrastructure/ files
5. application/ files
6. cli.py
7. launcher.bat
8. requirements.txt

### Rule 5 -- Save path
Every file delivery must include the recommended Windows save path:
```
DOWNLOAD READY: filename.py
Save to: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_XXX_ProjectName\python\[subfolder]\
```

---

## Python Style Standards

- PEP 8 formatting and naming conventions
- Type hints on all function signatures and return values
- Docstrings on every function and class (Google style)
- Imports ordered: standard library -> third-party -> local (blank line between groups)
- ALL_CAPS constants defined in config.py
- try/except in the infrastructure layer; raise in the domain layer
- logging module for all output -- never bare print() in production code
- f-strings for string formatting

---

## Schema Rules (Non-Temporary Files)

Any file that is read from or written to disk on a non-temporary basis MUST have
a Pydantic schema defined before the read/write code is written.

### What counts as non-temporary
- CSV, JSON, XLSX, or any data file that persists between runs
- Config files loaded at startup
- Log files written during a session
- Any file stored in the Hub folder structure

### Schema location
```
python/
L schemas.py      <- All Pydantic models for this project
```

Shared schemas: shared_resources/python_utils/schemas.py

### Enforcement rule
- Reading a file? -> Schema must exist first.
- Writing a file? -> Schema must exist first.
- Add schemas.py to the file plan whenever any persistent file I/O is involved.
- Deliver schemas.py immediately after config.py in multi-file sessions.

---

## Environment Reference

| Item | Value |
|------|-------|
| Conda environment | p140 |
| Python executable | C:\Users\Trader\.conda\envs\p140\python.exe |
| VS Code interpreter | Set to the path above |
| LLM preference | Local LM Studio (when available) -> Claude API (fallback) |
| Hub root | C:\Users\Trader\AI-Agent-Learning-Hub\ |

---

## Common Mistakes to Avoid

| Mistake | Correct Approach |
|---------|-----------------|
| Writing all logic in main.py | Split across domain / infra / application layers |
| Hardcoding file paths | Put all paths in config.py |
| Hardcoding OneDrive path (e.g. C:\Users\Trader\Documents) | Use Path(os.environ["OneDrive"]) -- survives drive migrations |
| Mixing I/O with logic in same function | Separate into domain vs infrastructure |
| Writing 200-line functions | Break into smaller functions, each under 50 lines |
| Delivering files without save paths | Always include Save to: with every file |
| Starting to code without a file plan | Always output the file plan first |

---

## Quick Reference Card

```
BEFORE CODING:        List all files + line counts -> get approval
ENVIRONMENT:          p140 conda env always
LAYER ORDER:          config -> schemas -> domain -> infra -> application -> cli -> .bat
FILE LIMIT:           300 lines hard / 250 lines split trigger
FUNCTION LIMIT:       50 lines hard
SCHEMAS:              Required for ALL non-temporary file reads and writes
ONE FILE PER BLOCK:   Always
ONEDRIVE PATHS:       ALWAYS use Path(os.environ["OneDrive"]) -- never hardcode drive letters
NON-ONEDRIVE PATHS:   HUB_ROOT only hardcoded path allowed (C:\Users\Trader\AI-Agent-Learning-Hub)
```

---

## Last Updated
March 16, 2026 -- Added OneDrive path rules (use %OneDrive% env variable, never hardcode drive paths)
