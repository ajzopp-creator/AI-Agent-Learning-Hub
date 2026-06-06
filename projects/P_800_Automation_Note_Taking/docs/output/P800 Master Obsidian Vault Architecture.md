# P800 Master Obsidian Vault Architecture

## Purpose
This document defines a personal knowledge base for capturing emails, articles, PDFs, bookmarks, and other raw inputs, then turning them into a searchable Obsidian vault.

## Architecture summary
The vault uses five layers:
1. Inbox and source intake.
2. Source notes for raw material.
3. Concept notes for reusable ideas.
4. Entity notes for stable named things.
5. MOCs, review notes, migration logs, and archive for navigation and maintenance.

## Folder structure
- 00 Inbox/
- 01 Sources/
  - Email/
  - Articles/
  - PDFs/
  - Web Clips/
  - Bookmarks/
  - Transcripts/
  - Screenshots/
  - Datasets/
- 02 Concepts/
- 03 Entities/
- 04 Systems/
- 05 MOCs/
- 06 Reviews/
- 07 Archive/
  - Migration Logs/

## Operating model
### 1. Capture
Dump raw material into Inbox or the matching source subfolder quickly.

### 2. Classify
Assign each item a source_type, topic_cluster, priority, and processing_status.

### 3. Extract
Convert each source into a source note with summary, key claims, and links.

### 4. Promote
Promote repeated or reusable ideas into concept notes and named things into entity notes.

### 5. Navigate
Maintain MOCs and indexes so the vault can be entered from a few curated hubs.

### 6. Maintain
Run daily review, weekly cleanup, and monthly lint.

### 7. Migrate
Backfill old notes into the new structure using migration logs.

## Source note standard
A source note records one raw input.

### Frontmatter
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

### Template
# {{title}}

## Summary

## Key claims
- 

## Related concepts
- 

## Related entities
- 

## Contradictions / open questions
- 

## Next action
- summarize
- link
- promote to concept
- promote to entity
- archive

## Concept note standard
A concept note captures one reusable idea in your own words.

### Frontmatter
```yaml
---
title:
note_type: concept
topic_cluster: Trading | LLM Architecture | Research Methods | General
concept_status: seed | active | mature | deprecated
aliases: []
source_notes: []
related_entities: []
related_projects: []
related_concepts: []
contradicts: []
supersedes: []
confidence: low | medium | high
created: YYYY-MM-DD
updated: YYYY-MM-DD
owner: P800
---
```

### Promotion rules
Create a concept note when an idea appears repeatedly, affects decisions, or needs contrasts and examples.

## Entity note standard
An entity note captures a stable named thing like a person, company, ticker, system, tool, or dataset.

### Frontmatter
```yaml
---
title:
entity_type: person | company | ticker | system | tool | dataset | source
status: active | inactive | merged | deprecated
aliases: []
related_concepts: []
related_sources: []
related_projects: []
related_entities: []
identifier:
region:
industry:
created: YYYY-MM-DD
updated: YYYY-MM-DD
owner: P800
---
```

### Promotion rules
Create an entity note when a name must be searched, disambiguated, reused, or linked across many sources.

## MOC and index standard
Use curated navigation hubs instead of relying on memory or search alone.

### Core MOCs
- Global Index
- Trading Index
- LLM Architecture Index
- Research Methods Index
- Projects Index
- Source Intake Index
- Entity Index
- Contradictions Index
- Recently Updated

### MOC frontmatter
```yaml
---
title:
note_type: moc
topic_cluster: Trading | LLM Architecture | Research Methods | Global
status: active | maintenance | deprecated
children: []
related_mocs: []
related_concepts: []
related_entities: []
related_sources: []
updated: YYYY-MM-DD
owner: P800
---
```

## Review and lint standard
Use review notes as the maintenance loop.

### Cadence
- Daily: process inbox.
- Weekly: update MOCs and resolve obvious contradictions.
- Monthly: run full lint.
- Quarterly: audit naming, taxonomy, and archive policy.

### Lint checks
- Missing frontmatter.
- Missing backlinks.
- Orphans.
- Duplicates.
- Stale notes.
- Broken links.
- Missing contradiction flags.
- MOC coverage gaps.
- Wrong folder placement.
- Unprocessed sources.

## Migration and backfill standard
Backfill old notes conservatively and log the process.

### Principles
- Preserve history.
- Do not overwrite useful context.
- Normalize metadata before content.
- Backfill in batches.
- Keep a migration log.

### Migration frontmatter
```yaml
---
title:
note_type: migration
migration_status: planned | in_progress | complete
source_system:
legacy_path:
new_path:
coverage: partial | full
risk_level: low | medium | high
created: YYYY-MM-DD
updated: YYYY-MM-DD
owner: P800
---
```

## Source classification standard
Classify each item immediately and route it to the right place.

### source_type values
- email
- article
- pdf
- webclip
- bookmark
- transcript
- screenshot
- note
- dataset

### processing_status values
- inbox
- triaged
- extracted
- summarized
- linked
- archived

## Dataview starter queries
```dataview
TABLE source_type, topic_cluster, priority, processing_status
FROM "01 Sources"
SORT created DESC
```

```dataview
TABLE concept_status, confidence, updated
FROM "02 Concepts"
SORT updated DESC
```

```dataview
TABLE entity_type, status, updated
FROM "03 Entities"
SORT updated DESC
```

```dataview
TABLE title, updated
FROM "05 MOCs"
SORT updated DESC
```

## Recommended implementation order
1. Build folders.
2. Create source note template.
3. Create concept note template.
4. Create entity note template.
5. Create MOCs.
6. Add review notes and lint workflow.
7. Add migration logs.
8. Start classifying incoming sources.

## Practical rule
If a note is raw and temporary, it belongs in Sources.
If it is reusable and conceptual, it belongs in Concepts.
If it is a stable named thing, it belongs in Entities.
If it helps you navigate, it belongs in an MOC.
If it keeps the system clean, it belongs in Reviews.
If it is old history being normalized, it belongs in Migration Logs.

Would you like me to paste Gap 1 next?