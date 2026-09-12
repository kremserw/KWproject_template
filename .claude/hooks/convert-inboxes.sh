#!/bin/bash
# SessionStart hook: convert new inbox drops to Markdown, so a session opens knowing what
# arrived rather than discovering it later.
#
# What it does: hands every TOP-LEVEL file in this project's inbox/ to `md-convert`, which
# writes <name>.md beside the original (PDF, DOCX, PPTX, XLSX, HTML, CSV, EPUB…), OCRs a
# scanned PDF, and skips anything already converted. Originals are never touched or deleted.
# The processed/ archive is deliberately NOT rescanned — the point is to surface what was
# just dropped, not to re-walk what has already been filed.
#
# Dependency, and it is optional: `md-convert` is NOT part of this repo. If it is absent the
# hook exits silently and nothing breaks — the inbox-processor then reads originals with the
# document skills as before. Install it (MarkItDown + ocrmypdf + poppler-utils) only if you
# want the automatic conversion; see SETUP.md.
#
# Scope: CLAUDE_PROJECT_DIR, i.e. THIS repo's inbox and no other. Do not widen this to a
# shared parent directory — on a machine where several projects sit under one mount, a
# session in one project would start converting another project's inbox.
#
# Output: only a JSON object on stdout (per the hooks contract). Exit 0 always.

set -uo pipefail

MDCONVERT="${MDCONVERT:-}"
if [[ -z "$MDCONVERT" ]]; then
  if command -v md-convert >/dev/null 2>&1; then
    MDCONVERT=md-convert
  else
    exit 0   # not installed — this feature is optional, stay silent
  fi
fi
[[ -x "$MDCONVERT" || "$MDCONVERT" == "md-convert" ]] || exit 0
command -v jq >/dev/null 2>&1 || exit 0

ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
inbox="$ROOT/inbox"
[[ -d "$inbox" ]] || exit 0

# Top-level drops only; processed/ is intentionally skipped.
mapfile -d '' files < <(find "$inbox" -mindepth 1 -maxdepth 1 -type f ! -name '.*' -print0 2>/dev/null)
(( ${#files[@]} )) || exit 0

n=$("$MDCONVERT" "${files[@]}" 2>/dev/null | grep -cE '^ok') || true
[[ -n "${n:-}" ]] || n=0
(( n > 0 )) || exit 0

names=$(printf '%s\n' "${files[@]}" | xargs -n1 basename 2>/dev/null | paste -sd', ' -)
msg="INBOX: ${#files[@]} file(s) in inbox/ ($names). $n newly converted to Markdown beside the original. Run the inbox-processor before other work."

jq -n --arg m "$msg" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$m}}'
exit 0
