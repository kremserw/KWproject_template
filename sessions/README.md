# Session Logs

Each working session produces a log file here named:
`<session-prefix>-<YYYY-MM-DD>.md`

(The `<session-prefix>` is set during `/setup-project` — e.g. the project's repo slug.)

A session log records:
- What the session was asked to do
- Which agents ran and in what order
- What was found / produced
- What files were created or updated
- What still needs work or follow-up

These logs are the connective tissue that lets agents resume work intelligently
without starting over. They are append-only and never overwritten. Once more than ~30
accumulate, `/session-wrap` rolls the oldest into `archive/`.
