# P_820 SYSTEM_DOCUMENTATION
## Order Signal Capture

---

**Project ID:** P_820
**Version:** 1.2
**Created:** 2026-08-16
**Last Updated:** 2026-09-06
**Owner:** Anthony Zoppi
**Status:** Active
**Template:** Adapted from UNIVERSAL_PROJECT_TEMPLATE_v1_1 -- condensed per the template's own Documentation Decision Protocol (architecture content here is under one page and specific to this project, so it stays in this master doc rather than a separate Interface-Arch-style file, matching P_800's practice for content that size).

---

## Section 1 -- Project Overview

### 1.1 Purpose

Captures the signal source for trades that never touch a Hub-built
scanner -- SNT, OIL/P_116, WSZ/P_117, Eddie Z/P_118 -- the exact gap
P_400 cannot close, since P_400 only ever sees P_115/P_300 packets
(confirmed live, P_020 session 2026-08-16: an archived packet sample
showed no other signal_source value). No evaluation logic -- viability
was already decided upstream, either by the subscription service or by
Tony personally verifying an idea through VantagePoint/WSZ.

**Second function, added 2026-09-04:** capturing a full discretionary/
override order when P_400's own `record` path structurally cannot
accept it -- e.g. a Council-BLOCKED verdict (R:R fail, macro freeze,
etc.) that Tony trades anyway. P_400's `record --order-id` only submits
a cached APPROVED/APPROVED_WITH_CAUTION/APPROVED_WITH_SEVERE_WARNING
verdict, by design -- no discretionary-override path exists there
(confirmed live 2026-09-04, CRUS/P_300 case: BLOCKED on R:R ~1.78:1, no
eval_cache present, `record` would refuse outright). P_820 is the
fallback record path for these trades -- it does not replace or
retroactively grant Council approval, it only preserves the fact the
trade happened.

### 1.2 Scope

**Covers:**
- Logging a dictated signal (symbol, date, source, entry/stop/target,
  notes) directly to the vault at or near order time
- Serving as the highest-priority source in P_020's attribution resolver
- Logging a discretionary/override order when the major-project
  pipeline cannot accept it -- e.g. P_400's `record` refuses a BLOCKED
  verdict, or no eval_cache exists for the symbol (added 2026-09-04)

**Does NOT cover:**
- Signal evaluation or scoring (P_115/P_300 own this)
- Position sizing, R:R validation, or options-gate checks (P_400 owns)
- Trade execution of any kind
- Performance analysis (P_020 owns)
- Retroactively approving a BLOCKED trade -- P_820 records that a
  discretionary trade happened, it does not grant Council approval
  after the fact (added 2026-09-04)

### 1.3 Project Details

