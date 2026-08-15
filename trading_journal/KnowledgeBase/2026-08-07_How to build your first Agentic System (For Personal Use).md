---
title: "How to build your first Agentic System (For Personal Use)"
source: "https://substack.com/home/post/p-206434003"
author:
  - "[[Danica Simic]]"
date: "2026-08-07"
published: 2026-07-09
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
sector:
origin:
---
![](https://substackcdn.com/image/fetch/$s_!8QPA!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F89a97151-4482-45a9-ab33-115b506a6fd9_1536x1024.png)

Building your first agentic system is much different from building software solutions or machine learning models. However, knowing one of the two greatly helps you frame the problem and create a workflow you’ll follow.

A lot of people have this illusions that AI agents are just chatbots or workflows that function on hard rules, and that anyone can build them in 5 minutes. Perhaps, you can, but it won’t work the way you imagined it and it won’t be long before its functionality is fully broken.

In this post, we’ll skip the universal assistant. Instead we’ll build a system that does one specific job, well enough that you can tell it worked. Here’s a full step-by-step build, using an engineering review assistant as the working example (as the vast majority of readers have tech background.)

> Attention: The guide is very long. If you are reading this from email. Make sure to open the full version.

### Step 1: Define the job before you touch a model

Do not start with “build an agent that helps me code.” Start with something you can finish a sentence about.

Build an agent that reviews pull requests for design and security issues before a human reviewer looks at them.

For that one job, write down five things.

1. **What goes in:** a diff, the PR description, the affected files
2. **What comes out**: a structured review with flagged issues and suggested fixes
3. **What context it needs**: the team’s style guide, past review comments, the service’s architecture notes
4. **What tools it needs**: diff parser, style checker, security pattern scanner
5. **What should never happen without you:** approving the PR, merging, commenting publicly on someone’s code without a human reading it first

Job: Engineering Review Assistant

Input: PR diff, PR description, changed file list

Output: structured review with severity-tagged findings

Context needed: style guide, prior review history, architecture notes

Tools: parse\_diff, check\_style, scan\_for\_risks

Requires approval: posting the review, approving the PR

Skipping this step is why people end up with a reviewer that flags fifty things nobody asked about and misses the one that mattered.

The narrower the job, the easier the system is to design, evaluate, and improve.

### Step 2: Build a router, not a brain

Before your AI agent can reason, it needs to decide what kind of review your task actually needs. That’s the first working piece.

Write down how a human would complete the task.

For example:

Trigger → Collect sources → Filter irrelevant information → Rank important items → Create summary → Verify claims → Draft output → Request approval

This matters because an agentic system is not just a prompt.

It is a workflow containing decisions, state transitions, tool calls, failure conditions, and stopping rules.

Before writing code, identify:

- deterministic steps
- decisions requiring reasoning
- external data requirements
- actions with real-world consequences
- points where the system should stop

Not every step needs an agent. In many cases, the best architecture combines deterministic automation with agentic reasoning.

```markup
def route(pr_description: str, changed_files: list) -> str:
    text = pr_description.lower()
    if any(f.endswith((".sql", ".yml", "schema.py")) for f in changed_files):
        return "schema_change_review"
    if "security" in text or "auth" in text:
        return "security_focused_review"
    if len(changed_files) > 15:
        return "large_change_review"
    return "standard_review"
```

That is the whole router. It does not need to be clever. It needs to correctly separate a routine formatting PR from a schema migration touching production data.

### Step 3: Add a planner

![](https://substackcdn.com/image/fetch/$s_!43mH!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F28daef82-cc4f-42aa-89b4-e0b34d4c2cf4_1536x1024.png)

The planner turns “review this PR” into a visible list of steps, so you can see what the agent intends to check before it checks it.

At the center of the system is a loop:

**Observe → Reason → Act → Evaluate**

```markup
def build_plan(review_type: str) -> list:
    plans = {
        "schema_change_review": [
            "check for backward-incompatible column changes",
            "verify migration has a rollback path",
            "check for missing indexes on new foreign keys",
            "check style guide compliance",
        ],
        "security_focused_review": [
            "scan for hardcoded secrets",
            "check auth checks on new endpoints",
            "check input validation on new user-facing fields",
            "check style guide compliance",
        ],
        "large_change_review": [
            "summarize the change at a high level",
            "flag files with no test coverage change",
            "check style guide compliance",
        ],
    }
    return plans.get(review_type, ["check style guide compliance", "flag obvious risks"])
```

Nothing here is model-generated yet. It is a lookup table, which means when the review misses something, you know exactly which checklist to fix, not which prompt to reword.

### Step 4: Design memory in layers, not as one pile

A single dump of “every past PR ever” makes the reviewer worse, because it has to sift through irrelevant history to find what matters for this diff. Split it by purpose.

Working memory: the current diff, description, and file list Standing preferences: the team’s style guide, naming conventions, things that do not change PR to PR History: past review comments and whether they were accepted or overridden Reference material: architecture docs, service ownership maps

```markup
class ReviewMemory:
    def __init__(self):
        self.style_guide = {}
        self.past_reviews = []
        self.architecture_notes = []

    def load_style_guide(self, rules: dict):
        self.style_guide = rules

    def log_review_outcome(self, pr_id, comment, was_accepted):
        self.past_reviews.append({"pr_id": pr_id, "comment": comment, "accepted": was_accepted})

    def find_architecture_notes(self, service_name):
        return [n for n in self.architecture_notes if service_name.lower() in n.lower()]
```

Tracking whether past comments were accepted or overridden matters more than people expect. A reviewer that keeps flagging things engineers keep dismissing is training itself to be ignored.

### Step 5: Keep tools small and boring

A tool should have one job and a name that says exactly what it checks.

A model cannot read your repo, run a linter, or check who owns a service. It only knows what is in the text you send it. A tool is how you close that gap. It is a plain function with three parts: a name that says exactly what it does, an input the model can fill in, and an output the model can read back and reason about.

That is the entire definition. Nothing about “tool” implies intelligence. The intelligence is the model deciding when to call it. The tool itself should be the most boring, predictable piece of the whole system.

For an engineering review agent, it helps to think about tools in layers, based on what kind of question they answer.

Inspection tools, which read the change itself

```markup
def parse_diff(raw_diff: str) -> dict:
    added_lines = [l for l in raw_diff.splitlines() if l.startswith("+")]
    removed_lines = [l for l in raw_diff.splitlines() if l.startswith("-")]
    return {"added": added_lines, "removed": removed_lines}
```

Static analysis tools, which check the change against fixed rules

```markup
def check_style(diff_text: str, style_guide: dict) -> list:
    violations = []
    if "print(" in diff_text and not style_guide.get("allow_print_debug", False):
        violations.append("uses print() instead of the logger")
    if "except:" in diff_text:
        violations.append("bare except clause, should catch a specific exception")
    return violations

def scan_for_risks(diff_text: str) -> list:
    risks = []
    if "API_KEY" in diff_text or "SECRET" in diff_text:
        risks.append("possible hardcoded credential")
    if "SELECT *" in diff_text.upper():
        risks.append("unbounded SELECT * query")
    return risks

def parse_diff(raw_diff: str) -> dict:
    added_lines = [l for l in raw_diff.splitlines() if l.startswith("+")]
    removed_lines = [l for l in raw_diff.splitlines() if l.startswith("-")]
    return {"added": added_lines, "removed": removed_lines}
```

This is where most first attempts stop. It is also where a review agent is still just a fancier linter. The more useful layer is the next one.

Context tools, which compare the change against things the model cannot see in the diff alone

```markup
def check_test_coverage_delta(changed_files: list, test_files: list) -> list:
    warnings = []
    for f in changed_files:
        if f.endswith(".py") and "test" not in f.lower():
            expected_test = f"test_{f.split('/')[-1]}"
            if expected_test not in test_files:
                warnings.append(f"{f} changed with no matching test file touched")
    return warnings

def check_breaking_change_for_consumers(changed_files: list, service_map: dict) -> list:
    warnings = []
    for f in changed_files:
        consumers = service_map.get(f, [])
        if consumers:
            warnings.append(f"{f} is used by {', '.join(consumers)}, confirm they were notified")
    return warnings

def check_similar_past_incidents(pr_description: str, incident_log: list) -> list:
    keywords = pr_description.lower().split()
    matches = [
        incident for incident in incident_log
        if any(k in incident["summary"].lower() for k in keywords)
    ]
    return [m["summary"] for m in matches]
```

These three are the ones that make the agent feel like an actual senior reviewer instead of a linter with a chat interface. A linter can tell you a function is missing a docstring. It cannot tell you this exact file caused an outage eight months ago, or that three other services quietly depend on the function you just renamed. That kind of check only exists if you build a tool that goes looking for it.

## Step 6: Setting guardrails (Important)

![](https://substackcdn.com/image/fetch/$s_!LWrC!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd93210ad-a29c-4458-b0e0-a3b9c0618db6_1536x1024.png)

An engineering review agent needs clear rules, written down, not implied by a prompt.

Example system policies:

1\. Never post a review comment without human approval.

2\. Never approve or merge a PR automatically.

3\. Never request changes on someone's behalf without review.

4\. Always flag when a changed file has no matching test update.

5\. Always disclose when a finding is a guess versus a confirmed match.

6\. Ask for confirmation before contacting another team about their service.

7\. Log every tool call and every finding it produced.

8\. Stop and flag for a second reviewer after a fixed complexity threshold.

Reading a diff and generating comments is cheap. Posting to a real PR or approving it is not.

```markup
requires_approval = {"post_review_comment", "approve_pr", "request_changes"}

def can_auto_run(action: str) -> bool:
    return action not in requires_approval

def run_action(action: str, approved: bool = False):
    if action in requires_approval and not approved:
        return {"status": "blocked", "reason": "needs a human to approve posting this"}
    return {"status": "executed", "action": action}
```

This one function is why an engineering review agent is safe to run on every PR instead of just the low-stakes ones. It can read and draft freely. It cannot post or approve without a human in the loop.

### Step 7: Verify before it reaches you

Agentic systems should not treat their own outputs as automatically correct.

Add verification before important actions.

Depending on the workflow, verification may include:

- checking whether sources actually support a claim
- validating structured outputs
- confirming required fields
- comparing results against explicit rules
- running a second evaluation step
- requesting human approval

The verifier checks the draft review against a short list of concrete, checkable things, not a subjective “is this a good review.”

```markup
def verify_review(findings: list, diff_stats: dict) -> dict:
    checks = {
        "has_findings_or_explicitly_clean": len(findings) > 0 or diff_stats.get("added", 0) < 5,
        "no_duplicate_findings": len(findings) == len(set(findings)),
        "severity_tagged": all(":" in f for f in findings),
    }
    return {"passed": all(checks.values()), "details": checks}
```

This will not catch a subtly wrong architectural judgment. It will catch a review that flagged the same issue three times, or one that produced nothing at all on a fifty-line diff, before a human wastes time reading it.

### Step 8: Decide when the human gets pulled in

This is where trust gets built, not through a confident-sounding review, but through knowing exactly when the system waits for you.

Low risk, runs alone: parsing the diff, running style checks, drafting findings Medium risk, drafts and waits: a full structured review comment High risk, always waits: approving the PR, requesting changes, merging Never automatic: overriding a human reviewer’s decision

The requires\_approval set from step 6 is already enforcing this. The discipline is making sure every code path actually checks it, including the ones you added later and forgot were in scope.

### Step 9: Log everything

![](https://substackcdn.com/image/fetch/$s_!xbta!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9939f874-bdc0-4758-90e6-5943d9c364c2_1536x1024.png)

Once a review runs through routing, planning, tool calls, and verification, you need a record of what happened at each stage, or a wrong review becomes a mystery instead of a fixable bug.

```markup
def log_step(run_log: list, step_name: str, status: str, detail: str = ""):
    run_log.append({"step": step_name, "status": status, "detail": detail})
    return run_log
```

A run log for one PR review might look like this.

```markup
[
  {"step": "route", "status": "done", "detail": "security_focused_review"},
  {"step": "plan", "status": "done", "detail": "4 checks selected"},
  {"step": "tools", "status": "done", "detail": "2 style violations, 1 risk flagged"},
  {"step": "verify", "status": "warning", "detail": "duplicate finding detected"}
]
```

Without this, "the agent flagged something wrong on PR 482" stays unsolvable. With it, you can see exactly which check produced the bad finding.

Log:

- model decisions
- tool calls
- failures
- retries
- verification results
- human overrides
- task completion

## Step 10: Build a working version

Do not start with a multi-agent architecture. The best system is often the simplest one.

Build the smallest version that completes one useful workflow.

Then observe what actually happens.

Your first version should help you answer:

- Where does the system fail?
- Which steps are unnecessary?
- Where does it need more context?
- Where is deterministic logic better than reasoning?
- Which decisions require human judgment?

Only after answering those questions should you add more tools, more memory, more autonomy, or more agents.

Now let’s put every piece from steps 2 through 9 into one system.

This version can:

1. Accept a PR description, changed file list, and raw diff
2. Route it to the right kind of review
3. Build a plan of what to check
4. Run every tool from step 5, inspection, static analysis, and context tools
5. Verify the findings before anything goes further
6. Check whether posting requires human approval
7. Log every step along the way

```markup
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ReviewState:
    pr_id: str
    review_type: str
    plan: List[str]
    findings: List[str]
    complexity: str
    verification: Dict
    requires_human_approval: bool
    run_log: List[Dict] = field(default_factory=list)

class EngineeringReviewAgent:
    def __init__(self, memory):
        self.memory = memory

    def route(self, pr_description: str, changed_files: list) -> str:
        text = pr_description.lower()
        if any(f.endswith((".sql", ".yml", "schema.py")) for f in changed_files):
            return "schema_change_review"
        if "security" in text or "auth" in text:
            return "security_focused_review"
        if len(changed_files) > 15:
            return "large_change_review"
        return "standard_review"

    def build_plan(self, review_type: str) -> list:
        plans = {
            "schema_change_review": [
                "check for backward-incompatible column changes",
                "verify migration has a rollback path",
                "check test coverage on changed files",
                "check style guide compliance",
            ],
            "security_focused_review": [
                "scan for hardcoded secrets",
                "check auth checks on new endpoints",
                "check style guide compliance",
            ],
            "large_change_review": [
                "estimate review complexity",
                "check test coverage on changed files",
                "flag downstream consumers of changed files",
            ],
        }
        return plans.get(review_type, ["check style guide compliance", "flag obvious risks"])

    def run_tools(self, raw_diff: str, changed_files: list, pr_description: str) -> list:
        findings = []

        style_issues = check_style(raw_diff, self.memory.style_guide)
        findings += [f"style: {s}" for s in style_issues]

        risk_issues = scan_for_risks(raw_diff)
        findings += [f"risk: {r}" for r in risk_issues]

        coverage_gaps = check_test_coverage_delta(changed_files, self.memory.test_files)
        findings += [f"coverage: {c}" for c in coverage_gaps]

        breaking_changes = check_breaking_change_for_consumers(changed_files, self.memory.service_map)
        findings += [f"consumers: {b}" for b in breaking_changes]

        past_incidents = check_similar_past_incidents(pr_description, self.memory.incident_log)
        findings += [f"history: {p}" for p in past_incidents]

        return findings

    def run(self, pr_id: str, pr_description: str, changed_files: list, raw_diff: str) -> ReviewState:
        log = []

        review_type = self.route(pr_description, changed_files)
        log.append({"step": "route", "status": "done", "detail": review_type})

        plan = self.build_plan(review_type)
        log.append({"step": "plan", "status": "done", "detail": f"{len(plan)} checks"})

        parsed = parse_diff(raw_diff)
        diff_stats = {"added": len(parsed["added"]), "removed": len(parsed["removed"])}

        findings = self.run_tools(raw_diff, changed_files, pr_description)
        log.append({"step": "tools", "status": "done", "detail": f"{len(findings)} findings"})

        complexity = estimate_review_complexity(diff_stats, changed_files)
        log.append({"step": "complexity", "status": "done", "detail": complexity})

        verification = verify_review(findings, diff_stats)
        status = "done" if verification["passed"] else "warning"
        log.append({"step": "verify", "status": status, "detail": str(verification["details"])})

        needs_approval = not can_auto_run("post_review_comment")
        log.append({"step": "approval_check", "status": "done", "detail": f"requires_approval={needs_approval}"})

        return ReviewState(
            pr_id=pr_id,
            review_type=review_type,
            plan=plan,
            findings=findings,
            complexity=complexity,
            verification=verification,
            requires_human_approval=needs_approval,
            run_log=log,
        )
```

Example memory, fully populated this time, not just a placeholder list:

python

```markup
class ReviewMemory:
    def __init__(self):
        self.style_guide = {"allow_print_debug": False}
        self.test_files = ["test_billing.py", "test_auth.py"]
        self.service_map = {
            "billing/invoice.py": ["payments-service", "reporting-dashboard"],
        }
        self.incident_log = [
            {"summary": "auth token refresh caused a production outage in March"},
        ]
```

Run it:

python

```markup
memory = ReviewMemory()
agent = EngineeringReviewAgent(memory)

sample_diff = """
+ API_KEY = "sk-12345"
+ except:
+     pass
"""

state = agent.run(
    pr_id="PR-482",
    pr_description="Refactor billing auth flow",
    changed_files=["billing/invoice.py"],
    raw_diff=sample_diff,
)

print(state.findings)
print(state.verification)
print(state.requires_human_approval)
print(state.run_log)
```

That produces something like this.

```markup
['style: bare except clause, should catch a specific exception',
 'risk: possible hardcoded credential',
 'consumers: billing/invoice.py is used by payments-service, reporting-dashboard, confirm they were notified',
 'history: auth token refresh caused a production outage in March']

{'passed': True, 'details': {'has_findings_or_explicitly_clean': True, 'no_duplicate_findings': True, 'severity_tagged': True}}

True

[{'step': 'route', 'status': 'done', 'detail': 'security_focused_review'},
 {'step': 'plan', 'status': 'done', 'detail': '3 checks'},
 {'step': 'tools', 'status': 'done', 'detail': '4 findings'},
 {'step': 'complexity', 'status': 'done', 'detail': 'low'},
 {'step': 'verify', 'status': 'done', 'detail': "{'has_findings_or_explicitly_clean': True, 'no_duplicate_findings': True, 'severity_tagged': True}"},
 {'step': 'approval_check', 'status': 'done', 'detail': 'requires_approval=True'}]
```

Notice what happened without a single line of model-generated text. The agent caught a hardcoded credential, a bare except, flagged that two other services depend on the file being touched, and surfaced a related incident from March, all before deciding it still needs a human to actually post any of it.

This is intentionally rule-based rather than model-generated, so you can see the full mechanics with nothing hidden. But even this version is already a real agentic system, because it has:

A router that decides what kind of review this is A plan you can inspect before anything runs Layered memory instead of one undifferentiated pile Tools with one job each, including ones that see context a linter never could Risk tiers that block posting and approving by default A verifier catching duplicate or missing findings A full log of every decision, in order

Swap run\_tools and generate\_output style logic for real model calls where judgment is genuinely needed, keep everything else exactly as it is, and this becomes the review agent you actually run on real PRs.

### Why the boring parts are the actual system

None of these ten pieces are impressive alone. A router. A checklist. Layered memory that tracks what got overridden. Narrow tools with one job each. A risk list. A verifier that catches duplicates. A log. Put together, they are the difference between a review bot people learn to ignore and one they actually trust, because when it flags something wrong, you know exactly which of the ten pieces to fix.

### Final Words

That is the actual shape of an agentic system. Not one clever prompt. Ten small, boring, inspectable pieces working together.

What’s next:

- Replacing the rule-based checks with real reasoning, the version that reads a diff the way a senior engineer would and explains why something is risky, not just that it matched a pattern
- A second build many of you have asked for, a research agent that searches, reads, cross-checks itself, and hands you a summary you can actually trust

If you want both builds, full code, no simplified version:

- Subscribe to my Substack to be the first one to get exclusive tips, career guides and projects with code + 3 exclusive posts per month.

If you want the complete system to develop agentic AI systems, orchestrate agents and become AI-savvy:

- Agentic Intelligence is the full guide, the complete architecture, the reasoning layer, multi-agent coordination, and the production concerns one blog post cannot cover
- You will get 3 free guides on OpenClaw, n8n and Claude Code
- If the ten steps above made sense to you, the rest of it will move fast
- Check my other [Guides & Resources](https://stan.store/codingmermaid)

Until next Friday,  
Danica