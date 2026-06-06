# LM Studio Wrapper — Architecture Overview

**File:** `integrations/lm_studio/docs/LM_Studio_Wrapper_Architecture_Overview.md`  
**Version:** 1.0  
**Date:** May 28, 2026  
**Applies To:** All trading projects using local LLM processing

---

## Project Purpose

The LM Studio Wrapper provides a **unified, standardized interface** for local LLM access across all trading projects. It abstracts model management, task routing, and health checking so projects focus on trading logic, not infrastructure.

**Philosophy:** Local processing first. Privacy preserved. Cost optimized.

---

## Architecture Layers

### 1. Configuration Layer (`config.py`)

**Responsibility:** All constants, paths, and routing tables live here.

- Model definitions (three-tier stack)
- Task-to-model routing table
- Temperature presets
- API endpoint configuration
- Logging setup

**Why separate:** Changes to routing or models only require editing one file. Projects importing from config get automatic updates.

---

### 2. Infrastructure Layer (`infrastructure/`)

**Responsibility:** Pure I/O with external systems.

#### `lm_studio_api.py` — LM Studio Native API Calls
- `load_model()` — Load a model via `/api/v1/models/load`
- `unload_model()` — Unload current model
- `send_chat_request()` — Send prompt to loaded model via `/api/v1/chat`
- `get_available_models()` — Fetch model list
- `check_lm_studio_health()` — Verify LM Studio is responding

**Constraints:** No business logic. Only fetch, send, return raw data.

#### `lm_studio_launcher.py` — LM Studio Lifecycle
- `find_lm_studio_executable()` — Locate LM Studio installation
- `start_lm_studio()` — Launch LM Studio if not running
- `ensure_lm_studio_running()` — Guarantee startup

**Constraints:** Handles only startup automation. No model loading logic.

---

### 3. Domain Layer (`domain/`)

**Responsibility:** Business logic for task routing and model selection.

#### `task_router.py` — Task Classification
- `route_task(task_type)` → (model_tier, model_id)
- `get_temperature_for_task(task_type)` → float
- `get_context_for_model(model_tier)` → int (tokens)
- `validate_task_type(task_type)` → bool
- `list_all_tasks()` → list of valid task types

**Constraints:** No I/O. Pure decision-making. Returns data to application layer.

---

### 4. Application Layer (`application/`)

**Responsibility:** Orchestration. Coordinates domain + infrastructure.

#### `lm_studio_client.py` — Main Interface
```python
class LMStudioClient:
    async def startup()          # Ensure LM Studio is running
    async def switch_model()     # Unload current, load new
    async def chat()             # Send prompt (auto-routes if task_type given)
    async def get_models()       # List available models
```

**Key feature:** `chat()` accepts optional `task_type` parameter:
- If provided → auto-loads correct model, sets temperature, proceeds
- If not provided → uses currently loaded model

---

## Three-Tier Model Stack

| Tier | Model | Speed | Quality | Context | Best For |
|---|---|---|---|---|---|
| **Primary** | DeepSeek R1 14B | Fast (20–40 tok/s) | Strong | 16K | Real-time analysis, trade setup evaluation, quick coding |
| **Batch** | Qwen 32B | Slow (5–12 tok/s) | Highest | 8K | Document analysis, trade journal processing, heavy code generation |
| **Long Context** | Llama 4 Scout 17B | Medium (10–20 tok/s) | Good | 65K | Full document ingestion, architecture review, large dataset analysis |

**Selection is declarative:** Specify `task_type` → wrapper loads correct tier automatically.

---

## Task Routing Table (13 Types)

### Primary Tier (Real-Time)
```
market_analysis              → DeepSeek R1 14B
trade_setup_evaluation      → DeepSeek R1 14B
quick_coding                → DeepSeek R1 14B
python_debugging            → DeepSeek R1 14B
sql_schema_design           → DeepSeek R1 14B
vantagepoint_analysis       → DeepSeek R1 14B
```

### Batch Tier (Analysis)
```
trade_journal_analysis      → Qwen 32B
document_summarization      → Qwen 32B
code_generation_heavy       → Qwen 32B
pattern_analysis            → Qwen 32B
```

### Long Context Tier (Large Documents)
```
full_document_ingestion     → Llama 4 Scout 17B
architecture_review         → Llama 4 Scout 17B
large_codebase_analysis     → Llama 4 Scout 17B
```

**To add a new task type:**
1. Edit `config.py` `TASK_ROUTING` dict
2. Assign to one of three tiers
3. Update this documentation

---

## Control Flow: Chat Request

```
Trading Project
    ↓
client.chat(messages=[...], task_type="market_analysis")
    ↓
application/lm_studio_client.py:LMStudioClient.chat()
    ├─ route_task("market_analysis")  [domain layer]
    │   → returns ("primary", "deepseek-r1-distill-qwen-14b")
    │
    ├─ switch_model("deepseek-r1-distill-qwen-14b")  [infra layer]
    │   → calls /api/v1/models/load
    │
    ├─ get_temperature_for_task("market_analysis")  [domain layer]
    │   → returns 0.7 (analysis preset)
    │
    └─ send_chat_request(messages, temp=0.7)  [infra layer]
        → calls /api/v1/chat
        → returns response
    ↓
Trading Project (uses response)
```

