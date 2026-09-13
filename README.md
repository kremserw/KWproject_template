# KWproject — Knowledge-Work Project Template

A reusable, **self-instantiating** scaffold for running any knowledge-work project with Claude Code.
Copy it into a new folder, start Claude Code, answer a short interview, and it configures itself —
folders, config files, dashboards, and a knowledge base tuned to your purpose.

> **This is the template explainer.** While the project is still un-instantiated (a
> `.template-uninstantiated` file is present at the root), this README documents the *template*. After
> you run `/setup-project`, the initializer moves this file to `.claude/TEMPLATE-GUIDE.md` and writes a
> fresh, project-specific `README.md` in its place.

There is no application code here. Everything is plain markdown operated on by Claude Code agents.

---

## 1. The idea: knowledge work has a generic shape

Most knowledge-work projects — a literature review, a topic knowledge base, an administrative
initiative, a curriculum redesign — share the same five-layer rhythm. This template gives each layer a
home:

| Layer | What it does | Where it lives |
|---|---|---|
| **L1 — Scan & analyze** | take in new material; do exploratory work | `inbox/`, `working/` |
| **L2 — Ingest** | compile material into a structured, cross-linked knowledge base | `knowledge/` |
| **L3 — Create** | produce outputs from the base (reports, decks, memos, syntheses) | `outputs/` |
| **L4 — Track** | keep the project navigable; record progress | `INDEX.md`, `ARTIFACTS.md`, `OPEN-QUESTIONS.md`, `sessions/` |
| **L5 — Infrastructure / double-loop** | improve the structure itself as the purpose emerges | `.claude/`, `knowledge/LESSONS.md`, `knowledge/LINK-GRAPH.md` |

The knowledge base **compounds**: every session's findings get filed back, cross-linked, and
periodically health-checked, so the project gets more useful over time instead of dying in chat history.

---

## 2. How to use it (the 60-second version)

1. Copy the **contents** of this template folder into a fresh project folder.
2. Start Claude Code there and run **`/session-start`** (or `/setup-project` directly).
3. It detects the fresh `.template-uninstantiated` sentinel and runs a short **setup interview**:
   project name, goal, type, outputs, knowledge domains, framework, the "unit" of work, collaborators,
   git remote, language, and dashboard trajectories.
4. The `project-initializer` agent fills in every config file, prunes the knowledge base to fit your
   project type, seeds the dashboard, writes a **project charter**, and deletes the sentinel.
5. From then on, `/session-start` and `/session-wrap` bookend every working session.

`git checkout .` undoes the whole instantiation if it isn't what you wanted.

---

## 3. The first-run bootstrap (how self-configuration works)

```
copy template → start Claude Code → /session-start
        │
        ▼  detects  .template-uninstantiated
   /setup-project  ── short interview (5 question groups, with defaults) ──▶ a structured "brief"
        │
        ▼  dispatches
   project-initializer agent
        │  • replaces every {{TOKEN}} in the config files & machinery
        │  • prunes / renames knowledge-base folders for the chosen project type
        │  • seeds INDEX trajectories, resets ARTIFACTS / OPEN-QUESTIONS
        │  • writes knowledge/project-management/project-charter.md (records the brief)
        │  • removes the FIRST-RUN notice and the sentinel
        ▼
   a configured project  →  /session-start runs the normal routine (Session 1)
```

**Sentinel.** `.template-uninstantiated` at the root is the single source of truth for "not yet
configured." A configured project simply doesn't have it. `session-start` checks for it first
(Step 0) and routes into setup; the initializer deletes it only once no `{{TOKEN}}` markers remain
(so a half-finished run is detectable and resumable). Re-running setup on a configured project is a
safe no-op unless you force it.

**Placeholder tokens.** Template files ship as valid markdown containing `{{UPPER_SNAKE}}` tokens that
render as literal text until filled. Key tokens:

