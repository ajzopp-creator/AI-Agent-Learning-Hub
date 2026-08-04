# P_000 — SYSTEM DOCUMENTATION
## AI-Agent-Learning-Hub | Foundation & Master Reference Project

---

| Field | Value |
|---|---|
| **Project ID** | P_000 |
| **Project Name** | Python, Claude & Local LLM Learning Hub |
| **Version** | 1.6 |
| **Created** | March 8, 2026 |
| **Last Updated** | 2026-07-29 |
| **Owner** | Tony (Trader) |
| **Status** | Active |

---

## Section 1 — Project Overview

### 1.1 Purpose

P_000 is the **foundation project** for the AI-Agent-Learning-Hub. It serves five roles:

1. **Python Learning Lab** — A safe sandbox to learn and test Python concepts before applying them to live trading projects
2. **Claude API Integration** — Test and develop code that connects to Anthropic's Claude API
3. **LM Studio / Local LLM Testing** — Build and validate local LLM workflows using LM Studio (Llama models) without cloud dependencies
4. **Reusable Script Library** — Store proven, working scripts that other projects can pull from
5. **Master Project Architecture Reference** — Defines folder structure, environment standards, and conventions used across the entire Hub

### 1.2 Primary Goals

- Develop Python skills as a novice coder in a safe environment
- Build and test local LLM integrations using LM Studio before deploying to production projects
- Create reusable utilities that serve P_010, P_020, P_300, and future projects
- Serve as the architectural reference — when in doubt, look here first

### 1.3 Scope

**In scope:**
- Python script development and testing
- Claude API connection and testing
- LM Studio / local LLM integration
- FastAPI agentic workflow development
- Shared utility scripts for all Hub projects
- Folder structure and environment standards

**Out of scope:**
- Live trade execution (handled by other projects)
- Production market data analysis (handled by P_010, P_300)

### 1.4 Related Projects

| Project ID | Description |
|---|---|
| P_010 | Current Market Posture — Daily/intraday market posture analysis |
| P_020 | AJZ Strategies Performance Analysis System |
| P_115 | Buy the Dip Trading System |
| P_300 | Vantage Point Pattern Recognition |
| P_301 | Bullish Trend Pattern V2.5 |
| P_400 | Trade Order Management |
| P_800 | Automation / Note-Taking (Claude–Obsidian MCP) |
| P_805 | Email Trade Extractor |
| P_110 | TradetheBounce OIL analysis |

### 1.5 Definitions & Acronyms

| Term | Definition |
|---|---|
| **Hub** | AI-Agent-Learning-Hub — the root project folder containing all trading sub-projects |
| **p140** | Shared conda environment used by ALL projects. Path: `C:\Users\Trader\.conda\envs\p140\` |
| **LM Studio** | Local LLM application running Llama models. API endpoint: `http://localhost:1234/v1` |
| **DeepSeek R1 14B** | Primary local model (daily driver): `deepseek-r1-distill-qwen-14b` |
| **Qwen 32B** | Batch processing model: `qwen2.5-coder-32b-instruct` |
| **Llama 4 Scout** | Long-context specialist: `llama-4-scout-17b-16e-instruct` |
| **TOS** | ThinkOrSwim — charting and ThinkScript development platform |
| **ThinkScript** | Proprietary scripting language used inside ThinkOrSwim |
| **VantagePoint** | Pattern recognition trading software (no public API) |
| **P_000** | This project — the foundation and master reference |
| **FastAPI** | Python web framework used for agentic workflow architecture |
| **MCP** | Model Context Protocol — allows Claude to connect to external tools/services |
| **Artifact** | A downloadable file delivered by Claude (Python, Markdown, batch, config, etc.) |
| **Monolith** | Anti-pattern: a single large script doing everything — NEVER build these |
| **Bat file** | Windows batch file (.bat) used to launch Python scripts without manual activation |
| **venv** | Python virtual environment — NOT used here; p140 conda env is used instead |
| **GitHub MCP Server** | Future tool to let Claude interact directly with GitHub repos |

---

## Section 2 — Environment & Infrastructure

### 2.1 Python Environment