---

## Usage Patterns

### Pattern 1: Auto-Routing (Recommended)

```python
from application.lm_studio_client import LMStudioClient

client = LMStudioClient()
await client.startup()

response = await client.chat(
    messages=[{"role": "user", "content": "Analyze SPY daily..."}],
    task_type="market_analysis"  # ← Wrapper handles model selection
)
```

**Best for:** Projects that follow task type conventions.

---

### Pattern 2: Manual Model Selection

```python
client = LMStudioClient()
await client.startup()

# Load Qwen 32B for heavy work
from config import MODELS
await client.switch_model(MODELS["batch"]["id"])

response = await client.chat(
    messages=[{"role": "user", "content": "Summarize 200-page doc..."}]
)
```

**Best for:** Edge cases where task type doesn't fit.

---

## Operational Files

| File | Purpose | Operator Access |
|---|---|---|
| `config.py` | All constants, routing, models | Edit directly to add task types |
| `cli.py` | Command-line commands | `python cli.py health-check` |
| `test_health_check.py` | Verify wrapper is ready | `python test_health_check.py` |
| `outputs/logs/lm_studio_client.log` | Activity log | Read-only (for debugging) |
| `Launch_LM_Studio_Wrapper.bat` | Desktop launcher | Double-click to test |

---

## Integration with Trading Projects

### Minimal Integration (Any Project)

1. **Import client:**
   ```python
   from pathlib import Path
   import sys
   sys.path.insert(0, str(Path(__file__).parent.parent / "integrations" / "lm_studio"))
   from application.lm_studio_client import LMStudioClient
   ```

2. **Initialize at startup:**
   ```python
   client = LMStudioClient()
   await client.startup()
   ```

3. **Use as needed:**
   ```python
   response = await client.chat(
       messages=[...],
       task_type="your_task_type"
   )
   ```

### Project-Specific Task Types (Extension)

If a project needs task types beyond the 13 standard ones:

1. Edit `config.py` `TASK_ROUTING` dict
2. Add entry: `"your_new_task": "primary"  # or batch or long_context`
3. Use in project: `task_type="your_new_task"`

**Example:** P_300 might add `"vantagepoint_pattern_train"` → batch tier.

---

## Testing & Validation

### Quick Verification (All Projects)

```powershell
cd C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio
& "C:\Users\Trader\.conda\envs\p140\python.exe" cli.py health-check
```

**Expected:** ✓ All checks pass.

### Detailed Model Info

```powershell
python cli.py model-info
```

### Task Routing Check

```powershell
python cli.py task-routing                    # All 13 task types
python cli.py route market_analysis           # Where does this route?
```

---

## Design Decisions

### Why Separate Layers?

- **Config:** Single source of truth for routing and models
- **Infrastructure:** Testable without trading logic
- **Domain:** Pure business rules; reusable
- **Application:** Clean orchestration; easy to mock in tests

### Why Auto-Startup?

- Reduces friction for operators
- Trading projects can focus on trading, not LM Studio lifecycle
- Health check is mandatory anyway — startup is part of it

### Why Task Routing Is Declarative?

- No magic string parsing
- Type safety (ValueError if unknown task)
- Easy to audit (one dict in config.py)
- Adding new tasks is trivial

### Why Three Tiers?

- **Primary:** Balances speed + quality for real-time work
- **Batch:** Maximum quality for research/analysis (speed acceptable)
- **Long Context:** Unique capability (no other local model reaches 65K+)

Trade-off: Requires operator to understand when each is appropriate.

---

## Future Extensions

Potential additions (not in MVP):

- **Streaming responses:** Yield tokens as they arrive
- **Token counting:** Pre-flight context fit check
- **Model persistence:** Cache loaded model state across calls
- **Telemetry:** Track model selection accuracy, token usage
- **Custom prompt templates:** Per-task system prompts
- **Fine-tuning integration:** Support for locally fine-tuned models

---

## Support & Maintenance

| Issue | Fix |
|---|---|
| "LM Studio not responding" | Run `cli.py health-check` — auto-starts LM Studio |
| "Unknown task type" | Run `cli.py task-routing` to see all valid types |
| "Model didn't load" | Check LM Studio UI; verify model exists |
| "Chat returned error" | Check logs at `outputs/logs/lm_studio_client.log` |

---

## Files Reference

```
integrations/lm_studio/
├── config.py                           [Constants & routing]
├── cli.py                              [Command-line interface]
├── test_health_check.py                [Health verification]
├── requirements.txt
│
├── infrastructure/
│   ├── lm_studio_api.py                [LM Studio API calls]
│   └── lm_studio_launcher.py           [Startup automation]
│
├── domain/
│   └── task_router.py                  [Task classification logic]
│
├── application/
│   └── lm_studio_client.py             [Main client interface]
│
├── docs/
│   ├── LM_Studio_Wrapper_System_Initialization_Prompt_v1.0.md
│   ├── LM_Studio_Wrapper_Architecture_Overview.md   [This file]
│   └── Quick_Start_Guide.md            [Getting started]
│
└── outputs/
    └── logs/
        └── lm_studio_client.log        [Activity log]
```

---

**End of LM Studio Wrapper Architecture Overview v1.0**
