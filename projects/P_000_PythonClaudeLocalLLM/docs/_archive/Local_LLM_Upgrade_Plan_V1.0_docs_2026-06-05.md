# Local LLM Upgrade Plan — V1.0
## AI-Agent-Learning-Hub | P_000 Foundation Reference

---

| Field | Value |
|---|---|
| **Document ID** | LLM-UPGRADE-001 |
| **Version** | 1.0 |
| **Created** | April 29, 2026 |
| **Last Updated** | April 29, 2026 |
| **Owner** | Tony (Trader) |
| **Status** | ✅ COMPLETE — April 29, 2026 |
| **Applies To** | All Hub Projects (P_000, P_010, P_020, P_300, D_130) |

---

## Section 1 — Purpose

This document captures the research, hardware analysis, model selection, and implementation plan for upgrading the local LLM configuration across the AI-Agent-Learning-Hub. It replaces Llama 4 Scout as the daily driver with a three-tier model stack optimized for Tony's ASUS TUF F16 hardware.

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

The 96GB system RAM is the hardware advantage that separates this setup from typical laptop configurations. Most laptops cap at 16–32GB, making 32B model offload impractical. At 96GB, Qwen2.5-Coder-32B via CPU offload is a legitimate batch processing option.

The Intel Core Ultra 9 275HX with 24 cores provides significantly better CPU offload throughput than typical 8-core laptop CPUs. Set CPU Threads to 20 in LM Studio for all models.

---

## Section 3 — Benchmark Context

Claude Sonnet 4 scores approximately 65% on SWE-bench Verified — the standard test for LLM coding quality. The best consumer-runnable local models now reach 49–59% on the same benchmark, a gap that has closed dramatically since 2024.

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
Strengths: 10M token context window. Weaknesses: Mid-tier coding and reasoning benchmarks. Retained as long-context specialist only.

### 4.2 Three-Tier Model Stack

#### Tier 1 — Primary Daily Driver
**DeepSeek R1 Distill Qwen 14B (Q4_K_M)**
- Size: ~9GB — fits within 8GB VRAM with minimal offload
- Speed: 20–40 tokens/second
- License: MIT
- Source: lmstudio-community (downloaded April 29, 2026)
- Key capability: Visible `<think>` reasoning chain — audit whether the model is applying trading rules correctly
- Best for: Daily market analysis, trade setup evaluation, Python debugging, SQLite work, iterative coding

#### Tier 2 — Long Context Specialist (Retained)
**Llama 4 Scout 17B (llama-4-scout-17b-16e-instruct)**
- Size: ~69GB
- Key capability: 10M token context window
- Best for: Full architecture document ingestion, 200+ page documents, context over 128K tokens

#### Tier 3 — Batch Processing
**Qwen2.5-Coder-32B Instruct (Q4_K_M)**
- Size: ~20GB — CPU offload to 96GB RAM
- Speed: 5–12 tokens/second
- License: Apache 2.0
- Best for: Heavy code generation, trade journal batch analysis, document summarization

---

## Section 5 — Task Routing Table

| Task | Model |
|---|---|
| Real-time market analysis chat | DeepSeek R1 14B |
| Trade setup evaluation (BT, CAVP) | DeepSeek R1 14B |
| Python coding — quick iterations | DeepSeek R1 14B |
| Trade journal batch analysis | Qwen2.5-Coder-32B |
| Document summarization (under 128K) | Qwen2.5-Coder-32B |
| Long document ingestion (128K+) | Llama 4 Scout 17B |
| Complex multi-file refactoring | Claude (cloud escalation) |

---

## Section 6 — LM Studio Configuration

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
| Context Length | 8192 |
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

## Section 7 — Troubleshooting Reference

| Symptom | Fix |
|---|---|
| Model fails to load — VRAM error | Reduce GPU Layers by 5, reload |
| Responses under 2 tokens/second | Reduce Context Length to 4096 |
| `<think>` block not appearing (R1) | Set temperature to 0.6 minimum — not 0 |
| Qwen 32B crashes on load | Drop GPU Layers to 5, increase CPU Threads to 22 |
| Wrong model name in API response | Check model card tab in LM Studio — use exact string shown |
| LM Studio not responding | Verify LM Studio running before executing any Hub scripts |

---

## Section 8 — Operational Rules

1. Only one model can be loaded in LM Studio at a time.
2. DeepSeek R1 14B is the default unless a specific task demands a different tier.
3. Llama 4 Scout remains installed — do not delete. Only local option for 128K+ context.
4. Qwen 32B is a batch model. Load it, start the task, step away.
5. For complex multi-file architecture or decisions that are hard to verify — escalate to Claude.

---

## Section 9 — Implementation Status

| Step | Status |
|---|---|
| LM Studio installed (v0.4.12) | ✅ Complete |
| DeepSeek R1 14B Q4_K_M downloaded | ✅ Complete — April 29, 2026 |
| DeepSeek R1 14B loaded and verified | ✅ Complete |
| Qwen2.5-Coder-32B Q4_K_M downloaded | ✅ Complete — April 29, 2026 |
| config.json updated | ✅ Complete — April 29, 2026 |
| GPU layers / CPU threads configured | ✅ Complete — April 29, 2026 |

---

*Update Section 7 when new errors are discovered. Update Section 9 as steps are completed.*
*Hardware profile verified April 29, 2026 via PowerShell system query.*
