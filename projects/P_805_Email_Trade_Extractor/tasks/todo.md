# P_805 — Current State (todo.md)
Last updated: 2026-09-06 (sector data + parent_domain dedup + WO-P800-E5.001 criterion 4 session)

## Done this session (2026-09-06)
- Sector data: tagged 14 senders with confirmed/identified sectors (6 by
  same-domain match to an already-tagged sibling: analystratings.net x3,
  zacks.com x2, t3live.com; 7-8 identified via web research: Colibri
  Trader/Hima Reddy/BigTrends x2 -> technical or options, Hedgeye ->
  macro, MarketTaker -> options, Earnings Whispers -> analyst_ratings,
  Katusa Research -> new sector `resources`). Tagged the remaining 14
  no-public-info senders `Notclassified` (Tony's call, so they stand out
  for his own research later instead of sitting blank). ~7 low-confidence
  naming-pattern guesses (dividendbrief, elitetrade.club, chaikinanalytics
  x2, Kiyosaki, Michael Burry substack, mlquant) deliberately left blank —
  Tony's call, not filed as fact.
- parent_domain dedup: **dropped, not built.** KryptonStreet/MarketCrux
  footers show two different LLCs at two different addresses (Krypton
  Street Media 1717 LLC, Delray Beach FL vs. Headline Media LLC, St.
  Petersburg FL) — the "same publisher" premise this backlog item rested
  on doesn't hold. Building dedup around it would have silently understated
  consensus on any ticker where both fire. No other verified pair exists.
  Off the backlog until a real pair turns up.
