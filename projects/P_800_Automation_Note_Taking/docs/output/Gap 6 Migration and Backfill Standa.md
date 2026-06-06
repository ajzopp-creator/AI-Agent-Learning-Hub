Gap 6: Migration and Backfill Standard

## Purpose
Define how legacy notes are normalized into the new vault structure without losing history, provenance, or searchability.

## Role of migration
Migration moves notes into the new standard. Backfill updates older notes so they become compatible with the new system.

## What this covers
- existing raw notes
- old concept pages
- old entity pages
- old MOCs
- generated trade/system notes that predate the new schema

## What this does not cover
- rewriting original source documents
- deleting history
- changing the meaning of existing notes

## Migration principles
1. Preserve history.
2. Do not overwrite useful context.
3. Normalize metadata before content.
4. Backfill in batches.
5. Keep a migration log.
6. Mark uncertain mappings explicitly.

## Migration note location
- 07 Archive/Migration Logs/

Suggested files:
- 07 Archive/Migration Logs/Backfill Plan.md
- 07 Archive/Migration Logs/Migration Log.md
- 07 Archive/Migration Logs/Legacy Mapping Table.md

## Migration frontmatter
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

## Migration plan template
# {{title}}

## Scope
What is being migrated.

## Source state
What exists today.

## Target state
What the note should look like after migration.

## Mapping rules
- old frontmatter field -> new frontmatter field
- old file name -> new file name
- old folder -> new folder

## Exceptions
- 

## Risks
- 

## Backfill steps
1. Inventory the legacy notes.
2. Map each note to the new schema.
3. Fix frontmatter first.
4. Fix folder placement second.
5. Add backlinks and MOC links third.
6. Log the migration result.
7. Mark the note as migrated.

## Legacy mapping table
| Legacy item | New standard | Notes |
|---|---|---|
| source note | 01 Sources | Preserve raw source data |
| evergreen note | 02 Concepts | One idea per note |
| named thing | 03 Entities | People, companies, tickers, systems |
| hub note | 05 MOCs | Curated navigation |
| review note | 06 Reviews | Maintenance and lint |

## Backfill rules
- Backfill only after the schema is stable.
- Use the same migration logic for all old notes in the same class.
- Do not mix migration with content editing unless required.
- Keep original content intact whenever possible.
- Add a migrated-from field if useful.

## Dataview queries
```dataview
TABLE migration_status, coverage, risk_level, updated
FROM "07 Archive/Migration Logs"
SORT updated DESC
```

```dataview
TABLE legacy_path, new_path, migration_status
FROM "07 Archive/Migration Logs"
WHERE migration_status != "complete"
```

## Quality rules
- Every migrated note should be discoverable through an MOC.
- Every migration batch should produce a log entry.
- Never backfill blindly without a mapping table.
- If a legacy note does not map cleanly, leave a clear exception note.
- Prefer conservative migration over clever migration.

## Next gap to tackle
Gap 7 should define the Source Classification Standard so emails, articles, PDFs, web clips, and bookmarks are tagged and routed consistently.

Would you like Gap 7 now?