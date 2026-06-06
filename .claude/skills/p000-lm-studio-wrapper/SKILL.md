---
name: lm-studio-wrapper
description: >
  Protection rules, critical paths, and operational constraints for the LM Studio wrapper
  architecture. Establishes safety boundaries for model loading, task routing, LM Studio
  lifecycle management, and API consistency across all trading projects.
---

# LM Studio Wrapper — SKILL: Protection Rules & Critical Paths

**Version:** 1.1  
**Created:** May 28, 2026  
**Updated:** May 28, 2026 (Added API consistency rules)  
**Applies To:** All trading projects using LM Studio wrapper (P_010, P_020, P_115, P_300, D_130)  
**Pairs With:** `LM_Studio_Wrapper_System_Initialization_Prompt_v1.0.md`

---

## Core Operating Rules

### R-001: Three-Tier Model Stack Is Immutable

The model stack is defined in `config.py` and never changes during a session:

| Tier | Model | When to Use |
|---|---|---|
| **Primary (Daily Driver)** | `deepseek-r1-distill-qwen-14b` | Real-time analysis, trade setup evaluation, quick coding |
| **Batch (Heavy Analysis)** | `qwen2.5-coder-32b-instruct` | Document summarization, trade journal analysis, pipeline builds |
| **Long Context (Specialist)** | `llama-4-scout-17b-16e-instruct` | Documents over 128K tokens, architecture review, full-project ingestion |

**Enforcement:** Always route via `task_type` parameter. Never manually override model selection unless explicitly instructed by operator.

---

### R-002: Task Routing Is Declarative

Task-to-model mapping is defined in `config.py` under `TASK_ROUTING`. When a task type is not recognized:

1. Check `TASK_ROUTING` dict in config.py
2. If task type exists → route to assigned tier automatically
3. If task type missing → raise ValueError with available task types listed
4. Never invent a task type

**Valid task types (as of v1.0):**
```
market_analysis, trade_setup_evaluation, quick_coding, python_debugging, sql_schema_design,
vantagepoint_analysis, trade_journal_analysis, document_summarization, code_generation_heavy,
pattern_analysis, full_document_ingestion, architecture_review, large_codebase_analysis
```

Add new task types ONLY by editing `config.py` and documenting in `TASK_ROUTING`.

---

### R-003: LM Studio Auto-Startup Is the Default

If LM Studio is not responding when `client.startup()` is called:

1. Wrapper automatically attempts to launch `C:\Program Files\LM Studio\LM Studio.exe`
2. Wrapper waits up to 30 seconds for health check to pass
3. If launch succeeds → session proceeds normally
4. If launch fails → HALT with error message; operator must manually start LM Studio

**Never skip startup verification.** The wrapper health check is mandatory.

---

### R-004: Model Loading Is Exclusive

Only ONE model can be loaded in LM Studio at a time.

When switching models:

1. **Current model unloaded** via `/api/v1/models/unload`
2. **New model loaded** via `/api/v1/models/load`
3. **No parallel loading** — operations block until the load completes

**Do not attempt to load two models simultaneously.** The wrapper enforces serial loading.

---

### R-005: Chat Requests Must Include Model Parameter

**NEW (2026-05-28):** All chat requests MUST include the model ID in the payload. This is required by LM Studio API.

```python
payload = {
    "model": "deepseek-r1-distill-qwen-14b",  # REQUIRED
    "messages": [...],
    "temperature": 0.7,
}
```

Never send a chat request without specifying the model.

---

### R-006: API Endpoint Consistency — Native LM Studio API Only

**CRITICAL (2026-05-28):** The wrapper uses **native LM Studio `/api/v1/*` endpoints** exclusively.

| Endpoint | Purpose | Status |
|---|---|---|
| `/api/v1/models` | List available models | ✅ Working |
| `/api/v1/models/load` | Load a model | ✅ Working |
| `/api/v1/models/unload` | Unload current model | ✅ Working |
| `/api/v1/chat` | Send chat request | 🔧 IN DEVELOPMENT (request format TBD) |

**DO NOT switch to OpenAI-compatible endpoints** (`/v1/chat/completions`) without explicit operator approval. The architecture is built on native APIs.

**If an endpoint doesn't work:**
1. Document the issue in `tasks/lessons.md`
2. Investigate the request/response format
3. Ask operator for approval before changing architecture

---

### R-007: Chat Generation Temperature Is Task-Aware

Temperature is automatically selected based on task type:

| Task Category | Temperature | Reason |
|---|---|---|
| `*_analysis`, `*_evaluation`, `*_design` | 0.7 | Balanced reasoning |
| `*_coding`, `*_code_*`, `*schema*` | 0.3 | Deterministic code generation |
| `*creative`, `*generate` | 0.9 | Exploratory output |

**Override only if explicitly needed.** Pass `temperature=X` to `client.chat()` to override.

---

### R-008: No Market Data Analysis in INIT

