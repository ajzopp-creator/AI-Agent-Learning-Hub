Gap 2: Concept Note Standard

## Purpose
Define a normalized evergreen concept-note standard so source notes can be distilled into reusable knowledge objects across Trading, LLM Architecture, Research Methods, and future systems.

## Role of a concept note
A concept note is not a raw source and not a project plan. It is a durable knowledge note that captures one idea clearly enough to be reused across multiple contexts.

## Folder location
- 02 Concepts/

Optional subfolders:
- 02 Concepts/Trading/
- 02 Concepts/LLM Architecture/
- 02 Concepts/Research Methods/

## Naming rules
- One concept per file.
- Title Case file names.
- Prefer the idea name, not the source name.
- Examples:
  - Stop Hunt.md
  - Retrieval-Augmented Generation.md
  - Contradiction Tracking.md
  - Market Regime Detection.md

## Concept note frontmatter
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

## Concept note template
# {{title}}

## Definition
A 2-4 sentence definition of the concept in your own words.

## Why it matters
- 

## Core mechanics
- 
- 
- 

## Signals / indicators
- 

## Common mistakes
- 

## Contrasts
- Compare with:
- Do not confuse with:

## Evidence from source notes
- [[Source Note 1]]
- [[Source Note 2]]

## Related concepts
- 

## Related entities
- 

## Open questions
- 

## Usage contexts
- Trading
- Research
- System design

## Promotion rules
A source note should become a concept note when at least one of these is true:
1. The same idea appears in 2 or more source notes.
2. The idea is important enough to be reused in decisions or prompts.
3. The idea is likely to need updating over time.
4. The idea benefits from contrasts, examples, or explicit contradictions.

## Quality rules
- One note, one idea.
- Write in your own words.
- Link back to source notes for evidence.
- Do not bury raw excerpts here unless essential.
- Explicitly note contradictions instead of flattening them.
- Update the concept note instead of making duplicates.

## Relationship rules
Every mature concept note should link to:
- at least 2 source notes
- at least 1 related concept
- at least 1 entity or project where relevant

## Dataview queries
```dataview
TABLE topic_cluster, concept_status, confidence, updated
FROM "02 Concepts"
SORT updated DESC
```

```dataview
TABLE concept_status, length(source_notes) AS Sources, length(related_concepts) AS Related
FROM "02 Concepts"
WHERE concept_status != "deprecated"
SORT length(source_notes) DESC
```

```dataview
TABLE contradicts, supersedes
FROM "02 Concepts"
WHERE length(contradicts) > 0 OR length(supersedes) > 0
```

## Workflow
1. Capture raw material as a source note.
2. Extract recurring ideas.
3. Promote the idea to a concept note when promotion rules are met.
4. Link the concept note to source notes, entities, and projects.
5. Update MOCs so the concept becomes discoverable.
6. Review mature concept notes monthly for drift or contradiction.

## Examples
- Trading: Stop Hunt, Absorption, Liquidity Void
- LLM Architecture: Retrieval, Tool Calling, Context Compression
- Research Methods: Source Triangulation, Hypothesis Tracking, Gap Analysis

## Next gap to tackle
Gap 3 should define the Entity Note Standard so people, companies, systems, and tickers connect cleanly to concepts and sources.

Would you like Gap 3 now?