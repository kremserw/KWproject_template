#!/bin/bash
# SubagentStop hook: backstop for the inbox-processor's Step 3 ("clear the inbox").
#
# Why this exists: giving each original a terminal home is the most mechanical step in the
# processor protocol and the one most often skipped, which strands originals in inbox/ root
# where the next session re-reads them as new. This hook fires the moment the inbox-processor
# finishes and, if loose files remain, nudges it once.
#
# HOW IT REACHES THE AGENT — measured on Claude Code 2.1.238, not assumed. `additionalContext`
# on SubagentStop is injected back into the SUBAGENT, which then CONTINUES instead of stopping.
# It is therefore not a note to the orchestrator: it is a second turn for the agent that left
# the files. That is the right audience — but without a guard it is also a loop, because the
# agent stops again, the hook fires again, and so on. An instrumented run looped a subagent ten
# times before it refused to answer. `stop_hook_active` is the guard: false on the first fire,
# true on every re-entry. This hook exits silently when it is true, so the agent gets exactly
# one nudge and an agent that ignores it is allowed to stop.
#
# What the orchestrator sees is therefore the agent's own report — which is why the protocol
# requires it to NAME any file it deliberately left in inbox/ and say why.
#
# Scope: registered under SubagentStop with matcher "inbox-processor", so it never fires after
# any other subagent or on an ordinary turn. A hook binds only a Claude Code session started
# inside this repo; that is why Step 3 also carries `ls inbox/` as a procedural verification.
#
# Terminal home: this hook only checks that inbox/ ROOT is clear, so it is agnostic about where
# the files went — inbox/processed/ (this template's default) or a versioned corpus folder such
# as knowledge/sources/<type>/. If your project chose the latter, adjust the wording below.
#
# Output: only a JSON object on stdout (per the hooks contract). Exit 0 always.

input=$(cat)

HOOK_JSON="$input" python3 <<'PY'
import json, os, sys

try:
    d = json.loads(os.environ.get("HOOK_JSON", "") or "{}")
except Exception:
    sys.exit(0)

# The matcher already scopes this to inbox-processor; if agent_type is populated, double-check
# it. Treat empty/missing as "trust the matcher" so the hook still works on any version that
# does not echo agent_type into the SubagentStop payload.
agent_type = (d.get("agent_type") or "")
if agent_type and agent_type != "inbox-processor":
    sys.exit(0)

# Re-entry guard: we are here because a previous fire made the subagent continue. Nudge once,
# never twice — see the header.
if d.get("stop_hook_active"):
    sys.exit(0)

cwd = d.get("cwd") or os.getcwd()
inbox = os.path.join(cwd, "inbox")
if not os.path.isdir(inbox):
    sys.exit(0)

def is_loose(name):
    # never count the folder marker, the readme, or cloud-sync sidecars
    if name in ("README.md", ".gitkeep"):
        return False
    if name.endswith(":com.dropbox.attrs"):
        return False
    return os.path.isfile(os.path.join(inbox, name))  # top-level files only; skips processed/

loose = sorted(n for n in os.listdir(inbox) if is_loose(n))
if not loose:
    sys.exit(0)

listing = ", ".join(loose[:10]) + ("…" if len(loose) > 10 else "")
msg = (
    "INBOX NOT CLEARED — you finished but {n} file(s) still sit in inbox/ root: {listing}. "
    "Per Step 3 of your protocol every file there must reach exactly one terminal home: the "
    "original AND any Markdown conversion of it are moved to inbox/processed/ (never deleted). "
    "Resolve each remaining file now — move it, or, if you deliberately flagged it as unclear, "
    "say so explicitly and BY NAME in your summary, because your report is the only thing the "
    "orchestrator sees. After this, inbox/ root should contain only the processed/ folder."
).format(n=len(loose), listing=listing)

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SubagentStop",
        "additionalContext": msg
    }
}))
PY
