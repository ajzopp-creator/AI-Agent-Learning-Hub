You’re right — pasting a link or file reference keeps triggering the same issue. So I’ll paste the content directly here from now on.

# Gap 8: Prompt and Workflow Standard

## Purpose
Define the repeatable instruction set that runs the vault so capture, processing, querying, maintenance, and migration happen consistently.

## Why this matters
The vault structure only works if the prompts are stable. Without prompt standards, the same source can be processed differently each time, which creates drift, duplicates, and inconsistent indexing.

## Folder location
- `05 MOCs/Prompt Library/`
- `07 Archive/Prompt History/`

## Prompt categories
- Ingest prompts.
- Query prompts.
- Review prompts.
- Migration prompts.
- Maintenance prompts.
- Exploration prompts.
- Briefing prompts.

## Prompt library frontmatter
```yaml
---
title:
note_type: prompt
prompt_type: ingest | query | review | migration | maintenance | explore | brief
topic_cluster: Trading | LLM Architecture | Research Methods | General
status: active | deprecated
version: 1
created: YYYY-MM-DD
updated: YYYY-MM-DD
owner: P800
---
```

## Prompt note template
# {{title}}

## Use case
What the prompt is for.

## When to use
- 
- 
- 

## Prompt
```text
PASTE PROMPT TEXT HERE
```

## Expected output
- 

## Failure modes
- 

## Related prompts
- 

## Related notes
- 

## Prompt design rules
1. One prompt should do one job.
2. Use the same prompt structure every time.
3. Prefer explicit instructions over implied behavior.
4. Name the inputs clearly.
5. Name the desired output clearly.
6. State the order of operations if sequence matters.
7. Include a fallback action when the model is uncertain.
8. Keep prompts short enough to reuse but precise enough to avoid drift.

## Core workflows

### Ingest workflow
1. Read one source.
2. Summarize it.
3. Extract claims.
4. Link entities and concepts.
5. Flag contradictions.
6. Update index pages.
7. Log the action.

### Query workflow
1. Read the index.
2. Find the relevant source, concept, or entity notes.
3. Answer using only the vault.
4. Cite the notes used.
5. Create new notes if a new stable connection appears.

### Review workflow
1. Check for orphans.
2. Check for broken links.
3. Check for stale notes.
4. Check for duplicates.
5. Check for missing backlinks.
6. Check for unresolved contradictions.
7. Produce a report.

### Migration workflow
1. Map the legacy note.
2. Preserve history.
3. Backfill metadata.
4. Move or copy into the new folder.
5. Log what changed.

## Prompt quality rules
- Prompts must be written so another version of the model can follow them.
- Prompts should not depend on hidden context.
- Prompts should avoid vague phrases like “organize this better.”
- Prompts should specify the output format.
- Prompts should specify what to do when data is missing.
- Prompts should be versioned when behavior changes.

## Example prompt structure
```text
Read [SOURCE].
Create [OUTPUT TYPE].
Use [RULES].
Include [SECTIONS].
If [CONDITION], do [FALLBACK].
```

## Dataview queries
```dataview
TABLE prompt_type, status, version, updated
FROM "05 MOCs/Prompt Library"
SORT updated DESC
```

```dataview
TABLE prompt_type, status
FROM "05 MOCs/Prompt Library"
WHERE status = "active"
```

## What this unlocks
- Stable ingestion from raw material.
- Repeatable querying.
- Predictable review and linting.
- Consistent migration and backfill.
- Easier training of future workflows.

## Next step
Gap 9 should define the **System Command and Automation Interface Standard** so prompts can trigger the right workflow in a controlled way.

Should I continue with Gap 9 directly in chat?