| Setting | Value |
|---|---|
| **Environment name** | p140 |
| **Type** | Conda (shared across all projects) |
| **Python executable** | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| **Activation** | NOT required — all .bat files call python.exe directly by full path |

**Key packages installed in p140:**
- pandas, numpy — data analysis
- pandas_ta — technical analysis indicators
- numba — performance acceleration
- python-dotenv — environment variables
- pyyaml — config file support
- loguru — logging
- colorama, tqdm, pytz, pytest
- fastapi, uvicorn, httpx, pydantic-settings (for agentic migration work)

### 2.2 LM Studio Configuration

| Setting | Value |
|---|---|
| **API endpoint** | http://localhost:1234/api/v1 |
| **Priority** | LOCAL FIRST — always prefer LM Studio over cloud APIs |

**Three-tier model stack implemented April 29, 2026.**
See `Local_LLM_Upgrade_Plan_V2.0.md` for full implementation detail.

| Tier | Model | Use Case |
|---|---|---|
| **Primary (daily driver)** | deepseek-r1-distill-qwen-14b | Real-time analysis, coding, trade setup evaluation |
| **Batch (heavy analysis)** | qwen2.5-coder-32b-instruct | Trade journal processing, document summarization, pipeline builds |
| **Long context (specialist)** | llama-4-scout-17b-16e-instruct | Documents over 128K tokens, full architecture ingestion |

**Hardware context:** ASUS TUF Gaming F16 FX608LP — Intel Core Ultra 9 275HX (24 cores) + RTX 5070 Laptop (8GB GDDR7 VRAM) + 96GB DDR5 RAM.
The 96GB RAM enables CPU offload of the 32B model — viable for batch work at 5–12 tokens/sec.

**LM Studio model configuration:**

| Model | GPU Layers | Context Length | Temperature |
|---|---|---|---|
| DeepSeek R1 14B | 33 | 16384 | 0.7 (analysis) / 0.3 (coding) |
| Qwen2.5-Coder-32B | 10 | 8192 | 0.2 |
| Llama 4 Scout 17B | 28 | 65536 | 0.7 |

**Task routing (13 standard types — full table in `P_000_LMS_Integration_Guide.md`):**

| Task | Model |
|---|---|
| Real-time market analysis chat | DeepSeek R1 14B |
| Trade setup evaluation (BT, CAVP) | DeepSeek R1 14B |
| Python coding — quick iterations | DeepSeek R1 14B |
| Trade journal batch analysis | Qwen2.5-Coder-32B |
| Document summarization (under 128K) | Qwen2.5-Coder-32B |
| Long document ingestion (128K+) | Llama 4 Scout 17B |
| Complex multi-file refactoring | Claude (cloud escalation) |

**LM Studio Wrapper** — shared interface for all Hub projects.
Owned by P_000. Any project integrates with two lines at startup.
See `P_000_LMS_Integration_Guide.md` for the standard init pattern.

| Layer | File | Purpose |
|---|---|---|
| Config | `integrations\lm_studio\config.py` | Model definitions, task routing, endpoints |
| Interface | `integrations\lm_studio\infrastructure\lm_studio_api.py` | `get_wrapper_status()` — import from here |
| Launcher | `integrations\lm_studio\infrastructure\lm_studio_launcher.py` | Auto-start LM Studio if not running |

**Init pattern (every project):** Declare `task_type` at startup → wrapper auto-launches LM Studio → loads correct model → project proceeds.

### 2.3 Claude API

