---
name: session-start
description: Runs the mandatory start-of-session routine. On a fresh template copy it detects the
  un-instantiated state and routes into /setup-project. Otherwise it pulls latest from git, reads
  INDEX.md, checks inbox, reviews the latest session log, determines the session number, checks lint
  staleness, and briefs the user. Use at the beginning of every working session.
---

# Session Start-Up

Run the mandatory start-of-session routine for the {{PROJECT_NAME}} project.

## Step 0 — Template Detection (run FIRST, before anything else)

Check for the bootstrap sentinel:

```bash
test -f .template-uninstantiated && echo UNINSTANTIATED || echo CONFIGURED
```

- If `UNINSTANTIATED`: this is a fresh, un-configured copy of the knowledge-work template.
  Do **NOT** run git sync, do **NOT** read INDEX.md (it still has placeholders), do **NOT** check
  inbox or session logs. Tell the user:
  > "This is a fresh, un-configured copy of the knowledge-work project template. Before we can work,
  >  it needs a one-time setup. I'll run the setup interview now."
  Then immediately invoke the `/setup-project` skill and STOP the normal routine.
- If `CONFIGURED`: proceed to Step 1.

## Step 1 — Git Sync (Pull Latest)

> If this project was configured as **local-only** (no remote), skip this step and note "local-only — no remote sync".

This project is shared via git ({{REPO_REMOTE}}). A collaborator ({{COLLABORATORS}})
may have pushed changes since the last session.

### 1a — Check working tree status

```bash
git status
```

If there are **uncommitted local changes**:
- List them for the user
- Ask: "There are uncommitted local changes. Stash them and pull, or skip pull?"
- If the user says stash: `git stash` → proceed to pull → `git stash pop` after
- If the user says skip: skip the pull, warn that the session may be working on stale data

### 1b — Fetch and pull

```bash
git fetch origin
```

Check if local branch is behind `origin/main`:
```bash
git rev-list --count HEAD..origin/main
```

If behind (count > 0):
```bash
git pull --rebase origin main
```

If there are **merge conflicts**:
- **Stop immediately** and report each conflicted file to the user
- Do NOT auto-resolve — the other collaborator's changes must be reviewed
- List the conflicted files and ask the user how to proceed

### 1c — Report sync status

Tell the user one of:
- "Pulled [N] new commits from origin/main. Up to date."
- "Already up to date with origin/main."
- "Pull skipped (local changes present — user chose to skip)."
- "Conflicts detected — needs manual resolution." (then stop the startup routine)

## Step 2 — Read INDEX.md

Read `INDEX.md` to understand the current project state. Extract:
- Session number and date from the header
- Trajectory statuses and current focus items
- Current main output version

Also glance at `OPEN-QUESTIONS.md` for any high-priority open items.

Do NOT print the full INDEX.md to the user — just note key facts for the briefing.

## Step 3 — Check Inbox

```bash
ls inbox/
```

Identify any files that are NOT in `inbox/processed/` (i.e., new unprocessed files).

If new files exist:
- List them for the user
- Note: "These will need processing. Want me to run the inbox-processor now, or later?"

If inbox is empty (only `processed/` folder): note "Inbox clear."

## Step 4 — Read Recent Session Logs

Read the **5 most recent** session log files for multi-session continuity:
```bash
ls -t sessions/{{SESSION_PREFIX}}-*.md 2>/dev/null | head -5
```

For each file, extract:
- Session number(s) and short title(s)
- What was done
- What was left incomplete ("What Still Needs Work")
- Any knowledge candidates that were filed

Focus the briefing on the most recent session's details, but scan the older 4
for **carryover items** — incomplete work threads that may still be relevant.

## Step 5 — Determine Next Session Number

Parse the latest session log to find the highest session number used.
The next session is **N+1**. Note this for the briefing.

## Step 6 — Lint Staleness Check

Check `working/review/` for the most recent `knowledge-lint-*.md` file.
Count how many sessions have occurred since that lint date.

- If **>3 sessions since last lint** (or no lint exists): flag for the user
  in the briefing. Do NOT auto-run — just note it.
- If **≤3 sessions**: note "Lint is current" in the briefing.

## Step 7 — Brief the User

Present a compact status report. Use this format:

```
## Session [N+1] — [today's date]

**Git**: [sync status]
**Last session**: Session [N] — [short title] ([date])
**Main output**: [version] — [status]
**Inbox**: [clear / N new files]
**Lint**: [current (last: date) / stale — N sessions since last lint]
**Carryover**: [1-3 key items left incomplete from last session]
**Older threads**: [any unaddressed items from the 4 prior sessions, or "none"]

Ready to work. What would you like to tackle?
```

If there are new inbox files, add:
```
**Action needed**: [N] new inbox file(s) waiting for processing.
```

If lint is stale, add:
```
**Suggestion**: Run `/lint` — it's been [N] sessions since the last check.
```

## Notes

- This skill is the bookend to `/session-wrap`. Start every session with
  `/session-start`, end every session with `/session-wrap`.
- If git pull brings in changes that affect INDEX.md, re-read the pulled
  version (not a cached one).
- The skill does NOT auto-process inbox files or auto-run lint — it flags
  them and lets the user decide. The session-start should be fast and
  non-destructive.
