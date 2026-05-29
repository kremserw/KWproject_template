---
name: session-wrap
description: Runs the mandatory end-of-session wrap-up. Updates the session log,
  INDEX.md, ARTIFACTS.md, and OPEN-QUESTIONS.md to reflect what was accomplished.
  Use at the end of every working session to keep the project navigable across conversations.
---

# Session Wrap-Up

Run the mandatory end-of-session wrap-up for the {{PROJECT_NAME}} project.

## Step 1 — Gather What Was Done

Ask the user (or infer from the conversation if clear):
- What was accomplished this session? (2–4 bullet points)
- What files were created or significantly modified?
- What still needs work or was left incomplete?

## Step 1b — Identify Knowledge Candidates

Review the session's conversation for findings that should be persisted to knowledge/.
A finding is a **knowledge candidate** if it:

- Corrects or refines an existing fact in knowledge/ (e.g., citation correction, figure update)
- Introduces a new empirical data point with a verifiable source
- Resolves an open question listed in OPEN-QUESTIONS.md
- Establishes a new conceptual framing endorsed by the user
- Is a synthesis or analysis that future queries would benefit from (compounding principle)

A finding is **NOT** a knowledge candidate if:

- It is a working decision about output structure or wording
- It is a to-do item (those go to OPEN-QUESTIONS.md)
- It is speculative or unverified

For each knowledge candidate, note:

| Field | Value |
|---|---|
| **Finding** | One-line summary |
| **Source** | How it was established: session-N, web-scrape-URL, user-correction, inbox-file |
| **Target file** | Which knowledge/ file to append to |
| **Verification** | `source-verified`, `user-confirmed`, or `llm-derived` |
| **Confidence** | `single-source`, `corroborated`, or `contested` |

Include these in the session log under a `### Knowledge Candidates` subsection.
Then actually file each candidate to its target knowledge/ file using this format:

```markdown
## [Topic] — YYYY-MM-DD
*Source: [session-N | inbox-file | web-scrape-URL | user-correction]*
*Verification: [source-verified | user-confirmed | llm-derived]*
*Confidence: [single-source | corroborated | contested]*

[content]
```

The `_summary.md` updates for filed candidates are handled by Step 3b (which
covers all changed knowledge/ folders). Do not duplicate that work here.

## Step 1c — Capture Pitfalls (what didn't work)

Knowledge candidates record what we *learned*; this step records what we got *wrong*.
Failure-derived lessons are what make the system robust — and they are exactly what
success-biased logs miss.

Review the session for a **repeatable** mistake — not a one-off typo, but a trap a future session
could fall into again. Signals:
- The linter flagged something we caused (a hallucinated specific, a drifted count, a stale tag).
- We did real work down a path that turned out wrong and had to back out.
- A convention was violated because it wasn't written down anywhere shared.

If you find one, add a lesson to `knowledge/LESSONS.md` using its **Title / When it applies /
Guardrail** schema plus the standard `Source/Verification/Confidence` tags. If the session also
*resolved* a confidence carryover, update `LESSONS.md`: either upgrade the claim's tag, correct it,
or add it to the **Won't-Fix Register** with a rationale (this is what closes the L3 loop). If
nothing repeatable went wrong this session, skip silently — do not invent pitfalls.

## Step 2 — Append to Session Log

File: `sessions/{{SESSION_PREFIX}}-<YYYY-MM-DD>.md`
- If the file already exists for today, append a new numbered session block
- If it does not exist, create it

Format:
```markdown
## Session [N]: [YYYY-MM-DD] — [Short Title]

### What Was Done
[bullet points]

### Files Created / Modified
| File | Change |
|------|--------|
| ... | ... |

### What Still Needs Work
[bullet points]
```

## Step 3 — Update INDEX.md, ARTIFACTS.md, and OPEN-QUESTIONS.md

Read the current files and update as needed:

**INDEX.md** (compact dashboard — keep it short):
- Update the **Session** number and date in the header
- Update **trajectory statuses** and **Current focus** items to reflect this session's work
- Do NOT add session history or append-only content — INDEX.md must stay under ~100 lines

