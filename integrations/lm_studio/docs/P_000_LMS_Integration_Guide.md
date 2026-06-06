# P_000_LMS_Integration_Guide
## LM Studio Wrapper -- Integration Guide for All Hub Projects

**Version:** 1.0
**Date:** 2026-05-29
**Owner:** P_000 (Python, Claude & Local LLM Learning Hub)
**Applies To:** All Hub projects (P_010, P_115, P_300, P_400, D_130, and future)

---

## Purpose

This guide defines how any Hub project integrates with the LM Studio wrapper. The wrapper is owned and maintained by P_000. Projects consume it -- they do not modify it.

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
| **Batch** | `qwen2.5-coder-32b-instruct` | Heavy analysis, documents, pipelines |
| **Long Context** | `llama-4-scout-17b-16e-instruct` | Documents over 128K tokens |

Task routing is declared in `integrations\lm_studio\config.py`. Projects do not touch this file unless adding a new task type (see below).

---

## Standard Init Pattern (All Projects)

Every project that uses local LLM adds this block at startup -- before any trading logic runs.

```python
import asyncio
import sys
from pathlib import Path

# Add Hub root to path
hub_root = Path(__file__).parent.parent.parent  # adjust depth as needed
sys.path.insert(0, str(hub_root))

from integrations.lm_studio.infrastructure.lm_studio_api import get_wrapper_status

async def init_lm_studio(task_type: str) -> bool:
    """
    Initialize LM Studio for this project.
    Declare the task type -- wrapper handles the rest.
    Returns True if ready, False if unrecoverable error.
    """
    status = await get_wrapper_status(task_type=task_type)

    if not status['lm_studio_running']:
        print(f"ERROR: {status['action_required']}")
        return False

    if status['model_mismatch']:
        print(f"ERROR: {status['action_required']}")
        return False

    print(f"OK {status['message']}")
    return True


# In your project's main startup:
if not asyncio.run(init_lm_studio(task_type="market_analysis")):
    sys.exit(1)

# Continue with project workflow
```

**One rule:** call `init_lm_studio()` once at startup. Never call it inside trading loops.

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
| `model_mismatch` | bool | True if current != expected |
| `action_required` | str or None | What to do if something is wrong |
| `message` | str | Human-readable status summary |

---

## Startup Flow

```
Project startup
    |
init_lm_studio(task_type="your_task")
    |
get_wrapper_status(task_type)
    |
    +-- LM Studio not running?
    |   -> Auto-launch LM Studio
    |   -> Wait for readiness
    |   -> Continue
    |
    +-- Wrong model loaded?
    |   -> Load correct model for task_type
    |   -> Continue
    |
    +-- Ready?
        -> Return True
        -> Project workflow begins
```

---

## File Locations

| File | Path | Purpose |
|---|---|---|
| Shared interface | `integrations\lm_studio\infrastructure\lm_studio_api.py` | Import `get_wrapper_status()` from here |
| Config / routing | `integrations\lm_studio\config.py` | Model definitions, task routing table |
| Launcher | `integrations\lm_studio\infrastructure\lm_studio_launcher.py` | Auto-start LM Studio |
| Health check | `projects\P_000_PythonClaudeLocalLLM\test_health_check.py` | Verify wrapper end-to-end |

All paths relative to Hub root: `C:\Users\Trader\AI-Agent-Learning-Hub\`

---

## Project Integration Checklist

For any new project adding LM Studio support:

- [ ] Add Hub root to `sys.path` at top of startup script
- [ ] Import `get_wrapper_status` from shared interface
- [ ] Call `init_lm_studio(task_type=...)` once at startup
- [ ] Choose task type from the 13 standard types (or add one to config.py)
- [ ] Confirm `init_lm_studio()` returns True before any LLM work begins
- [ ] Never call wrapper inside trading loops -- startup only

---

## Projects Currently Integrated

| Project | Task Type | Status |
|---|---|---|
| P_000 | `quick_coding` | OK Health check passing |
| P_300 | `vantagepoint_analysis` | OK Integration test passing |
| P_010 | -- | Pending |
| D_130 | -- | Pending |

---

*P_000_LMS_Integration_Guide v1.0 -- Owner: P_000*
*Update the Projects Currently Integrated table when a new project completes integration.*
