# P_300 — Chaikin MCP Pull Runbook

**File:** `docs/processes/chaikin_mcp_pull.md`
**Version:** 1.1
**Status:** Live operator runbook
**Last Updated:** 2026-09-04
**Audience:** Anthony Zoppi
**Pairs With:** `RunChaikinBatch.ps1` (Hub-root), `shared_resources\chaikin_enrichment\`, WO-P300-E4.009, WO-P800-E4.001

---

## Purpose

Session-driven replacement for the `claude -p --chrome` step when it fails. Not
unattended automation — a human still has to open a chat and say "run the
Chaikin batch." What it replaces is the broken part: the headless
native-messaging bridge. This runbook uses the same `claude-in-chrome` MCP
tools any Claude session with the connector enabled already has — no CLI
subprocess, no bridge to reconnect.

**When to use this:** `RunChaikinBatch.ps1 -Schema P300` ran, the red banner
fired (or you just want to skip the CLI path entirely), and real Power Gauge
data still needs to land in today's vault notes.

**When NOT to use this:** if `RunChaikinBatch.ps1` itself hasn't run yet —
run it first regardless of whether the Chaikin call inside it succeeds. It's
still the thing that determines today's actionable BUY/WATCH list and
resolves exact note paths. This runbook consumes that output; it doesn't
replace the scanning/filtering step.

---

## 1. Get today's candidate list

`RunChaikinBatch.ps1 -Schema P300` (run via the normal DailyEval batch or
standalone) writes the resolved candidate list to:

```
C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\chaikin_enrichment\_last_prompt.txt
```

This file's `NOTE_TABLE` section has each symbol already paired with its
exact vault note path — skip-list filtering already applied, no path
guessing needed. Read it directly:

```
windows-mcp:FileSystem mode=read, path=..._last_prompt.txt
```

Confirm the file's `info` timestamp is today's before trusting it — a stale
`_last_prompt.txt` from a prior day is the same M-054 risk as any other
cached artifact.

## 2. Confirm the domain is approved (one-time, already done)

`members.chaikinanalytics.com` is in the extension's "Your approved sites"
list as of 2026-08-21 (persistent, browser-level, ref M-113). If a
permission prompt appears anyway, ask Tony to click Approve once — see
M-113 for the two known Anthropic-side bugs that can cause this, and the
one-off-vs-repeatable threshold for when it's worth investigating further.

## 3. Pull each symbol

For each symbol/note-path pair from step 1, in order:

1. `claude-in-chrome:navigate` to `https://members.chaikinanalytics.com/pgr/stock/{TICKER}`
   — the main company page, NOT `/20-factors` (that page renders the four
   category ratings as bar gauges only and is missing the Quick Stats
   block entirely — a real mistake made and caught during the first run
   of this runbook, 2026-08-21).
2. `claude-in-chrome:get_page_text` on the same tab.
3. **If the result looks empty or placeholder** (zero-width characters,
   "N/A" rating with no Quick Stats values) — this is very likely a
   page-load race, not real no-coverage, especially for any liquid/
   well-known symbol. Re-run `get_page_text` once before concluding
   anything. Confirmed real on 2026-08-21 (CBOE): first read empty,
   second read complete.
3b. **If the page returns "Oops! Something went wrong. Please try again
   later."** — before treating this as a real failure, retry once at
   `https://members.chaikinanalytics.com/pgr/etf/{TICKER}` (note `/etf/`,
   not `/stock/`). `/pgr/stock/{TICKER}` throws this exact error for ETF
   tickers; it is a wrong-URL-template symptom, not an engine fault, and
   reads identically to a real error unless you know to check the other
   path. Confirmed 2026-09-04 (SARK): `/pgr/stock/SARK` "Oops!" on three
   separate sessions (08-28, 09-03, 09-04) before the `/pgr/etf/SARK`
   path was checked and resolved cleanly to Rating: None / unrated. If
   `/pgr/etf/{TICKER}` also errors or 404s, it's a genuine failure —
   report per step 5 below (no-coverage) or as Failed, not retried
   further.
4. Extract exactly per `chaikin_prompt_template.txt`'s existing field
   list (Rating, Price, Quick Stats — Fundamentals/Technicals/
   Performance/Earnings/Ratios/Dividends — and the Power Gauge Summary
   paragraph(s), verbatim). Do not invent a value that isn't on the page;
   write the field's real displayed value (including literal `N/A` where
   the page shows it).
5. **No-coverage rule unchanged from the template:** Rating widget shows
   "None" AND the page states the symbol is unrated — skip the note
   entirely, report as no-coverage, don't append a stub section. A
   price quote alone is not evidence of coverage.
6. Append the `## Chaikin Power Gauge` section (exact format in
   `chaikin_prompt_template.txt`) to the note via
   `windows-mcp:PowerShell` `Add-Content -Encoding utf8` — do not touch
   frontmatter or any existing section.
7. Verify immediately: `Select-String -Pattern "## Chaikin Power Gauge" -Quiet`
   on the file just written. Don't move to the next symbol on an
   unverified write.

## 4. Close out

- Close any browser tab(s) opened for this (`claude-in-chrome:tabs_close_mcp`)
  — don't leave scratch tabs open.
- Report results in the same three buckets the template already specifies:
  Updated / No-coverage / Failed. Don't hedge or merge them.
- Do a final independent sweep across every symbol pulled — LastWriteTime
  and `## Chaikin Power Gauge` presence, matched against what was actually
  extracted per symbol — before telling Tony it's done. Console/tool-call
  success is not itself evidence; the file is.
- Log a `todo.md` entry (F2 — state changed, mandatory) naming which
  symbols were pulled this way, since it's a different mechanism than the
  automated pipeline and future sessions need to know which path produced
  which note.

---

## Known limitations

- **Not unattended.** Requires an open Claude session with `claude-in-chrome`
  connected and a human to kick it off. Does not run at 6am on its own.
  True unattended automation (Chrome extension native scheduling, or a
  properly verified headless MCP configuration in Claude Code — NOT the
  `--chrome` flag's own bridge, which is what's broken) remains an open
  question, not attempted as of this runbook's creation. See WO-P300-E4.009.
- **Approval dependency.** Relies on the domain already being in "Your
  approved sites." See M-113 if that ever needs re-establishing.
- **Page-load races.** `get_page_text` can return before client-side JS has
  finished populating the page. Always sanity-check an apparently-empty or
  all-N/A result before treating it as real, per step 3 above.

---

## Version History

- **2026-09-04 (v1.1)** — Added step 3b: an "Oops! Something went
  wrong" response on `/pgr/stock/{TICKER}` is a wrong-URL-template
  symptom for ETF tickers, not a real engine error — retry at
  `/pgr/etf/{TICKER}` before reporting Failed. Root-caused after SARK's
  identical "Oops!" was misdiagnosed as a recurring engine fault across
  three separate sessions (08-28, 09-03, 09-04); Tony's screenshot of
  `/pgr/etf/SARK` showed a clean unrated-ETF page the whole time. Same
  failure shape the existing skip-list ETF entries (XYLD/BITX/CRPT/CLIX)
  were already evidence of — this runbook just never carried the check.
- **2026-08-21 (v1.0)** — Initial release, written the same session this
  method was first proven: 8/8 real symbols pulled and independently
  verified (AGCO, CBOE, CLSK, GLPI, GPK, MSCI, RIOT, YUM), after
  `claude -p --chrome` was confirmed structurally broken (headless
  native-messaging bridge, extension/auth otherwise fine — see
  WO-P300-E4.009's 2026-08-21 entries).

---

**End of Chaikin MCP Pull Runbook**
