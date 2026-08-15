# p115-project-context -- Changelog Archive

Entries prior to 2026-08-03, moved out of SKILL.md during the 2026-08-06 compression pass (Tony directive) to cut load size. Verbatim, unedited.

---

### 2026-07-24
- P_115 Order Management removed (Tony directive). Architecture doc
  Section 8.2 changed from Position Sizing to Signal Emission -- P_400
  owns all sizing/R:R/stop/target/order-formatting decisions now
  (P_400 architecture doc Section 3.1), confirmed P_400's screen-all is
  fully source-agnostic (no P_400-side change needed for P_116/P_118/
  P_910/P_920 packets). schemas.py archived (dead code, unused
  VALID_SOURCES gate that would've blocked non-P_115/P_300 source tags
  if ever reconnected). File table row above corrected -- it pointed at
  POSITION_SIZING_THREE_GATE_REFERENCE.md, a file that never existed
  on disk; actual file is P_115_ Asset Sizing Requirements.md, now
  marked superseded. Note: found but did NOT fix -- LogEntry Field Order
  section below still says STR valid range is -1 to 2, but the 2026-07-08
  (update 4) entry below corrected it to -2 to 2; out of scope for this
  session's task, flagged for a future pass.

### 2026-07-24 (correction, same day)
- v1.3's Section 8.2 Step 3 wrongly had signal_source varying by
  P_115/P_116/P_118/P_910/P_920 (Tony caught this). Corrected in the
  architecture doc (v1.4): P_115 is the analytical process (V110 scoring
  engine) -- P_116/P_118/P_910/P_920 are scan sources / chart-pattern
  variants that feed candidates INTO P_115's analysis, not separate
  emitters. signal_source is always P_115 in the P_400 packet. strategy
  still carries the setup-type distinction (dip_buy/breakout/
  mean_reversion/support_bounce); scan/variant provenance is a
  27-column-tracker-level detail only. The schemas.py archival itself
  still stands (genuinely dead code either way) but the "would block
  P_116/P_118/P_910/P_920 tags" rationale in the entry below is wrong --
  those tags should never have gone in signal_source to begin with.
### 2026-07-08 (update 4)
- STR valid range corrected again: -2 to 2, not -1 to 2 as the 7/6/26
  correction had it. -2 is a legitimate falling-knife/regime reading, not
  out of range -- confirmed by repeated live LogEntry data across multiple
  tickers (WYFI, ANET-batch PASS rows) and the architecture doc's own
  FISV-style Cause A worked example, which uses STR=-2 as the falling-knife
  trigger alongside Fund=0. LogEntry Field Order section and Must-Not #2
  both updated.
### 2026-07-08 (update 3)
- Anti-pattern #17 added: the 27-column tab-delimited tracker row is owed
  on every BUY/ASYM immediately alongside the vault write, even on a
  single-ticker STEP 1->2->3 flow -- not just on batch STEP 1 runs. Missed
  live on ANET (P_118 BUY, 2026-07-08); vault write landed clean but the
  Excel row was never output until Tony asked for it retroactively.
### 2026-07-08 (update 2)
- Anti-pattern #16 added: `P115Record` requires `signal_date`/`run_date`/
  `run_ts`/`written_by` -- the deprecated `date` field alone fails Pydantic
  validation. Discovered live via PEH handoff on the ANET P_118 BUY write
  (2026-07-08_ANET.md, version 1, confirmed clean via readback -- no
  double-write despite an earlier MCP 4-minute timeout on the same script).
  Claude Code fixed the missing fields using the `P_118/session`
  `written_by` convention already established in `2026-07-06_JPM.md`.

### 2026-07-08- Initial build. Created under WO-P000-E6.001 (Gap 3 of the 2026-07-06
  context-engineering KB review — P_115 was one of three active projects
  with no project-context layer). Content sourced from
  `SESSION_INITIALIZATION_PROMPT.md` v3.4, `P_115_System_Architecture.v1.0.md`
  (EC log, scoring chain, schema), and accumulated session memory (vault-write
  lessons, STR range correction 7/6/26, P_910 SignalSource fix, P_920 Fund
  Verification gap).