The System Initialization Prompt (SIP) validates infrastructure only:
- ✅ Wrapper files present
- ✅ Configuration loaded
- ✅ LM Studio health check
- ✅ Model stack accessible
- ❌ Market posture (handled by P_010)
- ❌ Pattern data (handled by P_300)
- ❌ Account parameters (handled by P_000)

**Separation of concerns:** The wrapper is a utility layer. Market/trading logic is project-specific.

---

## Critical Paths

| Path | Purpose |
|---|---|
| `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\` | Wrapper root |
| `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\config.py` | All constants, models, routing |
| `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\infrastructure\` | API I/O layer (lm_studio_api.py, lm_studio_launcher.py) |
| `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\domain\` | Task routing logic (task_router.py) |
| `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\application\` | Main client interface (lm_studio_client.py) |
| `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\tasks\lessons.md` | Methodology rules, operational lessons, errors |
| `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\tasks\todo.md` | Current state, active stage, upcoming work |
| `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\outputs\logs\` | Activity logs (lm_studio_client.log) |
| `C:\Program Files\LM Studio\LM Studio.exe` | LM Studio executable (auto-startup target) |
| `http://localhost:1234/api/v1` | LM Studio native API endpoint |
| `C:\Users\Trader\.conda\envs\p140\python.exe` | Python interpreter (all calls use full path) |

---

## Anti-Patterns (Never Do These)

| Anti-Pattern | Why It's Wrong | Correct Approach |
|---|---|---|
| Hardcode model name in project code | Models change; routing is centralized | Use `task_type` parameter; routing handles it |
| Manually switch models in LM Studio UI during a chat | Breaks async state tracking | Use `client.switch_model(model_id)` |
| Skip `client.startup()` | Health check is mandatory | Always call `startup()` before `chat()` |
| Create new task type without updating config.py | Breaks routing validation | Edit `config.py` `TASK_ROUTING` dict first |
| Use venv instead of p140 | Breaks hub consistency | All projects use `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Mix market analysis into wrapper INIT | Scope creep | Keep SIP focused on infrastructure verification only |
| Hardcode LM Studio path | Paths may change | Use launcher's path search (config.py) |
| Load two models at once | LM Studio is single-model | Always unload before loading new model |
| **Switch API endpoints without approval** | Breaks architecture | Native `/api/v1/*` only. Ask operator first if changing. |
| **Send chat request without model parameter** | LM Studio API requires it | Always include `"model": model_id` in payload |

---

## Fail-Fast Conditions

These conditions HALT the session immediately:

| Condition | Message | Operator Action |
|---|---|---|
| Wrapper file missing (Step 2 of SIP) | "HALT — Wrapper file missing: [path]" | Re-run wrapper build from P_000 |
| LM Studio fails to start (Step 5 of SIP) | "LM Studio failed to start" | Manually launch `C:\Program Files\LM Studio\LM Studio.exe` |
| Task type not in TASK_ROUTING | ValueError raised with available types | Check config.py; add new type if needed |
| Model load fails after 3 retries | Error logged; chat request rejected | Check LM Studio running; verify model name in config |
| Chat request fails with API error | Error logged with LM Studio response | Document in lessons.md; investigate format |

---

## Testing & Validation

### Health Check (Verify Wrapper Works)
```powershell
cd C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio
& "C:\Users\Trader\.conda\envs\p140\python.exe" test_health_check.py
```

Expected output: `✓ WRAPPER HEALTH CHECK PASSED`

### Config Verification
```python
from config import MODELS, TASK_ROUTING
print("Models:", list(MODELS.keys()))
print("Tasks:", len(TASK_ROUTING))
```

Expected: 3 models (primary, batch, long_context), 13+ task types

---

## Maintenance & Evolution

### When to Update This SKILL
- New task type added to config.py
- Model stack changes (new model replaces existing)
- New anti-pattern discovered in practice
- API endpoint or request format changes
- New fail-fast condition identified
- **Architectural decisions change** (requires explicit operator approval first)

### How to Update
1. Edit this file
2. Increment version number in header
3. Add entry to "Changelog" section (below)
4. Document changes in `tasks/lessons.md`
5. Push to `.claude/skills/lm-studio-wrapper/SKILL.md`
6. Notify operator

---

## Changelog

### v1.1 — 2026-05-28
- Added R-005: Chat requests must include model parameter (discovered during testing)
- Added R-006: API endpoint consistency — native LM Studio API only (CRITICAL rule)
- Added critical anti-pattern: "Switch API endpoints without approval"
- Updated Critical Paths to include `tasks/lessons.md` and `tasks/todo.md`
- Pairs with updated SIP and new operational documentation structure

### v1.0 — 2026-05-28
- Initial release
- Three-tier model stack defined
- Task routing rules established
- Anti-patterns documented
- Critical paths defined
- Pairs with SIP v1.0

---

**End of LM Studio Wrapper SKILL v1.1**
