---
name: doc-editor
description: >
  Read, edit, and rewrite project documentation files. Triggers when the user
  wants to update, correct, revise, or add content to any Markdown or text doc
  in the Hub — including architecture docs, skill files, READMEs, and project
  notes. Use this skill whenever the user says "update the doc", "add this to
  the architecture file", "fix the system doc", "rewrite section X", or pastes
  doc content and asks for changes. Also triggers when a session produces new
  decisions that should be recorded in a living document.
---

# doc-editor

Reads a documentation file, applies the user's requested changes, previews
the diff, then — if more than one line changed — rewrites the full document
and delivers a downloadable `.md` artifact.

---

## Step 1 — Locate the File

Check in order:
1. User provided a full path → use it directly
2. User named a file → search project knowledge base for a match
3. User described a doc → ask for the filename before proceeding

State the resolved path in one line before continuing.

---

## Step 2 — Read the Document

Load the full file contents into context. If the file exceeds 500 lines,
confirm with the user which section to target before loading the rest.

---

## Step 3 — Apply the Changes

Make the requested edits in memory. Follow these rules:

- Preserve all existing formatting, headers, and section order unless the
  user explicitly asks to restructure
- Never remove content unless instructed
- Maintain the document's versioning convention if one exists (e.g. `v1.10`)
- Increment the version number by one patch level (e.g. `v1.10` → `v1.11`)
  unless the user specifies otherwise
- Update the `Last Updated` line to today's date if one exists

---

## Step 4 — Show the Diff

Present a compact before/after diff in the chat. Format:

```
CHANGED — Section: [section name or line reference]
BEFORE: [original text]
AFTER:  [revised text]
```

If only one line changed → show the diff and stop. No file rewrite needed.
State: `Single-line change — no file rewrite required.`

If more than one line changed → proceed to Step 5.

---

## Step 5 — Rewrite and Deliver

Rewrite the complete document with all changes applied. As you rewrite,
compress the document: remove redundant phrases, verbose explanations, and
filler words. Preserve all meaning and structure — shorten the language, not
the content. Every sentence should earn its place.

Deliver as a downloadable artifact:

```
📥 DOWNLOAD READY: [filename].md
📁 Save to: C:\Users\Trader\AI-Agent-Learning-Hub\[original file path]
```

Publish the artifact BEFORE giving save instructions.

After delivery, state the version change in one line:
`📌 Version bumped: v1.10 → v1.11 — [one-line summary of what changed]`

---

## Edge Cases

| Situation | Action |
|---|---|
| File not found in knowledge base | Ask user to paste the content directly |
| User says "just show me the changes" | Stop after Step 4 regardless of line count |
| User says "rewrite it anyway" | Skip the 1-line check, go straight to Step 5 |
| No version number in doc | Do not add one — preserve the doc's existing conventions |
| User pastes new content to append | Treat as an insert at the end of the relevant section |
