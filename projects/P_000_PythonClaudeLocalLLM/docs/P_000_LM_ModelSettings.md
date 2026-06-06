# P_000 — LM Studio Model Settings Reference v1.1
## AI-Agent-Learning-Hub | Local LLM Configuration

| Version | 1.1 | Last Updated | April 29, 2026 |
|---|---|---|---|

---

## Section 1 — Hardware

| Component | Spec |
|---|---|
| Laptop | ASUS TUF Gaming F16 FX608LP |
| CPU | Intel Core Ultra 9 275HX — 24 cores |
| GPU | RTX 5070 Laptop — 8GB GDDR7 VRAM |
| RAM | 96GB DDR5 |
| LM Studio | v0.4.12 |
| API | http://localhost:1234/v1 |

---

## Section 2 — DeepSeek R1 14B — Daily Driver

| Field | Value |
|---|---|
| API identifier | deepseek-r1-distill-qwen-14b |
| Quantization | Q4_K_M — 8.99 GB |
| Preset | DeepSeek-R1-Trading |
| Context Length | 16384 |
| GPU Layers | 33 |
| CPU Threads | 20 (10 when TOS open) |
| Temperature | 0.7 analysis / 0.3 coding |
| System Prompt | P300_LMStudio_System_Prompt.md |
| Verified | ✅ April 29, 2026 |

---

## Section 3 — Qwen2.5-Coder-32B — Batch Model

| Field | Value |
|---|---|
| API identifier | qwen2.5-coder-32b-instruct |
| Quantization | Q4_K_S — 18.78 GB |
| Preset | Qwen32B-Batch |
| Context Length | 32768 |
| GPU Layers | 10 |
| CPU Threads | 20 (10 when TOS open) |
| Temperature | 0.2 |
| System Prompt | None |
| Verified | ✅ April 29, 2026 |

Close TOS before loading. Load → start task → step away.

---

## Section 3b — Qwen2-VL-7B — Vision Model

| Field | Value |
|---|---|
| API identifier | qwen2-vl-7b-instruct |
| Quantization | Q4_K_M — 4.36 GB + 2.58 GB mmproj |
| Preset | Qwen2VL-Vision |
| Context Length | 16384 |
| GPU Layers | 33 |
| CPU Threads | 20 |
| Temperature | 0.7 |
| System Prompt | None — leave blank |
| Structured Output | OFF (grey) — blue = empty response |
| Verified | Pending — vision test in progress |

### Use Cases
- P_300 workflow diagram reading
- SQLite schema screenshot analysis
- VantagePoint grid data extraction
- Any task anchored to image content

### Known Issues
| Date | Issue | Fix |
|---|---|---|
| 2026-04-29 | Q3_K_S returned empty responses | Upgraded to Q4_K_M |
| 2026-04-29 | Structured Output ON = empty {} | Toggle OFF |
| 2026-04-29 | Code Interpreter plugin crashed responses | Remove × from toolbar |
| 2026-04-29 | Context 8192 too small (8887 tokens) | Increased to 16384 |

---

## Section 4 — Llama 4 Scout 17B — Long Context

| Field | Value |
|---|---|
| API identifier | lmstudio-community/Llama-4-Scout-17B-16E-Instruct |
| Quantization | Q4_K_M — 69.29 GB |
| Context Length | 65536 |
| GPU Layers | 28 |
| CPU Threads | 20 (10 when TOS open) |
| Temperature | 0.7 |

Do NOT use as daily driver. Keep installed — only local option for 128K+ tasks.

---

## Section 5 — Task Routing

| Task | Model |
|---|---|
| Real-time analysis, coding, SQLite | DeepSeek R1 14B |
| Trade setup evaluation (BT, CAVP) | DeepSeek R1 14B |
| P_300 session work | DeepSeek R1 14B |
| Workflow/schema screenshot reading | Qwen2-VL-7B Vision |
| VantagePoint grid screenshot | Qwen2-VL-7B Vision |
| Trade journal batch analysis | Qwen2.5-Coder-32B |
| Heavy code generation | Qwen2.5-Coder-32B |
| Documents over 128K tokens | Llama 4 Scout 17B |
| Architecture decisions, multi-file | Claude (cloud) |

---

## Section 6 — Operating Rules

1. One model at a time in LM Studio
2. Default = DeepSeek R1 14B every session
3. TOS running = drop CPU threads to 10
4. Qwen 32B = close TOS first, step away
5. Never delete Llama 4 Scout
6. Escalate to Claude for hard architecture problems

---

## Section 7 — Process Lasso

| Process | Priority |
|---|---|
| LM Studio.exe | Below Normal |
| TOS / java.exe | Above Normal |

Crash: CLOCK_WATCHDOG_TIMEOUT April 29, 2026 — Qwen 32B 20 threads + TOS. Fixed by Lasso.

---

## Section 8 — MCP Servers

`C:\Users\Trader\.lmstudio\mcp.json` — mirrors Claude Desktop

filesystem, Windows-MCP, obsidian

---

*v1.1 April 29, 2026 — Added Qwen2-VL-7B vision model. Context 16384. Code Interpreter crash documented.*