- Used for testing and integration work within P_000
- API keys stored in `.env` files only — never in code
- Reference `integrations\claude_api\` for working connection examples
- Production projects use local LM Studio; Claude API is the escalation path only

### 2.4 Development Tools

| Tool | Purpose |
|---|---|
| Visual Studio Code | Primary code editor |
| ThinkOrSwim | Charting and ThinkScript development |
| VantagePoint | Pattern recognition (no public API — GUI scripting considered) |
| PowerShell | Primary command-line interface |
| FFmpeg | Audio processing |
| Whisper | Audio transcription (combined with LM Studio for analysis) |

---

## Section 3 — Architecture Standards

### 3.1 Folder Structure (All Projects)

```
ProjectName/
├── python/          # All Python scripts
├── tos_scripts/     # ThinkScript files
├── data/
│   ├── xml_exports/ # TOS grid exports
│   ├── processed/   # Cleaned data
│   └── historical/  # Historical reference data
├── outputs/
│   ├── reports/
│   ├── charts/
│   └── alerts/
├── docs/
│   └── notes/
└── README.md
```

### 3.2 P_000 Specific Folder Structure

```
P_000_PythonClaudeLocalLLM/
├── python/
├── tos_scripts/
├── data/
│   ├── xml_exports/
│   ├── processed/
│   └── historical/
├── outputs/
│   ├── reports/
│   ├── charts/
│   └── alerts/
├── docs/                    # P_000-owned documentation
│   ├── notes/
│   └── examples/
└── tasks/                   # lessons.md, todo.md
```

**LM Studio wrapper code lives at Hub root, not inside P_000:**

```
AI-Agent-Learning-Hub/
├── integrations/
│   └── lm_studio/               # Shared wrapper (P_000 owns, all projects use)
│       ├── config.py            # Model definitions, routing, endpoints
│       ├── infrastructure/
│       │   ├── lm_studio_api.py     # Shared interface — import get_wrapper_status() here
│       │   └── lm_studio_launcher.py  # Auto-start LM Studio
│       ├── domain/
│       │   └── task_router.py       # Task-to-model routing logic
│       └── application/
│           └── lm_studio_client.py  # Full async client (future use)
└── docs/
    └── lm_studio/               # Shared LM Studio documentation
        ├── P_000_LMS_Integration_Guide.md
        ├── P_000_LM_Studio_Wrapper_Architecture_Overview.md
        └── P_000_LM_Studio_Wrapper_System_Initialization_Prompt_v1.0.md
