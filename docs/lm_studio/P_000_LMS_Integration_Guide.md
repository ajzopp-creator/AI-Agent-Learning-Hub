# P_000_LMS_Integration_Guide
## LM Studio Wrapper — Integration Guide for All Hub Projects

**Version:** 1.0
**Date:** 2026-05-29
**Owner:** P_000 (Python, Claude & Local LLM Learning Hub)
**Applies To:** All Hub projects (P_010, P_115, P_300, P_400, P_110, and future)

---

## Purpose

This guide defines how any Hub project integrates with the LM Studio wrapper. The wrapper is owned and maintained by P_000. Projects consume it — they do not modify it.

---

## Design Principle

**The project knows which model it needs. The wrapper handles everything else.**

At startup, a project declares its task type. The wrapper:
1. Auto-launches LM Studio if it is not running
2. Routes the task type to the correct model tier
3. Loads that model
4. Confirms readiness before the project does any work

Projects never manage LM Studio lifecycle. That is the wrapper's responsibility.

---

## Three-Tier Model Stack

| Tier | Model | Use Case |
|---|---|---|
| **Primary** | `deepseek-r1-distill-qwen-14b` | Real-time analysis, coding, trade setup evaluation |
| **Batch** | `qwen2.5-coder-32b-instruct-abliterated` | Heavy analysis, documents, pipelines |
| **Long Context** | `llama-4-scout-17b-16e-instruct` | Documents over 128K tokens |

Task routing is declared in `integrations\lm_studio\config.py`. Projects do not touch this file unless adding a new task type (see below).

---

## Standard Init Pattern (All Projects)

Every project that uses local LLM adds this block at startup — before any trading logic runs.

### Option A — Simple status check (recommended for most projects)

```python
from pathlib import Path
import sys

# Add Hub root to path (adjust depth to match your project's location)
hub_root = Path(__file__).resolve().parent.parent.parent.parent
if str(hub_root) not in sys.path:
    sys.path.insert(0, str(hub_root))

from integrations.lm_studio.infrastructure.lm_studio_status import check

if not check(diag_log=Path("logs/lms_diag.log"), task_type="vantagepoint_analysis"):
    sys.exit(1)

# Continue with project workflow
```

`check()` is synchronous — no asyncio required. It returns `True` if LM Studio is running with the correct model loaded. Diagnostic output goes to the caller-supplied log path, keeping the console clean.

### Option B — Full launcher (auto-start + model switching)

Use when you want the launcher to auto-start LM Studio and prompt for model switching:

```python
import asyncio
from integrations.lm_studio.infrastructure.lm_studio_launcher import ensure_lm_studio_ready

if not asyncio.run(ensure_lm_studio_ready(task_type="market_analysis")):
    sys.exit(1)
```

**One rule:** call either option once at startup. Never call inside trading loops.

---

## Task Types (13 Standard)

Declare one of these as your `task_type`. The wrapper routes to the correct model automatically.

**Primary tier (real-time):**
- `market_analysis`
- `trade_setup_evaluation`
- `quick_coding`
- `python_debugging`
- `sql_schema_design`
- `vantagepoint_analysis`

**Batch tier (heavy analysis):**
- `trade_journal_analysis`
- `document_summarization`
- `code_generation_heavy`
- `pattern_analysis`

**Long context tier (large documents):**
- `full_document_ingestion`
- `architecture_review`
- `large_codebase_analysis`

To add a new task type: edit `TASK_ROUTING` in `integrations\lm_studio\config.py`, assign to a tier, update this document.

---

## Status Response Reference

`get_wrapper_status()` returns:

| Key | Type | Meaning |
|---|---|---|
| `lm_studio_running` | bool | Is LM Studio responding? |
| `current_model` | str or None | Model loaded right now |
| `expected_model` | str | Model required for declared task type |
| `model_mismatch` | bool | True if current ≠ expected |
| `action_required` | str or None | What to do if something is wrong |
| `message` | str | Human-readable status summary |

---

## Startup Flow

```
Project startup
    ↓
init_lm_studio(task_type="your_task")
    ↓
get_wrapper_status(task_type)
    ↓
    ├─ LM Studio not running?
    │  → Auto-launch LM Studio
    │  → Wait for readiness
    │  → Continue
    │
    ├─ Wrong model loaded?
    │  → Load correct model for task_type
    │  → Continue
    │
    └─ Ready?
       → Return True
       → Project workflow begins
```

---

## File Locations

| File | Path | Purpose |
|---|---|---|
| Status check | `integrations\lm_studio\infrastructure\lm_studio_status.py` | `check()` — simple synchronous gate, recommended for most projects |
| Shared interface | `integrations\lm_studio\infrastructure\lm_studio_api.py` | `get_wrapper_status()` — low-level async status query |
| Launcher | `integrations\lm_studio\infrastructure\lm_studio_launcher.py` | `ensure_lm_studio_ready()` — auto-start + model switching |
| Config / routing | `integrations\lm_studio\config.py` | Model definitions, task routing table |
| Health check | `projects\P_000_PythonClaudeLocalLLM\python\tests\test_health_check.py` | Verify wrapper end-to-end |

All paths relative to Hub root: `C:\Users\Trader\AI-Agent-Learning-Hub\`

---

## Project Integration Checklist

For any new project adding LM Studio support:

- [ ] Add Hub root to `sys.path` at top of startup script
- [ ] Import `check` from `lm_studio_status` (Option A) or `ensure_lm_studio_ready` from launcher (Option B)
- [ ] Call once at startup with your project's `task_type` and `diag_log` path
- [ ] Choose task type from the 13 standard types (or add one to config.py)
- [ ] Confirm call returns True before any LLM work begins
- [ ] Never call inside trading loops — startup only

---

## Projects Currently Integrated

| Project | Task Type | Status |
|---|---|---|
| P_000 | `quick_coding` | ✅ Health check passing |
| P_300 | `vantagepoint_analysis` | ✅ Fully integrated — `check()` in daily_evaluate_pipeline.py v1.12 |
| P_010 | — | ⏳ Pending |
| P_110 | — | ⏳ Pending |

---

*P_000_LMS_Integration_Guide v1.0 — Owner: P_000*
*Update the Projects Currently Integrated table when a new project completes integration.*