| Token | Becomes |
|---|---|
| `{{PROJECT_NAME}}` / `{{PROJECT_GOAL}}` / `{{PROJECT_TYPE}}` | identity & purpose |
| `{{REPO_SLUG}}` / `{{SESSION_PREFIX}}` | canonical-output filename / session-log stem |
| `{{REPO_REMOTE}}` / `{{COLLABORATORS}}` | git remote / who shares the repo |
| `{{UNIT_NOUN}}` (+ plural, + `{{UNIT_NUMBERING}}`) | what a "unit" of work is called |
| `{{TRAJECTORIES}}` | the dashboard's progress slices |
| `{{OUTPUT_TYPES}}` / `{{CANONICAL_OUTPUT}}` | what the project produces |
| `{{DOMAINS}}` / `{{ANALYTIC_FRAMEWORK}}` | knowledge areas / research question or model |
| `{{OUTPUT_LANGUAGE}}` | primary output language + register |
| `{{SNAPSHOT_CADENCE}}` | how often `domain/landscape/` snapshots roll |

---

## 4. Project-type presets

The setup interview offers six starting points. Each keeps a different slice of the knowledge base and
maps the generic "unit" to a concrete concept:

| Preset | A "unit" is… | Canonical output | KB emphasis |
|---|---|---|---|
| **literature-review** | a theme | a synthesis / review | `foundations/` (RQ + framework), `sources/articles/` |
| **knowledge-base** | a topic | the KB itself (feeds decks + reports) | `domain/`, `sources/` |
| **admin-project** | a work-package | a proposal / memo set | `project-management/` (central) |
| **curriculum-redesign** | a course (numbered) | a program report | all areas (the original shape) |
| **course-redesign** | (a single course) | a course report + materials | `foundations/`, `domain/` |
| **blank / custom** | a unit | up to you | everything kept; prune later |

You're never locked in — the structure is plain folders you can rename or extend at any time (that's
the L5 double-loop: the scaffold adapts as the project's real shape emerges).

---

## 5. Full structure — every component

```
<project>/
├── README.md                 project README (this file, pre-setup = the template explainer)
├── CLAUDE.md                 process instructions Claude reads every session
├── SETUP.md                  how to install the tooling on a new machine
├── INDEX.md                  L4 dashboard: trajectories + current focus (start here each session)
├── ARTIFACTS.md              L4 registry of outputs + inventory of the knowledge base
├── OPEN-QUESTIONS.md         L4 open questions / decisions / to-dos, by theme
├── .template-uninstantiated  bootstrap sentinel (deleted at setup)
├── .gitignore
│
├── inbox/                    L1 drop new source files here (hook-protected, read-only)
│   └── processed/            originals after digestion (never deleted; gitignored)
├── working/                  L1 scratch space
│   ├── research/ planning/ drafts/ review/ scripts/
│
├── knowledge/                L2 the knowledge base
│   ├── README.md             KB map + conventions
│   ├── LESSONS.md            L5 pitfall/guardrail register (ships with 8 portable lessons)
│   ├── LINK-GRAPH.md         L5 auto-generated cross-link graph (regenerated by /lint)
│   ├── foundations/          stable scope facts (program / mandate / research question / framework)
│   ├── project-management/   project ops as knowledge (team, budget, timeline, governance)
│   ├── units/                per-unit knowledge (one subfolder per unit)
│   ├── domain/               external research synthesis
│   │   └── landscape/        dated snapshots of the fast-moving environment
│   ├── outreach/             outward-facing materials
│   └── sources/              raw archives: articles/ deepresearch/ official/ materials/
│
├── outputs/                  L3 generated artifacts
│   ├── reports/main/         canonical <slug>-current.md + archive/
│   ├── reports/units/        per-unit reports + archive/
│   ├── deliverables/         built artifacts (slides, exercises, memos)
│   ├── exports/              snapshots for Claude Team Projects (gitignored)
│   └── scripts/              build/export scripts
│
├── sessions/                 L4 append-only session logs + archive/
│
└── .claude/                  L5 the machinery
    ├── agents/               5 subagents (below)
    ├── skills/               6 slash-command skills (below)
    ├── hooks/                4 hooks (below)
    ├── templates/            reusable content skeletons agents copy from
    └── settings.json         hook wiring (tracked — this is what makes the hooks run)
```

