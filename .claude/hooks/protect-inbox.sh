#!/bin/bash
# PreToolUse hook: block edits to inbox/ originals.
# Agents must move files to inbox/processed/ before touching them.

input=$(cat)
file=$(echo "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null)

if [[ "$file" == *"/inbox/"* ]] && [[ "$file" != *"/inbox/processed/"* ]]; then
    echo "BLOCKED: inbox/ originals are read-only." >&2
    echo "Move '$file' to inbox/processed/ first, then operate on the copy there." >&2
    exit 2
fi

exit 0
