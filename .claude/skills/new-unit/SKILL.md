---
name: new-unit
description: Scaffolds all files needed to begin developing a single unit of work (a
  {{UNIT_NOUN}} — e.g. a course, theme, topic, or work-package, depending on the project).
  Usage: /new-unit <slug> <full name>   Example: /new-unit market-entry "Market Entry Analysis"
---

# New {{UNIT_NOUN}} Scaffolding

Create all the files needed to start developing a detailed plan for one {{UNIT_NOUN}}.

> The "unit" concept and its naming were set at `/setup-project`. In this project a unit is a
> **{{UNIT_NOUN}}**, and unit folders are named `{{UNIT_NUMBERING}}` (numbered `01-slug` or slug-only).

## Input Expected

The user provides:
- **Slug**: lowercase, hyphens (e.g. `market-entry`). Prefix with a zero-padded number only if this
  project uses numbered units (`{{UNIT_NUMBERING}}`).
- **Full name**: the human-readable {{UNIT_NOUN}} name.

If not provided, ask the user for both before proceeding.

## Step 1 — Create Knowledge File

File: `knowledge/units/<slug>/knowledge.md`

```markdown
# {{UNIT_NOUN}} Knowledge: [Full Name]
*Folder*: knowledge/units/<slug>/
*Created*: YYYY-MM-DD

## Overview
[What this {{UNIT_NOUN}} is and why it is in scope — pull from the foundational scope file]

## Current State
[Leave blank — to be populated from sources or user input]

## Relevance / Angle
[Leave blank — how this unit connects to the project goal and analytic framework]

## Key Sources
[Leave blank — links to knowledge/sources/ files relevant to this unit]

## Notes
[Leave blank]

## See Also
- `../../foundations/` — project scope and framework
```

## Step 2 — Create Planning File

File: `working/planning/<slug>-<YYYY-MM-DD>.md`

```markdown
# Plan: [Full Name]
*Date*: YYYY-MM-DD
*Status*: Scaffolded — not yet planned

## Objectives
[To be completed]

## Options / Approaches Under Consideration
[List the candidate approaches for this unit]

## Open Questions
[To be completed]
```

## Step 3 — Create Report Stub

File: `outputs/reports/units/<slug>-current.md`

```markdown
# {{UNIT_NOUN}} Report: [Full Name]
*Status*: Stub — not yet written
*Last Updated*: YYYY-MM-DD

[Content to be added by Writing Agent]
```

## Step 4 — Update ARTIFACTS.md

Add the new {{UNIT_NOUN}} to the **Knowledge Inventory** table and (if applicable) the
**Unit-Level Reports** table in `ARTIFACTS.md`.

## Step 5 — Confirm

Report to the user:
- Three files created (knowledge, planning stub, report stub)
- What to do next: populate the knowledge file from `knowledge/foundations/`, then run the
  Research Agent for this unit, then Planning Agent, then Writing Agent
