---
name: kb-review-convention
description: >
  Mark review status directly in an Obsidian KnowledgeBase article's frontmatter
  whenever it's read and judged for strategy relevance -- in ANY project, not just
  P_115. Triggers on any read of a file under trading_journal\KnowledgeBase\.
---

# kb-review-convention
v1.0 | Created 2026-07-06 | Hub-wide -- applies regardless of which project session is active

## Trigger
- Reading/reviewing any note under `trading_journal\KnowledgeBase\`
- Tony asks "does this article apply here" / "read this and determine relevance"

## Rule
Every KB article gets its review recorded in its own frontmatter -- not in a separate
tracker -- so status never drifts out of sync with the article.

Frontmatter fields to add/update:
```yaml
review_status: reviewed-no-match | reviewed-relevant | implemented
review_date: YYYY-MM-DD
disposition: <one line -- which strategy it applies to, or why it does not>
```

- `reviewed-no-match` -- read, judged, does not apply to any active strategy
  (P_115/116/117/118/300)
- `reviewed-relevant` -- read, judged relevant to a named strategy, not yet acted on
- `implemented` -- a change was made because of this article; `disposition`
  references the WO or doc section changed

## How to patch
Obsidian MCP `obsidian_patch_content` with `target_type: frontmatter` fails
(invalid-target / merge error) when the field doesn't already exist or a sibling
field is null. Reliable path: edit the file directly via Windows-MCP PowerShell --
read lines, find the frontmatter close (`---`), insert the three fields before it,
backup first (`Copy-Item path "$path.bak_<date>" -Force`), write back with
`[System.Text.UTF8Encoding]::new($false)` (no BOM).

## Sequence
1. Read the article (`obsidian_get_file_contents` or direct file read).
2. Judge relevance against active strategies.
3. Report the verdict to Tony in chat.
4. Patch frontmatter (method above) with review_status/review_date/disposition.
5. Confirm patch on disk before reporting done.

## Canonical source
This file. `P_000_SYSTEM_DOCUMENTATION.md` Section 8.4 points here rather than
duplicating the rule -- update this file only.

## History
- v1.0 (2026-07-06): created after MEAN-REVERSION and "Profitable Strategy" KB
  articles reviewed under P_115 session; convention needed to be Hub-wide since
  KB reviews happen from any project.