```

### 3.3 Hub-Wide Shared Resources

```
shared_resources/
├── tos_scripts/
│   ├── indicators/
│   ├── scanners/
│   ├── strategies/
│   └── templates/
├── python_utils/
│   ├── xml_parser.py
│   ├── data_cleaner.py
│   ├── chart_generator.py
│   ├── alert_system.py
│   └── config.py
├── data_exports/
│   ├── raw/
│   ├── cleaned/
│   └── combined/
├── llm_prompts/
│   ├── analysis/
│   ├── summarization/
│   └── trade_review/
├── chaikin_enrichment/      # P_800 Chaikin Power Gauge enrichment -- application/domain/infrastructure layers + tests (added 2026-07-24)
├── skills/                  # reserved, empty as of 2026-07-27
├── tools/                   # reserved, empty as of 2026-07-27
├── __init__.py
└── hub_mcp_launcher.ps1
```

*(Section 3.3 refreshed 2026-07-27 -- ref WO-P000-E9.001. Excludes __pycache__/ as a generated cache artifact, not tracked structure.)*

#### Shared-Layer Boundary (added 2026-06-05)
The Hub has two distinct shared layers. They are NOT duplicates -- keep them separate:

| Layer | Folder | Holds | Referenced by |
|---|---|---|---|
| Code library | `shared_resources\` | python_utils, llm_prompts, tos_scripts, data_exports, hub_mcp_launcher.ps1 | Python imports + initializer skill Protocol C |
| Governance / ops | `Agentic-Hub-Governance\` | work_orders ledger, governance prompts, config, api-credentials | all project INIT prompts (`$LEDGER`) |

`Agentic-Hub-Governance` is a directory junction pointing at `04-Shared-Resources` from 2026-06-05 to 2026-07-11, when the junction was retired and the folder renamed to `Agentic-Hub-Governance` directly. The `$LEDGER` standard is `Agentic-Hub-Governance\work_orders`. Numbered top-level folders were retired 2026-06-05: 06-Experiments deleted (empty); 01-Learning-Path -> `_archive\`; 02-Production-Agents -> `docs\project_notes\production_agents\`; 03-Local-LLM (audio system, still working) -> `integrations\local_llm\`; 05-Documentation -> `docs\reference\`.

### 3.4 AI Behavior Rules & Constraints

**Claude MUST follow these rules in every session for this project:**

#### Python Code Rules
| Rule | Detail |
|---|---|
| **MUST use p140 environment** | Always reference `C:\Users\Trader\.conda\envs\p140\python.exe` — never suggest creating a new venv |
| **MUST plan before coding** | List all files with estimated line counts BEFORE writing any code |
| **MUST limit file size** | Hard limit: 300 lines per file. Begin splitting at 250 lines |
| **MUST limit function size** | Hard limit: 50 lines per function |
| **MUST separate layers** | domain/ = logic only · infrastructure/ = IO only · application/ = orchestration |
| **MUST deliver one file per code block** | Never combine multiple Python files into one response block |
| **MUST confirm completion** | Output ✅ FILE COMPLETE: filename (N lines) after each file |
| **MUST NOT build monoliths** | Never write everything into a single main.py or single large script |
| **MUST deliver as artifacts** | All files delivered as downloadable artifacts with explicit Windows save paths |

#### LLM Priority Rules
| Rule | Detail |
|---|---|
| **MUST prefer local processing** | Default to LM Studio / local models for all AI features |
| **MAY use Claude API** | Only when local processing is insufficient for the task |
| **MUST NOT use other cloud APIs** | Avoid OpenAI, Cohere, etc. — privacy and cost reasons |

#### File Delivery Rules
| Rule | Detail |
|---|---|
| **MUST include save path** | Every file must include full Windows path: `C:\Users\Trader\AI-Agent-Learning-Hub\...` |
| **MUST deliver config files first** | Order: config → domain → infrastructure → application → CLI → .bat |
| **MUST NOT deliver incomplete files** | Pause and wait for "continue" if a file cannot be completed in one response |

#### Communication Rules
| Rule | Detail |
|---|---|
| **User is a Python novice** | Explain what each command does — no assumed knowledge |
| **User is a VS Code novice** | Include explicit VS Code instructions when relevant |
| **Step-by-step preferred** | Break tasks into clear numbered steps |
| **Test before proceeding** | Always instruct user to test each component before moving to the next |

---

## Section 4 — Active Projects Within P_000

### 4.1 FastAPI Agentic Migration (Claude Summarizer App)

**Location:** `integrations\claude_api\summarizer_app\`

**Status checklist:**
- [ ] Project structure created
- [ ] Claude API wrapper built and tested
- [ ] Prompt templates written
- [ ] FastAPI routes working
- [ ] Storage layer implemented
- [ ] History retrieval working

### 4.2 Audio Transcription System

**Status:** Working
**Components:** Whisper (transcription) + LM Studio local model (analysis)
**Analysis types supported:** Trade ideas, risk analysis, setup identification

---

## Section 5 — Migration Plan & Roadmap

### 5.1 Agentic Migration Next Steps

- [ ] Environment Setup — Install FastAPI dependencies into p140
- [ ] Move Prompts — Extract Claude prompts into `/prompts` folder
- [ ] Refactor Client — Move Claude logic into `app/utils/claude_client.py`
- [ ] Test End-to-End — Use FastAPI Swagger UI (`/docs`) to verify: Ingest → Summarize → View Result
- [ ] Set Up GitHub Private Repo — Push AI-Agent-Learning-Hub to private GitHub
- [ ] Install GitHub MCP Server *(requires GitHub repo to be live first)*

### 5.2 Future Development Considerations

- GUI scripting for VantagePoint using pywinauto (no public API available)
- Trade journal analysis using local LLM
- Document summarization pipeline
- Chart pattern analysis
- Email categorization automation
- Schwab API integration for account management
- Automated order submission for risk management (future)

---

## Section 6 — Error Corrections Log

| # | Date | Severity | Error Observed | Correct Behavior |
|---|---|---|---|---|
| 001 | 2026-03-08 | High | Claude generating incomplete Python scripts | Always plan all files with line counts first; deliver one complete file per code block; pause and wait for "continue" before next file |
| 002 | 2026-03-08 | High | Claude suggesting new venv creation | NEVER suggest creating a new venv — always use the shared p140 conda environment |
| 003 | 2026-03-08 | Medium | Claude writing monolithic scripts (everything in main.py) | Always split into domain / infrastructure / application layers; hard limit 300 lines per file |
| 004 | 2026-06-30 | High | An untraced session added extra="forbid" to P400Record (obsidian_writers\domain\vault_schemas.py) without accounting for write_handler.py's unconditional injected source key -- silently broke every P400 vault write for a ~90min window | Pydantic models backing a shared write path must be tested against the actual writer's injected/derived fields, not just the caller's explicit payload, before adding extra="forbid" |
| 005 | 2026-07-29 | Medium | WOs reaching OWNER_DONE without their Completion Gate checklist block present (WO-P000-E9.001 sat 2 days with none; ledger changelog separately notes ten prior P_300/P_400 WOs did the same) -- INIT's daily check surfaces it but nothing blocks OWNER_DONE from being set without the block already there | Completion Gate block must be copied into the WO in the same edit that sets Status=OWNER_DONE, not backfilled later at Independent Review; see WO_COMPLETION_GATE.md Enforcement section added same day |

---

## Section 7 — Security & Sensitive Data Rules

- API keys stored in `.env` files ONLY — never in code, never committed to git
- `.gitignore` must exclude: `integrations/schwab_api/credentials/`, `*.env`, `**/api_keys.*`
- Large data files excluded from git: XML exports, historical price data
- Schwab API credentials: user must enter directly — Claude will never handle financial credentials

---

## Section 8 — Standard Workflows

### 8.1 Starting a New Python Script

1. Read `python-project-architecture` SKILL.md before writing any code
2. List all files with estimated line counts
3. Deliver config.py first
4. Deliver one file per response block
5. Confirm ✅ FILE COMPLETE after each file
6. Include .bat launcher last

### 8.2 Adding a New Project to the Hub

1. Use P_000 folder structure as the template
2. Point all .bat files to `C:\Users\Trader\.conda\envs\p140\python.exe`
3. Add project to the Related Projects table (Section 1.4 of this doc)
4. Create README.md in the new project folder
5. Add shared utilities to `shared_resources\python_utils\` rather than duplicating

### 8.3 LM Studio Integration Workflow

1. At project startup, declare `task_type` — wrapper handles the rest
2. Wrapper auto-launches LM Studio if not running
3. Wrapper loads the correct model for the declared task type
4. Project proceeds only after wrapper confirms readiness
5. Never call the wrapper inside trading loops — startup only

See `P_000_LMS_Integration_Guide.md` for the standard init pattern and full task type list.


### 8.4 KB Article Review Convention (added 2026-07-06)

Canonical rule lives in skill `kb-review-convention` (`.claude\skills\kb-review-convention\SKILL.md`) -- Hub-wide, applies from any project session, not just P_115. Do not duplicate the rule here; update the skill file only.

---

## Section 9 — .gitignore Reference

```gitignore
# Sensitive data
# Active file: `C:\Users\Trader\AI-Agent-Learning-Hub\.gitignore` (created April 30, 2026 — content below matches the file on disk).
integrations/schwab_api/credentials/
*.env
**/api_keys.*

