<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Sad here they

Here is the cleaned, copy/paste-ready **final implementation checklist** for the P800 Obsidian vault, consolidated from the master architecture and gaps 1–7. I tightened the architecture into one build order, removed overlap, and kept the standards aligned across source notes, concept notes, entity notes, MOCs, review/lint, migration/backfill, and source classification.[^1][^2][^3][^4][^5][^6][^7][^8]

## P800 implementation checklist

### 1) Build the vault skeleton

- Create the top-level folders exactly as the master architecture defines: `00 Inbox`, `01 Sources`, `02 Concepts`, `03 Entities`, `04 Systems`, `05 MOCs`, `06 Reviews`, and `07 Archive/Migration Logs`.[^8]
- Under `01 Sources`, create the capture subfolders: `Email`, `Articles`, `PDFs`, `Web Clips`, `Bookmarks`, `Transcripts`, `Screenshots`, and `Datasets`.[^8]
- Keep `04 Systems` available for future system notes even though it is not yet fully specified in the gap set.[^8]


### 2) Lock the source-classification standard

- Classify every incoming item immediately using the shared fields: `source_type`, `source_channel`, `topic_cluster`, `priority`, `processing_status`, and `confidence`.[^7][^8]
- Use the allowed values exactly as defined, especially for `source_type` and `processing_status`, so future automation stays consistent.[^7]
- Route items by source type into the correct source folder, with `00 Inbox` reserved for uncaptured or not-yet-triaged material.[^1][^7]


### 3) Standardize source notes

- Use one source note per raw input, and keep the source note separate from evergreen concepts.[^1]
- Use the source frontmatter fields from the master doc and Gap 1, including `title`, `source_type`, `source_system`, `author_or_sender`, `received_or_published`, `url`, `attachment_path`, `related_tickers`, `topic_cluster`, `status`, `processed`, `summary_status`, `contradiction_status`, `concept_links`, `entity_links`, `created`, and `updated`.[^1][^8]
- Ensure each source note has at least a summary, key claims, related concepts, related entities, and contradictions/open questions.[^1]
- Process raw sources within the vault’s stated operating window and do not archive them until they are linked.[^1]


### 4) Standardize concept notes

- Create concept notes only for reusable ideas, not raw sources or project plans.[^3][^8]
- Use the concept frontmatter fields: `title`, `note_type`, `topic_cluster`, `concept_status`, `aliases`, `source_notes`, `related_entities`, `related_projects`, `related_concepts`, `contradicts`, `supersedes`, `confidence`, `created`, `updated`, and `owner`.[^3][^8]
- Keep the note to one idea per file, written in your own words, with a definition, why it matters, core mechanics, contrasts, evidence from sources, and open questions.[^3]
- Promote an idea into a concept note when it appears repeatedly, is useful for decisions or prompts, needs updating over time, or benefits from explicit contrasts.[^3]


### 5) Standardize entity notes

- Create entity notes for stable named things such as people, companies, tickers, systems, tools, and datasets.[^4][^8]
- Use canonical names and one entity per file, with aliases for alternate spellings or shorthand.[^4]
- Use the entity frontmatter fields: `title`, `entity_type`, `status`, `aliases`, `related_concepts`, `related_sources`, `related_projects`, `related_entities`, `identifier`, `region`, `industry`, `created`, `updated`, and `owner`.[^4][^8]
- Promote an entity note when the thing appears in multiple sources, needs disambiguation, or must be searchable across the vault.[^4]
- Make sure each important entity links back to sources and, when relevant, to at least one concept note.[^4]


### 6) Build the MOC layer

- Create the core index notes first: Global Index, Trading Index, LLM Architecture Index, Research Methods Index, Projects Index, Source Intake Index, Entity Index, Contradictions Index, and Recently Updated.[^5][^8]
- Use the MOC frontmatter fields: `title`, `note_type`, `topic_cluster`, `status`, `children`, `related_mocs`, `related_concepts`, `related_entities`, `related_sources`, `updated`, and `owner`.[^5][^8]
- Keep MOCs curated and selective; do not let them become dumping grounds.[^5]
- Update the relevant MOC whenever you promote a source to a concept, an entity, or a navigational hub.[^5]


### 7) Install the review and lint loop

- Create review notes in `06 Reviews` for daily, weekly, monthly, and quarterly maintenance.[^6][^8]
- Use review notes to manage inbox processing, MOC updates, contradiction resolution, and taxonomy audits.[^6]
- Run lint for missing frontmatter, missing backlinks, orphans, duplicates, stale notes, broken links, missing contradiction flags, MOC coverage gaps, wrong-folder placement, and unprocessed sources.[^6][^8]
- Treat critical lint issues as blockers before adding more notes.[^6]


### 8) Add migration and backfill controls

- Put migration logs in `07 Archive/Migration Logs` and keep legacy mapping work there.[^2][^8]
- Use the migration frontmatter fields: `title`, `note_type`, `migration_status`, `source_system`, `legacy_path`, `new_path`, `coverage`, `risk_level`, `created`, `updated`, and `owner`.[^2][^8]
- Backfill in batches, preserve history, normalize metadata before content, and log every batch.[^2]
- Do not overwrite useful legacy context or do speculative cleanup during migration.[^2]


### 9) Enforce the operating model

- Capture fast, classify immediately, extract source notes, promote reusable ideas to concepts, promote stable names to entities, navigate through MOCs, maintain through review/lint, and migrate old material only through the backfill process.[^8]
- Keep the rule set simple: raw and temporary goes to Sources, reusable and conceptual goes to Concepts, stable named things go to Entities, navigation goes to MOCs, cleanliness goes to Reviews, and legacy normalization goes to Migration Logs.[^8]
- Use Dataview as the standard reporting layer for source queues, concept status, entity status, MOC maintenance, review reports, and migration tracking.[^7][^2][^3][^5][^6][^4][^1]


## Final build order

1. Create folders.[^8]
2. Install source classification and source templates.[^7][^1]
3. Install concept and entity templates.[^3][^4]
4. Build core MOCs.[^5]
5. Add review and lint notes.[^6]
6. Add migration logs and legacy mapping tables.[^2]
7. Start classifying new intake immediately.[^7][^8]

## Cleaned architecture rule

The vault should maintain a strict separation between raw material, reusable ideas, stable named things, navigation, maintenance, and migration history.[^2][^3][^4][^5][^6][^1][^8]

If you want, I can turn this next into a **single master Obsidian checklist note** in final markdown form, with headings and checkboxes ready to paste into your vault.
<span style="display:none">[^9]</span>

<div align="center">⁂</div>

[^1]: Gap-1-Unified-Inbox-and-Source-Note.md

[^2]: Gap-6-Migration-and-Backfill-Standa.md

[^3]: Gap-2-Concept-Note-Standard.md

[^4]: Gap-3-entity-Note-Standard.md

[^5]: Gap-4-MOC-and-Index-Standard.md

[^6]: Gap-5-Review-and-Lint-Standard.md

[^7]: Gap-8-Source-Classification-Standar.md

[^8]: P800-Master-Obsidian-Vault-Architecture.md

[^9]: Gap-8-Prompt-and-Wrkflow-Standards.md

