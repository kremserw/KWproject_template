---
name: setup-project
description: First-run setup for a fresh copy of the knowledge-work project template. Runs a guided
  interview (project name, goal, type, outputs, domains, framework, units, collaborators, language,
  cadence), then dispatches the project-initializer agent to fill in every config file and tailor the
  folder structure. Auto-invoked by session-start when the .template-uninstantiated sentinel is present;
  can also be run manually.
---

# Setup Project (First-Run Bootstrap)

Turn this fresh template copy into a configured project for the user's specific purpose.
You run a short interview, confirm the answers, then hand a structured brief to the
`project-initializer` agent which writes all the files. **You do not write project files
yourself** — keep the interview thin and let the agent do the writing in one reviewable place.

## Step 0 — Confirm we should run

```bash
test -f .template-uninstantiated && echo OK || echo ALREADY-CONFIGURED
```
- `OK`: proceed.
- `ALREADY-CONFIGURED`: tell the user the project looks already set up and ask whether to re-run
  setup (default: no). Only continue if they confirm a deliberate re-instantiation.

Open with: *"I'll ask a handful of questions in five short groups. Say 'default' to accept the
suggested answer. At the end I'll build out the whole project for you — and `git checkout .` undoes
it all if it's not what you wanted."*

## Step 1 — The interview

Ask the groups below. Use `AskUserQuestion` for the multiple-choice items (Groups B, E); use plain
prompts for free-text. Carry sensible defaults so a user can move fast.

### Group A — Identity (free text)
1. **Project name** — human-readable (e.g. "Renewable-Energy Policy Review"). → `PROJECT_NAME`
2. **One-line goal** — what success looks like, one sentence. → `PROJECT_GOAL`
   - Derive and show for confirmation: **repo slug** = lowercase-hyphen of the name (→ `REPO_SLUG`);
     **session-log prefix** = the slug (→ `SESSION_PREFIX`).

### Group B — Type & Outputs (multiple choice)
3. **Project type** — pick one (this drives how the knowledge base is pruned): → `PROJECT_TYPE`
   - `literature-review` — a research question + analytic framework; ingest papers; output a synthesis/review
   - `knowledge-base` — a topic/phenomenon KB that feeds presentations & reports
   - `admin-project` — an administrative project (mandate, budget, timeline, stakeholders); output memos/proposals
   - `curriculum-redesign` — a multi-course program redesign (the original shape this template came from)
   - `course-redesign` — a single course
   - `blank` — none of the above; keep everything and prune later
4. **Primary output types** (multi-select; default per preset): reports / presentations / memos /
   synthesis / deliverables. The first becomes `CANONICAL_OUTPUT`. → `OUTPUT_TYPES`

### Group C — Domain & Framing (free text; all skippable)
5. **Key knowledge domains / themes** — 2–6, comma-separated. Seeds the `knowledge/domain/` files
   and the INDEX "What This Project Is". → `DOMAINS`
6. **Analytic framework or central research question** — if any (a competency model, a PICO question,
   a thesis, a decision framework). Default: none. → `ANALYTIC_FRAMEWORK`
7. **The "unit" of work** — what the repeatable atom is called (singular + plural) and whether units
   are numbered. Default per preset: curriculum→"course/courses, numbered"; course-redesign→none;
   literature-review→"theme/themes, slug"; knowledge-base→"topic/topics, slug";
   admin-project→"work-package/work-packages, slug". → `UNIT_NOUN`, `UNIT_NOUN_PLURAL`, `UNIT_NUMBERING`

### Group D — Collaboration & Git (mixed)
8. **Collaborators** — names/handles sharing the repo (default: solo). → `COLLABORATORS`
9. **Git remote** — detect first: `git remote get-url origin 2>/dev/null`. If set, confirm it; else
   ask for `owner/repo`, or accept "local-only". → `REPO_REMOTE`

### Group E — Language & Cadence (multiple choice)
10. **Output language + register** — English / German (formal "Sie") / German (informal) / other.
    Default English. If a formal register is chosen, the initializer records it as a standing
    convention. → `OUTPUT_LANGUAGE`
11. **Dashboard trajectories** — how to slice progress on the INDEX dashboard. Offer the preset's
    default set (editable):
    - literature-review → Corpus & Ingestion · Synthesis · Infrastructure
    - knowledge-base → Ingestion · Synthesis/Reports · Presentations · Infrastructure
    - admin-project → Steering · Stakeholders · Deliverables · Infrastructure
    - curriculum-redesign → Steering · Program Redesign · Unit Work · Foundations · Communication · Infrastructure
    - course-redesign → Course Redesign · Foundations · Infrastructure
    → `TRAJECTORIES`. Also ask **cadence** (how often sessions happen; default "ad hoc"). → `CADENCE`

## Step 2 — Confirm

Echo a compact summary table of every answer plus the derived `REPO_SLUG` / `SESSION_PREFIX` /
`CANONICAL_OUTPUT`. Ask: **"Build the project with these settings? (yes / edit a field)"**. On "edit",
re-ask just that field. Only proceed on an explicit yes.

## Step 3 — Dispatch the initializer

Get today's date (`date +%Y-%m-%d` via Bash) and pass it as `DATE`. Dispatch the
`project-initializer` agent (Agent tool) with the full structured brief — every field from the
interview plus the derived values and `DATE`. Let it write the files, prune the KB, seed the
dashboards, write the charter, and remove the sentinel.

## Step 4 — Hand off

When the initializer reports back, relay its summary to the user and point them to the next step:
run `/session-start` (which will now run the real Session-1 routine). Do not do further work in this
turn — setup is complete.
