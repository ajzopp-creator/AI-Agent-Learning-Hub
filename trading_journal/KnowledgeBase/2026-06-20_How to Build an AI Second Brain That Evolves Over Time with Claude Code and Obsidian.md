---
title: "How to Build an AI Second Brain That Evolves Over Time with Claude Code and Obsidian"
source: "https://www.mindstudio.ai/blog/ai-second-brain-claude-code-obsidian-architecture"
author:
  - "[[MindStudio Team]]"
date: "2026-06-20"
published: 2026-04-03
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
  - "MindStudio"
sector:
origin:
review_status: reviewed-relevant
review_date: 2026-08-11
disposition: "Informs P_400/P_020/Obsidian performance-data architecture initiative (vault-as-memory-substrate, layered memory, feedback loops); not tied to a specific trading system"
---
## The Problem with Static Knowledge Systems

Most productivity systems have a fundamental flaw: they’re passive. You dump information in, and it sits there. Your notes from six months ago don’t connect to what you’re learning today. Your AI assistant starts fresh every conversation. The knowledge you’ve accumulated doesn’t actually work for you — it just accumulates.

Building an AI second brain with Claude Code and Obsidian changes that. The architecture covered here gives you a system that reads, writes, and reasons about your notes — and gets smarter over time by scheduling its own reflection cycles, managing discrete capabilities as skills, and maintaining layered memory that persists across sessions.

This isn’t a simple ChatGPT-over-your-notes setup. It’s a full architecture for a self-improving knowledge agent.

---

## What This Architecture Actually Does

Before getting into implementation, it’s worth being clear about what you’re building and what makes it different from simpler setups.

### The Core Idea

Your second brain is a Claude-powered agent that:

- Reads and writes to your Obsidian vault as its long-term memory store
- Maintains multiple memory layers (working, episodic, semantic) with different lifespans and purposes
- Runs scheduled “heartbeat” cycles to consolidate, synthesize, and surface insights without you asking
- Manages a modular skills system that lets it acquire new capabilities over time
- Supports multiple clients — CLI, web, API — without duplicating logic

## Plans first. Then code.

PROJECTYOUR APP

SCREENS12

DB TABLES6

BUILT BYREMY

1280 px · TYP.

yourapp.msagent.ai

A · UI · FRONT END

Remy writes the spec, manages the build, and ships the app.

The Obsidian vault isn’t just a place to store outputs. It’s the agent’s actual memory substrate. Claude reads vault structure, understands your note-linking patterns, and writes back to the vault in ways that maintain that structure.

### Why Claude Code Specifically

Claude Code (Anthropic’s CLI agent) is well-suited for this because it can execute file operations, run shell commands, and call external APIs natively. It’s designed for agentic, multi-step tasks — not just single-turn conversations.

Combined with the Model Context Protocol (MCP), Claude Code can interact with your Obsidian vault, manage schedules, and call external tools in a way that lighter integrations can’t match.

---

## Setting Up Obsidian as Your Memory Substrate

The Obsidian vault is the foundation. How you organize it determines how well the agent can reason about your knowledge.

### Vault Structure for Agent Compatibility

Create a dedicated structure that separates agent-managed content from your personal notes:

```plaintext
vault/
├── _agent/
│   ├── memory/
│   │   ├── working/          # Short-term, session-scoped
│   │   ├── episodic/         # Timestamped experience records
│   │   └── semantic/         # Distilled concepts and facts
│   ├── skills/               # Skill definitions and metadata
│   ├── heartbeat/            # Scheduled task logs and outputs
│   └── context/              # Active context windows
├── notes/                    # Your regular notes
├── projects/                 # Project-specific knowledge
└── inbox/                    # Unprocessed capture
```

This separation is important. The agent needs predictable paths for reading and writing. If it’s hunting through an unstructured vault to find its own memory, you’re burning context on navigation.

### Enabling the Obsidian Local REST API

