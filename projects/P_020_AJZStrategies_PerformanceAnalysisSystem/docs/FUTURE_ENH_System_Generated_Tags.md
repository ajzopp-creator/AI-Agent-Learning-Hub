# Future Enhancement: System-Generated TOS Comment Tags

**Captured:** 2026-04-26
**Status:** Backlog — scope in a future session
**Priority:** Medium (quality-of-life; not blocking)
**Affects:** P_115, P_116, P_117, P_118, P_300, SNT, Day — all trading system projects
**Consumes:** P_020 (paper_import.py + ThinkLog tag format)

---

## The Idea

When any trading system project (starting with P_115 BTD) fires a BUY or PAPER
TRADE signal, it should emit a ready-to-paste tag string in the canonical
ThinkLog format:

```
MMDD: [WHY] [SIG] free text
```

Tony copies the string, pastes into the TOS order comment field, places the
trade. Zero typing, zero remembering vocabulary, zero risk of typos in the
WHY or SIG codes.

## Why This Matters

- Eliminates the only remaining manual step in the paper-trade tagging flow
- Forces vocabulary consistency at the source (system projects own their
  WHY code; no drift)
- Auto-fills the SIG code from whatever signal-strength logic the system
  already computes internally
- Free text portion can include the actual signal trigger (e.g. "RSI 28,
  bounce off 50DMA") so the DB notes column has real analytical content

## Proposed Architecture

A shared helper module that lives at the Hub level and is imported by every
system project:

```
C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\python\tag_emitter.py
```

Each system project calls it like:

```python
from tag_emitter import emit_tag

tag = emit_tag(
    why="BTD",
    sig=compute_signal_strength(),  # returns "A", "B", "C", "X"
    free_text=f"RSI {rsi:.0f}, bounce off {ma}DMA",
)
# Returns: "0427: [BTD] [A] RSI 28, bounce off 50DMA"
print(tag)  # or: clipboard.copy(tag), or: write to alert email/Slack
```

Each system project owns its own WHY constant (e.g. P_115 always emits
`why="BTD"`, P_116 always emits `why="OIL"`).

## Open Questions for Future Session

1. Do system projects have a shared signal_strength contract (A/B/C/X), or
   does each one compute strength differently?
2. Where does the emitted tag actually surface to Tony — clipboard, email,
   Slack, console print, alert popup?
3. Does P_115 currently have any output stage we'd plug into, or does this
   require new code at the alert level?
4. Should the helper auto-copy to clipboard on Windows (via `pyperclip` or
   `win32clipboard`) so Tony can immediately Ctrl-V into TOS?

## Prerequisites

- Validate the TOS-comment-field round trip first (Monday 2026-04-27).
  Confirm TOS preserves the comment string through CSV account statement
  export. If it doesn't, this whole feature is moot — switch to .md file flow.
- Decide WHY-code vocabulary (one per system) and lock it into
  `SESSION_INITIALIZATION_PROMPT_v2_7.md`.
- Decide SIG-code vocabulary (A/B/C/X meaning) and lock it into the same
  file.

## Implementation Sketch (90 minutes)

1. Read P_115 code, locate the alert/output stage
2. Write `tag_emitter.py` (~50 lines) with `emit_tag()` function
3. Add WHY constant + emit call to P_115's BUY signal path
4. Test: trigger a paper BTD signal, confirm tag string appears
5. Roll out to P_116, P_117, P_118, P_300, SNT, Day in order
6. Update SKILL.md vocabulary section with the locked-in WHY codes

## Why Not Now

- Crosses project boundaries (P_115 → shared_resources → P_020)
- Requires reading P_115 code I haven't seen
- TOS-comment-field flow isn't validated yet — Monday's first paper trade
  is the test
- Sunday-night scope creep for a Monday kickoff = bad bet

---

*Captured during P_020 session 2026-04-26 after delivering SKILL.md v1.4,*
*thinklog_parser.py, migration_add_tag_columns.py, paper_import.py.*
