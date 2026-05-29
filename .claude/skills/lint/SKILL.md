---
name: lint
description: Run a knowledge base health check. Invokes the knowledge-linter agent
  to scan all knowledge/ files for inconsistencies, staleness, orphans, gaps, broken
  links, and confidence issues. Use anytime, or when prompted by session-wrap.
---

# Knowledge Base Lint

Run a health check over the entire knowledge base.

## What This Does

Invokes the `knowledge-linter` agent (`.claude/agents/knowledge-linter.md`) which:
- Reads all files in `knowledge/`
- Regenerates `knowledge/LINK-GRAPH.md` from current See Also sections
- Applies 10 lint criteria (consistency, staleness, broken refs, orphans, coverage gaps,
  structural integrity, connection suggestions, near-duplicates, confidence audit,
  pitfall-recurrence)
- Produces a structured report at `working/review/knowledge-lint-<YYYY-MM-DD>.md`

## Steps

### Step 1 — Check for prior lint

Look in `working/review/` for the most recent `knowledge-lint-*.md` file.
Report to the user: "Last lint was on [date]" or "No prior lint found."

### Step 2 — Run the linter

Invoke the knowledge-linter agent. It will:
1. Read all knowledge/ files (including `_summary.md` files)
2. Apply all 10 lint criteria
3. Write the report to `working/review/knowledge-lint-<YYYY-MM-DD>.md`

### Step 3 — Report results

Tell the user:
- Critical issues count
- Warning count
- The single most important thing to fix first
- Whether any `_summary.md` files have stale data

### Step 4 — Offer to fix

Ask the user: "Want me to fix the critical issues now?"

If yes, address them in priority order. After fixing, re-run the relevant
lint checks to confirm resolution.