Install the [Obsidian Local REST API plugin](https://github.com/coddingtonbear/obsidian-local-rest-api) to expose your vault over HTTP. This lets Claude Code read and write notes programmatically without needing to simulate keyboard input or use fragile file watchers.

Configure it with:

- A local API key for authentication
- HTTPS enabled (even for localhost)
- CORS settings that allow your agent’s origin

With this running, your agent can do things like:

```bash
# Read a note
GET /vault/notes/weekly-review-2024-11.md

# Create or update a note
PUT /vault/_agent/memory/semantic/productivity-patterns.md

# Search across the vault
POST /vault/search/simple?q=meeting+notes+Q4
```

### Linking Conventions That Agents Understand

Use consistent frontmatter so the agent can filter and reason about notes without reading full content:

```yaml
---
type: concept | project | person | meeting | resource
tags: [productivity, ai, research]
created: 2024-11-15
last-reviewed: 2024-11-20
importance: high | medium | low
agent-written: false
---
```

The `agent-written` flag lets you distinguish what the system generated versus what you wrote. This matters for trust calibration — you’ll want to review agent-synthesized content differently than your own notes.

---

## Building the Memory Layer Architecture

Memory management is where most “AI over notes” projects fall apart. They use a flat vector store and call it done. A proper second brain needs multiple memory types that serve different purposes.

### Layer 1: Working Memory

Working memory is session-scoped context. When you start a conversation or task, the agent loads relevant working memory into its context window and writes updates back at the end of the session.

Implement this as a set of small markdown files under `_agent/memory/working/`:

```markdown
# Working Context — 2024-11-21

## Active Focus
- Finishing Q4 planning document
- Reviewing project Alpha proposal

## Recent Decisions
- Decided to postpone vendor evaluation until January
- Chose framework B over A based on team capacity

## Open Threads
- [ ] Follow up with Sarah on budget numbers
- [ ] Review competitor analysis draft
```

## Other agents ship a demo. Remy ships an app.

UI

React + Tailwind ✓ LIVE

API

REST · typed contracts ✓ LIVE

DATABASE

real SQL, not mocked ✓ LIVE

AUTH

roles · sessions · tokens ✓ LIVE

DEPLOY

git-backed, live URL ✓ LIVE

Real backend. Real database. Real auth. Real plumbing. Remy has it all.

The agent reads this at session start, appends to it during the session, and archives it to episodic memory at the end. Working memory files older than 48 hours get automatically moved — they’re no longer “working.”

### Layer 2: Episodic Memory

Episodic memory stores time-stamped records of what happened: conversations, decisions, observations. Think of it as a structured journal that the agent maintains.

Each episode gets its own file:

```markdown
# Episode: 2024-11-21T14:32:00

## Context
Reviewed Q4 planning draft with user. Identified three gaps in resource allocation section.

## Observations
- User tends to underestimate design time in estimates
- Q4 priorities shifted from last month — AI tooling now ranked higher
- User expressed frustration with async communication on Project Alpha

## Patterns
- Second time this month user revised timeline downward
- Consistent preference for written briefs over verbal summaries

## Links
- [[projects/q4-planning]]
- [[people/sarah]]
```

The agent builds pattern recognition over time by reviewing episodic memory during heartbeat cycles. This is how it learns your working style.

### Layer 3: Semantic Memory

Semantic memory is distilled knowledge — facts, concepts, preferences, and rules extracted from episodic records. It’s the compressed, structured version of what the agent has learned.

```markdown
# User Preference: Estimation Style

## Fact
User consistently underestimates design and review time in project plans.

## Evidence
- 3 instances in Q3 where design phases ran over by 30-40%
- Explicit acknowledgment in episode 2024-10-15

## Recommendation
When reviewing estimates, flag design phases and suggest adding 40% buffer.

## Confidence: High
## Last Updated: 2024-11-20
```

Semantic memory gets written by the heartbeat process, not directly during sessions. It’s the output of reflection — slow, deliberate synthesis rather than real-time capture.

---

## Implementing the Heartbeat Scheduler

The heartbeat is what makes the system self-improving. It’s a scheduled process that runs without user intervention and does the work of reflection, synthesis, and insight generation.

### What a Heartbeat Cycle Does

A standard heartbeat cycle (running, say, every morning at 6 AM) should:

1. **Archive stale working memory** — Move files older than 48 hours to episodic
2. **Review recent episodes** — Read the last N episodic entries
3. **Extract patterns** — Identify recurring themes, decisions, or observations
4. **Update semantic memory** — Write or update semantic notes with new insights
5. **Surface insights** — Create a daily briefing note in your inbox
6. **Prune outdated data** — Flag or archive semantic notes that haven’t been updated in 90+ days

### Setting Up the Scheduler

Use a cron job or a process manager like `pm2` to run the heartbeat:

```bash
# crontab entry — runs daily at 6 AM
0 6 * * * /path/to/run-heartbeat.sh
```

The heartbeat script calls Claude Code with a specific system prompt and task context:

```bash
#!/bin/bash
claude --system-prompt-file /path/to/heartbeat-system.md \
       --task "Run daily heartbeat cycle" \
       --context-file /path/to/heartbeat-context.md \
       --no-interactive
```

The system prompt for the heartbeat is distinct from your regular assistant prompt. It should emphasize:

- Pattern recognition over task completion
- Conservative writes — only update semantic memory when confidence is high
- Clear attribution — always cite which episodes support a new semantic note
- Minimal footprint — don’t create notes that don’t add new information

### Weekly Deep Review

Beyond the daily heartbeat, run a longer weekly cycle that looks back over a month of episodic memory:

- Identify projects that are drifting from original goals
- Surface connections between notes that aren’t explicitly linked
- Generate a weekly summary that goes into your inbox
- Update your “user model” — a semantic note about your own working patterns and preferences

This deeper cycle is where the most valuable synthesis happens. It’s the equivalent of a weekly review in GTD, but automated and grounded in your actual behavior rather than what you planned to do.

---

## Building the Skills Management System

Skills let you extend what the agent can do without rebuilding it from scratch. Each skill is a discrete capability with a defined interface, and the agent can call skills based on context.

### Skill Structure

Store each skill as a markdown file in `_agent/skills/`:

```markdown
# Skill: Web Research

## Purpose
Search the web and summarize findings into a structured note.

## Trigger Conditions
- User asks about current events or recent data
- Working memory contains flagged research needs
- Topic isn't covered in semantic memory

## Input
- search_query: string
- depth: shallow | deep
- output_path: vault path for result

## Output
Creates a note at output_path with:
- Summary of findings
- Key facts with source attribution
- Related vault notes (auto-linked)

## Implementation
Calls web search API, fetches top 3-5 results, synthesizes.

## Last Updated: 2024-11-15
## Status: active
```

The agent reads skill files at startup and knows what it can do. When a task matches a skill’s trigger conditions, it invokes the skill rather than trying to improvise.

### Core Skills to Build First

**Note synthesis** — Takes a folder of notes and produces a single summary document. Useful for project close-outs, research consolidation, and meeting prep.

**Context loader** — Given a topic or project name, pulls the relevant notes, people, decisions, and open threads into a single working context document. Speeds up re-engagement after context switching.

**Daily brief generator** — Reads your calendar (if connected), open projects, and recent episodic memory to generate a prioritized daily brief in your inbox.

**Backlink analyzer** — Identifies notes that should be linked but aren’t, based on semantic similarity. Surfaces hidden connections in your vault.

**Stale content detector** — Flags notes that haven’t been updated in a while but are still linked from active projects. Helps maintain note quality over time.

### Skill Versioning

As skills evolve, version them. Don’t overwrite — append a version suffix and keep the old version:

```plaintext
skills/
├── web-research-v1.md
├── web-research-v2.md    ← current
├── note-synthesis-v1.md
```

The agent should always use the highest version of each skill unless you explicitly pin it. This gives you an audit trail when behavior changes.

---

## Supporting Multiple Clients

Once your second brain has solid logic, you’ll want to access it from different contexts — a CLI for focused work, a web interface for quick captures, an API for integrations. The key is keeping the logic in one place and building thin client layers on top.

### Separating Logic from Interface

Create a core agent module that handles:

- Memory operations (read/write to vault)
- Skill invocation
- Context management
- Heartbeat execution
![Hermes Crash Course — free 1-hour live workshop](https://i.mscdn.ai/1b7301c0-de42-4e46-b110-e9c55396e7ca/generated-images/957ba1d7-9c1c-417e-97da-2a97eac46966.png?fm=auto&w=1200)

Then build clients that call this module:

```plaintext
core/
├── memory.js          # All vault read/write operations
├── skills.js          # Skill loader and invoker
├── context.js         # Context window management
├── heartbeat.js       # Scheduled reflection logic

clients/
├── cli/               # Command-line interface
├── web/               # Simple web UI
└── api/               # REST API for external integrations
```

Each client is a thin wrapper. The CLI client reads from stdin and writes to stdout. The web client renders a simple form. The API client exposes POST endpoints. All of them call the same core functions.

### Handling Authentication Across Clients

When the same second brain serves multiple clients — say, you access it from work and personal machines — you need to handle auth without duplicating configuration.

Store credentials and vault connection details in a single config file that all clients reference:

```yaml
vault:
  host: localhost
  port: 27123
  api_key: ${OBSIDIAN_API_KEY}
  base_path: /path/to/vault

claude:
  api_key: ${ANTHROPIC_API_KEY}
  model: claude-opus-4-5

heartbeat:
  schedule: "0 6 * * *"
  deep_review_schedule: "0 9 * * 0"
```

Use environment variables for secrets. Never commit actual keys to your vault or a shared repo.

---

## Where MindStudio Fits Into This Architecture

Building the core architecture above requires Claude Code, some scripting knowledge, and ongoing maintenance. If you want to extend your second brain’s capabilities — especially its ability to trigger actions in external tools — MindStudio’s [Agent Skills Plugin](https://mindstudio.ai/) is a natural fit.

The `@mindstudio-ai/agent` npm SDK lets your Claude Code agent call over 120 pre-built capabilities as simple method calls. Instead of building and maintaining integrations for sending emails, searching the web, posting to Slack, or generating images, you call them directly:

```javascript
import { MindStudioAgent } from '@mindstudio-ai/agent';
const agent = new MindStudioAgent();

// Send a digest email when heartbeat surfaces important insights
await agent.sendEmail({
  to: 'you@example.com',
  subject: 'Weekly Brain Digest',
  body: digestContent
});

// Search the web during a research skill invocation
const results = await agent.searchGoogle({
  query: 'latest research on spaced repetition 2024'
});

// Post a summary to Slack when a project milestone is detected
await agent.postToSlack({
  channel: '#updates',
  message: projectSummary
});
```

The SDK handles rate limiting, retries, and auth — the infrastructure layer your agent shouldn’t have to think about. This lets you focus on the reasoning and memory logic that makes the second brain actually useful, without getting stuck building API wrappers.

For teams who want a no-code path to similar functionality, MindStudio’s visual agent builder can replicate much of this architecture — with native Notion integration, scheduled background agents, and webhook triggers — without writing a line of code. You can [try it free at mindstudio.ai](https://mindstudio.ai/).

---

## Common Mistakes and How to Avoid Them

### Over-capturing Without Reflection

The most common failure mode: you set up the system, it captures everything, but the heartbeat never produces useful synthesis because there’s too much noise.

Fix this by being selective about what goes into episodic memory. Not every task needs an episode. Write episodes for decisions, observations, and patterns — not for routine task completions.

### Context Windows That Grow Without Bound

### Everyone else built a construction worker.We built the contractor.

🦺

CODING AGENT

Types the code you tell it to.  
One file at a time.

🧠

CONTRACTOR · REMY

Runs the entire build.  
UI, API, database, deploy.

If you keep loading more and more context into each session, you’ll hit token limits and the agent will start dropping important information.

Enforce hard limits on context size. Load a summary of semantic memory, not the full files. Use the context loader skill to pull only what’s relevant to the current task.

### Semantic Memory That Drifts From Reality

Semantic memory can become stale. If the agent wrote a note about your project priorities in March, and it’s now November, that note may be actively misleading.

Run a quarterly audit that compares semantic memory against recent episodic records. Flag anything where the semantic note contradicts recent episodes. The agent can do this automatically as part of the deep heartbeat cycle.

### Skills That Are Too Broad

A “do research” skill that tries to handle everything will be unreliable. Better to have five narrow, reliable skills than one broad, unpredictable one.

Keep each skill focused on a single transformation: search → summarize, folder → synthesis, topic → context. Single-responsibility principle applies to agent skills as much as to code.

---

## Frequently Asked Questions

### What is an AI second brain?

An AI second brain is a system that stores, connects, and actively reasons about your personal knowledge — notes, decisions, observations, and preferences — and can surface insights and take actions based on that knowledge without constant prompting. Unlike a static note app, it learns from how you work and adapts its behavior over time.

### Does Claude Code work with Obsidian out of the box?

Not directly. Claude Code can read and write files, but it doesn’t natively understand Obsidian’s vault structure, internal links, or metadata. You need to set up the Obsidian Local REST API plugin and write a connector that translates between Claude Code’s file operations and Obsidian’s API. The architecture in this guide handles that translation layer.

### How is this different from using a vector database for RAG?

RAG (retrieval-augmented generation) over a vector store gives you semantic search — you ask a question, the system finds relevant chunks and feeds them to the model. That’s useful, but it’s reactive and stateless. The architecture here adds active memory management, scheduled reflection, pattern recognition, and skill evolution. The agent isn’t just retrieving information — it’s maintaining an ongoing model of your knowledge and working style.

### How often should the heartbeat run?

For most people, a daily lightweight heartbeat (5-10 minutes) and a weekly deep review (30-60 minutes) works well. Running it too frequently creates noise without enough new data to synthesize meaningfully. Running it too rarely means the episodic memory backlog gets large and synthesis quality drops. Adjust based on how much you’re adding to your vault each day.

### Can I use this with tools other than Obsidian?

The memory layer architecture works with any tool that supports programmatic read/write access. Notion, Roam Research (with its API), or even a local folder of markdown files with a custom search layer can substitute for Obsidian. The key requirements are: structured metadata on notes, full-text search, and an API or file access method that Claude Code can use.

### Is this secure? Can Claude read sensitive notes?

## Remy doesn't build the plumbing. It inherits it.

Other agents wire up auth, databases, models, and integrations from scratch every time you ask them to build something.

WHAT REMY DOESN'T HAVE TO BUILD

200+

AI MODELS

GPT · Claude · Gemini · Llama

✓

1,000+

INTEGRATIONS

Slack · Stripe · Notion · HubSpot

✓

MANAGED DB

AUTH

PAYMENTS

CRONS

Remy ships with all of it from MindStudio — so every cycle goes into the app you actually want.

Claude Code sends note content to Anthropic’s API for processing. If your vault contains sensitive information, you should review Anthropic’s data handling policies and consider which notes you include in the agent’s context. You can exclude folders from agent access in the API configuration — for example, keeping personal or financial notes completely outside the `_agent/` accessible paths.

---

## Key Takeaways

- **Memory architecture matters more than model choice.** Layered memory (working, episodic, semantic) is what separates a genuine second brain from a sophisticated search engine over notes.
- **The heartbeat is the differentiator.** Scheduled reflection cycles are what make the system self-improving rather than static.
- **Skills should be narrow and versioned.** Single-responsibility skills are more reliable and easier to maintain than broad, catch-all capabilities.
- **Separate logic from clients.** Build a core module once, then layer thin clients on top so the system is accessible from wherever you work.
- **Semantic memory needs maintenance.** Without periodic audits, semantic notes drift from reality and start producing bad recommendations.

Building this system takes real effort upfront. But once it’s running, you end up with something fundamentally different from a note app: a knowledge system that observes your patterns, synthesizes insights, and gets more useful the longer you use it.

If you want to add external integrations — email, Slack, search, workflows — without building each one from scratch, [MindStudio’s Agent Skills Plugin](https://mindstudio.ai/) gives your Claude Code agent ready-made capabilities it can call directly. It’s a practical way to extend what your second brain can act on, not just think about.
