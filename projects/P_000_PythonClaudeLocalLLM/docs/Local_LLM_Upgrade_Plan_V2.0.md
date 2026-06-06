# Local LLM Upgrade Plan — V2.0
## AI-Agent-Learning-Hub | P_000 Foundation Reference

---

| Field | Value |
|---|---|
| **Document ID** | LLM-UPGRADE-001 |
| **Version** | 2.0 |
| **Created** | April 29, 2026 |
| **Last Updated** | June 5, 2026 |
| **Owner** | Tony (Trader) |
| **Status** | COMPLETE — implemented April 29, 2026 |
| **Applies To** | All Hub Projects (P_000, P_010, P_020, P_115, P_300, D_130) |
| **Supersedes** | Local_LLM_Upgrade_Plan_V1.0.md (two divergent copies: docs\ and docs\notes\) |

> **V2.0 merge note (June 5, 2026):** Merged the two divergent V1.0 copies into one authoritative file. The `docs\` copy supplied the verified hardware profile (ASUS TUF F16 / Intel Core Ultra 9 275HX, confirmed via PowerShell) and the per-model configuration tables. The `docs\notes\` copy supplied the implementation steps, the parameter-registry mapping, the research sources, and the architecture-document reference block. Every hardware-derived value (CPU thread counts, model sizes, crash-fix settings) uses the verified F16 / Intel profile. The `docs\notes\` copy's AMD Ryzen / TUF A16 figures were a pre-verification draft and have been dropped.

---

## Section 1 — Purpose

This document captures the research, hardware analysis, model selection, and implementation plan for the local LLM configuration across the AI-Agent-Learning-Hub. It replaces Llama 4 Scout as the daily driver with a three-tier model stack tuned for Tony's ASUS TUF F16 hardware.

Trading-specific use cases drove all model selection decisions. Technology serves trading — not the reverse.

---

## Section 2 — Hardware Profile (Verified April 29, 2026)

| Component | Spec | LLM Implication |
|---|---|---|
| **Laptop** | ASUS TUF Gaming F16 FX608LP | Consumer laptop — no multi-GPU |
| **CPU** | Intel Core Ultra 9 275HX | 24 cores / 24 threads — excellent CPU offload capability |
| **GPU** | NVIDIA GeForce RTX 5070 Laptop | 8GB GDDR7 VRAM — hard ceiling for pure GPU inference |
| **System RAM** | 96GB DDR5 | Key asset — enables large model CPU offload |
| **OS** | Windows 11 Pro Build 26200 | LM Studio Windows build |
| **Inference Server** | LM Studio 0.4.12 | API endpoint: `http://localhost:1234/v1` |

The 96GB system RAM is the hardware advantage that separates this setup from typical laptop configurations. Most laptops cap at 16-32GB, making 32B model offload impractical. At 96GB, Qwen2.5-Coder-32B via CPU offload is a legitimate batch processing option.

The Intel Core Ultra 9 275HX with 24 cores provides significantly better CPU offload throughput than typical 8-core laptop CPUs. Set CPU Threads to 20 in LM Studio for all models.

---

## Section 3 — Benchmark Context

Claude Sonnet 4 scores approximately 65% on SWE-bench Verified — the standard test for LLM coding quality. The best consumer-runnable local models now reach 49-59% on the same benchmark, a gap that has closed dramatically since 2024.

| Benchmark Reference | Score |
|---|---|
| Claude Sonnet 4 (cloud) | ~65% SWE-bench Verified |
| Qwen3-Coder-Next (local, 24GB GPU) | 58.7% SWE-bench Verified |
| Qwen2.5-Coder-32B Q4 (local) | ~49% SWE-bench Verified |
| DeepSeek R1 14B Distilled (local) | Strong reasoning; best fit for 8GB VRAM |

The remaining gap versus Claude is concentrated in complex multi-file reasoning and architectural decisions. Those tasks continue to route to Claude. Local models handle the high-volume routine work.

---

## Section 4 — Model Selection

### 4.1 Current Model — Replaced as Daily Driver

**Llama 4 Scout 17B (llama-4-scout-17b-16e-instruct)**

Strengths: 10M token context window — the largest of any consumer-runnable model.
Weaknesses: Mid-tier coding and reasoning benchmarks. Context window performance degrades in practice with quantized models running CPU offload. Not the right tool for daily analytical or coding tasks. Retained as long-context specialist only.

### 4.2 Three-Tier Model Stack

#### Tier 1 — Primary Daily Driver

**DeepSeek R1 Distill Qwen 14B (Q4_K_M)**

