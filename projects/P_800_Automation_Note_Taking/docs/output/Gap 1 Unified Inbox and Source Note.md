Gap 1: Unified Inbox and Source Notes

## Purpose
Create a single capture and processing layer for emails, articles, PDFs, bookmarks, and other raw sources in Obsidian.

## Folder structure
- 00 Inbox/
- 01 Sources/
  - Email/
  - Articles/
  - PDFs/
  - Web Clips/
  - Bookmarks/

## Processing states
- inbox
- triaged
- summarized
- linked
- reviewed
- archived

## Source note frontmatter
```yaml
---
title:
source_type: email | article | pdf | webclip | bookmark
source_system:
author_or_sender:
received_or_published: YYYY-MM-DD
url:
attachment_path:
related_tickers: []
topic_cluster:
status: inbox
processed: false
summary_status: draft
contradiction_status: none
concept_links: []
entity_links: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

## Source note template
# {{title}}

## Summary

## Key claims
- 

## Quotes worth keeping
- 

## Related concepts
- 

## Related entities
- 

## Contradictions / open questions
- 

## Processing rules
1. Dump raw material into 00 Inbox or directly into the appropriate 01 Sources subfolder.
2. Within 24 to 72 hours, triage each item.
3. Convert each item into a source note.
4. Link source notes to at least 2 concept or entity notes.
5. Update the relevant MOC after processing.
6. Mark contradictions explicitly instead of burying them in prose.
7. Move completed source notes to Archive only after they are linked.

## Dataview queries
```dataview
TABLE source_type, source_system, received_or_published, status, topic_cluster
FROM "01 Sources"
WHERE status = "inbox" OR status = "triaged"
SORT received_or_published DESC
```

```dataview
TABLE source_type, source_system, topic_cluster, processed, contradiction_status
FROM "01 Sources"
WHERE processed = false
SORT file.ctime DESC
```

```dataview
LIST FROM "05 MOCs"
```

## Recommended operating rules
- One source note per source.
- One inbox item should become one source note, even if long.
- Never leave a raw source unprocessed for more than 72 hours.
- Never archive a source until it has at least two outgoing links.
- Keep source notes separate from evergreen concept notes.
- Use tags sparingly; rely on folders, frontmatter, and links first.

## Next gaps to tackle
1. Define the concept/entity note standards.
2. Define the MOC/index structure.
3. Define migration/backfill rules for old notes.
4. Define the lint/review workflow.

Would you like Gap 2 now?