# Data files (too large for git)
**/data/xml_exports/*.xml
**/data/historical/
**/data/price_data/

# Outputs (regenerated)
**/outputs/
**/forecasts/archive/

# Python
__pycache__/
*.pyc
.venv/
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

## Section 10 — Document Index

*Architecture docs are disk-canonical (read from disk, not Project knowledge). Only TONY_ABOUT_ME.md and TONY_STYLE_RULES.md stay in Project knowledge -- always-on, mirrored to disk. Set 2026-06-05.*

| Document | Location | Purpose |
|---|---|---|
| `README.md` | Hub root / P_000 root | Project overview and quick reference |
| `Trading_Projects_Folder_Architecture.md` | Hub root | Folder structure and environment standards for all projects |
| `Claude_Summarizer_App_Architecture.md` | P_000 project files | FastAPI summarizer app architecture detail |
| `Claude-Python_Agentic_Migration_1.md` | P_000 project files | Agentic migration plan and task checklist |
| `P_000_SYSTEM_DOCUMENTATION.md` | P_000 docs folder | **This file** — master reference for all sessions |
| `Local_LLM_Upgrade_Plan_V2.0.md` | P_000 docs folder | Three-tier local LLM model stack — hardware analysis, model selection, implementation steps |
| `P_000_LM_Studio_Wrapper_Complete_Delivery.md` | P_000 docs folder | Full delivery record for LM Studio wrapper build |
| `P_000_LMS_Integration_Guide.md` | `docs\lm_studio\` (Hub shared) | Standard init pattern for all projects integrating LM Studio |
| `P_000_LM_Studio_Wrapper_Architecture_Overview.md` | `docs\lm_studio\` (Hub shared) | Full technical design of the LM Studio wrapper |
| `P_000_LM_Studio_Wrapper_System_Initialization_Prompt_v1.0.md` | `docs\lm_studio\` (Hub shared) | 6-step bootstrap prompt for Claude sessions |
| `P_000_Account_Parameters_Current.md` | `config\` (P_000 project) | Current account balance, risk-per-trade, position-sizing gates, and risk-mode adjustments — applies to all trading projects. Manually reviewed monthly by Tony. |
| `Agentic-Hub-Governance` | Hub root | Governance / ops layer -- real folder since 2026-07-11 (formerly `04-Shared-Resources`, accessed via junction 2026-06-05 to 2026-07-11; junction retired, folder renamed). |
| Work-order ledger | `Agentic-Hub-Governance\work_orders\` | Single source of truth for all work orders, per HUB_INIT_REFACTOR_AND_WO_GOVERNANCE v1.1. |
| `CLAUDE_ASSISTANT_INSTRUCTIONS_v2_1_.md` | P_000 docs folder | Hub-wide Claude role/workflow rules across P_115/P_116/P_117/P_118/P_300 (references P_400). Moved from P_115 2026-07-27 -- scope was never P_115-only. Requires Claude.ai Project Knowledge re-attachment (P_115 -> P_000), file move alone does not migrate that. |

---

## Section 11 — Parameter Registry

### 11.1 Environment Parameters

| Parameter | Value |
|---|---|
| conda_env_name | p140 |
| python_exe_path | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| hub_root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| lm_studio_endpoint | `http://localhost:1234/v1` |
| lm_studio_model | deepseek-r1-distill-qwen-14b |
| lm_studio_model_batch | qwen2.5-coder-32b-instruct |
| lm_studio_model_longcontext | llama-4-scout-17b-16e-instruct |

