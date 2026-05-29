---
name: file-back
description: File a finding from the current conversation back into the knowledge
  base. Use when the user says "file that back", "keep that", "remember this",
  or when a Q&A session produces a finding worth persisting. Applies the tagging
  convention and updates the relevant _summary.md.
---

# File Back to Knowledge Base

Persist a finding from the current conversation into the knowledge base so it
compounds for future sessions.

## When to Use

- User says "file that back", "keep that", "save this to knowledge"
- A Q&A exchange produced a corrected fact, new data point, or useful synthesis
- Research turned up something that should live in knowledge/ not just session logs

## Steps

### Step 1 — Identify the finding

Summarize what should be filed. If unclear, ask the user:
- "What specifically should I file back?"
- Show a one-line summary for confirmation

### Step 2 — Determine the target file

Based on the finding's content, select the appropriate target:

| Content type | Target |
|---|---|
| Fast-moving external landscape (tool/model capabilities, market or policy changes) | `knowledge/domain/landscape/<YYYY-MM>.md` |
| Durable domain research / synthesis | `knowledge/domain/<domain-slug>.md` |
| Stable scope / foundational facts (program, mandate, research question, framework) | `knowledge/foundations/<topic>.md` |
| Project operations (team, budget, timeline, governance, stakeholders) | `knowledge/project-management/<relevant-file>.md` |
| {{UNIT_NOUN}}-specific content | `knowledge/units/<unit-slug>/knowledge.md` |
| New source archive | `knowledge/sources/<type>/<filename>.md` |

Not every project keeps every area (setup prunes to the project type) — route to a target whose folder
exists; if the natural target was pruned, file under the nearest kept area. If the target is ambiguous,
ask the user to choose.

### Step 3 — Determine tags

Assess and apply:

- **Source**: Where did this finding come from?
  - `session-N` — emerged from conversation/Q&A
  - `web-scrape-URL` — from web research
  - `user-correction` — user corrected a prior fact
  - `inbox-file` — from processed inbox material

- **Verification**: How reliable is it?
  - `source-verified` — backed by a cited external source
  - `user-confirmed` — user explicitly endorsed this framing
  - `llm-derived` — synthesized by the LLM without independent verification

- **Confidence**: How well-supported?
  - `single-source` — one source only
  - `corroborated` — multiple independent sources agree
  - `contested` — sources disagree or finding is uncertain

### Step 4 — Append to target file

Add to the bottom of the target file (before any `## See Also` section):

```markdown
## [Topic] — YYYY-MM-DD
*Source: [value]*
*Verification: [value]*
*Confidence: [value]*

[content]
```

### Step 5 — Update _summary.md

If the target folder has a `_summary.md`, check whether:
- The Key Facts section needs updating (if this finding changes a key fact)
- A new file was created (add a row to Contents table)

### Step 6 — Add cross-links if needed

If the finding connects to other knowledge files, add entries to the target
file's `## See Also` section.

### Step 7 — Confirm

Report to the user:
- What was filed
- Where it was filed
- What tags were applied
- One line: "Filed. This will be visible to future sessions."
