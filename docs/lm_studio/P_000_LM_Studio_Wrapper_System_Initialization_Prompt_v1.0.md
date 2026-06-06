# LM Studio Wrapper — System Initialization Prompt (SIP) v1.0

**File:** `integrations/lm_studio/docs/LM_Studio_Wrapper_System_Initialization_Prompt_v1.0.md`  
**Version:** 1.0  
**Created:** May 28, 2026  
**Pairs With:** `integrations/lm_studio/` (full wrapper architecture)  
**Applies To:** All trading projects (P_010, P_020, P_115, P_300, D_130)

---

## Purpose

This prompt initializes the LM Studio wrapper architecture in every new trading project session. It verifies environment capability, loads wrapper state (configuration, models, task routing), and confirms the interface is ready for operational use.

The SIP establishes:
- **Environment Capability Discovery** — Verify filesystem/shell MCP availability
- **Wrapper State Verification** — Confirm all config, infrastructure, domain, and application layers are present
- **Model Stack Readiness** — Verify the three-tier model stack is accessible (primary/batch/long_context)
- **Task Routing Validation** — Confirm task-to-model routing table is loaded and operational
- **Architecture Readiness** — Confirm the CLI interface can be invoked

---

## How to Trigger

Type into a new chat focused on a trading project:

```
LM STUDIO INIT
WRAPPER INIT
P_XXX INIT (LM Studio)
```

If the wrapper SKILL is not auto-loaded, paste this prompt directly.

---

## INIT Sequence (Mandatory Execution Order)

### Step 0 — Environment Capability Discovery (Silent Pre-Check)

BEFORE displaying anything, call `tool_search` to verify:

- `windows-mcp:FileSystem` (file reads/writes)
- `windows-mcp:PowerShell` (optional: model loading via CLI)
- `filesystem:read_text_file` (alternative: file reads)

**Behavior:**
- **Available** → INIT proceeds with live disk verification (Steps 1–4)
- **Unavailable** → INIT falls back to upload-and-download; warn operator at Step 6

Per P_000 architecture: Filesystem MCP determines whether Hub is directly accessible.

---

### Step 1 — Session Header

Display exactly:

```
LM STUDIO WRAPPER [Day, Month DD, YYYY — HH:MM ET]
```

Example: `LM STUDIO WRAPPER [Wednesday, May 28, 2026 — 14:45 ET]`

**Wall-clock time fallback:** Call `bash_tool` first: `TZ='America/New_York' date '+%A, %B %d, %Y — %H:%M ET'`  
If unavailable, use `windows-mcp:PowerShell`:  
`[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTime]::UtcNow, "Eastern Standard Time").ToString("dddd, MMMM dd, yyyy — HH:mm")`

If no clock is reachable: `LM STUDIO WRAPPER [time not available]`

---

### Step 2 — Verify Wrapper Files Exist

Check via `windows-mcp:FileSystem info` mode that ALL of these files are present:

**Critical files (HALT if missing):**
```
C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\config.py
C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\requirements.txt
C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\infrastructure\lm_studio_api.py
C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\infrastructure\lm_studio_launcher.py
C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\domain\task_router.py
C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\application\lm_studio_client.py
```

**If any file is missing:**

> "HALT — Wrapper file missing. Run full wrapper rebuild from `integrations/lm_studio/` before proceeding. Missing file: [path]"

Do not proceed past this point.

---

### Step 3 — Load Wrapper Configuration

Read via filesystem MCP:

```
C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\config.py
```

Extract and display:
- **LM_STUDIO_HOST** and **LM_STUDIO_PORT** (verify endpoint is `http://localhost:1234`)
- **MODELS** dict (all three tiers: primary, batch, long_context)
- **TASK_ROUTING** dict (count of task types available)
- **TEMPERATURE_SETTINGS** (analysis, coding, creative presets)

---

### Step 4 — Verify Model Stack Accessibility

Via `windows-mcp:PowerShell`, run from the wrapper root:

```powershell
& "C:\Users\Trader\.conda\envs\p140\python.exe" -c "
import sys
sys.path.insert(0, '.')
from config import MODELS
for tier, config in MODELS.items():
    print(f'{tier}: {config[\"id\"]}')
"
```

**Expected output:**
```
primary: deepseek-r1-distill-qwen-14b
batch: qwen2.5-coder-32b-instruct
long_context: llama-4-scout-17b-16e-instruct
```

**If output differs:**
> "WARNING — Model IDs in config.py do not match expected stack. Verify against Local_LLM_Upgrade_Plan_V1.0.md Section 4.2."

Proceed with warning noted.

---

### Step 5 — Test LM Studio Health Check

Run the health check script:

```powershell
cd "C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio"
& "C:\Users\Trader\.conda\envs\p140\python.exe" test_health_check.py
```

**Expected result:**
```
✓ LM Studio is healthy and responsive
✓ Found [N] model(s):
  - [model names...]
✓ Configured task routing:
  - [task examples...]
✓ WRAPPER READY TO USE
```

