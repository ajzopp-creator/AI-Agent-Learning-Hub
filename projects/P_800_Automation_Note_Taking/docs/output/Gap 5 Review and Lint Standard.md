Gap 5: Review and Lint Standard

## Purpose
Define the maintenance workflow that keeps the vault accurate, deduplicated, linked, and free of silent drift.

## Role of review
Review is the human maintenance loop. It catches ambiguity, weak links, stale notes, and unresolved contradictions before they compound.

## Role of lint
Lint is the structural health check. It scans the vault for missing links, orphan notes, stale timestamps, broken references, duplicated ideas, and incomplete metadata.

## Review cadence
- Daily: clear inbox and process new source notes.
- Weekly: update MOCs, review new concepts and entities, resolve obvious contradictions.
- Monthly: run full lint across the vault.
- Quarterly: review taxonomy, naming, and archive policy.

## Review note location
- 06 Reviews/

Suggested review files:
- 06 Reviews/Daily Review.md
- 06 Reviews/Weekly Review.md
- 06 Reviews/Monthly Lint Report.md
- 06 Reviews/Quarterly Vault Audit.md

## Review frontmatter
```yaml
---
title:
note_type: review
review_type: daily | weekly | monthly | quarterly
status: open | complete
scope: inbox | sources | concepts | entities | mocs | full_vault
findings: []
actions: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
owner: P800
---
```

## Review template
# {{title}}

## Scope
What was reviewed.

## Findings
- 
- 
- 

## Actions
- 
- 
- 

## Contradictions found
- 

## Orphans found
- 

## Stale notes found
- 

## Duplicates found
- 

## Lint categories
1. Missing frontmatter.
2. Missing backlinks.
3. Orphan notes.
4. Duplicate concepts or entities.
5. Stale updated timestamps.
6. Broken links.
7. Contradiction flags missing.
8. MOC coverage gaps.
9. Notes in wrong folder.
10. Sources not processed.

## Lint report structure
Each lint report should include:
- severity: critical / high / medium / low
- issue description
- affected notes
- recommended fix
- owner
- due date

## Dataview queries
```dataview
TABLE review_type, status, updated
FROM "06 Reviews"
SORT updated DESC
```

```dataview
TABLE findings, actions
FROM "06 Reviews"
WHERE review_type = "monthly"
SORT updated DESC
```

```dataview
TABLE file.name, file.mtime
FROM "02 Concepts"
WHERE file.mtime < date(today) - dur(90 days)
SORT file.mtime ASC
```

## Lint workflow
1. Check frontmatter completeness.
2. Verify backlinks exist.
3. Find orphan notes.
4. Find duplicate concepts and entities.
5. Flag stale notes older than the configured threshold.
6. Check MOC coverage for all active clusters.
7. Confirm sources marked processed have been linked.
8. Export a lint report with severities and actions.

## Quality rules
- Never let lint findings sit unresolved indefinitely.
- Resolve critical issues before adding new notes.
- Use review notes to turn maintenance into a repeatable process.
- Track recurring problems as process issues, not just one-off mistakes.
- Update the rules if the same lint issue appears repeatedly.

## Next gap to tackle
Gap 6 should define the Migration and Backfill Standard so old notes can be normalized without losing history.

Would you like Gap 6 now?