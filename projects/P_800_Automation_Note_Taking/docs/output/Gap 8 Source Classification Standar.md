Gap 7: Source Classification Standard

## Purpose
Define how every incoming item is classified so raw material is routed consistently into the right folders and note types.

## Classification dimensions
Every source should be classified by:
- source_type
- source_channel
- topic_cluster
- priority
- processing_status
- confidence

## source_type values
- email
- article
- pdf
- webclip
- bookmark
- transcript
- screenshot
- note
- dataset

## source_channel values
- inbox
- browser
- newsletter
- clipboard
- download
- attachment
- export
- manual capture

## topic_cluster values
- Trading
- LLM Architecture
- Research Methods
- Operations
- General

## priority values
- urgent
- high
- normal
- low

## processing_status values
- inbox
- triaged
- extracted
- summarized
- linked
- archived

## Classification frontmatter
```yaml
---
title:
note_type: source
source_type: email | article | pdf | webclip | bookmark | transcript | screenshot | note | dataset
source_channel: inbox | browser | newsletter | clipboard | download | attachment | export | manual capture
topic_cluster: Trading | LLM Architecture | Research Methods | Operations | General
priority: urgent | high | normal | low
processing_status: inbox | triaged | extracted | summarized | linked | archived
confidence: low | medium | high
created: YYYY-MM-DD
updated: YYYY-MM-DD
owner: P800
---
```

## Source note routing rules
- email -> 01 Sources/Email
- article -> 01 Sources/Articles
- pdf -> 01 Sources/PDFs
- webclip -> 01 Sources/Web Clips
- bookmark -> 01 Sources/Bookmarks
- transcript -> 01 Sources/Transcripts
- screenshot -> 01 Sources/Screenshots
- note -> 00 Inbox or 01 Sources/Notes depending on state
- dataset -> 01 Sources/Datasets

## Source template
# {{title}}

## Source metadata
- Type:
- Channel:
- Topic cluster:
- Priority:
- Confidence:

## Extracted summary
- 

## Key claims
- 

## Tags and links
- 

## Next action
- summarize
- link
- promote to concept
- promote to entity
- archive

## Classification rules
1. Classify immediately on capture.
2. Use the best available source_type even if imperfect.
3. If the item can belong to multiple topic clusters, choose one primary cluster and add secondary tags.
4. If priority is uncertain, default to normal.
5. If the item is raw but useful, keep it in inbox until processed.

## Promotion rules
- source -> concept when the item contains reusable ideas
- source -> entity when the item introduces or updates a stable named thing
- source -> MOC when the item changes navigation or topic coverage
- source -> archive when it has been processed and linked

## Dataview queries
```dataview
TABLE source_type, source_channel, topic_cluster, priority, processing_status
FROM "01 Sources"
SORT created DESC
```

```dataview
TABLE source_type, source_channel, processing_status
FROM "00 Inbox"
SORT file.ctime DESC
```

```dataview
TABLE topic_cluster, priority, processing_status
FROM "01 Sources"
WHERE processing_status != "archived"
SORT priority DESC
```

## Quality rules
- Every item gets one primary classification.
- Do not let classification depend on memory alone; write it down.
- Keep source_type values constrained and reusable.
- Use routing rules consistently so future automation stays simple.
- Update the source note once classification changes.

## Next gap to tackle
Gap 8 should define the Prompt and Workflow Standard so the vault can be operated by a repeatable set of instructions.

Would you like Gap 8 now?