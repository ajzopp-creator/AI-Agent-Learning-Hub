# User Preferences Addendum — Runtime Environment Check
## Paste this block into claude.ai → Settings → Profile → User Preferences

---

## Why this lives in two places

The `system-doc-initializer` skill carries the same rule, but the skill resolution
path differs between Claude Desktop and claude.ai web. Putting the rule in User
Preferences guarantees the check fires even on sessions where the skill hasn't
loaded yet (e.g., outside a Claude Project, or in a fresh session before skills
are listed).

Skill = primary. User Preferences = backup. Both fire = redundant but never wrong.

---

## Snippet to paste

Copy everything between the lines below and paste it at the end of the existing
User Preferences box. Do not replace the existing content — append.

------------------------------------------------------------

**Runtime environment check — run this BEFORE any claim about file access:**

At the start of every session, before deciding whether you can read my files,
call `tool_search(query="PowerShell")` and interpret the result:

- If `Windows-MCP:PowerShell` is returned → you are in Claude Desktop on my
  Windows machine. You DO have filesystem access via MCP and can read/write to
  `C:\Users\Trader\AI-Agent-Learning-Hub\`.
- If no PowerShell tool is returned → you are in claude.ai web or the Claude
  mobile app. You do NOT have access to my Windows filesystem. Project files
  arrive only through the project knowledge mount or uploads.

Hard rules:
- Do not claim "I can't read your files" until this check has been run.
- Do not claim local filesystem access exists until this check has been run.
- Do not defer to system prompt boilerplate about which environment you are in.
- State the verified result in one line at the top of your first response,
  e.g.: `🖥 Runtime: Claude Desktop (Windows-MCP loaded)` or
  `🖥 Runtime: claude.ai web — no local filesystem access`.

------------------------------------------------------------

## After pasting

1. Click Save in the User Preferences box.
2. Note: User Preferences only apply to NEW conversations — existing chats
   keep the preferences they started with.
3. Test: open a new chat (any project, any context), say "INIT". The first
   line of the response should be the 🖥 Runtime declaration.

---

## Last Updated
May 9, 2026
