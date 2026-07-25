# P_805 — Current State (todo.md)
Last updated: 2026-07-18 (v2.2 session)

## Status
Full daily pipeline live end to end: Phase 3 -> 3.5 -> 4 -> 5.3.
Scheduled task `P_805_Daily_Pipeline_915AM` -- daily 9:15 AM, Ready.
Phase 4 now weights consensus by sector (`sector_count` column, live).

## Done this session (2026-07-18, v2.2)
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
1. Sector data -- 34 of 59 senders still untagged, fill in as they
   accumulate ticker-producing history
2. parent_domain dedup -- KryptonStreet/MarketCrux case; not yet built
3. Yahoo retention policy -- set 10-day retention once Yahoo's
   ExtractedNewsletterFolder has content
4. Outlook OAuth2 -- deferred, not currently planned

## Next session first task
Confirm the 9:15 AM scheduled run actually fired unattended and check
`python\logs\pipeline_runs.log` for a clean run. Also worth checking
whether sector data can be extended now that more signals history exists.