### 11.2 Code Quality Parameters

| Parameter | Value |
|---|---|
| max_lines_per_file | 300 |
| split_warning_threshold | 250 |
| max_lines_per_function | 50 |

### 11.3 Project Naming Convention

| Parameter | Value |
|---|---|
| prefix_format | P_NNN (e.g., P_000, P_010, P_115, P_300) |
| demo_prefix | D_NNN (no active D_NNN projects -- D_130 renamed to P_110 on 2026-06-30) |
| master_reference | P_000 |

### 11.4 Parameter Registry (Quick Load — Session Init)

| Parameter | Value |
|---|---|
| python_exe | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| lm_studio_url | `http://localhost:1234/v1` |
| lm_studio_model | deepseek-r1-distill-qwen-14b |
| lm_studio_model_batch | qwen2.5-coder-32b-instruct |
| lm_studio_model_longcontext | llama-4-scout-17b-16e-instruct |
| hub_root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| max_file_lines | 300 |
| max_function_lines | 50 |
| user_skill_level_python | novice |
| user_skill_level_vscode | novice |
| llm_priority | local (LM Studio first, Claude API second) |

---

*This document is the authoritative reference for P_000. Update Section 6 whenever a new error is identified and corrected. Update Section 11.4 whenever key parameters change.*
*Version 1.2 — Updated April 29, 2026: Hardware profile corrected to ASUS TUF F16 / Intel Core Ultra 9 275HX 24-core. CPU Threads parameter updated to 20 across all models.*
*Version 1.4 — Updated June 3, 2026: Section 1.4 reconciled with on-disk projects/ folder — added P_301, P_400, P_800, P_805. Section 10 — added P_000_Account_Parameters_Current.md. Note: P_116/P_117/P_118 referenced in the account-parameters file are strategy buckets, not Hub project folders.*
*Version 1.6 — Updated July 29, 2026: Section 6 — added EC-005 (Completion Gate checklist backfilled after OWNER_DONE instead of present at time of set). Section 3.3 shared_resources tree refresh (v1.5, WO-P000-E9.001) passed Independent Review same day.*
