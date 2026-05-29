# {{PROJECT_NAME}} — Project Index

**Project**: {{PROJECT_NAME}} — {{PROJECT_TYPE}}
**Session**: 0 (not yet started)
**Canonical Output**: {{CANONICAL_OUTPUT}} — `outputs/reports/main/{{REPO_SLUG}}-current.md`
**Instructions**: Update the trajectory statuses and current-focus items at the end of every session (`/session-wrap`).

For artifact locations and knowledge inventory → [ARTIFACTS.md](ARTIFACTS.md)
For open questions and next steps → [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md)

---

## What This Project Is

{{PROJECT_GOAL}}

Knowledge domains in scope: {{DOMAINS}}.
Analytic framework / central question: {{ANALYTIC_FRAMEWORK}}.

---

## Project Trajectories

<!-- The project-initializer expands {{TRAJECTORIES}} into one block per trajectory, using
     .claude/templates/index-trajectory.md. The block below is the shape each one takes. -->

{{TRAJECTORIES}}

### N. [Trajectory Name]

[One-line description of this trajectory and what it tracks.]
-> `knowledge/<relevant-folder>/`

**Current focus**: Not started — set during the first working session.

---

## Quick Reference

| Item | Location |
|------|----------|
| Canonical output | `outputs/reports/main/{{REPO_SLUG}}-current.md` |
| Output archive | `outputs/reports/main/archive/` |
| Per-{{UNIT_NOUN}} reports | `outputs/reports/units/` |
| Built deliverables | `outputs/deliverables/` |
| Artifact registry + KB inventory | [ARTIFACTS.md](ARTIFACTS.md) |
| Open questions | [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) |
| Project charter (the setup brief) | `knowledge/project-management/project-charter.md` |
| Pitfall/guardrail register | `knowledge/LESSONS.md` |
| Latest lint | `working/review/knowledge-lint-*.md` |
| Latest session log | `sessions/{{SESSION_PREFIX}}-*.md` |

---

## How to Resume Work

1. Read this file for trajectory status and current focus
2. Check `inbox/` for new files
3. Read latest session log in `sessions/` for detail on prior work
4. Consult [ARTIFACTS.md](ARTIFACTS.md) to locate specific files
5. Proceed from where things left off — never start from scratch