**If LM Studio is not responding:**
- Wrapper will auto-start LM Studio (5–30 second delay)
- If auto-start fails: > "LM Studio failed to start. Verify installation at `C:\Program Files\LM Studio\LM Studio.exe`"

**If auto-start succeeds:**
> "LM Studio auto-started successfully. (took N seconds)"

---

### Step 6 — Session Summary

Display exactly this block:

```
═══════════════════════════════════════════════════════════════════════════════
LM STUDIO WRAPPER INITIALIZATION — COMPLETE
═══════════════════════════════════════════════════════════════════════════════

Wrapper Status:       READY
Endpoint:             http://localhost:1234/v1
Filesystem MCP:       [available | unavailable]
LM Studio:            [online | auto-started]

Model Stack:
  Primary (daily):    deepseek-r1-distill-qwen-14b
  Batch (analysis):   qwen2.5-coder-32b-instruct
  Long Context:       llama-4-scout-17b-16e-instruct

Task Routing:         [N] task types configured
CLI Interface:        Ready for use

Config Location:      integrations/lm_studio/config.py
Logs:                 integrations/lm_studio/outputs/logs/lm_studio_client.log

═══════════════════════════════════════════════════════════════════════════════
```

---

## Fail-Fast Conditions

| Condition | Action |
|---|---|
| Wrapper file missing (Step 2) | HALT. Re-run wrapper build. |
| Model IDs ≠ expected stack (Step 4) | WARN. Verify against upgrade plan. Proceed. |
| LM Studio auto-start fails (Step 5) | HALT. Manual start required. Verify installation. |
| Filesystem MCP unavailable (Step 0) | WARN. Fall back to upload-download. Proceed. |
| PowerShell times out (Step 4 or 5) | NOTE timeout. Use wrapper CLI from operator ISE if needed. |

Never proceed past a HALT condition silently. Initialize only after explicit operator confirmation.

---

## Operational Reminders

### For Trading Projects
- **Wrapper is a utility layer**, not a trading system. It provides LM Studio access to trading projects.
- **Three-tier routing is automatic** — specify `task_type` in chat calls; wrapper loads the correct model.
- **No market analysis in INIT** — this SIP verifies infrastructure only. Market posture, data analysis, pattern recognition are project-specific.

### For New Projects (P_010, P_020, P_115, etc.)
1. Copy wrapper reference path: `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\`
2. In your project's CLI or application layer, import: `from infrastructure.lm_studio_api import ...`
3. Initialize client at startup: `await LMStudioClient().startup()`
4. Route tasks by type: `client.chat(messages=[...], task_type="your_task")`

### Files to Reference
- **Architecture:** `integrations/lm_studio/config.py` (all constants and routing)
- **API Reference:** `integrations/lm_studio/infrastructure/lm_studio_api.py`
- **Task Routing Logic:** `integrations/lm_studio/domain/task_router.py`
- **Main Interface:** `integrations/lm_studio/application/lm_studio_client.py`
- **Logs:** `integrations/lm_studio/outputs/logs/lm_studio_client.log`

---

## Quick Reference (Operator-Facing)

### Critical Paths
- **Wrapper root:** `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\`
- **Python:** `C:\Users\Trader\.conda\envs\p140\python.exe`
- **LM Studio executable:** `C:\Program Files\LM Studio\LM Studio.exe`
- **LM Studio API:** `http://localhost:1234/api/v1`

### Tooling Requirements
- **`windows-mcp:FileSystem`** — for file verification and reads
- **`windows-mcp:PowerShell`** — for health check and model verification (optional fallback: operator manual)
- **`bash_tool`** — for wall-clock time (optional fallback: PowerShell or date-only)

### Common Issues & Fixes

| Issue | Fix |
|---|---|
| "LM Studio not responding" | Run test_health_check.py — it auto-starts LM Studio |
| "Model not loading" | Load model in LM Studio UI first, or use `client.switch_model(model_id)` |
| "Task routing unknown" | Check `config.py` `TASK_ROUTING` dict for available task types |
| "PowerShell timeout" | Operator can run `python cli.py catalog-summary` manually from ISE |
| "Wrapper file missing" | Re-run wrapper build from P_000 foundation project |

---

## Manual Fallback

If this SIP file is not auto-loaded by the project and the SKILL is not present, paste this prompt directly into a new chat, then manually:

1. Verify `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\` exists
2. Run: `& "C:\Users\Trader\.conda\envs\p140\python.exe" integrations/lm_studio/test_health_check.py`
3. Paste the output
4. Proceed with Step 6 session summary

---

## Changelog

### v1.0 — 2026-05-28
- Initial release
- Based on P_300 SIP v2.7 pattern
- Adapted for wrapper infrastructure (no market analysis)
- Three-tier model stack integrated
- Task routing validation included

---

## Maintenance

- **Owner:** Claude (drafting), Tony (review)
- **Update trigger:** Wrapper version change, new task types added, model stack update
- **Applies To:** All trading projects using LM Studio wrapper
- **Companion:** `integrations/lm_studio/config.py`, `Local_LLM_Upgrade_Plan_V1.0.md`

---

**End of LM Studio Wrapper System Initialization Prompt v1.0**
