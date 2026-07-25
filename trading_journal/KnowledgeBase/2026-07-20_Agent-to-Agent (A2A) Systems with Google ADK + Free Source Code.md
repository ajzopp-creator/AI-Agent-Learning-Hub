---
title: "Agent-to-Agent (A2A) Systems with Google ADK + Free Source Code"
source: "https://aiengineeringinsider.substack.com/p/agent-to-agent-a2a-systems-with-google"
author:
  - "[[AI Engineering Insider]]"
date: "2026-07-20"
published: 2026-07-09
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
sector:
origin:
---
**ebook preview: [preview](https://drive.google.com/file/d/1MDwJdIxqlvdK3Db1gnACbwJWmR-y7R5q/view?usp=sharing)**

**ebook link: [premium guide](https://shop.beacons.ai/aiengineeringinsider/cea258cf-8615-4ae0-b1f0-1fcd347f7cfd)**

**Github repo: [https://github.com/lamhotsiagian/agent-to-agent-adk](https://github.com/lamhotsiagian/agent-to-agent-adk)**

Build multi-agent AI systems that actually ship — and ace the interviews that ask about them.

Single-prompt assistants have hit their ceiling. Production AI now means teams of specialized agents that plan, delegate, coordinate, remember, and act — and engineers who can design those systems are the most sought-after in the industry.

Agent-to-Agent (A2A) AI Systems Design with Google ADK is a build-first engineering guide. Every chapter pairs a deep technical treatment with production-grade code you run immediately in Google ADK’s built-in web UI — entirely on a free local stack (llama3.1 + nomic-embed-text via Ollama). No API keys. No cloud bills. Just working on systems, you can inspect event by event.

![](https://substackcdn.com/image/fetch/$s_!A2p4!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6520175c-91b1-4733-9707-086bad9376bf_1241x1754.jpeg)

## Video demo

![](https://www.youtube.com/watch?v=MqoovEkaGyI)

Inside, you will master:

- **Agent Architecture** — coordinator/specialist hierarchies and routing contracts that don’t misfire
- **Agent Communication** — the A2A protocol: agent cards, JSON-RPC tasks, exposing and consuming remote agents
- **Task Planning & Delegation** — validated plans, plan–delegate–verify pipelines, failure recovery
- **Agent Coordination** parallel fan-out, critic loops with bounded budgets, race-condition-free state
- **Shared Memory**: an embedding-backed team blackboard with provenance and namespaces
- State Management — event-sourced session state, scopes, persistence, and concurrency discipline
- **Tool Orchestration** tool contracts, guardrail callbacks, human-in-the-loop approval
- Plus 110 interview questions with senior-level answers: ten per chapter spanning system design, production operations, and debugging, and a bonus chapter with the top 30 agentic-AI interview questions answered as STAR-format production stories, the way staff engineers actually answer them.

## Setup

```markup
# 1. Local models (Ollama must be running: ollama serve)
ollama pull llama3.1
ollama pull nomic-embed-text

# 2. Python environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 3. Smoke tests (no model calls needed)
pytest tests/ -q

# 4. Launch the web UI
adk web        # http://localhost:8000
```

## How to test each chapter

Pick the chapter agent from the dropdown at

http://localhost:8000

Paste the prompts in order, and check the Events tab (model and tool calls, transfers) and the State tab (session state).

### Ch 1 — ch01\_hello\_a2a

1. Is my local stack healthy? Expect a check\_local\_stack tool call and a report on Ollama and both models.
2. What is the difference between ADK and the A2A protocol? Expect a direct answer with no tool call.

Pass: tool used for stack status, never for conceptual questions.

### Ch 2 — ch02\_agent\_architecture

1. How much is express shipping for a 2.5 kg parcel? Expect a transfer to shipping\_agent and a quote\_shipping call.
2. Where is order 84312? Expect a transfer to orders\_agent and a track\_order call.
3. My delivery arrived broken, order 55110 — I want my money back. Expect a transfer to refunds\_agent; open\_refund\_case returns a case id.
4. Where is order 84312, and how much is express shipping for 2.5 kg? Expect two transfers, handled one concern at a time.

Pass: the coordinator always transfers; each specialist calls only its own tool.

### Ch 3 — ch03\_agent\_communication (two processes)

```markup
# Terminal 1 — start the remote analyst first
./scripts/run_remote_a2a.sh
curl -s http://localhost:8001/.well-known/agent-card.json | head -c 200
# Terminal 2
adk web
```
1. Size the EU market for B2B expense-management SaaS. Expect delegation to remote\_market\_analyst; the task appears in the uvicorn log.
2. Assess the risk of this plan: hire 50 people to build a health-data platform. Expect remote assess\_risk with execution and regulatory risk high.
3. Stop the remote server and repeat prompt 1. Expect a graceful “analyst service is down” message.

Pass: cross-process calls visible on both sides; graceful degradation when the remote agent is unreachable.

### Ch 4 — ch04\_task\_planning

1. Produce a short briefing on migrating our monolith to microservices.
2. Watch the State tab: plan:tasks, then plan:results filling per task id, then verification\_report with a GO or NO-GO verdict.

Pass: submit\_plan accepted; every task id gets a record\_result; verifier runs last.

### Ch 5 — ch05\_agent\_coordination

1. Review this proposal: store all user passwords in a shared spreadsheet to simplify onboarding. Expect three reviewers running in parallel, a synthesis step, one or two editor/critic rounds, then approve\_assessment ends the loop.

Pass: review\_security, review\_cost and review\_ux are three distinct state keys; the loop never exceeds 3 iterations.

### Ch 6 — ch06\_shared\_memory

Multi-turn, same session:

1. We chose Postgres over MongoDB for the ledger because of transactional guarantees.
2. Our p99 latency target is 300 ms.
3. What database did we pick, and why? Expect recall hits with scores; the answer cites the author agent.
4. What did we decide about caching? Expect empty hits and an honest “no record” answer.

Pass: answers come only from retrieved hits; empty memory produces an admission, not a guess.

### Ch 7 — ch07\_state\_management

Multi-turn, same session:

1. I prefer aisle seats and vegetarian meals. Expect user:pref\_\* keys to appear.
2. Plan a trip to Lisbon from 2026-09-02 to 2026-09-09, budget 1200. Expect trip\_draft to fill field by field.
3. Book it. Expect validate\_trip then book\_trip in the same turn; user:trip\_history grows.
4. Book a trip to Oslo ending 2026-08-01 starting 2026-08-10. Expect validation to fail and booking refused.
5. In a new session: What do you know about my preferences? Expect user: preferences to survive; the trip draft does not.

Pass: step 4 never books; step 5 proves the scope model.

### Ch 8 — ch08\_tool\_orchestration

Multi-turn, same session:

1. Checkout is erroring — diagnose and fix. Expect metrics fetched; restart only if thresholds are breached.
2. Payments is erroring — diagnose and fix. Expect the restart to be blocked by the guardrail; the agent asks for approval.
3. Approved. Expect grant\_restart\_approval, a successful retry, and incident:timeline growing.
4. Write the postmortem. Expect the postmortem\_writer tool to return a structured postmortem.

Pass: payments and auth can never be restarted without step 3; the approval does not survive into a new invocation.

## Troubleshooting

- “model not found”: run ollama pull llama3.1 (tag must match ADK\_CHAT\_MODEL).
- Agent card fetch fails (ch03): start./scripts/run\_remote\_a2a.sh first.
- Slow first response: Ollama loads the model into memory on the first call.
- Empty memory hits (ch06): run ollama pull nomic-embed-text and store facts before asking questions.

Link and apply coupon code 100 % Free: [A2AFREE](https://shop.beacons.ai/aiengineeringinsider/cea258cf-8615-4ae0-b1f0-1fcd347f7cfd?)