- **Size:** ~9-10GB at Q4_K_M — fits within 8GB VRAM with minimal offload
- **Speed:** 20-40 tokens/second on this hardware
- **License:** MIT — no restrictions, free commercial use
- **Source:** lmstudio-community (downloaded April 29, 2026)
- **Key capability:** Visible `<think>` reasoning chain before every response. You can audit whether the model is applying your trading rules correctly, not just accept its output.
- **Best for:** Daily market analysis chat, trade setup evaluation, Python debugging, workflow design, SQLite schema work, iterative coding, P_300 reasoning tasks

#### Tier 2 — Long Context Specialist (Retained)

**Llama 4 Scout 17B (llama-4-scout-17b-16e-instruct)**

- **Size:** ~69GB — CPU offload via 96GB RAM
- **Speed:** Variable depending on offload configuration
- **Key capability:** 10M token context window
- **Best for:** Full architecture document ingestion, 200+ page documents, massive prompt packs, any task where context volume exceeds 128K tokens

#### Tier 3 — Batch Processing / Maximum Coding Quality

**Qwen2.5-Coder-32B Instruct (Q4_K_M)**

- **Size:** ~20GB at Q4_K_M — requires CPU offload to 96GB RAM
- **Speed:** 5-12 tokens/second (CPU offload — slower but functional)
- **License:** Apache 2.0 — free commercial use
- **Key capability:** Highest coding benchmark scores of any consumer-runnable model
- **Best for:** Heavy code generation, trade journal batch analysis, long document summarization, Python pipeline builds where response time is not the constraint

---

## Section 5 — Task Routing Table

| Task | Model | Reason |
|---|---|---|
| Real-time market analysis chat | DeepSeek R1 14B | Fast, VRAM-resident, strong reasoning |
| Trade setup evaluation (BT, CAVP) | DeepSeek R1 14B | Reasoning chain shows rule application |
| Python coding — quick iterations | DeepSeek R1 14B | Fast turnaround, good code quality |
| SQL schema design and debugging | DeepSeek R1 14B | Reasoning-focused, fast iteration |
| VantagePoint pattern analysis | DeepSeek R1 14B | Daily driver default |
| Trade journal batch analysis | Qwen2.5-Coder-32B | Higher quality, slower is acceptable |
| Document summarization (under 128K) | Qwen2.5-Coder-32B | Depth of analysis worth the wait |
| Long document ingestion (128K+) | Llama 4 Scout 17B | Only model with sufficient context |
| Architecture document review | Llama 4 Scout 17B | Full document fits in one context window |
| Complex multi-file refactoring | Claude (cloud) | Escalation path for hard problems |

---

## Section 6 — LM Studio Configuration

CPU Threads = 20 for all models (Intel Core Ultra 9 275HX, 24 cores). Qwen context synced to live Qwen32B-Batch preset (32768) on June 5, 2026.

### DeepSeek R1 14B Settings
| Parameter | Value |
|---|---|
| Context Length | 16384 |
| GPU Layers | 33 |
| CPU Threads | 20 |
| Temperature | 0.7 (analysis) / 0.3 (coding) |

### Qwen2.5-Coder-32B Settings
| Parameter | Value |
|---|---|
| Context Length | 32768 |
| GPU Layers | 10 |
| CPU Threads | 20 |
| Temperature | 0.2 |

### Llama 4 Scout 17B Settings
| Parameter | Value |
|---|---|
| Context Length | 65536 |
| GPU Layers | 28 |
| CPU Threads | 20 |
| Temperature | 0.7 |

---

## Section 7 — Implementation Steps

### Step 1 — Download Models in LM Studio

1. Open LM Studio, click the **Search** icon (magnifying glass) in the left sidebar.
2. Search `deepseek-r1-distill-qwen-14b`, choose the **Q4_K_M** build, Download (~10GB).
3. Search `qwen2.5-coder-32b-instruct`, choose the **Q4_K_M** build, Download (~20GB).
4. Both can be queued — LM Studio downloads in sequence.

### Step 2 — Configure DeepSeek R1 14B

Load the model and apply the DeepSeek R1 14B settings from Section 6. Reduce GPU Layers to 28 if you hit an OOM error.

**Verification test prompt:**
```
Given a stock showing a flag pattern on the daily chart with rising volume on the breakout,
what are the three most important confirmation signals before entering a BT strategy trade?
```
Confirm a `<think>` block appears before the answer.

### Step 3 — Configure Qwen2.5-Coder-32B

Load the model and apply the Qwen2.5-Coder-32B settings from Section 6. Allow 60-90 seconds for initialization — this is normal, layers stream from RAM.

