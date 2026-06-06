# Gap 4: MOC and Index Standard

## Purpose
Define the navigation layer of the vault so sources, concepts, entities, and projects are discoverable through a small number of maintained index pages.

## Role of an MOC
A Map of Content is a curated hub note. It does not contain every detail. It points to the right pages and shows the structure of a topic area.

## Core index pages
- 05 MOCs/Global Index.md
- 05 MOCs/Trading Index.md
- 05 MOCs/LLM Architecture Index.md
- 05 MOCs/Research Methods Index.md
- 05 MOCs/Projects Index.md

Optional supporting MOCs:
- 05 MOCs/Source Intake Index.md
- 05 MOCs/Entity Index.md
- 05 MOCs/Contradictions Index.md
- 05 MOCs/Recently Updated.md

## MOC frontmatter
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

## MOC template
# {{title}}

## Purpose
One or two sentences explaining what this index covers.

## Start here
- 
- 
- 

## Concepts
- 

## Entities
- 

## Sources
- 

## Projects
- 

## Contradictions
- 

## Recently updated
- 

## Sub-indexes
- 

## Maintenance rules
- Each active topic cluster must have at least one MOC.
- Every mature concept should appear in at least one MOC.
- Every important entity should appear in at least one MOC.
- Every raw source should be reachable from the Source Intake Index.
- Update the relevant MOC every time a concept or entity is promoted.

## Global Index rules
The Global Index should be the top-level entry point for the vault. It should:
1. Link to every major MOC.
2. Show the current topic clusters.
3. Surface recent additions and active contradictions.
4. Point to the most used source, concept, entity, and project hubs.

## Topic Index rules
Each topic index should:
- group pages by subtopic,
- link to the most important concepts,
- link to the most relevant entities,
- link to a small set of representative sources,
- and note unresolved gaps.

## Contradiction Index rules
Create a contradiction hub when:
- two sources disagree,
- two concept notes conflict,
- or an entity has multiple meanings that need separation.

## Dataview queries
```dataview
TABLE topic_cluster, status, updated
FROM "05 MOCs"
SORT updated DESC
```

```dataview
LIST FROM "05 MOCs"
WHERE status = "active"
```

```dataview
TABLE children, related_concepts, related_entities
FROM "05 MOCs"
WHERE contains(file.name, "Index")
```

## Workflow
1. Create the Global Index first.
2. Create topic MOCs for each major cluster.
3. Add source, concept, and entity links as they appear.
4. Maintain a Recently Updated MOC for quick review.
5. Add a Contradictions MOC whenever disagreements start to matter.
6. Use MOCs as the primary entry point for query and review.

## Quality rules
- MOCs should be concise and curated.
- Do not let MOCs become dumping grounds.
- Keep topic MOCs intentionally selective.
- Every link should have a reason to be there.
- MOCs should make the vault easier to navigate, not noisier.

## Next gap to tackle
Gap 5 should define the Review and Lint Standard so the vault stays clean, accurate, and deduplicated over time.

Would you like Gap 5 now?