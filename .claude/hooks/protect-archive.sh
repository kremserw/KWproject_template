#!/bin/bash
# PreToolUse hook: block edits to archived report versions.
# Archived files in outputs/reports/*/archive/ are permanent history — never edit them.
# To update a report: overwrite the -current.md file; the Writing Agent archives the old one first.

input=$(cat)
file=$(echo "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null)

if [[ "$file" == *"/outputs/reports/"* ]] && [[ "$file" == *"/archive/"* ]]; then
    echo "BLOCKED: archived reports are read-only history." >&2
    echo "Edit the canonical -current.md report instead (e.g. outputs/reports/main/<slug>-current.md)." >&2
    echo "The Writing Agent will archive the old version before overwriting." >&2
    exit 2
fi

exit 0
