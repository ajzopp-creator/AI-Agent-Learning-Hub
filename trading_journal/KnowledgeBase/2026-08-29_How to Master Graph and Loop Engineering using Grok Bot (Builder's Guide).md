---
title: "How to Master Graph and Loop Engineering using Grok Bot (Builder's Guide)"
source: "https://x.com/Av1dlive/status/2092622516544270781"
author:
  - "[[@Av1dlive]]"
date: "2026-08-29"
published: 2026-08-26
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
  - "X (formerly Twitter)"
sector:
origin:
---
![Image](https://pbs.twimg.com/media/HQp5-J2bwAAUGws?format=jpg&name=large)

i wrote the A-Z blueprint for mastering loop and graph engineering using Grok bot.

not another swarm of bots... a system that decides what work matters, what agents may do, and what they must leave behind.

Most agent systems do not fail because the model is weak.

They fail because no one owns the return path, the shared state, or the approval boundary.

The fix is a control system:

- Grokbot owns the outer loop.
- Kimi Code with K3 performs the deep pass.
- A knowledge graph stores source-backed claims.
- A DAG controls execution order.
- A context pack limits drift.
- Two policy layers control tool use.
- An append log records each transition.

This article shows how to build that system.

I use **Grokbot** as shorthand for the official **Grok Bot** product.

# First, understand the product boundary

Grok Bot provides persistent Bots, a shared cloud computer, browser access, a filesystem, a terminal, handoffs, skills, routines, and approval controls. Read the official Grok Bot overview.

Kimi Code provides K3, custom agents, sub-agents, Agent, AgentSwarm, MCP, permission rules, hooks, sessions, and a programmatic SDK. Read the Kimi Code model guide and agent guide.

There is no documented native Grokbot-to-Kimi handoff.

There is no documented native knowledge-graph engine in Grokbot.

There is no documented arbitrary DAG scheduler in Kimi Code.

The file bridge, graph store, loop controller, and DAG runner below are proposed integration patterns.

Grok Bot does not document K3 selection or a native Kimi integration. Its managed architecture controls model selection and failover. See Grok Bot team architecture.

Kimi Code runs on the host. K3 inference normally runs on Moonshot's hosted service or API.

Moonshot publishes open K3 weights. A self-hosted deployment needs large accelerator infrastructure. The official vLLM recipe lists eight high-memory accelerators for a validated deployment. See the K3 model card and vLLM deployment recipe.

Do not promise full system control.

Build **bounded operational control** with least privilege, explicit approvals, stored evidence, and live verification.

# 1\. Loops: make the return path explicit

![Image](https://pbs.twimg.com/media/HQpRbm3bAAArzma?format=jpg&name=large)

A useful loop is not an instruction to keep going.

A useful loop has an owner, a worker, a verifier, and a stop rule.

**Grokbot owns the outer loop. Kimi Code with K3 completes one bounded inner round.**

## Use Grokbot alone first

Create three Bots:

- Coordinator owns the result.
- Worker produces one candidate.
- Verifier checks fixed acceptance tests.

Put the Bots in one group chat.

Grok Bot supports groups with two to six Bots. It also supports asynchronous Bot-to-Bot messages that wake the receiver. See Grok Bot collaboration.

Use this kickoff prompt:

```text
@Coordinator own this job from start to finish.

Use this loop:

1. Create one stable job_id from the source event.
2. Ask @Worker for one candidate.
3. Ask @Verifier for PASS, REVISE, or BLOCKED.
4. If the result is REVISE, send only failed checks to @Worker.
5. Stop after three rounds.
6. Stop when two rounds produce the same fingerprint.
7. Stop when a required source is missing or stale.
8. Keep every external action in draft mode.
9. Show the exact target and payload before approval.
10. Append one event after each handoff.
```

Test the loop with safe data.

Save the stable method as a skill. Then assign the skill to a routine.

Grok Bot documents scheduled and supported event routines. It also recommends idempotent retries, stale-data rules, and approval before consequential actions. See skills and routines.

## Use Kimi Code with K3 for one bounded round

Install Kimi Code on macOS or Linux:

```sh
curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash
kimi --version
kimi
```

On Windows, install Git for Windows first. Kimi Code uses Git Bash on its first launch.

Then use the official PowerShell installer:

```powershell
irm https://code.kimi.com/kimi-code/install.ps1 | iex
```

Then run:

```text
/login
/model
```

Select the K3 alias shown by /model.

The current documentation uses kimi-code/k3 in configuration examples. See Kimi Code installation and model configuration.

Create a narrow custom agent:

Save it as \<project-root>/.kimi-code/agents/loop-worker.md.

```markdown
---
name: loop-worker
description: Produces one bounded handoff result
tools:
  - Read
  - Grep
  - Glob
  - Agent
  - AgentSwarm
subagents:
  - explore
---

${base_prompt}

Run one round only.

Read the request packet and the prior verifier result.

Use AgentSwarm only for independent checks.
Use no more than four swarm items.

Do not perform an external action.
Do not run shell commands.
Do not edit files.

Return one JSON object with:
job_id, round, status, summary, evidence,
failed_checks, next_step, and requires_human_approval.

Do not compute the output fingerprint.
The bridge computes it after validation.
```

This profile excludes Bash, Write, Edit, and write-capable MCP tools.

That limit matters in unattended mode.

kimi -p uses automatic permission handling. It does not stop for an interactive ask decision.

Static deny rules and narrow tool lists remain the security boundary in print mode. See the kimi command reference.

Run one round:

```sh
PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"
JOB_ID="${JOB_ID:-demo-001}"
cd "$PROJECT_ROOT"

kimi \
  -m kimi-code/k3 \
  --agent-file .kimi-code/agents/loop-worker.md \
  -p "Read runs/${JOB_ID}/task.json and runs/${JOB_ID}/verdict.json when present. Run one round." \
  --output-format stream-json
```

stream-json is an event stream.

Your bridge must extract the final assistant text. It must also validate the returned JSON before the next step.

The bridge then writes the validated object to runs/<job\_id>/candidate.json.

Use this bridge contract:

- Start kimi -p as a child process.
- Set a wall-clock timeout and terminate the process on expiry.
- Read standard output as JSONL.
- Retry only timeouts, rate limits, transport failures, and service-unavailable errors.
- Permit two retries with exponential backoff.
- Keep the same round key for every retry attempt.
- Block on schema, policy, authentication, and other nonzero failures.
- Extract final assistant text through a release-specific event adapter.
- Parse the text as JSON and validate every required field.
- Remove job\_id, round, and any model-supplied fingerprint from the semantic payload.
- Serialize the semantic payload as RFC 8785 canonical JSON.
- Store its SHA-256 digest as output\_fingerprint.
- Write runs/<job\_id>/candidate.tmp, flush it, and rename it to candidate.json in the same directory.
- Append one sanitized run event after the atomic rename.

Pin the Kimi Code release used by the adapter.

Test the adapter against a recorded event stream before unattended use.

## Add Kimi Code with K3 to the Grokbot computer

![Image](https://pbs.twimg.com/media/HQpVUnzasAAD7dM?format=jpg&name=large)

Grok Bot provides a managed Linux computer and a durable /workspace project area. All Bots for one user share that computer. See the computer guide.

Give Grokbot this setup prompt:

```text
Open the computer terminal.

Use /workspace/grok-kimi as the project directory.

Install Kimi Code with Moonshot's official Linux installer.

Run kimi --version.

Show the version and installation path.

Do not start authentication.
Do not change system packages.
Stop if the installer requires root access.
```

Complete /login yourself.

Do not paste a token into a Bot message.

Keep requests, evidence, results, and logs under /workspace.

Manually installed packages can disappear after a computer rebuild. Durable project files should remain under /workspace. See Grok Bot computer recovery guidance.

## Build the automatic handoff contract

![Image](https://pbs.twimg.com/media/HQpV7gAaAAABfVX?format=jpg&name=large)

Use this run layout:

```text
/workspace/grok-kimi/
├── AGENTS.md
├── .kimi-code/
│   └── agents/
│       └── loop-worker.md
├── handoffs/
│   ├── inbox/
│   └── outbox/
├── runs/
│   └── <job_id>/
│       ├── task.json
│       ├── context.md
│       ├── candidate.json
│       ├── evidence.json
│       ├── verdict.json
│       └── events.jsonl
└── effects/
    └── <idempotency_key>.json
```

Use one stable key for each round:

```text
job_id + round + input_sha256
```

Use a separate key for the final external effect:

```text
job_id + ":commit"
```

This separation helps detect retries. It does not make an external effect idempotent by itself.

Before an external effect, atomically claim the key or pass it to a provider that supports idempotency.

After approval, execute once, verify the live result, store its receipt, and only then write the completion marker.

On resume, reconcile every claimed effect before another attempt.

Retry a missing result automatically only when the provider accepts the same idempotency key.

Otherwise, stop for human reconciliation.

## Grokbot coordinator prompt

```text
You are the outer-loop coordinator.

Read the current task envelope and prior verdict.

Do one loop round.

Use Kimi only for planning, code, and review.
Use Grokbot tools for browser, connector, and computer work.

Write evidence before a status change.

Stop on:
- DONE
- BLOCKED
- APPROVAL_REQUIRED
- round 3
- repeated output fingerprint
- missing or stale source data

Never send, publish, purchase, delete, change permissions,
or change production without approval.

Append one sanitized record to runs/<job_id>/events.jsonl.
```

## Kimi worker prompt

```text
You are the worker inside a Grokbot-controlled loop.

Read AGENTS.md, the task envelope, and prior evidence.

Plan only the next safe step.

Use one Agent for one specialist task.

Use AgentSwarm only for two or more independent items.
Give each sub-agent all required facts and file paths.

Do not start another outer loop.
Do not contact the user.
Do not perform an external action.

Return:
- status: CANDIDATE, BLOCKED, or NEEDS_APPROVAL
- evidence for each claim
- failed acceptance checks
- the smallest next change

Omit output_fingerprint.

The bridge adds the output fingerprint after validation.

Stop after this response.
```

Kimi sub-agents use isolated contexts.

Each task must include its goal, inputs, constraints, acceptance tests, file paths, and output contract. See Kimi agents and sub-agents.

## Automatic loop logic

```text
job_id = stable_id(source_system, source_event_id)

if completion_marker(job_id) exists:
    return DUPLICATE

effect = read_effect_record(job_id + ":commit")

if effect.status == CLAIMED:
    reconcile the target against live provider state

    if the effect already happened:
        store the receipt and write the completion marker
        return RECOVERED

    if the provider supports the same idempotency key:
        resume with that key
    else:
        stop as HUMAN_RECONCILIATION

for round in 1..3:
    write runs/<job_id>/task.json with round and input_sha256

    run one Kimi round
    validate the final result
    fingerprint = bridge_sha256(canonical_semantic_payload)
    append the result to runs/<job_id>/events.jsonl

    ask Grokbot to verify acceptance tests

    if verdict == PASS and no external effect is required:
        write completion marker with verified artifact hashes
        stop

    if verdict == PASS and an external effect is required:
        request approval with the exact target and payload
        atomically claim the external idempotency key
        execute once with provider idempotency when available
        verify live state and store the provider receipt
        write completion marker with the receipt hash
        stop

    if verdict == BLOCKED:
        stop

    if fingerprint == prior_fingerprint:
        stop as NO_PROGRESS

    send only failed checks into the next round

stop as MAX_ROUNDS
```

Do not count a transient retry as a new round.

A retry repeats the same request.

A new round must contain new verifier evidence.

## Choose the correct swarm

Kimi Code AgentSwarm supports up to 128 sub-agents in one tool call.

The managed K3 Swarm product documents up to 300 sub-agents and more than 4,000 tool calls.

These are different products and limits. See the Kimi Code tool reference and K3 Agent Swarm guide.

Start with four concurrent workers.

```sh
export KIMI_CODE_AGENT_SWARM_MAX_CONCURRENCY=4
```

Increase the limit only after the source systems and approval flow remain stable.

# 2\. Graphs: separate memory from execution

![Image](https://pbs.twimg.com/media/HQpRixCawAE5kIe?format=jpg&name=large)

A knowledge graph stores the system's source-backed working knowledge.

A directed acyclic graph encodes nodes and dependencies.

The run's state.json stores status, attempts, and readiness.

Do not mix these two responsibilities.

**The knowledge graph stores source-backed claims. The DAG defines order. The state file records progress.**

## Build a knowledge graph on the Grokbot computer

Grokbot does not document a native knowledge-graph engine.

Build a file-backed graph under /workspace.

```text
/workspace/graphops/
├── kg/
│   ├── schema.json
│   ├── nodes.jsonl
│   ├── edges.jsonl
│   ├── sources.jsonl
│   ├── events.jsonl
│   ├── inbox/
│   └── snapshots/
├── dag/
│   └── pipeline.yaml
├── runs/
└── artifacts/
```

Use JSONL for the first version.

It is easy to inspect, append, diff, hash, and move between both harnesses.

A node stores an entity or claim:

```json
{"id":"claim:kimi-swarm","kind":"claim","label":"Kimi Code includes AgentSwarm","source_ids":["src:kimi-tools"],"status":"verified","rev":1}
```

An edge stores a typed relation:

```json
{"id":"edge:1","from":"product:kimi-code","type":"DOCUMENTS","to":"claim:kimi-swarm","source_ids":["src:kimi-tools"],"confidence":1.0,"observed_at":"2026-08-26T00:00:00Z","rev":1}
```

A source record stores provenance:

```json
{"id":"src:kimi-tools","url":"https://www.kimi.com/code/docs/en/kimi-code-cli/reference/tools.html","retrieved_at":"2026-08-26T00:00:00Z","sha256":"<content-hash>"}
```

Use these minimum fields:

- id: stable identifier.
- kind or type: controlled category.
- source\_ids: evidence for the record.
- status: proposed, verified, rejected, or superseded.
- rev: monotonic revision.
- confidence: only for inferred relations.
- observed\_at: observation time.
- valid\_from and valid\_to: optional validity bounds.

Use one writer Bot for the authoritative graph.

Other Bots write proposed patches to kg/inbox/.

This rule prevents concurrent writers from corrupting graph state.

## Grokbot graph setup prompt

```text
Create these durable directories:

/workspace/graphops/kg/inbox
/workspace/graphops/kg/snapshots
/workspace/graphops/dag
/workspace/graphops/runs
/workspace/graphops/artifacts

Keep all durable files under /workspace/graphops.

Use JSONL, Markdown, and SHA-256 manifests.
Do not install a graph database yet.

Return the created paths and an action log.
Do not change an external system.
```

## Knowledge Steward prompt

```text
You are the Knowledge Steward.

The authoritative graph is in /workspace/graphops/kg.

For each proposed fact:

1. Find or create its source record.
2. Use a stable ID.
3. Reject duplicate nodes.
4. Require source_ids for every verified claim.
5. Require source_ids for every evidence-bearing relation.
6. Mark uncertain relations as proposed.
7. Append the mutation to events.jsonl.
8. Never delete history.
9. Append a tombstone or SUPERSEDES relation.
10. Accept patches only from kg/inbox.
11. Create a snapshot and SHA-256 manifest before Kimi runs.

Return changed IDs, source IDs, and unresolved conflicts.
```

An Obsidian-style vault can become a human view.

Create one Markdown page per node. Use YAML properties and \[\[wikilinks\]\] for relations.

Keep JSONL as the source of truth.

The current Grok Bot documentation does not name Obsidian as a built-in integration.

## Build a DAG in Kimi Code

![Image](https://pbs.twimg.com/media/HQpVbjUbUAAMAx9?format=jpg&name=large)

Kimi Code does not document an arbitrary project DAG format.

Define your own contract. Then use Agent and AgentSwarm to run the ready frontier.

```yaml
version: 1
input_snapshot: kg/snapshots/<sha256>.json
max_retries: 2

nodes:
  - id: observe
    needs: []
    owner: grokbot.researcher
    output: runs/$RUN/observations.json
    check: valid_json

  - id: plan
    needs: [observe]
    owner: kimi.root
    model: k3
    output: runs/$RUN/plan.json
    check: valid_json

  - id: research
    needs: [plan]
    owner: kimi.agent
    output: runs/$RUN/research.json
    check: source_ids_present

  - id: compare
    needs: [plan]
    owner: kimi.agent
    output: runs/$RUN/compare.json
    check: source_ids_present

  - id: review
    needs: [research, compare]
    owner: kimi.root
    model: k3
    output: runs/$RUN/review.json
    check: verdict_pass

  - id: act
    needs: [review]
    owner: grokbot.executor
    approval: external_effect
    output: runs/$RUN/receipt.json
```

This YAML is your contract.

It is not a built-in Kimi format.

## Grokbot DAG-dispatcher prompt

```text
You are the outer DAG dispatcher and the only state.json writer.

Read dag/pipeline.yaml and the immutable graph snapshot.

Before execution:

1. Reject duplicate node IDs.
2. Reject missing dependency IDs.
3. Reject self-dependencies.
4. Run a topological check.
5. Stop when a cycle exists.

During execution:

1. Load runs/<run_id>/state.json.
2. Compute the ready frontier.
3. Route grokbot.* owners to the named Grokbot Bot.
4. Route kimi.* owners through the Kimi bridge.
5. Never ask Kimi to dispatch a Grokbot node.
6. Give each worker a complete task packet.
7. Require node_id in every result.
8. Run the node's declared check before success.
9. Hash and persist a valid output before state changes.
10. Retry only retryable failures up to max_retries.
11. Block descendants after a permanent parent failure.
12. Pause before a node with approval: external_effect.
13. Append one event after each state transition.
14. Unlock a child only after all parents succeed.

Do not merge the knowledge graph.

Return a candidate patch, evidence, validation result,
and final DAG state.
```

## Kimi frontier-controller prompt

```text
You are the Kimi root for ready kimi.* nodes only.

Use AgentSwarm for two or more independent ready nodes.
Use Agent for one ready node.

Give each worker the complete node contract,
snapshot hash, inputs, check, and output path.

Do not run grokbot.* nodes.
Do not write global state.json.
Do not perform an external effect.

Return one result packet per node.
Include node_id, status, evidence, output path,
check result, and error class.
```

Use these states:

```text
pending → running → succeeded
                  ↘ failed → pending
                           ↘ blocked
```

Persist a compact state record:

```json
{"run_id":"2026-08-26-001","snapshot_sha256":"<hash>","nodes":{"research":{"status":"succeeded","attempt":1,"output_sha256":"<hash>"},"review":{"status":"pending","attempt":0}}}
```

Write state atomically.

Write a temporary file, flush it, and rename it to state.json.

## Connect both graphs

Use files as the interface:

1. Grokbot validates the knowledge graph.
2. Grokbot creates an immutable snapshot.
3. Grokbot dispatches each ready node to its declared owner.
4. Kimi Code with K3 runs only kimi.\* nodes.
5. Grokbot validates artifacts, hashes, checks, and DAG state.
6. Grokbot reviews the candidate patch.
7. Grokbot appends accepted changes to the graph log.
8. Grokbot creates the next snapshot.

Use this merge prompt:

```text
Review the Kimi candidate patch against:

- the frozen input snapshot
- source records
- node validation results
- final DAG state

Reject an operation when it has no source ID.
Reject an operation from a failed or blocked node.
Reject an operation that conflicts with a verified fact.

Append accepted operations to kg/events.jsonl.

Rebuild materialized node and edge files.

Return accepted IDs, rejected IDs, reasons,
and the new snapshot hash.
```

The knowledge graph is long-lived memory.

The DAG is the execution contract.

The run state is temporary execution state.

Do not let both systems write the authoritative graph at the same time.

# 3\. Context and harness engineering: control the nested runtimes

![Image](https://pbs.twimg.com/media/HQpRp8KbwAAahk-?format=jpg&name=large)

Kimi K3 is a model.

Kimi Code is a harness for that model.

Grokbot is a separate product with its own computer and approval system.

Do not describe them as one native runtime.

**Grokbot controls the outer action. Kimi Code controls its inner tools.**

## Use the correct architecture

Use Grokbot as the outer coordinator.

Run Kimi Code as an external process on one of these hosts:

- Your local computer
- The Grokbot managed Linux computer

These hosts are alternatives. Only the selected host runs the Kimi Code process.

The local path runs independently unless Grok Bot local execution is enabled and approved.

Local file and shell tools inherit that host user's permissions.

Remote MCP actions use the MCP server's credentials and authority.

Scope each MCP credential to the smallest required account, resource, and action.

K3 inference normally runs on Moonshot's hosted service.

The K3 weights do not automatically run on either host.

## Install the local harness

```sh
curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash
kimi --version
cd <project-directory>
kimi
```

Then use:

```text
/login
/model
/mcp
```

Keep the permission mode at manual.

Do not use --yolo for work that can write files, run commands, or call external services.

## Install the VM harness

Give Grokbot this prompt:

```text
Open the computer terminal.

Use /workspace/grok-kimi-harness as the project directory.

Install Kimi Code with Moonshot's official Linux installer.

Run kimi --version.
Show the version and installation path.

Do not authenticate.
Do not change system packages.
Stop if root access is required.
```

Complete authentication yourself.

This installs Kimi Code on the VM.

It does not install K3 weights on the VM.

## Build one context pack

Do not rely only on either product's conversation memory.

Keep operational context in files:

```text
grok-kimi-harness/
├── AGENTS.md
├── context/
│   ├── mission.md
│   ├── constraints.md
│   ├── definitions.md
│   ├── state.md
│   └── acceptance-tests.md
├── handoffs/
│   ├── inbox/
│   ├── outbox/
│   └── handoff.schema.json
├── policy/
│   ├── tool-policy.md
│   └── approval-policy.md
├── prompts/
│   ├── grokbot.md
│   └── kimi-system.md
├── ops/
│   ├── run-log.jsonl
│   └── checkpoints/
└── artifacts/
```

Kimi Code loads AGENTS.md instruction files.

Grok Bot does not document automatic AGENTS.md loading from /workspace.

Tell Grokbot to read the context pack at the start of each run.

Save that procedure as a Grokbot skill.

## Grokbot outer-harness prompt

```text
You are the outer coordinator.

Before each run:

1. Read AGENTS.md.
2. Read context/mission.md.
3. Read context/constraints.md.
4. Read context/state.md.
5. Read the last valid checkpoint.
6. Read the last 20 sanitized log records.

Create one run_id.

Write one Kimi handoff envelope with:
- task
- allowed paths
- allowed tools
- prohibited actions
- acceptance tests
- approval boundary
- expected artifact
- next owner

Do not assume Auto Review sees Kimi's inner tool calls.

Require approval before an external effect.

After Kimi finishes, verify the artifact.
Record its hash and test result.
Update state only after verification.
```

## Kimi inner-harness prompt

Save this read-only print profile as .kimi-code/agents/harness-readonly.md.

Use [$KIMI\_CODE\_HOME](https://x.com/search?q=%24KIMI_CODE_HOME&src=cashtag_click)/SYSTEM.md only when you intend to replace the main system prompt.

Include ${base\_prompt} when the current Kimi documentation requires the built-in base context. See custom agents.

```markdown
---
name: harness-readonly
description: Completes one read-only nested-harness round
tools:
  - Read
  - Grep
  - Glob
  - Agent
  - AgentSwarm
subagents:
  - explore
---

${base_prompt}

You are the Kimi worker in a two-harness workflow.

Read AGENTS.md and its referenced context files.

Read the current handoff envelope.
Use its run_id for every output.

Work only in allowed paths.
Use only permitted tools.

Do not use Bash, Write, Edit, or MCP.
Do not send, publish, purchase, delete,
change permissions, or change production.

Return NEEDS_APPROVAL before a consequential action.

Return artifact payloads in the final JSON response.
Run each acceptance test.

Do not edit Kimi session wire.jsonl files.

Return:
- status
- completed work
- evidence
- artifact paths
- artifact hashes
- tests
- unresolved items
- requested approvals
- next owner
```

The bridge validates that JSON and writes artifacts under artifacts/<run\_id>/.

Never run a write-capable agent through kimi -p.

Use the SDK with yolo=False for an approved mutation profile.

## Apply the outer policy gate

Configure narrow Grokbot approval rules:

- Require approval before an external message.
- Require approval before publication.
- Require approval before deletion.
- Require approval before a production change.
- Require approval before a local-computer command.
- Allow only known read-only checks.

Grok Bot states that Require Approval takes priority over Always Allow.

Auto Review is model-based. It does not replace least privilege. See Grok Bot approvals.

Personal Auto Review rules belong to the current desktop installation.

Verify the rules on every desktop that can start the local Kimi harness.

## Apply the inner policy gate

Use ordered Kimi permission rules:

```toml
default_model = "kimi-code/k3"
default_permission_mode = "manual"

[loop_control]
max_steps_per_turn = 40
max_attempts_per_step = 3
reserved_context_size = 64000

[background]
max_running_tasks = 4
print_background_mode = "exit"
bash_task_timeout_s = 300

[subagent]
timeout_ms = 900000

[[permission.rules]]
decision = "allow"
pattern = "Read"

[[permission.rules]]
decision = "allow"
pattern = "Grep"

[[permission.rules]]
decision = "deny"
pattern = "Bash(rm -rf*)"
reason = "Recursive deletion is prohibited."

[[permission.rules]]
decision = "deny"
pattern = "mcp__mail__send"
reason = "This workflow creates drafts only."

[[permission.rules]]
decision = "ask"
pattern = "Bash"

[[permission.rules]]
decision = "ask"
pattern = "Write"

[[permission.rules]]
decision = "ask"
pattern = "Edit"
```

Kimi applies the first matching rule.

The ask rules pause interactive Kimi sessions.

They do not create a human checkpoint for kimi -p.

For unattended print mode, use static deny rules, narrow agent tool lists, and the limits above.

Use the bridge's wall-clock timeout to bound the full print-mode process.

Use the SDK with yolo=False when automation must surface approval requests.

MCP argument matching is not available for Kimi MCP tools. Match the tool name or server wildcard. See Kimi configuration.

## Keep MCP boundaries separate

A Grokbot connector does not automatically become a Kimi tool.

A Kimi MCP server does not automatically become a Grokbot connector.

Kimi project MCP configuration lives in .kimi-code/mcp.json.

Project MCP servers can start local processes. Review the file before you trust the repository. See Kimi MCP configuration.

Remote MCP servers can also act with credentials that exceed the local operating-system boundary.

Use the shared file contract first.

Add a read-only bridge later when both products and account policy support it.

## Understand the nested-harness gap

Grokbot can approve the command that starts Kimi Code.

It cannot be assumed to approve every tool call inside that process.

```sh
kimi \
  --agent-file .kimi-code/agents/harness-readonly.md \
  -p "Read handoffs/inbox/task.json. Complete one bounded round."
```

This selected print profile can use only its declared read and agent tools.

A different Kimi profile can make file, shell, agent, or MCP calls.

Kimi permissions must control tool selection.

Kimi hooks must record those calls.

Operating-system permissions must limit local file, process, and network effects.

Scoped server credentials and service policy must limit remote MCP effects.

This gap is the main reason to avoid broad automation modes.

In print mode, assume no human pause inside the process.

Use the SDK when an inner approval must reach a person.

Do not invoke a write-capable profile with kimi -p.

## Build a separate append log

Kimi sessions already store agents/\*/wire.jsonl.

Those files support recovery and replay. Do not edit them. They can contain sensitive data. See Kimi sessions and context.

Create a separate sanitized operational log:

```text
ops/run-log.jsonl
```

Use one record per line:

```json
{"v":1,"ts":"2026-08-26T12:00:00Z","run_id":"run_01","actor":"kimi","host":"grokbot-vm","event":"tool.request","tool":"Bash","target":"/workspace/grok-kimi-harness","args_sha256":"<hash>","decision":"ask","status":"pending","policy_rev":"policy_07","context_rev":"ctx_19","idempotency_key":"run_01-step_04","prev_hash":"<hash>","record_hash":"<hash>"}
```

Record these event types:

- handoff.created
- tool.request
- approval.result
- tool.result
- checkpoint
- handoff.completed
- recovery.started
- recovery.completed

Do not store tokens, cookies, passwords, raw secrets, or unredacted command output.

Use a single logger process with append mode and a file lock.

Hash each record with the prior record hash.

Create the record with prev\_hash and without record\_hash.

Serialize it as RFC 8785 canonical JSON encoded in UTF-8.

Store the lowercase SHA-256 digest of those bytes as record\_hash.

A hash chain can reveal later modification.

It cannot prevent modification by the same operating-system user.

Periodically anchor the chain head outside the writable VM.

Mirror the log to immutable storage when compliance requires a true append-only record.

## Connect Kimi hooks to the log

Kimi hooks receive lifecycle data as JSON through standard input.

```toml
[[hooks]]
event = "PreToolUse"
command = "./ops/audit-hook"
timeout = 5

[[hooks]]
event = "PermissionResult"
command = "./ops/audit-hook"
timeout = 5

[[hooks]]
event = "PostToolUse"
command = "./ops/audit-hook"
timeout = 5

[[hooks]]
event = "PostToolUseFailure"
command = "./ops/audit-hook"
timeout = 5
```

The hook must redact data before it appends a record.

Kimi hooks fail open after a script error or timeout.

Use hooks for logging and lightweight checks.

Use permissions and human confirmation for security. See Kimi hooks.

## Use the SDK when you need approval control

The Kimi Agent SDK wraps Kimi Code and exposes raw events and approval requests. See the SDK quickstart and Session guide.

```python
import asyncio

from kaos.path import KaosPath
from kimi_agent_sdk import ApprovalRequest, Session, TextPart

async def main() -> None:
    async with await Session.create(
        work_dir=KaosPath.cwd(),
        yolo=False,
        max_steps_per_turn=40,
    ) as session:
        async for msg in session.prompt("Read the handoff. Run one round."):
            match msg:
                case TextPart(text=text):
                    print(text, end="", flush=True)
                case ApprovalRequest() as request:
                    request.resolve("reject")

asyncio.run(main())
```

Replace the blanket rejection with a narrow policy function.

Surface uncertain or consequential requests to the human approval layer.

Do not set yolo=True in a production control loop.

## The operating principle

Models give the system capability.

Loops give the system persistence.

Graphs give the system memory and order.

Context gives each worker the correct frame.

Harnesses give the system control.

Start with one read-only task.

Use one Grokbot Coordinator, one Kimi worker, one verifier, and a three-round limit.

Add the swarm only after the single-worker loop is stable.

Add the DAG only after every output has a contract.

Add the knowledge graph only after every claim has a source.

Keep the human gate before every irreversible effect.

That is how Grokbot and Kimi K3 become one reliable agent system without pretending they are one native product.