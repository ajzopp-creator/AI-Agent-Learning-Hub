---
name: system-doc-initializer
description: >
  Automatically loads critical system context, determines execution environments dynamically, 
  and enforces strict system architecture boundaries at the start of every session. This skill 
  prevents parameter drift, structural hallucinations, and environment communication failures across 
  Claude Projects, Gemini workspaces, Perplexity Collections, and Copilot environments.
---

# System Documentation Initializer & Dynamic Thinking Skill
## Multi-Platform AI-Agent-Learning-Hub Edition

## Purpose
Establishes a rigorous operational boundary layer at session initialization. This skill neutralizes context dilution, eliminates blind copy-pasting, and ensures that the model executes tasks under explicit architectural boundaries rather than default assumptions.

---

## Step 0: Real-Time Environment Discovery (Run First)

Before asserting filesystem access capabilities, reading system prompt configuration text, or making assumptions about platform tools, perform a live, deterministic environment check.

### 1. Execution Routine
*   **Claude Desktop / Local Environments:** Execute `tool_search(query="PowerShell")` or run a local baseline environment query.
*   **Web-Based Ecosystems (Gemini, Perplexity, Claude Web):** Identify context availability via explicit project knowledge mounts, document attachments, or session uploads.

### 2. Environment Matrix & Mapping Rules

| Detected Interface Signals | Target Runtime Environment | Operational Permissions & Path Rules |
| :--- | :--- | :--- |
| Local Shell Tool Available / Validated | Local Desktop AI (Windows-MCP Active) | Full filesystem read/write access via MCP to host directory path structures (`C:\Users\Trader\AI-Agent-Learning-Hub\`). |
| No Host Shell Tools / Sandboxed Environment | Web-Based Cloud Container | No direct local execution. Operate strictly via Project Mounts (`/mnt/project/`), active attachments, or structured text paste blocks. |

### 3. Immediate State Declaration
Output the verified execution status line at the absolute top of the very first session response:
```text
🖥 Runtime: [Validated Platform Name] (Local Paths Available) — Workspace Verified