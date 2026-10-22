#!/usr/bin/env bash
# setup-keys.sh — store the Web of Science, Scopus and (optional) OpenAlex API keys for the /lit-search skill.
#
# Run it YOURSELF in a terminal, in the repo root:   bash .claude/skills/lit-search/setup-keys.sh
# Not through Claude, not in a chat: the keys are typed here, hidden, and go only into
#   .secrets/clarivate-wos.env     WOS_STARTER_API_KEY=…   (Clarivate developer portal, institutional Starter key)
#   .secrets/scopus-elsevier.env   SCOPUS_API_KEY=…        (dev.elsevier.com)
#   .secrets/openalex.env          OPENALEX_API_KEY=…      (optional, free: openalex.org/settings/api)
# Without WoS and Scopus keys the skill searches OpenAlex, which needs no key at all; skip what you lack.
# .secrets/ is created mode 700, the files 600. The script refuses to write unless git ignores .secrets/.
# A key already present is kept unless you pass --replace. Other lines in those files are left as they are.
# Nothing is ever printed back; at the end the preflight (lit-search.py --check) tests both keys live.
set -euo pipefail

replace=0
[ "${1:-}" = "--replace" ] && replace=1

root=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Run this inside the project's git repo." >&2; exit 2; }
cd "$root"
here="$root/.claude/skills/lit-search"

if ! git check-ignore -q .secrets/probe.env; then
  echo "REFUSED: .secrets/ is not gitignored in this repo. Add the line  .secrets/  to .gitignore first." >&2
  exit 3
fi

umask 077
mkdir -p .secrets
chmod 700 .secrets

store() {  # store VAR FILE LABEL
  local var=$1 file=$2 label=$3 key
  if [ -f "$file" ] && grep -q "^\(export \)\?$var=..*" "$file" && [ $replace -eq 0 ]; then
    echo "$label: key already stored in $file — kept (use --replace to change it)."
    return
  fi
  read -r -s -p "$label API key (input hidden, Enter to skip): " key; echo
  if [ -z "$key" ]; then echo "$label: skipped."; return; fi
  touch "$file"; chmod 600 "$file"
  { grep -v "^\(export \)\?$var=" "$file" || true; printf '%s=%s\n' "$var" "$key"; } > "$file.tmp"
  chmod 600 "$file.tmp"; mv "$file.tmp" "$file"
  unset key
  echo "$label: stored in $file (mode 600)."
}

store WOS_STARTER_API_KEY .secrets/clarivate-wos.env   "Web of Science (Clarivate Starter)"
store SCOPUS_API_KEY      .secrets/scopus-elsevier.env "Scopus (Elsevier)"
store OPENALEX_API_KEY    .secrets/openalex.env        "OpenAlex (optional)"

echo
echo "Testing the keys live (Scopus needs the JKU network or VPN):"
python3 "$here/lit-search.py" --check
