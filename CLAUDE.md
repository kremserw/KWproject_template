# {{PROJECT_NAME}} — Project Instructions

> ## ⚠️ FIRST RUN — read this if the project is not yet configured
> If a file named `.template-uninstantiated` exists at the repo root, this is a **fresh, un-configured
> copy of the knowledge-work template**. Do not start normal work. Run **`/setup-project`** (or just
> run `/session-start`, which detects this and routes you into setup). The setup interview configures
> this project for its specific purpose and removes this notice. The rest of this file is written with
> `{{PLACEHOLDER}}` tokens that setup fills in.

This project is a multi-agent **knowledge-work** workflow for: {{PROJECT_GOAL}}.
There is no application code here. Agents **scan & analyze** new knowledge, **ingest** it into a
structured knowledge base, **create** outputs from that base, track progress through a
**project-management** layer, and continuously **improve the structure itself** (the double-loop /
infrastructure layer). Project type: **{{PROJECT_TYPE}}**. Primary output: **{{CANONICAL_OUTPUT}}**.
Output language: **{{OUTPUT_LANGUAGE}}**.

---

## Start Every Session Here

1. **Read `INDEX.md`** — compact project dashboard with trajectory statuses and current focus items
2. **Check `inbox/`** — the user may have dropped new files since the last session
3. **Glance at the latest session log** in `sessions/` for detail on prior work
4. Consult `ARTIFACTS.md` to locate specific files; `OPEN-QUESTIONS.md` for open items
5. Skim `knowledge/LESSONS.md` before any KB-maintenance or writing pass — it records past pitfalls and the guardrails that prevent repeats
6. Only search for what is genuinely missing or outdated — never start from scratch
7. **If >3 sessions since last lint**, run the `knowledge-linter` agent to check knowledge base health

(Or simply run `/session-start`, which automates all of the above.)

---

## Installed Skills & When to Use Them

### Research & Web
- **`firecrawl:firecrawl-cli`** — ALL web research, search, URL reading, news
  gathering, documentation fetching. This replaces WebFetch and WebSearch.
  Use this for every internet task without exception.
  Key commands: `firecrawl search`, `firecrawl scrape`, `firecrawl agent`
  Always run independent scrapes in parallel with `&` + `wait`.

### Document Output
- **`document-skills:doc-coauthoring`** — structured report writing and iteration
- **`document-skills:pdf`** — reading, extracting, and merging PDF sources
- **`document-skills:docx`** — producing polished Word document outputs
- **`document-skills:pptx`** — producing PowerPoint slide decks from reports

### Project skills (this template)
- **`/setup-project`** — one-time first-run configuration (see FIRST RUN above)
- **`/session-start`** / **`/session-wrap`** — session bookends
- **`/lint`** — knowledge base health check
- **`/file-back`** — persist a finding into `knowledge/`
- **`/new-unit`** — scaffold a new {{UNIT_NOUN}}

---

## Folder Structure

The structure expresses the five layers of knowledge work. (`L1` scan · `L2` ingest · `L3` create ·
`L4` track · `L5` infrastructure / double-loop.)

```
{{REPO_SLUG}}/
├── CLAUDE.md / README.md / SETUP.md      ← L5 process docs (you are here)
├── INDEX.md                              ← L4 dashboard: trajectories + current focus
├── ARTIFACTS.md                          ← L4 artifact registry + knowledge inventory
├── OPEN-QUESTIONS.md                     ← L4 open questions, thematically organized
│
├── inbox/                                ← L1 drop new material here (do not edit originals)
│   └── processed/                        ← move files here after digestion (don't delete)
│
├── working/                              ← L1 scratch space for in-progress agent work
│   ├── research/ · planning/ · drafts/ · review/ · scripts/
│
├── knowledge/                            ← L2 the knowledge base
│   ├── README.md · LESSONS.md (L5) · LINK-GRAPH.md (L5)
│   ├── foundations/                      ← stable scope facts: program / mandate / research question / framework
│   ├── project-management/               ← project ops as knowledge: team, budget, timeline, governance
│   ├── units/                            ← per-{{UNIT_NOUN}} knowledge (one subfolder per {{UNIT_NOUN}})
│   ├── domain/                           ← external research synthesis
│   │   └── landscape/                    ← dated snapshots of the fast-moving environment
│   ├── outreach/                         ← outward-facing materials (what we send out)
│   └── sources/                          ← raw archived inputs by type
│       ├── deepresearch/ · official/ · articles/ · materials/
│
├── outputs/                              ← L3 generated artifacts
│   ├── reports/main/                     ← the canonical {{REPO_SLUG}}-current.md + archive/
│   ├── reports/units/                    ← per-{{UNIT_NOUN}} reports + archive/
│   ├── deliverables/                     ← built artifacts: slides / exercises / memos
│   ├── exports/                          ← generated snapshots for Claude Team Projects
│   └── scripts/                          ← build/export scripts
│
├── sessions/                             ← L4 session logs: append-only, never overwrite
│
└── .claude/                              ← L5 agents, skills, hooks, settings, templates
```

---

## Agent Roles

### Research Agent
- **Before searching**: check `inbox/` for user-supplied material and `knowledge/`
  for anything already collected. Do not re-fetch sources already in `knowledge/sources/`.