**ARTIFACTS.md** (artifact registry):
- Add rows for any new artifacts created this session (reports, working docs, deliverables)
- Update status of existing artifacts if they changed

**OPEN-QUESTIONS.md** (open questions):
- Add any new open questions that emerged this session
- Remove any questions that were resolved
- Keep the file thematically organized

## Step 3b — Refresh _summary.md for changed folders

From the files modified this session (gathered in Step 1), identify which
`knowledge/` subfolders were affected. For each affected folder that has a
`_summary.md`, do an **incremental** update — Contents table only:

1. Run `ls` on the folder to get the current file list
2. Read the existing `_summary.md`
3. **Add** a row for any file that exists in the folder but is missing from the
   Contents table. For the description, read the file's title line and first
   paragraph — do NOT guess or paraphrase from memory.
4. **Update** the "Last Modified" date for any file that was modified this session
5. **Remove** rows for any file listed in the table that no longer exists in the folder
6. **Update** the file count in the `**Files**:` header line
7. **Update** the `**Last updated**:` date in the header to today's date

**Do NOT touch** the Key Facts or Connections sections. Those are hand-written
and only change when the user or the linter explicitly requests it.

If no knowledge/ folders were affected this session, skip this step.

## Step 4 — Lint Staleness Check

Check `working/review/` for the most recent `knowledge-lint-*.md` file.
Count how many sessions have occurred since that lint date (check session log dates).

- If **>3 sessions since last lint** (or no lint exists): tell the user
  "It's been [N] sessions since the last knowledge lint. Running `/lint` now."
  Then invoke the `/lint` skill.
- If **≤3 sessions**: skip silently.

## Step 4b — Archive Old Session Logs

If `sessions/` contains more than 30 log files (excluding `README.md` and the
`archive/` subfolder), move the oldest files to `sessions/archive/`:

```bash
mkdir -p sessions/archive
ls -t sessions/{{SESSION_PREFIX}}-*.md | tail -n +31 | xargs -I {} mv {} sessions/archive/
```

This keeps the active directory lean for `ls -t` scans in `/session-start`
while preserving all history. Only run if the count exceeds 30 — skip silently
otherwise.

## Step 5 — Git Sync

> If this project is **local-only** (no remote), commit locally and skip the fetch/pull/push steps.

This project is shared via git. All session work must be committed and pushed.

### 5a — Pull & check for conflicts

```bash
git fetch origin
git status
```

If the local branch is behind `origin/main`, attempt:
```bash
git pull --rebase origin main
```

If there are **merge conflicts**:
- **Stop immediately** and report each conflicted file to the user
- Do NOT auto-resolve conflicts — the other collaborator's changes must be reviewed
- List the conflicted files and ask the user how to proceed before continuing

### 5b — Commit all changes

Stage all modified and new files (but never `.env`, credentials, or other secrets):
```bash
git add -A
```

Review what's staged with `git status`. Then commit with a message summarizing
the session:

```
Session [N]: [short title]

[2-3 line summary of what changed]

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 5c — Push

```bash
git push origin main
```

If the push is **rejected** (someone else pushed while this session was running):
- Pull with rebase: `git pull --rebase origin main`
- If conflicts arise, stop and flag them to the user (same as 5a)
- If clean, push again

### 5d — Confirm sync status

Run `git status` and `git log --oneline -1` to confirm:
- Working tree is clean
- Latest commit is pushed to origin

## Step 6 — Confirm

Report to the user:
- Session log: confirmed appended to `sessions/{{SESSION_PREFIX}}-<date>.md`
- INDEX.md: confirmed updated
- Knowledge candidates filed: [count] (or "none this session")
- Lint: [ran / not needed]
- Git: [committed + pushed / committed locally / conflicts flagged]
- One-line summary of the session for their reference

## Step 7 — Prompt User to Clear Conversation History

Tell the user:

> "Session wrapped. Run `/clear` to free up context and start fresh for the next session."

Note: `/clear` is a Claude Code CLI command that only the user can execute — this step cannot be automated.
