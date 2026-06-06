# P_000 Research Integrated Architecture v0.2

## Change Log
- Renamed the document from P_800 to P_000 to make the architecture layer the top-level research hub.
- Kept P_800 as the automation layer inside the larger architecture instead of as the primary umbrella.
- Merged the Trading Brain / Obsidian implementation into the document as a dedicated integrated section.
- Integrated the "Using Obsidian and Claude to Learn a Subject" workflow as the standard research and learning engine for trading concepts.
- Updated the folder structure so the vault now supports both trading execution and research learning in one system.

## Purpose and Scope
This document defines a unified "System of Systems" that connects:

- P_800 automation and template control.
- The Trading Brain / P_115 Obsidian implementation.
- The AJZ Strategies 2026 Trading Plan V2.0 risk framework.
- The P_000 research and learning workflow powered by Obsidian + Claude.

The goal is to ensure that execution, risk, and learning all operate from a single coherent architecture.

## Updated Folder Structure
```text
P_000 Research /
├── 00 Dashboard /
│   ├── Home.md
│   ├── Daily Dashboard.md
│   └── Weekly Review Hub.md
├── 01 Daily Flow /
│   ├── YYYY-MM-DD Daily Note.md
│   └── Archive /
├── 02 Pre-Market /
│   ├── YYYY-MM-DD Pre-Market Prep.md
│   └── Archive /
├── 03 Trade Setups /
│   ├── YYYY-MM-DD SYMBOL Setup.md
│   └── Archive /
├── 04 Trade Journal /
│   ├── YYYY-MM-DD SYMBOL Trade.md
│   └── Archive /
├── 05 Research Knowledge Base /
│   ├── P_000 Master Index.md
│   ├── Concepts /
│   ├── Connections /
│   ├── Questions /
│   ├── Reviews /
│   ├── Synthesis /
│   └── Skills /
├── 06 Trading Brain /
│   ├── Liquidity Theory.md
│   ├── Absorption Mechanics.md
│   ├── Stop Hunt Mechanics.md
│   ├── Momentum Phases.md
│   ├── Cycle Integration.md
│   ├── Execution Framework.md
│   └── Quick Reference Card.md
├── 07 Concepts & Definitions /
│   ├── BSL.md
│   ├── SSL.md
│   ├── Stop Hunt.md
│   ├── Absorption.md
│   ├── Compression Phase.md
│   ├── Expansion Phase.md
│   ├── Kill Zones.md
│   └── Confluence Stack.md
├── 08 Playbooks /
│   ├── Bullish Stop Hunt Playbook.md
│   ├── Bearish Stop Hunt Playbook.md
│   └── Confluence Stack Playbook.md
├── 09 Metrics & Reviews /
│   ├── Win Rate Tracker.md
│   ├── R-Multiple Log.md
│   ├── Weekly Review Template.md
│   └── Monthly / Quarterly Review Templates.md
└── 10 Resources /
    ├── Templates /
    ├── Glossary.md
    └── Config /
```

- Folders 01–04 are execution-focused.
- Folder 05 is the research and learning engine.
- Folder 06 contains Trading Brain system logic.
- Folders 07–09 support definitions, playbooks, and performance reviews.

## Research Knowledge Graph Workflow (Using Obsidian + Claude)
The "Using Obsidian and Claude to Learn a Subject" method is adopted as the standard way to learn and maintain any trading-related knowledge.
It is implemented inside `05 Research Knowledge Base/` and wired into weekly and daily workflows.

### 5.1 Concept Notes (Atomic Knowledge Units)
Location: `05 Research Knowledge Base/Concepts/`

Each major idea (e.g., "Bullish Stop Hunt", "ATR-Based Stops", "Daily Loss Limits") is captured as a single concept note using this frontmatter:

```markdown
---
concept: [name]
subject: [subject area, e.g., P_115, AJZ-Risk, Macro]
source: [where this came from]
date-added: YYYY-MM-DD
review-due: YYYY-MM-DD
connections: []
mastery: 0
---
```

Sections:
- What It Is
- Why It Matters
- The Mechanism
- Where It Breaks Down
- Connections
- The Test

