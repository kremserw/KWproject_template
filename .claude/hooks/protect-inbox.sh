#!/bin/bash
# PreToolUse hook: block edits to inbox/ originals.
# Agents must move files to inbox/processed/ before touching them.

input=$(cat)
# The path lives under tool_input, not at the top level of the payload — read both, because a
# hook that reads the wrong key blocks nothing and looks like it is working. (Measured against a
# live PreToolUse payload, Claude Code 2.1.238.) MultiEdit/NotebookEdit carry other key names,
# so check those too rather than silently passing them through.
file=$(echo "$input" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print(''); raise SystemExit
ti = d.get('tool_input') or {}
for k in ('file_path', 'notebook_path', 'path'):
    v = ti.get(k) or d.get(k)
    if v:
        print(v); break
else:
    print('')
" 2>/dev/null)

if [[ "$file" == *"/inbox/"* ]] && [[ "$file" != *"/inbox/processed/"* ]]; then
    echo "BLOCKED: inbox/ originals are read-only." >&2
    echo "Move '$file' to inbox/processed/ first, then operate on the copy there." >&2
    exit 2
fi

exit 0