| Field | Value |
|---|---|
| Start Date | 2026-08-16 |
| Current Status | Active |
| Primary AI Engine | Claude (Desktop, for vault write access) |
| Primary Platform | Obsidian vault (via P_800's `write_to_vault()` API) |
| Project Location | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_820_OrderSignalCapture\` |
| Related Projects | P_800 (vault write path owner), P_020 (sole consumer of P_820 data) |

**Suggested Claude Project description (for the Claude.ai project details field):**
> Thin capture utility -- logs trade signal sources that never touch a
> Hub scanner (SNT, OIL, WSZ, Eddie Z) by writing structured entries
> directly to the vault at dictation time. No code, no evaluation
> logic. Highest-priority source in P_020's attribution chain.

### 1.4 Reference Materials

| Document | Location | Notes |
|---|---|---|
| P_820_System_Initialization_Prompt_v1_0.md | `docs\` | Paste/trigger at session start |
| p820-project-context SKILL | `<Hub>\.claude\skills\p820-project-context\SKILL.md` | Field list, exact `write_to_vault()` call shape, P_115 routing table |

### 1.5 Definitions & Acronyms

| Term | Definition |
|---|---|
| P_820 | This project -- Order Signal Capture |
| why_code | Open-vocabulary field identifying the signal source (SNT, P_116, P_117, WSZ, etc.) -- becomes `trades.system` directly in P_020 |
| sig_code | Signal conviction, same convention as P_020's ThinkLog tags (A/B/C/X) |
| write_to_vault() | Public API in `shared_resources\python_utils\vault_interface.py`, owned by P_800 |
| P820Record | Pydantic schema (P_800-owned, `obsidian_writers\domain\vault_schemas.py`) validating every P_820 write |
| P_115/300/400/020 | See each project's own SYSTEM_DOCUMENTATION for full definitions |

---

## Section 2 -- Operating Rules

### 2.1 AI Behavior Rules & Constraints

**MUST:**
- Resolve `signal_date` to a real `YYYY-MM-DD` before writing -- never
  pass a relative string ("today", "yesterday") through to the vault
- Use snake_case for every `write_to_vault()` dict key -- PascalCase is
  silently dropped by Pydantic (same failure mode as every other Hub
  project's vault write)
- Read the file back after any `write_to_vault()` call to confirm
  fields landed -- a `True`/`PASS` return alone is not proof (Hub-wide
  rule)
- Route P_118/P_910/P_920 through P_115's evaluation first, then log
  the real source to P_820 -- see Section 4 routing table
- Route P_117 (email/newsletter, e.g. P_805 consensus) through P_115
  evaluation by default too -- same as above -- unless Tony calls the
  pick convincing enough on its own to skip evaluation and log straight
  to P_820 (Section 4 exception, corrected 2026-09-06)
- Route P_116/SNT to P_820 directly -- no P_115 involvement needed
  just to get a trade logged

**MUST NOT:**
- Add any evaluation, scoring, or verdict logic to P_820 -- viability
  is already decided upstream by the time a signal reaches here
- Create Python code for P_820 without a real second consumer beyond
  Claude's own `write_to_vault()` calls -- stays a scaffold-only
  project until that changes
- Silently overwrite a same-day, same-symbol entry that might be a
  genuinely distinct second signal rather than a correction -- flag it
  to Tony instead (no disambiguator exists yet for this case)

---

## Section 3 -- System Architecture

### 3.1 High-Level Flow

```
[Tony dictates a signal in chat]
         |
         v
[Claude resolves signal_date, builds the field dict]
         |
         v
[write_to_vault("P820", {...})  -- P_800's shared interface]
         |
         v
[P820Record validated, note written to
 trading_journal\TradeOrderManagement\P820\]
         |
         v
[P_020's p820_reader.py reads it on next weekly run or backfill --
 highest-priority match in the resolver chain: P_820 > ThinkLog >
 Tracker > default]
```

### 3.1b Override Order Flow (added 2026-09-04)

```
[Tony executes a trade P_400 Council BLOCKED, or that never got a
 cached evaluate/spec result]
         |
         v
[Claude confirms the trade's TRUE origin project for why_code --
 P_820 never becomes the attributed source itself]
         |
         v
[Claude builds the field dict: entry/stop/target from the actual fill,
 override context (BLOCKED reason, R:R, etc.) folded into notes --
 quantity/paper-real also go in notes until schema gains real fields]
         |
         v
[write_to_vault("P820", {...}) -- same mechanism, same schema, as
 Workflow 6.1]
         |
         v
[P820Record validated, note written to
 trading_journal\TradeOrderManagement\P820\ -- P_020 resolves it same
 as any other P_820 entry]
```

### 3.2 Core Components

#### Component 1: Capture (this project)
- **Responsibility:** Resolve a dictated signal into a valid field dict
  and call `write_to_vault("P820", ...)`.
- **Inputs:** Tony's spoken/typed signal at or near order time.
- **Outputs:** One `P820Record` note per signal.
- **Tools Used:** Claude (chat), `shared_resources.python_utils.vault_interface`.
- **Dependencies:** P_800's `write_to_vault()` API being live.

#### Component 2: Vault write path (P_800-owned, not this project)
- **Responsibility:** Validate against `P820Record`, build the frontmatter
  note, write to the correct folder.
- **Inputs:** The field dict from Component 1.
- **Outputs:** `trading_journal\TradeOrderManagement\P820\YYYY-MM-DD_SYMBOL.md`
- **Tools Used:** `obsidian_writers` package (Hub root).
- **Dependencies:** None -- P_820 is purely additive; no other schema's
  behavior changes.

#### Component 3: Resolver consumption (P_020-owned, not this project)
- **Responsibility:** Read P_820 notes, resolve to `trades.system`
  ahead of ThinkLog/Tracker/default.
- **Inputs:** Notes in the P_820 vault folder.
- **Outputs:** `system`/`reason`/`signal_strength` on matched trades.
- **Tools Used:** `infrastructure/p820_reader.py`, `domain/p820_override.py`,
  `application/p820_capture.py` (all P_020-owned).
- **Dependencies:** P_820 having a note for the relevant symbol/date
  within the 3-day forward-matching window.

### 3.3 Design Rationale

**Why this architecture?**
- **Simplicity:** No Python code needed in this project at all -- the
  entire mechanism is one function call P_800 already provides.
- **Reliability over ThinkLog:** ThinkLog requires a manual TOS export
  with no reliable cutoff, is watchlist-scoped at export time
  regardless of entry date, and returns one symbol per search
  (confirmed live, same-day: 2026-08-16 session). P_820 has none of
  these failure modes -- structured write, no export, no re-parsing.
- **Reuse over invention:** Vault write path, schema validation, and
  filename logic are all P_800's existing, tested machinery -- P_820
  adds one schema entry, not a parallel system.

**Alternatives considered:**

| Option | Pros | Cons | Decision |
|---|---|---|---|
| Extend ThinkLog parsing further | No new schema needed | Doesn't fix the export-lag/watchlist-scope/one-symbol-search problems -- those are TOS platform limits, not parser bugs | Rejected |
| Fold into P_020 as a module | Fewer moving parts | P_020 has no reason to own vault-write logic; couples an attribution consumer to a capture mechanism | Rejected -- Tony's call, kept as its own project for future flexibility |
| Standalone P_820 project (chosen) | Matches every other Hub project's vault-write pattern; room to grow if a second consumer appears | Slightly more overhead for a thin utility | **Selected** |

---

## Section 4 -- Signal Source Routing Rules

Confirmed directly with Tony, 2026-08-16 P_020 session. P_117 row
corrected 2026-09-06 -- see note below table. Do not route P_116/SNT
through P_115 just to get them into the Tracker -- that workaround
predates P_820 and is retired for those two sources.

| Source | Goes through P_115? | Why |
|---|---|---|
| P_118 (Eddie Z), P_910, P_920 | **Yes, always** | Genuinely evaluated by P_115's scoring engine. |
| P_116 (OIL) | **No** | Pure external swing-trade alert. Historical P_115 routing was only Tony fudging trades in to get them tracker-logged before P_820 existed. |
| P_117 (email/newsletter, e.g. P_805 consensus) | **By default, yes** | Genuinely evaluated through P_115 (SignalSource=P_117 in tracker) -- corrected 2026-09-06, reverses the original "No, by default" line below. **Exception:** Tony's judgment call per signal, not a fixed split -- skips straight to P_820 only when the pick (or an occasional convincing social-media post) is compelling enough on its own that he trades it without running P_115 evaluation. `why_code` stays `P_117` either way. |
| SNT | **No, never** | Pure subscription alert -- one option/week, pre-set stop+target, closes Friday. |

**2026-09-06 correction:** the row above originally read "No, by
default" for P_117, on the reasoning that P_115 routing was only ever
the pre-P_820 tracker-fudge workaround, same as P_116. Tony corrected
this directly: for P_117 specifically (email/newsletter picks,
including P_805's daily consensus), P_115 evaluation is the real
default -- most newsletter picks get the STEP 1 recheck. P_820 is the
exception path, used only when a pick is convincing enough on its own
that Tony skips evaluation entirely. This is a judgment call per
signal, not a percentage rule. P_116/SNT are unaffected -- those stay
workaround-free, straight to P_820.

**Override-order case (added 2026-09-04):** if the trade came from a
major-project pipeline (P_115/P_300/P_400) but was BLOCKED/failed there
and Tony traded anyway, `why_code` stays that project's own code (e.g.
`P_300`) -- never `P_820` or `OVERRIDE`. A P_820 write records that the
trade happened outside the pipeline's accept path; it never changes
attribution.

---

## Section 5 -- Folder Structure

```
C:\Users\Trader\AI-Agent-Learning-Hub\
|-- projects\
|   `-- P_820_OrderSignalCapture\
|       |-- README.md
|       `-- docs\
|           |-- P_820_SYSTEM_DOCUMENTATION.md      <- this file
|           `-- P_820_System_Initialization_Prompt_v1_0.md
|-- .claude\skills\p820-project-context\
|   `-- SKILL.md                                    <- field list, call shape, routing table
|-- obsidian_writers\                               <- P_800-owned, not this project
|   `-- (P820Record registered in domain/vault_schemas.py + schemas.py + config.py)
`-- trading_journal\
    `-- TradeOrderManagement\
        `-- P820\                                   <- vault output, one .md per signal
```

No `python\` folder -- by design, per Section 2.1 MUST NOT.

---

## Section 6 -- Workflows

### Workflow 6.1 -- Log a Signal (the only workflow)

**Trigger:** Tony dictates a trade signal in chat, in any session.
**Frequency:** Per signal, at or near order time.
**Time Required:** Under a minute.

**Steps:**
1. Tony states symbol, source, and whatever else is known (date,
   entry/stop/target, notes).
2. Claude resolves `signal_date` to `YYYY-MM-DD` explicitly if Tony
   said something relative.
3. Claude calls `write_to_vault("P820", {...})` per the field list in
   the skill file.
4. Claude reads the written note back to confirm fields landed.
5. Claude confirms to Tony in one line what was logged.

**Expected Output:** One `P820Record` note in
`trading_journal\TradeOrderManagement\P820\`.

**Decision gate:**
```
If source is P_118/P_910/P_920        --> confirm it already went through P_115, then log to P_820
If source is P_117 (email/newsletter) --> by default, confirm it went through P_115 first; log straight to P_820 only if Tony says this pick skipped evaluation
If source is P_116/SNT                --> log to P_820 directly, no P_115 step
If signal_date is relative             --> resolve to a real date before writing, never guess
If same symbol+date already logged today --> confirm correction vs. distinct second signal before overwriting
```

---

### Workflow 6.2 -- Log an Override Order (added 2026-09-04)

**Trigger:** Tony executed a trade that the major-project pipeline
either BLOCKED (Council verdict) or never evaluated (no eval_cache) --
P_400's `record` path structurally cannot accept it.
**Frequency:** Per override, at or near fill time.
**Time Required:** Under a minute.

**Steps:**
1. Confirm the trade's true origin project (e.g. P_300) -- `why_code`
   stays that project's code, never `P_820` or `OVERRIDE` (see Section
   4 override-case note).
2. Capture entry/stop/target from the actual fill.
3. Fold the override context into `notes` -- what blocked it and why
   (e.g. "Discretionary override -- BLOCKED on R:R ~1.78:1 in P_400
   Council, no eval_cache present"). Quantity and paper-vs-real go in
   `notes` too -- no dedicated schema field yet (Section 9.1 Known Gaps).
4. Call `write_to_vault("P820", {...})` per the field list in the
   skill file.
5. Read the written note back to confirm fields landed.
6. Confirm to Tony in one line what was logged.

**Expected Output:** One `P820Record` note in
`trading_journal\TradeOrderManagement\P820\`, same as Workflow 6.1.

**Decision gate:**
```
If P_400 BLOCKED the trade (or no eval_cache exists) and Tony traded anyway --> log to P_820, why_code = true origin project, override context in notes
If quantity or paper/real is known --> include in notes as free text (no schema field yet)
```

---

## Section 7 -- Error Corrections Log

*Permanent record, per Hub-wide convention. None yet -- this section
exists so a future error gets documented here rather than
rediscovered.*

| # | Date | Error | Correction | Severity |
|---|---|---|---|---|
| -- | -- | -- | -- | -- |

---

## Section 8 -- Session Log

| Date | Session Topic | Key Decisions |
|---|---|---|
| 2026-08-16 | Project inception, scoping | P_820 identified as the fix for ThinkLog's export fragility (no reliable cutoff, watchlist-scoped export, one-symbol-per-search). Scoped as a standalone project, not a P_020 module, per Tony's own reasoning: requirements will likely evolve and a dedicated project gives room to grow. |
| 2026-08-16 | Build session | P_800 schema registration (`P820Record`, 5 additive files, all existing tests unchanged), P_020 resolver wiring (`p820_reader.py`/`p820_override.py`/`p820_capture.py`, chain now P_820 > ThinkLog > Tracker > default), project scaffold + skill file. Full write-and-read-back smoke test and end-to-end integration test both passed. |
| 2026-08-16 | Routing rules | Worked through P_115/P_116/P_117/P_920/P_910/P_118/SNT routing directly with Tony. Corrected an initial assumption that P_116 evaluation via P_115 was real -- it was a tracker-logging workaround, now retired. Confirmed P_117's occasional P_115 fundamentals recheck is real and separate from that workaround. |
| 2026-09-06 | P_117 routing correction (P_805 session) | Tony corrected the 2026-08-16 P_117 rule: newsletter/P_805-sourced picks go through P_115 evaluation by default (SignalSource=P_117 in tracker); P_820 is the exception, used only when a pick is convincing enough on its own to skip evaluation. Judgment call per signal, not a fixed split. Section 4 table, Section 2.1 Musts, and Workflow 6.1 decision gate all updated same session (imperative sweep). P_116/SNT rows unchanged. |

---

## Section 9 -- Parameter Registry

| Parameter | Value |
|---|---|
| Project ID | P_820 |
| Project structure | Single project, scaffold only -- no Python code |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| Project folder | `...\projects\P_820_OrderSignalCapture\` |
| Docs folder | `...\projects\P_820_OrderSignalCapture\docs\` |
| Skill file | `...\.claude\skills\p820-project-context\SKILL.md` |
| Vault output folder | `trading_journal\TradeOrderManagement\P820\` |
| Vault write API | `shared_resources\python_utils\vault_interface.py` -- `write_to_vault("P820", {...})` |
| Schema owner | P_800 (`obsidian_writers\domain\vault_schemas.py` -- `P820Record`) |
| Sole data consumer | P_020 (`infrastructure/p820_reader.py`) |
| Resolver priority | P_820 > ThinkLog > Tracker Dashboard > default (`TOS_Import`) |
| Forward-match window | 3 days (`config.P820_MATCH_FORWARD_DAYS` in P_020) |
| Conda environment | p140 (not used directly by this project -- referenced for consistency) |
| Python skill level | Novice |
| VS Code skill level | Novice |

### 9.1 Known Gaps (added 2026-09-04)

- **No `quantity` field** in `P820Record` -- capture in `notes` as free
  text until a P_800-owned follow-on WO adds it properly.
- **No `trade_mode` (paper/real) field** -- same treatment, `notes` for
  now.
- **No `override_reason`/`is_override` field** -- override context
  currently lives entirely in free-text `notes`, not a queryable field.
  P_020's resolver can't yet filter/report on override trades
  separately from ordinary P_820 signal-source entries.
- Follow-on schema WO not yet opened -- P_800 owns `vault_schemas.py`,
  this doc only defines the requirement (WO-P820-E1.001).

---

*End of P_820 SYSTEM DOCUMENTATION v1.2 -- 2026-09-06*
