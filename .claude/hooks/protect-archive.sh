#!/bin/bash
# PreToolUse hook: block edits to archived report versions.
# Archived files in outputs/reports/*/archive/ are permanent history — never edit them.
# To update a report: overwrite the -current.md file; the Writing Agent archives the old one first.

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

if [[ "$file" == *"/outputs/reports/"* ]] && [[ "$file" == *"/archive/"* ]]; then
    echo "BLOCKED: archived reports are read-only history." >&2
    echo "Edit the canonical -current.md report instead (e.g. outputs/reports/main/<slug>-current.md)." >&2
    echo "The Writing Agent will archive the old version before overwriting." >&2
    exit 2
fi

exit 0