- WO-P800-E5.001 criterion 4 closed out: staged a real message from
  `trading-protraderstrategies.com@shared1.ccsend.com` out of the live
  iCloud mbox, ran `--kb-mode full`. First run failed validation
  (`KBRecord` requires `signal_date`/`written_by`, neither auto-injected).
  Real bug in `application\p805_kb_writer.py`'s `build_kb_record()` — it
  only ever set the deprecated `date` field. Fixed: now sets `signal_date`
  and `written_by: "P_805/kb_writer"`. Re-ran clean — note landed in
  `KnowledgeBase\Newsletters\`, `.eml` deleted on success. This means
  every prior `--kb-mode` run (there had been none against a real `.eml`)
  would have failed the same way — not caught until this session.
- WO-P810-E1.001 Independent Review performed (separate session from the
  2026-08-20 build) — PASS, moved OWNER_DONE -> CLOSED. One unrelated
  anomaly flagged for Tony: a stray `docs\P805 IMAP OAuth.txt` (bare GUID,
  dated 8/23) sitting in the P_810 folder, likely misplaced from
  WO-P805-E2.001's Outlook OAuth2 work.

## Done this session (2026-08-24)
- WO-P805-E2.001 (Outlook OAuth2) Independent Review performed fresh, in a
  separate session from the 2026-08-23 build: live `--check-imap-auth
  --account outlook` re-run (PASS, silent refresh), full test suite re-run
  (23/23 passing), `.secrets\outlook_oauth_cache.bin` confirmed on disk,
  requirements.txt / MOVE_SKIP_ACCOUNTS / .gitignore all confirmed. **Status
  moved OWNER_DONE -> CLOSED.**
- New one-off diagnostic (peh-handoff, not merged into production python\):
  `Agentic-Hub-Governance\verify\run_this_P805_20260824_123944.py` scans
  INBOX + spam/junk mbox exports across all 4 accounts for senders not on
  `sender_sheet.csv` (enabled or disabled), writes
  `data\candidate_senders\<date>_candidate_senders.csv`. Read-only, no
  IMAP/keyring/LLM calls. Hit and fixed two real bugs before the good run:
  (1) path join used `config.IMAP_ROOT` instead of `config.PROFILE_ROOT`
  -- `MBOX_FILES`/`SPAM_MBOX_FILES` values already start with
  `ImapMail\`, so joining to IMAP_ROOT double-counted it and every mailbox
  silently resolved to a nonexistent path (false PASS, 0 candidates found,
  script still exited clean -- caught by Tony, not by the script's own PASS
  check); (2) `Subject` header read raw instead of through
  `domain.headers.decode_header_safe()` (the exact fix already documented
  as Entry 007 in this project's own system doc), leaving ~188 raw RFC 2047
  tokens across the report. Both fixed, re-verified: 343 unique candidates,
  0 raw tokens, PASS. New spam/junk mbox paths (not yet in config.py --
  this was a one-off, not promoted to a pipeline phase) confirmed on disk:
  icloud `ImapMail\imap.mail.me-1.com\Junk`, gmail
  `ImapMail\imap.gmail-1.com\[Gmail].sbd\Spam`, outlook
  `ImapMail\outlook.office365.com\Junk`, yahoo
  `ImapMail\imap.mail.yahoo.com\Bulk`.

## Status
Full daily pipeline live end to end: Phase 3 -> 3.5 -> 4 -> 5.3.
Scheduled task `P_805_Daily_Pipeline_915AM` -- daily 9:15 AM, Ready.
Phase 4 weights consensus by sector (`sector_count` column, live).
Outlook OAuth2 IMAP support is CONFIRMED LIVE (Entries 013/014/015) --
first browser login succeeded, `--check-imap-auth --account outlook`
passes silently on refresh. All four accounts now covered by Phase 5.3.

## Done this session (2026-08-23, v2.5)
- Tony re-ran `--outlook-oauth-login`: browser succeeded but terminal
  showed nothing -- traced to a missing `configure_logging()` call, the
  only `cli.py` path that skipped it
- Added `application/outlook_oauth_login.py` (new, thin wrapper matching
  imap_auth_check.py's pattern); cli.py now imports from there
- Verified fix live: `--check-imap-auth --account outlook` passes with
  visible output, no browser reopened (DPAPI cache round-trips correctly)
- Verified from msal_extensions source directly (not assumed):
  PersistedTokenCache.modify() auto-persists on every token op -- no gap
  in the silent-refresh path
- System doc bumped v2.4 -> v2.5, Entry 015 logged
- **Outlook OAuth2 is done. WO-P805-E2.001 awaiting Independent Review.**

## Done prior session (2026-08-23, v2.4)
- Tony's first live `--outlook-oauth-login` run crashed: WinError 1783
  writing the MSAL token cache to keyring (Windows Credential Manager
  caps a single entry ~1280-2560 chars; a real cache exceeds that)
- Found the fix already implemented on disk mid-session -- NOT written
  by this chat. Verified rather than trusted: read config.py,
  oauth2_outlook.py, requirements.txt, ran the full test suite
- Design found in place: msal-extensions' FilePersistenceWithDataProtection
  (DPAPI-encrypted file cache at python\.secrets\outlook_oauth_cache.bin),
  replacing the keyring approach entirely
- Found and fixed one real test bug: `patch.object()` fails on `Path`
  instances (uses `__slots__`) -- fixed via `patch("pathlib.Path.mkdir")`
- 10/10 tests passing after the fix
- `.gitignore` +`**/.secrets/` (defense in depth; `*.bin` already covered
  it incidentally via an unrelated model-file pattern)
- System doc bumped v2.3 -> v2.4, Entry 014 logged; WO-P805-E2.001 updated

## Done prior session (2026-08-23, v2.3)
- WO-P805-E2.001 opened and taken to OWNER_DONE (Independent Review still
  needed before CLOSED)
- Walked Tony through Azure AD app registration live, in-chat -- hit and
  fixed three real gotchas: personal outlook.com account landing in
  Microsoft's internal "Microsoft Services" tenant (fixed via free Azure
  signup), IMAP.AccessAsUser.All living under the Microsoft Graph
  permission picker not a separate Exchange Online API, and an
  `api.requestedAccessTokenVersion is invalid` error fixed via direct
  manifest edit
- Built `infrastructure/oauth2_outlook.py` (new) -- MSAL token cache
  lifecycle: get_access_token() (silent refresh), interactive_login()
  (one-time browser consent, Tony-run-only)
- `infrastructure/imap_mover.py._connect()` branches to XOAUTH2 for
  outlook via `config.OAUTH_ACCOUNTS`; all other accounts unchanged
- `cli.py --outlook-oauth-login` flag added
- `config.MOVE_SKIP_ACCOUNTS` reverted from `{"outlook"}` to empty
- `msal` added to requirements.txt and installed into p140
- 9 new tests (`tests/test_oauth2_outlook.py`) + 2 new tests extending
  `tests/test_imap_mover.py` (XOAUTH2 string format) -- 11/11 passing via
  PEH (`Agentic-Hub-Governance\verify\run_this_P805_20260823_094510.py`)
- System doc bumped v2.2 -> v2.3, Entry 013 logged

## Done prior session (2026-07-18, v2.2)
- Added `RankedSignal.sector_count` to schemas.py
- Added `load_sender_sectors()` to infrastructure/sender_sheet.py
- Wired domain/ranker.py + application/phase4_rank.py to compute sector_count
- Populated `sector` for 25 of 59 senders in sender_sheet.csv from real
  evidence (subject lines / raw_context across 4 days of signals history)
  -- did not guess sectors for senders with no real content to go on
- Flagged alex@kryptonstreet.ccsend.com / gary@marketcrux.ccsend.com as
  likely same publisher (same platform, same tickers same days, near-
  identical copy) -- tagged both momentum_promo; confirmed the mechanism
  catches it (GIPR -> sector_count=1 in the live test)
- Verified live: --phase 4 run against real 2026-07-18 signals, 25
  consensus tickers, sector_count column correct
- System doc bumped to v2.2

## Known issues -- carry forward
1. `P_805_daily_pipeline_mcp.ps1` did not launch the bat on first call from
   Windows-MCP PowerShell (no status file, no process spawned) -- see prior
   session note. Scheduled task calls the bat directly, unaffected.
2. NEW (v2.2): Windows-MCP PowerShell hangs (~4 min, transport error) on
   `python ... | Select-Object -Last N`-style piped calls, even for
   sub-second commands. Workaround: `Start-Process -Wait` with
   `-RedirectStandardOutput/-RedirectStandardError` to a file, then read
   the files separately. Confirmed reliable. See Entry 012 in system doc.
3. Hit a real PermissionError writing the ranked CSV because Tony had it
   open in Excel -- not a code bug, just close the file before Phase 4 runs
   during an interactive session.

## Queued (priority order)
1. Sector data -- confirmed/identified sectors written for 20 of the 34
   previously-untagged senders (2026-09-06); 14 tagged `Notclassified`
   (no public info, Tony's own read needed); ~7 low-confidence guesses
   left blank pending Tony's call. Fill in as real ticker-producing
   history accumulates or Tony confirms a guess.
2. ~~parent_domain dedup~~ DROPPED (2026-09-06) -- KryptonStreet/MarketCrux
   confirmed as two different LLCs, not one publisher. Off the backlog.
3. ~~Yahoo retention policy~~ DONE (2026-09-06) -- 10-day retention set.
4. ~~Outlook retention policy~~ DONE (2026-09-06) -- 10-day retention set.
   All four accounts now covered.
5. P_115 dashboard scoping (Tony's stated ultimate goal) -- design
   principle decided 2026-09-06: candidate list, not an auto-trigger.
   P_805 output sits at the same tier as P_117's subscription-service
   inputs (Big Trends/SNT) -- P_115's mandatory chart-pattern check and
   "analysis first, decide after" rule for outside signals stays intact,
   dashboard surfaces candidates for Tony to glance at and manually run
   through P_115's diagnostic. Tony's stated longer-term aspiration is
   full automation (P_115 diagnostic auto-gating on its own criteria,
   still no skipped checks) -- not building toward that yet, but noting
   it so today's structure doesn't foreclose it later.
   Tracker placement decided 2026-09-06: fold into P_117's existing
   "Outside Recommendations" bucket, no new distinct tier -- Tony doesn't
   need to separate newsletter-consensus signals from Big Trends/SNT
   right now (would only matter if he wanted to selectively pause just
   the email-sourced ones; reversible later if that changes).
   Still greenfield otherwise -- touches P_805 (source), P_800
   (dashboard/vault owns all display), and P_115 (tracker/consumer).
   No WO opened yet, no build started.

## Next session first task
If starting the P_115 dashboard scoping (talked through 2026-09-06, no
decision yet on P_115 auto-consumption vs. manual candidate report):
read P_115's own project context first -- this todo.md has no prior
integration notes to build from. Otherwise, retention policies and
both WOs are closed -- nothing else queued except sector data as it
accumulates history.
