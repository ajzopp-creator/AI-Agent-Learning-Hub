# Code Migration Gap Log

Running list of gaps found while working in Claude Desktop's Code tab instead of the Chat tab.
Direction agreed 2026-09-25 (recorded in WO-P000-E29.001): work in the pre-built Code-tab boot
sessions for a few mornings, log every gap here, then file one WO for the full Code migration
scoped from these real gaps.

One entry per gap: date found, project, what was missing, current workaround, fix needed (Y/N/later).

---

## G-001 -- No project grouping in the Code tab

- **Found:** 2026-09-26, P_400 (first live morning of the auto-boot)
- **What:** The Code tab has no Projects. It groups sessions by git repository, and the whole Hub
  is one repo, so P_115, P_300, P_400 and every other project share a single
  "AI-Agent-Learning-Hub" list.
- **Not affected:** Each session still runs in its own project folder and reads that folder's
  CLAUDE.md -- confirmed from Desktop's session store (P_400 session ran in
  projects\P_400_TradeOrderManagement).
- **Workaround:** The standard "P_xxx Day, Month DD, YYYY HH:MM ET" name prefix, plus the search
  icon at the top of the list to filter by project.
- **Fix needed:** Later -- revisit when scoping the migration WO.

---

## Findings

Observations about how well Code works, as opposed to gaps. These decide which projects move first.

### F-001 -- Code proven for WO work; trade analysis in Code untested

- **Found:** 2026-09-26, P_400 (WO work in the auto-booted Code session)
- **What:** Code was far more effective than Chat for WO work (Tony's assessment). It reads,
  edits and runs files directly, with no windows-mcp relay, 4-minute timeouts or PEH handoff scripts.
- **Open question:** Trade analysis leans on posture context, claude.ai Project knowledge files,
  memory and back-and-forth judgment. Whether a trade analysis session in Code holds up as well
  as one in Chat is untested.
- **Next test:** Run at least one P_115 trade analysis session in Code before deciding to move
  the trading side of the Hub.