- **Where to save**:
  - Fast-moving environment snapshots → `knowledge/domain/landscape/<YYYY-MM>.md` (new file per {{SNAPSHOT_CADENCE}})
  - Durable domain research → append to the relevant `knowledge/domain/<domain-slug>.md`
  - Scope / foundational facts → `knowledge/foundations/<topic>.md`
  - Raw archived sources → `knowledge/sources/<type>/` (see source type table below)
  - {{UNIT_NOUN}}-specific material → `knowledge/units/<slug>/`
  - Working notes → `working/research/<topic>-<YYYY-MM-DD>.md`

### Planning Agent
- Read all relevant files in `knowledge/` before planning.
- Save plan/outline to `working/planning/<topic>-<YYYY-MM-DD>.md`.
- When replanning, append a new dated section — do not overwrite.

### Writing Agent
- Read the current plan from `working/planning/` and all relevant `knowledge/` files.
- **Main output**: overwrite `outputs/reports/main/{{REPO_SLUG}}-current.md`;
  move the prior version to `outputs/reports/main/archive/{{REPO_SLUG}}-vN.md` first.
- **Per-{{UNIT_NOUN}} outputs**: save as `outputs/reports/units/<slug>-current.md` (same archive pattern).
- In-progress drafts go in `working/drafts/` until ready to promote to `outputs/reports/`.
- **There is only ONE current version of each output at any time — no copies or "latest" duplicates.**

### Review Agent
- Read the latest output from `outputs/reports/`.
- Save review feedback to `working/review/<topic>-review-<YYYY-MM-DD>.md`.
- Be specific: note which sections need work, what is missing, what is wrong.
- Do NOT rewrite — only critique and provide clear instructions for the Writing Agent.

### Fact-Checker Agent (`.claude/agents/fact-checker.md`)
- Read-only, adversarial verification of cited claims against `knowledge/sources/` (and live URLs via firecrawl).
- Invoke before publishing an output externally, or to settle a recurring `llm-derived`/`single-source`
  confidence carryover that the linter keeps flagging (see `knowledge/LESSONS.md` L3).
- Saves verdicts to `working/review/fact-check-<target>-<YYYY-MM-DD>.md`. Does NOT edit — only verifies.

---

## Workflow

```
User assigns task (or drops files in inbox/)
        ↓
Read INDEX.md + check inbox/ + check sessions/ (resume, don't restart)
        ↓
Knowledge Linter → working/review/knowledge-lint-<date>.md (if >3 sessions since last)
        ↓
Research Agent  →  knowledge/domain/ + knowledge/sources/ + knowledge/units/
        ↓
Planning Agent  →  working/planning/
        ↓
Writing Agent   →  outputs/reports/main/ or outputs/reports/units/
        ↓
Review Agent    →  working/review/
        ↓
  [needs revision?]
     yes → Writing Agent (reads review, archives old, overwrites current)
     no  → /session-wrap (file back findings, update INDEX/ARTIFACTS/OPEN-QUESTIONS, append session log)
```

---

## Source Type Handling

| Source type | Where to save |
|---|---|
| Deep research reports (GPT, Claude, etc.) | `knowledge/sources/deepresearch/` |
| Official / primary documents, regulations, protocols | `knowledge/sources/official/` |
| Academic papers, news articles | `knowledge/sources/articles/` |
| Slides (PPTX), syllabi (DOCX), books (PDF), datasets | `knowledge/sources/materials/` |
| Processed inbox items | `inbox/processed/` |

Always append to knowledge domain files — never overwrite. Use dated section headers.

When appending content from Q&A sessions, web research, or inbox processing, use
this tagging convention so the linter can track provenance and confidence:

```markdown
## [Topic] — YYYY-MM-DD
*Source: [session-N | inbox-file | web-scrape-URL | user-correction]*
*Verification: [source-verified | user-confirmed | llm-derived]*
*Confidence: [single-source | corroborated | contested]*

[content]
```

---

## Inbox Processing Protocol

1. List `inbox/` at session start
2. For each file: read it, extract relevant info, update `knowledge/`
3. Move processed file to `inbox/processed/` (never delete originals)
4. Note what was processed in the session log
5. Update `ARTIFACTS.md` if new artifacts were created

---

## Unit-Level Modularity

As the project matures, each {{UNIT_NOUN}} gets its own knowledge folder and (optionally) report:
- Knowledge: `knowledge/units/<slug>/` — facts, source excerpts, notes
- Report: `outputs/reports/units/<slug>-current.md`

The main output (`outputs/reports/main/{{REPO_SLUG}}-current.md`) is the cross-cutting synthesis and is
maintained in parallel with any per-{{UNIT_NOUN}} outputs. Use `/new-unit` to scaffold a new one.

---

## Session Wrap-Up (Required)

At the end of every session (use `/session-wrap`):

1. **Append to session log** — `sessions/{{SESSION_PREFIX}}-<YYYY-MM-DD>.md`
   Include: what was done, files created/modified, what still needs work.
2. **Update project files**: `INDEX.md` (trajectory statuses + current focus), `ARTIFACTS.md`
   (new artifacts), `OPEN-QUESTIONS.md` (add new / remove resolved).
3. **File knowledge candidates** back into `knowledge/`; capture any repeatable pitfall in `LESSONS.md`.

---

## File Naming Conventions

- Lowercase with hyphens: `market-entry-findings.md`
- Include date in working files: `<topic>-<YYYY-MM-DD>.md`
- Never delete prior output versions — archive them in `outputs/reports/*/archive/`
- Canonical current outputs use `-current.md` suffix (no date, no version number)