### Agents (`.claude/agents/`)
| Agent | Role |
|---|---|
| **inbox-processor** | Digests new `inbox/` files, extracts facts, files them into `knowledge/`, archives originals |
| **knowledge-linter** | Health-checks the KB against 10 criteria; regenerates `LINK-GRAPH.md`; enforces the close-the-loop rule |
| **report-reviewer** | Critiques the main output against quality criteria — critiques only, never rewrites |
| **fact-checker** | Adversarial, read-only verification of cited claims against `sources/` and live URLs |
| **project-initializer** | One-time bootstrap writer used by `/setup-project` (fills tokens, prunes the KB, seeds dashboards) |

### Skills (`.claude/skills/`)
| Skill | When | What it does |
|---|---|---|
| **/setup-project** | First run | Interview → dispatches `project-initializer` to configure the project |
| **/session-start** | Start of session | Detects a fresh template; else syncs git, reads INDEX, checks inbox, briefs you |
| **/session-wrap** | End of session | Files knowledge candidates + pitfalls, appends the session log, updates dashboards, commits |
| **/lint** | Periodically | Runs the knowledge-linter and reports issues |
| **/file-back** | "file that back" | Persists a finding into the right `knowledge/` file with provenance tags |
| **/new-unit** | New unit of work | Scaffolds a unit's knowledge + planning + report stubs |

### Hooks (`.claude/hooks/`)
| Hook | Event | Does |
|---|---|---|
| **protect-inbox.sh** | `PreToolUse` | Blocks edits to `inbox/` originals — forces a move to `processed/` first |
| **protect-archive.sh** | `PreToolUse` | Blocks edits to `outputs/reports/*/archive/` — archived versions are immutable history |
| **convert-inboxes.sh** | `SessionStart` | Converts every new PDF/Office/HTML file in `inbox/` to Markdown beside the original, so a dropped document is readable without a per-file conversion step. Optional dependency — silently does nothing if `md-convert` is not installed (see SETUP.md) |
| **verify-inbox-cleared.sh** | `SubagentStop` | After an `inbox-processor` run, checks that `inbox/` root is actually clear and names any file still sitting there. Nudges once, never loops |

All four are wired in `.claude/settings.json`, which is tracked. **A hook that is not wired does
nothing and looks like it is working** — if you add a hook, add it there in the same commit.

> **These hooks only run in a Claude Code session whose working directory is this repo.** An
> assistant that merely *reads* the repo from elsewhere never loads `.claude/` at all, and none of
> these protections apply to it.

---

## 6. Conventions worth knowing

- **Provenance tagging.** New knowledge entries carry a triplet so the linter can audit confidence:
  ```
  *Source: [session-N | inbox-file | web-scrape-URL | user-correction]*
  *Verification: [source-verified | user-confirmed | llm-derived]*
  *Confidence: [single-source | corroborated | contested]*
  ```
- **Append-only knowledge.** Knowledge files are never overwritten — new content is appended under a
  dated header. Outputs, by contrast, keep ONE `-current.md` version with old ones moved to `archive/`.
- **`_summary.md` per folder.** Each KB folder carries a contents table + key facts + connections. Read
  summaries first to orient, then drill in.
- **The double loop.** `LESSONS.md` records failure-derived guardrails; the linter enforces them and
  forces stale low-confidence claims to a decision. This is how the scaffold *learns*.

---

## 7. Adapting the template

- The structure is just folders and markdown — rename, add, or remove freely after setup.
- To change what a "unit" means later, the `{{UNIT_NOUN}}` it was set to lives in the charter; update
  `/new-unit` and the affected paths.
- To re-tailor the linter or reviewer to your domain, edit `.claude/agents/knowledge-linter.md`
  (Criterion 5) and `.claude/agents/report-reviewer.md` (the "Framework & Substance" block).
- Tooling install steps (Claude Code, Firecrawl, plugins, model, hooks) are in **SETUP.md**.

---

## 8. Tools & dependencies

- **Claude Code** (Anthropic CLI) — the orchestrator and primary agent
- **Firecrawl** (`firecrawl-cli`) — all web research, search, and URL scraping
- Optional document/plugin skills for PDF/DOCX/PPTX/XLSX output
- No database, no server, no build system — everything is plain markdown files
