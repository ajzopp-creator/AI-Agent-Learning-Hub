---
name: p820-project-context
description: >
  P_820 Order Signal Capture -- thin utility for logging non-Hub-generated
  trade signals (SNT, OIL/P_116, WSZ/P_117, Eddie Z/P_118) at dictation
  time. Triggers on any reference to P_820, "log this trade", "log this
  signal", or Tony dictating a signal source live in chat. Always read
  BEFORE writing to the vault via write_to_vault("P820", ...).
---

# P_820 Project Context

## Purpose & Pairs With

Captures the signal source for trades that never touch a Hub-built
scanner -- SNT (Sunday Night Trader), OIL/P_116, WSZ/P_117, Eddie Z/P_118
-- the exact gap P_400 cannot close, since P_400 only ever sees P_115/
P_300 packets (confirmed live, P_020 session 2026-08-16: a real archived
packet sample never showed any other signal_source value). No evaluation
logic here -- viability was already decided upstream, either by the
subscription service itself or by Tony personally verifying an idea
through VantagePoint/WSZ before it becomes a real order.

Highest-priority source in P_020's resolver chain:
**P_820 > ThinkLog > Tracker Dashboard > default (TOS_Import)**.

Built to replace ThinkLog's structural fragility for these sources --
ThinkLog requires a manual TOS export with no reliable cutoff, is
watchlist-scoped at export time regardless of entry date, and only
returns one symbol per search (all confirmed live, same session). P_820
has none of these problems: Claude writes structured data directly, no
export step, no re-parsing, no typo risk from bracket/tag formatting.

---

## Critical Paths

| Path | Resolution |
| :---- | :---- |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| Project root | `<Hub>\projects\P_820_OrderSignalCapture\` (scaffold only -- no Python code, see below) |
| Vault output | `<Hub>\trading_journal\TradeOrderManagement\P820\` |
| P_020 reader | `<Hub>\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database\infrastructure\p820_reader.py` |
| P_020 resolver | `<Hub>\projects\...\python\database\domain\p820_override.py` |
| P_020 caller | `<Hub>\projects\...\python\database\application\p820_capture.py` |
| P_800 schema | `<Hub>\obsidian_writers\domain\vault_schemas.py` -- `P820Record` |

**Vault-write import (Hub canonical, no sys.path hack):**
`from shared_resources.python_utils.vault_interface import write_to_vault`

---

## How to Log a Signal

When Tony dictates a trade signal in chat, call:

```python
from shared_resources.python_utils.vault_interface import write_to_vault

write_to_vault("P820", {
    "symbol": "MRK",
    "signal_date": "2026-07-12",       # YYYY-MM-DD -- resolve explicitly,
                                        # never guess a relative date
    "why_code": "SNT",                 # open vocabulary: SNT, P_116,
                                        # P_117, WSZ, etc. -- becomes
                                        # trades.system directly in P_020
    "sig_code": "A",                   # optional
    "entry_price": 8.00,               # optional
    "stop_price": 3.65,                # optional
    "target_price": 9.15,              # optional
    "notes": "Buy-to-Open Aug Monthly 120 Call",  # optional
    "written_by": "P_820/chat_dictation",
})
```

`run_date`/`run_ts`/`note_version`/`write_route_history` are auto-injected
by P_800's `write_handler.py` -- never set them manually. `write_route`
has no meaning for P_820 (no verdict concept) and is always null.

**Resolve `signal_date` explicitly.** If Tony says something relative
("today", "yesterday", "last Tuesday"), convert it to a real date before
writing -- never pass a relative string through.

---

## P_115 Routing Rules (confirmed live, 2026-08-16 session)

Do not send a trade through P_115's STEP1/2 just to get it into P_820 or
the Tracker -- that workaround is retired now that P_820 exists.

| Source | Goes through P_115? | Why |
| :---- | :---- | :---- |
| P_118 (Eddie Z), P_910, P_920 | **Yes, always** | Genuinely evaluated by P_115's scoring engine -- confirmed in `p115-project-context`'s own Signal Source table and Fund Verification scope (V111 mandatory for P_118). |
| P_116 (OIL) | **No** | Pure external swing-trade alert. Historical P_115 routing was only ever Tony fudging trades into P_115 to get them tracker-logged before P_820 existed -- not real evaluation. |
| P_117 (email, verify via VantagePoint/WSZ) | **No, by default** | Same tracker-fudge history as P_116 by default. **Exception:** an occasional, deliberate P_115 fundamentals recheck (V111, stockanalysis.com ROE/Debt-Cap/FCF) is real and legitimate when Tony chooses it -- confirmed this happens often on interesting email finds. Even then, `why_code` stays `P_117`, never `P_115` -- P_115 touching a trade for a quality check does not change its source, same principle as any P_115-flagged idea Tony executes under a different system. |
| SNT | **No, never** | Pure subscription alert -- one option/week, stop+target pre-set, closes Friday. |

If a P_117 recheck happens, capture it in `notes` (e.g. `"Fund
Verification recheck via stockanalysis.com -- confirmed Tier 3"`) --
no schema field for this, free text is enough.

---

## Anti-Patterns (Forbidden by Construction)

1. **PascalCase vault-write dict keys** -- Pydantic silently drops them,
   same failure mode as every other Hub project's `write_to_vault()` call.
   snake_case only.
2. **Trusting `write_to_vault()`'s True/PASS return as proof** -- always
   read the file back to confirm fields landed (Hub-wide rule).
3. **Guessing a relative date** ("today", "yesterday") instead of
   resolving it explicitly before writing `signal_date`.
4. **Routing P_116/P_117/SNT through P_115** "to get it tracked" -- that
   workaround is retired; write to P_820 directly.
5. **Same symbol + same date logged twice same day** -- `overwrite=True`
   replaces the note in place. If it's a correction, that's correct
   behavior. If it's a second, genuinely distinct signal for the same
   symbol/date, flag it to Tony rather than silently overwriting -- no
   disambiguator exists yet for this case (known limit, not yet needed
   in practice as of this writing).

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (drafting)
- **Update trigger:** A new signal source added, a routing-rule
  correction (per the table above), or a real formatting/matching issue
  discovered in a live session (add here same session, per Hub-wide rule
  in `WO_COMPLETION_GATE.md`).

## Changelog

### 2026-08-16
- **Initial version.** Built same session as the P_800 schema
  registration (`P820Record`) and the P_020 resolver wiring
  (`p820_reader.py` / `p820_override.py` / `p820_capture.py`). Routing
  rules for P_115/P_116/P_117/SNT/P_910/P_920/P_118 worked through and
  confirmed directly with Tony before being written here.

---

**End of P_820 Project Context SKILL**