Rules:
- One idea per note.
- "What It Is" and "Why It Matters" must be written in your own words before asking Claude for help.

### 5.2 Connection Notes (Non-Obvious Relationships)
Location: `05 Research Knowledge Base/Connections/`

At the end of a study or review session, run a connection protocol:

- Identify at least two existing concepts that relate to the new concept.
- Create or update a connection note describing the non-obvious relationship (e.g., "Phase 2 Liquidity Hunts" ↔ "Common Stop Placement Mistakes").
- Update the `connections` array in each concept frontmatter so links are bidirectional.

### 5.3 Active Recall Questions
Location: `05 Research Knowledge Base/Questions/`

Claude generates active recall questions instead of definitions:

- Never ask "What is X?".
- Prefer scenario, prediction, and connection questions.
- Each daily or weekly session pulls from:
  - Concepts added in the last 7 days.
  - Concepts with `mastery < 3`.
  - At least one connection question.

Daily notes and Weekly Review notes should embed a small block of recall questions, sourced from the Questions folder.

### 5.4 Spaced Review Scheduling
Location: `05 Research Knowledge Base/Reviews/`

Review intervals are based on Ebbinghaus-style spacing:

- 1, 3, 7, 14, 30, 60 days.

Workflow:
- Each concept has a `review-due` date and `mastery` score.
- Review sessions list concepts that are due and generate harder questions for higher-mastery topics.
- After each session, update `review-due` and `mastery` based on performance.

### 5.5 Synthesis Notes
Location: `05 Research Knowledge Base/Synthesis/`

Every 1–2 weeks per subject (e.g., P_115, AJZ risk, macro context), create a synthesis note:

- Summarize patterns across multiple concepts.
- Document the deepest connection discovered.
- Capture one predictive test or rule you will apply next week.
- Capture gaps or confusion that still need clarification.

These notes prove that understanding is improving, not just the volume of notes.

### 5.6 Skills and Claude Prompts
Location: `05 Research Knowledge Base/Skills/`

This folder stores Claude-facing skill notes such as:

- `concept-add.md` – instructions for helping you build a concept note.
- `connection-find.md` – instructions for finding non-obvious links.
- `recall-generate.md` – instructions for generating high-quality questions.
- `review-schedule.md` – instructions for selecting due concepts and updating review dates.

These skills are called from daily notes or Weekly Review notes via prompts and MCP tools.

## Integration with P_800 Automation
P_800 owns automation and templates across the vault.

P_800 responsibilities related to research:
- Provide commands/templates to create new concept notes with the standard frontmatter and section layout.
- Automatically insert links to relevant Trading Brain and AJZ notes when a concept is clearly tied to execution or risk.
- Generate daily and weekly recall blocks in the Daily Note and Weekly Review using the Questions and Reviews folders.

## Integration with Trading Brain / P_115
The Trading Brain defines liquidity theory, stop-hunt mechanics, phases, and execution framework.

Integration rules:
- Each Trading Brain core file (e.g., Liquidity Theory, Stop Hunt Mechanics) should have matching concept notes under `Concepts/` for key sub-ideas.
- Trade Setup and Trade Journal notes should link to relevant concept notes to make reviews easier.
- Weekly Reviews should include at least one synthesis note that ties Trading Brain concepts to actual trades taken.

## Integration with AJZ Risk Plan
The AJZ risk plan defines account-level risk parameters and process goals.

Integration rules:
- Create concept notes for each major risk rule (risk per trade, loss limits, stop-trading triggers, three-gate sizing).
- When a rule is violated, update mastery for the corresponding concept and add or refine recall questions.
- Weekly Review Templates should prompt you to:
  - List any risk violations.
  - Link them to concepts.
  - Capture learning and planned behavior changes.

## Knowledge Capture Workflow (Summary)
1. Capture a new idea in a concept note.
2. Link it to at least two existing concepts.
3. Generate at least one active recall question.
4. Set or update its `review-due` date based on mastery.
5. Periodically write synthesis notes that combine related concepts and recent trades.

## Version Note
- v0.1 = initial merged architecture draft.
- v0.2 = research-aware integrated architecture with cleaner folder structure and a concrete Obsidian + Claude learning workflow.
