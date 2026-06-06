
Gap 3: Entity Note Standard

## Purpose
Define a normalized entity-note standard so people, companies, tickers, systems, tools, and datasets can be tracked consistently across the vault.

## Role of an entity note
An entity note is a stable reference object. It helps different source notes and concept notes point to the same real-world thing without duplicating names or meanings.

## Folder location
- 03 Entities/

Optional subfolders:
- 03 Entities/People/
- 03 Entities/Companies/
- 03 Entities/Tickers/
- 03 Entities/Systems/
- 03 Entities/Tools/

## Naming rules
- Use the canonical entity name.
- One entity per file.
- Examples:
  - Donald Trump.md
  - Apple Inc.md
  - NVDA.md
  - Obsidian.md
  - Claude Desktop.md

## Entity note frontmatter
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

## Entity note template
# {{title}}

## Identity
One clear paragraph describing what the entity is.

## Key facts
- 
- 
- 

## Why it matters
- 

## Related concepts
- 

## Related sources
- 

## Related entities
- 

## Usage notes
- How this entity appears in trading notes
- How this entity appears in research notes
- Any naming quirks or aliases

## Contradictions / ambiguity
- 

## Lifecycle notes
- If merged, note the canonical replacement.
- If deprecated, explain why.

## Promotion rules
Create an entity note when:
1. A name, ticker, system, or tool appears in 2 or more source notes.
2. The entity is important to search across the vault.
3. The entity needs alias handling or disambiguation.
4. The entity is referenced in concepts or projects often enough to justify its own page.

## Quality rules
- Prefer canonical names over nicknames.
- Add aliases for alternate spellings and shorthand.
- Link source notes back to the entity.
- Use one entity note for one real-world thing.
- Merge duplicates instead of letting them drift.

## Relationship rules
Every entity note should link to:
- at least 2 source notes
- at least 1 concept note if relevant
- any relevant project or system note

## Dataview queries
```dataview
TABLE entity_type, status, aliases, updated
FROM "03 Entities"
SORT updated DESC
```

```dataview
TABLE entity_type, length(related_sources) AS Sources, length(related_concepts) AS Concepts
FROM "03 Entities"
WHERE status = "active"
SORT length(related_sources) DESC
```

```dataview
TABLE aliases, identifier
FROM "03 Entities"
WHERE length(aliases) > 0
```

## Workflow
1. Capture raw source material.
2. Identify repeated names, tickers, systems, tools, or datasets.
3. Create or update the entity note.
4. Link the entity to source notes and concept notes.
5. Add the entity to the relevant MOC.
6. Merge duplicates when discovered.

## Examples
- People: traders, authors, analysts, newsletter writers
- Companies: vendors, competitors, brokers, research firms
- Tickers: NVDA, SPY, ES, NQ
- Systems: P115, P800, P010
- Tools: Obsidian, Claude Desktop, Dataview
- Datasets: Excel tracker, market posture JSON, source archive

## Next gap to tackle
Gap 4 should define the MOC and Index Standard so everything becomes navigable from a few central map notes.

Would you like Gap 4 now?