### Step 4 — Update Hub Configuration

Update `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\integrations\lm_studio\config.json`:

```json
{
  "lm_studio_endpoint": "http://localhost:1234/v1",
  "models": {
    "primary": "deepseek-r1-distill-qwen-14b",
    "batch": "qwen2.5-coder-32b-instruct",
    "long_context": "llama-4-scout-17b-16e-instruct"
  },
  "notes": "Switch active model in LM Studio UI before running scripts. LM Studio serves whichever model is currently loaded."
}
```

### Step 5 — Update System Documentation

Apply these changes to `P_000_SYSTEM_DOCUMENTATION.md`:

- **Section 2.2** — Replace Llama 4 Scout as primary model; document all three tiers
- **Section 11.1** — Update `lm_studio_model` to `deepseek-r1-distill-qwen-14b`
- **Section 11.4** — Update Parameter Registry quick-load table
- **Section 10** — Add this document to the Document Index

---

## Section 8 — Troubleshooting Reference

| Symptom | Fix |
|---|---|
| Model fails to load — VRAM error | Reduce GPU Layers by 5, reload |
| Responses under 2 tokens/second | Reduce Context Length to 4096 |
| `<think>` block not appearing (R1) | Set temperature to 0.6 minimum — not 0 |
| Qwen 32B crashes on load | Drop GPU Layers to 5, increase CPU Threads to 22 |
| Wrong model name in API response | Check model card tab in LM Studio — use exact string shown |
| LM Studio not responding | Verify LM Studio running before executing any Hub scripts |

---

## Section 9 — Operational Rules

1. Only one model can be loaded in LM Studio at a time. Switch models in the UI before running any Hub script.
2. DeepSeek R1 14B is the default unless a specific task demands a different tier.
3. Llama 4 Scout remains installed — do not delete. It is the only local option for 128K+ context tasks.
4. Qwen 32B is a batch model. Load it, start the task, step away. Do not wait for real-time responses.
5. For complex multi-file architecture or decisions that are hard to verify — escalate to Claude.

---

## Section 10 — Parameters Updated in Master Registry

The following parameters in `P_000_SYSTEM_DOCUMENTATION.md` Section 11.4:

| Parameter | Old Value | New Value |
|---|---|---|
| lm_studio_model | llama-4-scout-17b-16e-instruct | deepseek-r1-distill-qwen-14b |
| lm_studio_model_batch | (not previously defined) | qwen2.5-coder-32b-instruct |
| lm_studio_model_longcontext | (not previously defined) | llama-4-scout-17b-16e-instruct |

---

## Section 11 — Research Sources

Benchmarks and hardware analysis from the following sources (April 2026):

- SWE-bench Verified leaderboard — coding benchmark standard
- WhatLLM.org local LLM rankings (updated April 2026)
- AI Hub best local LLM for coding guide (April 2026)
- DeepSeek V4 Flash local hardware guide — Compute Market
- ASUS TUF Gaming F16 (FX608LP) official tech specs
- Hardware profile verified April 29, 2026 via PowerShell system query

---

## Section 12 — Architecture Document Reference Block

Add to `P_000_SYSTEM_DOCUMENTATION.md` **Section 10 — Document Index**:

| Document | Location | Purpose |
|---|---|---|
| `Local_LLM_Upgrade_Plan_V2.0.md` | P_000 project docs | Three-tier local LLM model stack — hardware analysis, model selection, implementation steps |

Add to **Section 2.2 — LM Studio Configuration**:

```
Three-tier model stack implemented April 29, 2026.
See Local_LLM_Upgrade_Plan_V2.0.md for full implementation detail.
Primary: deepseek-r1-distill-qwen-14b (daily driver)
Batch:   qwen2.5-coder-32b-instruct (heavy analysis)
Context: llama-4-scout-17b-16e-instruct (128K+ tasks)
```

---

## Section 13 — Implementation Status

| Step | Status |
|---|---|
| LM Studio installed (v0.4.12) | Complete |
| DeepSeek R1 14B Q4_K_M downloaded | Complete — April 29, 2026 |
| DeepSeek R1 14B loaded and verified | Complete |
| Qwen2.5-Coder-32B Q4_K_M downloaded | Complete — April 29, 2026 |
| config.json updated | Complete — April 29, 2026 |
| GPU layers / CPU threads configured | Complete — April 29, 2026 |

---

*This document is the authoritative reference for the Hub local LLM configuration.*
*Update Section 8 when new errors or workarounds are discovered.*
*Update Sections 10 and 13 whenever model selection or implementation status changes.*
