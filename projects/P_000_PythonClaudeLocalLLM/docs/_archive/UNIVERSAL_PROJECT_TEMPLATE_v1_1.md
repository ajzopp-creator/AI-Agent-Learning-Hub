# [PROJECT NAME] â€” System Documentation
**Project ID:** [e.g., P_115 / P_300 / P_000]
**Version:** [e.g., 1.0]
**Last Updated:** [YYYY-MM-DD]
**Maintained By:** Anthony Zoppi
**Status:** [Active / In Development / Archived]

---

## DOCUMENTATION DECISION PROTOCOL
*Read this before creating any new documentation.*

### The Golden Rule
**Always try to fit new content into this master document first.**
Only create a separate file when one of the trigger conditions below is met.

### Decision Flow

```
New content needs to be documented
              |
              v
Does a section in this master doc already cover this topic?
              |
      Yes     |     No
              |
   Add it     |   Is the content > 1 page OR updated frequently
   here       |   OR shared across multiple projects?
              |            |
              |     Yes    |    No
              |            |
              |   Create   |   Add it
              |   separate |   here
              |   file     |
              |            |
              v            v
    Add a reference     Done
    link in the
    relevant section
    of this doc
```

### When to Add Directly to This Document
- Short content (under 1 page)
- Stable content that rarely changes
- Content specific to this project only
- Definitions, parameters, rules, checklists

### When to Create a Separate File
- Content exceeds 1 page of detail
- Updated frequently (e.g., daily/weekly logs)
- Shared or referenced across multiple projects
- Requires its own version history
- Operational prompts that are copy-pasted regularly

### When Creating a Separate File â€” Always Ask First

**Before creating any new document, ask:**

> "Should I add this to the master doc, or create a separate file?
> If separate â€” does a file already exist that this should merge into?"

**Then follow this checklist:**
- [ ] Check if content fits an existing section in this master doc
- [ ] Check if a related file already exists that should be updated instead
- [ ] If creating new â€” add a reference link in the relevant section here
- [ ] Name the file using the project convention: `[ProjectID]_[Topic]_v[X.X].md`
- [ ] Note the new file in Section 13 Appendix B (Related Documentation)

### Reference Link Format
When a separate file is created, place this in the relevant section:

```
> **Linked Document:** [Filename]
> **Location:** [Project Knowledge / Local Path / GitHub]
> **Purpose:** [One line â€” what this file contains]
> **Last Updated:** [Date]
```

---

## TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [AI Tools & Platforms](#3-ai-tools--platforms)
4. [Requirements](#4-requirements)
5. [Change Log](#5-change-log)
6. [Error Corrections Log](#6-error-corrections-log)
7. [Enhancement Log](#7-enhancement-log)
8. [AI Workflows & Processes](#8-ai-workflows--processes)
9. [Data Design](#9-data-design)
10. [Testing & Validation](#10-testing--validation)
11. [Daily Operations & Session Management](#11-daily-operations--session-management)
12. [Troubleshooting & Support](#12-troubleshooting--support)
13. [Appendices](#13-appendices)

---

## 1. PROJECT OVERVIEW

### 1.1 Purpose
**Objective:** [Clearly state the purpose of this system in 2-3 sentences. What problem does it solve? What is the expected outcome?]

*Example (Trading): "Systematic swing trading system using multi-tier diagnostics to identify high-probability dip-buying opportunities with defined risk parameters."*
*Example (Technical): "Python-based agentic workflow that automates Claude API calls for signal processing and trade log management."*

### 1.2 Scope

**What This System Covers:**
- [Core capability 1]
- [Core capability 2]
- [Core capability 3]

**What This System Does NOT Cover:**
- [Out of scope item 1]
- [Out of scope item 2]

### 1.3 Project Details

| Field | Value |
|---|---|
| Start Date | [Date] |
| Current Status | [Active / In Development / Archived] |
| Primary AI Engine | [Claude.ai / Local LLM / Grok / Other] |
| Primary Platform | [ThinkorSwim / Python / VS Code / Other] |
| Project Location | [Claude Project Name / GitHub Repo / Local Path] |
| Related Projects | [P_XXX / None] |

### 1.4 Reference Materials

| Document | Location | Notes |
|---|---|---|
| [Session Init Prompt] | [Project Knowledge / Local File] | [Paste at session start] |
| [Strategy Guide] | [Project Knowledge] | [Core rules] |
| [Quick Reference] | [Project Knowledge] | [Daily use] |
| [External Resource] | [URL / Path] | [Description] |

### 1.5 Definitions & Acronyms

| Term / Acronym | Definition |
|---|---|
| TOS | ThinkOrSwim â€” primary charting and execution platform |
| ATR | Average True Range â€” volatility-based position sizing input |
| Claude | Anthropic's AI assistant â€” core AI engine for this system |
| LLM | Large Language Model |
| [Term] | [Definition] |
| [Term] | [Definition] |

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Flow

```
[Data Input / Signal Source]
         |
         v
[AI Analysis Layer â€” Claude / LLM]
         |
         v
[Decision Engine â€” Rules / Scoring / Filters]
         |
         v
[Output / Execution / Logging]
         |
         v
[Review & Performance Tracking]
```

**Description:** [Explain in plain language how data moves through the system. What triggers the process? What comes out the other end?]

### 2.2 Core Components

#### Component 1: [Name â€” e.g., Signal Source / Data Input]
- **Responsibility:** [What it does]
- **Inputs:** [What feeds into it]
- **Outputs:** [What it produces]
- **Tools Used:** [Claude, TOS, Python, etc.]
- **Dependencies:** [What it relies on]

#### Component 2: [Name â€” e.g., Analysis / Decision Engine]
- **Responsibility:** [What it does]
- **Inputs:** [What feeds into it]
- **Outputs:** [What it produces]
- **Tools Used:** [Claude, TOS, Python, etc.]
- **Dependencies:** [What it relies on]

#### Component 3: [Name â€” e.g., Execution / Logging]
- **Responsibility:** [What it does]
- **Inputs:** [What feeds into it]
- **Outputs:** [What it produces]
- **Tools Used:** [Claude, TOS, Python, etc.]
- **Dependencies:** [What it relies on]

### 2.3 System Decomposition

```
[Project Root Name]
â”œâ”€â”€ [Module 1 â€” e.g., Data Management]
â”‚   â”œâ”€â”€ [Sub-component 1]
â”‚   â”œâ”€â”€ [Sub-component 2]
â”‚   â””â”€â”€ [Sub-component 3]
â”œâ”€â”€ [Module 2 â€” e.g., Analysis Engine]
â”‚   â”œâ”€â”€ [Sub-component 1]
â”‚   â”œâ”€â”€ [Sub-component 2]
â”‚   â””â”€â”€ [Sub-component 3]
â”œâ”€â”€ [Module 3 â€” e.g., Decision Logic]
â”‚   â”œâ”€â”€ [Sub-component 1]
â”‚   â””â”€â”€ [Sub-component 2]
â””â”€â”€ [Module 4 â€” e.g., Output / Reporting]
    â”œâ”€â”€ [Sub-component 1]
    â””â”€â”€ [Sub-component 2]
```

### 2.4 Design Rationale

**Why This Architecture?**
- **Simplicity:** [Why was this approach chosen over more complex alternatives?]
- **Claude-Centricity:** [How does Claude serve as the AI core?]
- **Maintainability:** [How is the system kept easy to update and audit?]
- **Independence:** [How does this system operate relative to other projects?]

**Alternatives Considered:**

| Option | Pros | Cons | Decision |
|---|---|---|---|
| [Option A] | [+] | [-] | [Why not selected] |
| [Option B] | [+] | [-] | [Why not selected] |

---

## 3. AI TOOLS & PLATFORMS

### 3.1 Tool Stack

| Tool / Platform | Role in System | Version / Tier | Notes |
|---|---|---|---|
| Claude.ai | Primary AI engine â€” analysis, decisions, output | [Pro / Team / API] | Core reasoning layer |
| [ThinkorSwim] | [Market data, charting, execution] | [Latest] | [ThinkScript indicators] |
| [Python] | [Automation, data processing] | [3.x] | [Optional â€” if applicable] |
| [VantagePoint] | [ML signal source] | [Latest] | [If applicable] |
| [Grok / ChatGPT] | [Secondary AI reference] | [â€”] | [If applicable] |
| [VS Code] | [Code editor] | [Latest] | [If applicable] |
| [Excel / Google Sheets] | [Tracking / logging] | [â€”] | [If applicable] |

### 3.2 Claude Project Configuration

| Setting | Value |
|---|---|
| Project Name | [Name in Claude.ai] |
| Knowledge Files | [List key files loaded] |
| Memory Enabled | [Yes / No] |
| Session Init Required | [Yes / No â€” paste prompt at start?] |
| Primary Model | [Claude Sonnet / Opus / Haiku] |

### 3.3 Prompt Library (Master List)

Save your best-performing prompts here. Update when a prompt is refined.

#### Prompt: [Name â€” e.g., Step 1 Signal Analysis]
```
[Paste full prompt template here]
```
**Purpose:** [What task this prompt performs]
**When to Use:** [Trigger condition]
**Last Updated:** [Date]

#### Prompt: [Name â€” e.g., Step 2 Position Sizing]
```
[Paste full prompt template here]
```
**Purpose:** [What task this prompt performs]
**When to Use:** [Trigger condition]
**Last Updated:** [Date]

#### Prompt: [Name â€” e.g., Weekly Review]
```
[Paste full prompt template here]
```
**Purpose:** [What task this prompt performs]
**When to Use:** [Trigger condition]
**Last Updated:** [Date]

### 3.4 AI Behavior Rules & Constraints

*Document rules Claude must follow within this project. Copy relevant rules from CLAUDE_ASSISTANT_INSTRUCTIONS if applicable.*

**Claude MUST:**
- [Rule 1 â€” e.g., Always search project knowledge before answering]
- [Rule 2 â€” e.g., Never fabricate diagnostic values]
- [Rule 3]

**Claude MUST NOT:**
- [Rule 1 â€” e.g., Invent account balance values]
- [Rule 2 â€” e.g., Apply hierarchy assumptions across systems]
- [Rule 3]

**Session Initialization:**
- [Describe what must be pasted or stated at session start, if anything]
- [e.g., "Paste SESSION_INITIALIZATION_PROMPT.md content at start of each session"]

---

## 4. REQUIREMENTS

### 4.1 Functional Requirements

#### FR-1: [Requirement Title]
- **Description:** [What the system must do]
- **Acceptance Criteria:**
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]
- **Component:** [Which module handles this]
- **Priority:** [High / Medium / Low]

#### FR-2: [Requirement Title]
- **Description:** [What the system must do]
- **Acceptance Criteria:**
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]
- **Component:** [Which module handles this]
- **Priority:** [High / Medium / Low]

#### FR-3: [Requirement Title]
- **Description:** [What the system must do]
- **Acceptance Criteria:**
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]
- **Component:** [Which module handles this]
- **Priority:** [High / Medium / Low]

### 4.2 Non-Functional Requirements

#### NFR-1: Accuracy
- **Requirement:** [e.g., Claude must not fabricate data or diagnostic values]
- **Target:** [e.g., Zero tolerance for invented values]
- **Implementation:** [e.g., Session prompt, project knowledge, memory rules]

#### NFR-2: Consistency
- **Requirement:** [e.g., Output format must be identical across sessions]
- **Target:** [e.g., Tab-delimited, 27-column, same every time]
- **Implementation:** [e.g., Locked schema in project knowledge]

#### NFR-3: Auditability
- **Requirement:** [e.g., Every signal must have a traceable source]
- **Target:** [e.g., SignalSource column populated on every row]
- **Implementation:** [e.g., Tracker schema enforcement]

#### NFR-4: [Other â€” e.g., Speed / Reliability / Security]
- **Requirement:** [Specification]
- **Target:** [Specific goal]
- **Implementation:** [How achieved]

### 4.3 Requirements Matrix

| ID | Description | Component | Status | Notes |
|---|---|---|---|---|
| FR-1 | [Description] | [Module] | [Complete / In Progress / Pending] | [Notes] |
| FR-2 | [Description] | [Module] | [Complete / In Progress / Pending] | [Notes] |
| NFR-1 | [Description] | [Module] | [Complete / In Progress / Pending] | [Notes] |

---

## 5. CHANGE LOG

*Document all intentional system changes, enhancements, and version releases.*

**Format:** Version | Date | Type | Description

### Version History

---

#### v[X.X] â€” [Date]
**Release Type:** [Major / Minor / Patch]

**Added:**
- [New feature or capability]

**Modified:**
- [Change to existing behavior or rule]

**Fixed:**
- [Correction to previous logic â€” reference Error Corrections Log if applicable]

**Removed / Deprecated:**
- [Anything removed from the system]

**Breaking Changes:** [Yes / No]
If yes: [Describe what breaks and how to handle it]

---

#### v[X.X] â€” [Date]
**Release Type:** [Major / Minor / Patch]

**Added:**
- [New feature]

**Modified:**
- [Changed behavior]

---

## 6. ERROR CORRECTIONS LOG

*Document critical errors that were discovered and corrected. This section is permanent â€” errors are never deleted, only marked Resolved.*

**Purpose:** Prevent the same mistake from recurring. Any error corrected 2+ times MUST be documented here.

---

### Error: [Short Title â€” e.g., Account Balance Confusion]
- **Date Discovered:** [Date]
- **Severity:** [Critical / High / Medium / Low]
- **Status:** [Resolved / Monitoring / Open]

**Wrong Behavior:**
[Describe exactly what was being done incorrectly. Be specific.]

```
Example of wrong output or logic:
[Paste example if applicable]
```

**Correct Behavior:**
[Describe what the correct behavior is.]

```
Example of correct output or logic:
[Paste example if applicable]
```

**Root Cause:** [Why did this error occur?]

**Fix Applied:**
- [Action 1 taken to prevent recurrence]
- [Action 2 â€” e.g., Added rule to project knowledge]
- [Action 3 â€” e.g., Updated session prompt]

**Verification:** [How to test that the fix is working]

---

### Error: [Short Title]
- **Date Discovered:** [Date]
- **Severity:** [Critical / High / Medium / Low]
- **Status:** [Resolved / Monitoring / Open]

**Wrong Behavior:**
[Description]

**Correct Behavior:**
[Description]

**Root Cause:** [Why it happened]

**Fix Applied:**
- [Actions taken]

---

## 7. ENHANCEMENT LOG

*Track planned improvements separately from bug fixes. Enhancements are intentional upgrades, not corrections.*

### Active Enhancements

#### Enhancement: [Title]
- **Status:** [Planned / In Development / Testing / Completed]
- **Priority:** [High / Medium / Low]
- **Target Date:** [Date or Quarter]
- **Description:** [What will be added or improved]
- **Expected Benefit:** [Why this is worth doing]
- **Dependencies:** [What must be done first]
- **Success Criteria:** [How will you know it worked?]

#### Enhancement: [Title]
- **Status:** [Planned / In Development / Testing / Completed]
- **Priority:** [High / Medium / Low]
- **Target Date:** [Date or Quarter]
- **Description:** [What will be added or improved]
- **Expected Benefit:** [Why this is worth doing]

### Completed Enhancements

| Enhancement | Completed Date | Result |
|---|---|---|
| [Title] | [Date] | [Outcome â€” e.g., Win rate improved 8%] |
| [Title] | [Date] | [Outcome] |

### Parked / Deferred

| Enhancement | Reason Deferred | Revisit Date |
|---|---|---|
| [Title] | [e.g., Need 3 months baseline data first] | [Date] |

---

## 8. AI WORKFLOWS & PROCESSES

*Document the actual step-by-step processes you run daily. These are your operating procedures.*

### 8.1 Primary Workflow: [Name â€” e.g., Signal Generation / Morning Setup]

**Trigger:** [What starts this workflow? e.g., Market open, daily scan, external alert]
**Frequency:** [Daily / Weekly / On-demand]
**Time Required:** [Estimated minutes]

**Steps:**
1. [Step 1 â€” e.g., Export TOS data / Run scan]
2. [Step 2 â€” e.g., Paste into Claude with STEP 1 prompt]
3. [Step 3 â€” e.g., Review output, verify verdict]
4. [Step 4 â€” e.g., Proceed to position sizing if BUY]
5. [Step 5 â€” e.g., Log result in tracker]

**Expected Output:**
[Describe what comes out of this workflow â€” format, decisions, next action]

**Decision Gate:**
```
If [condition] --> [action]
If [condition] --> [action]
If [condition] --> [action]
```

---

### 8.2 Secondary Workflow: [Name â€” e.g., Position Sizing / Code Review]

**Trigger:** [What starts this workflow]
**Frequency:** [When run]
**Time Required:** [Estimated minutes]

**Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Output:**
[Description]

---

### 8.3 Review Workflow: [Name â€” e.g., Evening Review / Weekly Strategy Check]

**Trigger:** [When]
**Frequency:** [Daily / Weekly]
**Time Required:** [Minutes]

**Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Prompt Template:**
```
[Paste the Claude prompt you use for this review]
```

---

### 8.4 Exception Workflows

*Document what to do when things go outside normal flow.*

#### Exception: [e.g., Signal conflict between two systems]
- **Trigger:** [When this exception occurs]
- **Action:** [What to do]
- **Documentation:** [How to record it]

#### Exception: [e.g., Claude gives unexpected output / error]
- **Trigger:** [When this occurs]
- **Action:** [What to do]
- **Documentation:** [How to record it]

---

## 9. DATA DESIGN

### 9.1 Data Inputs

| Data Type | Source | Format | How Fed to Claude |
|---|---|---|---|
| [e.g., Chart data] | [TOS / VantagePoint] | [Screenshot / CSV / Paste] | [Image / Text prompt] |
| [e.g., Scan results] | [TOS scan] | [Ticker list] | [Paste into prompt] |
| [e.g., Trade log] | [Excel / Sheets] | [CSV / Paste] | [Text] |
| [e.g., Code file] | [VS Code / GitHub] | [.py / .md] | [Upload / Paste] |

### 9.2 Data Outputs

| Output Type | Format | Destination | Frequency |
|---|---|---|---|
| [e.g., Signal verdict] | [Tab-delimited row] | [Excel tracker] | [Per signal] |
| [e.g., Position sizing] | [Formatted text] | [Manual entry] | [Per trade] |
| [e.g., Code module] | [.py file] | [Local / GitHub] | [Per session] |
| [e.g., Review summary] | [Text / Markdown] | [Notes / Journal] | [Daily / Weekly] |

### 9.3 Data Schema (if applicable)

*Document the structure of any tracking log, database, or file schema used by this system.*

**Schema Name:** [e.g., Trade Tracker / Signal Log / Code Registry]
**Version:** [e.g., v9.4.1]
**Columns / Fields:**

| Field Name | Type | Description | Valid Values |
|---|---|---|---|
| [Field 1] | [String / Integer / Date / Float] | [What it contains] | [Valid options] |
| [Field 2] | [Type] | [Description] | [Values] |
| [Field 3] | [Type] | [Description] | [Values] |

**Schema Rules:**
- [Critical rule 1 â€” e.g., Column order is locked, never reorder]
- [Critical rule 2 â€” e.g., Never insert placeholder dashes in computed columns]
- [Critical rule 3]

### 9.4 Data Integrity Rules

- [Rule 1 â€” e.g., Never fabricate values â€” if unknown, use "--"]
- [Rule 2 â€” e.g., Capture diagnostic values immediately when pasted]
- [Rule 3 â€” e.g., All outputs must be tab-delimited for Excel compatibility]

---

## 10. TESTING & VALIDATION

### 10.1 Testing Approach

**Philosophy:** [e.g., "Claude outputs validated against known examples before accepting as correct" / "Python code tested with sample data before live use"]

#### Manual Validation (Claude Outputs)
- **Method:** Compare Claude output to known good examples documented below
- **Frequency:** First output of each new session
- **Pass Criteria:** All fields match expected format and logic

#### Backtesting (if trading system)
- **Data Period:** [e.g., Last 6 months of TOS history]
- **Method:** [e.g., Feed historical data through Claude prompts, check verdicts]
- **Performance Threshold:** [Minimum acceptable metrics]

#### Code Testing (if technical project)
- **Method:** [e.g., Run with sample input file, verify output matches expected]
- **Tools:** [e.g., Python unittest / manual inspection]
- **Frequency:** [Every code change]

### 10.2 Known-Good Reference Examples

*Document verified correct outputs. Use these to validate Claude is working correctly.*

#### Example 1: [Name / Scenario]
**Input:**
```
[Paste the input that produces this output]
```
**Expected Output:**
```
[Paste the verified correct output]
```
**Notes:** [What makes this the correct answer]

#### Example 2: [Name / Scenario]
**Input:**
```
[Input]
```
**Expected Output:**
```
[Output]
```

### 10.3 Validation Checklist (Run at Session Start)

- [ ] [Check 1 â€” e.g., Account balance correct: $35,000]
- [ ] [Check 2 â€” e.g., Column order correct: PatternType before BreakoutVerdict]
- [ ] [Check 3 â€” e.g., Output is tab-delimited]
- [ ] [Check 4 â€” e.g., No fabricated diagnostic values]
- [ ] [Check 5 â€” e.g., Python output matches expected sample]

### 10.4 Known Issues & Limitations

| Issue ID | Description | Severity | Workaround | Status |
|---|---|---|---|---|
| [ID-001] | [Description] | [Critical / High / Medium / Low] | [Workaround] | [Open / Resolved] |
| [ID-002] | [Description] | [Severity] | [Workaround] | [Status] |

---

## 11. DAILY OPERATIONS & SESSION MANAGEMENT

### 11.1 Session Startup Checklist

*Run this at the start of every Claude session for this project.*

```
[ ] Open correct Claude Project (not default chat)
[ ] Paste SESSION_INITIALIZATION_PROMPT (if required for this system)
[ ] Confirm Claude acknowledges key parameters
[ ] Verify today's date is correct
[ ] Confirm account/system parameters are loaded
[ ] Run one validation check before proceeding
```

### 11.2 Daily Operating Procedure

**[Morning / Pre-Session]** (~[X] min)
1. [Action 1 â€” e.g., Check market posture / Pull scan results]
2. [Action 2 â€” e.g., Export data from TOS / VantagePoint]
3. [Action 3 â€” e.g., Open Claude project, paste init prompt]

**[Main Session]** (~[X] min)
1. [Action 1 â€” e.g., Run Step 1 for each candidate]
2. [Action 2 â€” e.g., Run Step 2 for BUY signals]
3. [Action 3 â€” e.g., Paste option chain data for Step 3]
4. [Action 4 â€” e.g., Log results in tracker]

**[Post-Session / Evening Review]** (~[X] min)
1. [Action 1 â€” e.g., Update trade outcomes]
2. [Action 2 â€” e.g., Paste review prompt to Claude]
3. [Action 3 â€” e.g., Note any system observations for Enhancement Log]

### 11.3 Monthly Maintenance

| Task | Frequency | Owner | Notes |
|---|---|---|---|
| [Parameter review] | Monthly | Anthony | [e.g., Update account balance if 10%+ growth] |
| [Performance review] | Monthly | Anthony | [Win rate by system / source] |
| [Project file cleanup] | Monthly | Anthony | [Remove superseded files, stay under limit] |
| [Prompt library update] | As needed | Anthony | [Refine prompts that produce drift] |
| [Schema version review] | Quarterly | Anthony | [Update if new columns needed] |

### 11.4 Parameter Registry

*Fixed values that apply to this system. Update date when changed.*

| Parameter | Value | Last Reviewed | Next Review |
|---|---|---|---|
| [e.g., Account Balance] | [$35,000] | [Jan 2026] | [Feb 2026] |
| [e.g., Risk per Trade] | [1.5%] | [Jan 2026] | [Feb 2026] |
| [e.g., Max Position] | [5% of premium] | [Jan 2026] | [Feb 2026] |
| [Parameter] | [Value] | [Date] | [Date] |

---

## 12. TROUBLESHOOTING & SUPPORT

### 12.1 Common Issues & Solutions

#### Issue: Claude gives wrong or unexpected output
- **Symptoms:** Output doesn't match known-good examples, format drift, wrong values
- **Root Cause:** Context window drift, missing session init, conflicting instructions
- **Solution:**
  1. Paste SESSION_INITIALIZATION_PROMPT
  2. Restate the specific rule being violated
  3. Show Claude a known-good example and ask it to match
  4. If persistent: open new session and re-paste init prompt
- **Prevention:** Always paste init prompt at session start

#### Issue: [System-specific issue â€” e.g., No signals generating / Scan returning wrong tickers]
- **Symptoms:** [What you see]
- **Root Cause:** [Why it happens]
- **Solution:**
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
- **Prevention:** [How to avoid]

#### Issue: [System-specific issue â€” e.g., Python script error / API timeout]
- **Symptoms:** [What you see]
- **Root Cause:** [Why it happens]
- **Solution:**
  1. [Step 1]
  2. [Step 2]
- **Prevention:** [How to avoid]

#### Issue: Claude repeating a corrected error
- **Symptoms:** Error that was fixed in a past session reappears
- **Root Cause:** Memory not carried forward, session context reset
- **Solution:**
  1. Check Error Corrections Log (Section 6) for documented fix
  2. Paste the specific rule that was violated
  3. Ask Claude to confirm understanding with an example
  4. If error recurs 2+ times, escalate to project knowledge update
- **Prevention:** Document all recurring errors in Section 6

### 12.2 Debug & Audit Trail

**Where to find outputs:**
- Claude session: [Current conversation]
- Tracker log: [File location / Sheet name]
- Error log: [How you track errors â€” e.g., Error Corrections Log in this doc]
- Code outputs: [Local path / GitHub]

**How to audit a past decision:**
1. [Step â€” e.g., Filter tracker by date and SignalSource]
2. [Step â€” e.g., Check Comments column for diagnostic values]
3. [Step â€” e.g., Locate original Claude session if needed]

### 12.3 Escalation Path

| Level | Condition | Action |
|---|---|---|
| Self-resolve | Minor output format issue | Restate rule, show example |
| Session reset | Persistent drift or wrong logic | New session + init prompt |
| Documentation update | Same error 2+ times | Add to Error Corrections Log (Section 6) |
| System redesign | Fundamental logic failure | Open Enhancement Log item, plan fix |

---

## 13. APPENDICES

### Appendix A: Glossary of Terms

| Term | Definition |
|---|---|
| [Term] | [Definition] |
| [Term] | [Definition] |
| [Term] | [Definition] |
| Session Init | Session Initialization Prompt â€” pasted at the start of each Claude session to load context |
| Project Knowledge | Files uploaded to a Claude Project that Claude can search during conversations |
| Prompt Drift | When Claude's outputs gradually deviate from correct format over a long session |
| Error Corrections Log | Section 6 of this document â€” permanent record of all discovered and fixed errors |

### Appendix B: Related Project Documentation

| Document | Location | Purpose |
|---|---|---|
| SESSION_INITIALIZATION_PROMPT.md | [Project Knowledge] | Paste at session start |
| [Strategy or Technical Guide] | [Project Knowledge] | Core system rules |
| [Schema Reference] | [Project Knowledge] | Output format definition |
| [Quick Reference] | [Project Knowledge] | Daily shorthand commands |
| [External resource] | [URL] | [Purpose] |
| **python-project-architecture SKILL.md** | C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\skills\python-project-architecture\SKILL.md | Hub-wide Python coding standards, layer rules, file delivery rules, documentation standards (cross-reference rule + artifact publish rule) -- read BEFORE writing any Python |

### Appendix C: Code Repository (if applicable)

| Field | Value |
|---|---|
| Repository | [GitHub URL / Local path / N/A] |
| Primary Language | [Python / ThinkScript / N/A] |
| Branch Structure | [main / dev / feature branches] |
| Key Files | [List critical files and their purpose] |
| Dependencies | [requirements.txt contents or equivalent] |

### Appendix D: Architecture Diagram (Detailed)

```
[Expand the high-level diagram from Section 2.1 here with more detail]
[Use ASCII art or describe each layer]

Example:

+--------------------------+
|   DATA INPUT LAYER       |
|  TOS Chart / VP Export   |
|  Screenshots / CSV       |
+-----------+--------------+
            |
            v
+--------------------------+
|   AI ANALYSIS LAYER      |
|   Claude.ai Project      |
|   Project Knowledge      |
|   Session Init Prompt    |
+-----------+--------------+
            |
            v
+--------------------------+
|   DECISION ENGINE        |
|   Scoring Logic          |
|   Rules / Thresholds     |
|   Filters / Gates        |
+-----------+--------------+
            |
            v
+--------------------------+
|   OUTPUT / EXECUTION     |
|   Tab-Delimited Rows     |
|   Excel Tracker          |
|   TOS Order Entry        |
+--------------------------+
```

### Appendix E: Performance Benchmarks (if applicable)

| Metric | Baseline | Target | Current | Last Updated |
|---|---|---|---|---|
| [e.g., Win Rate] | [%] | [%] | [%] | [Date] |
| [e.g., Avg R:R] | [X:1] | [X:1] | [X:1] | [Date] |
| [e.g., Signal Accuracy] | [%] | [%] | [%] | [Date] |
| [e.g., Code Execution Time] | [ms] | [ms] | [ms] | [Date] |

### Appendix F: Configuration Reference (if applicable)

```
# [System Name] â€” Key Configuration Parameters
# Last Updated: [Date]

# Core Parameters
account_balance       = [value]
risk_per_trade_pct    = [value]
max_position_pct      = [value]

# AI Settings
primary_ai_engine     = "[Claude / Local LLM / Other]"
model_version         = "[claude-sonnet-4-6 / etc.]"
session_init_required = [true / false]

# Platform Settings
primary_platform      = "[TOS / Python / Other]"
data_format           = "[CSV / XML / Screenshot]"

# [Additional system-specific parameters]
```

### Appendix G: Document Version Control

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 1.0 | [Date] | Anthony Zoppi | Initial document |
| [X.X] | [Date] | Anthony Zoppi | [Summary] |

**Review Schedule:** Monthly (or when system changes significantly)
**Last Review:** [Date]
**Next Review:** [Date]

---

**Document Classification:** Internal
**Document Owner:** Anthony Zoppi
**Template Version:** UNIVERSAL_PROJECT_TEMPLATE_v1_1
**Template Last Updated:** 2026-02-25
**Template Applies To:** All Anthony Zoppi Claude Projects and Local LLM Python Projects

---

*END OF DOCUMENT*

