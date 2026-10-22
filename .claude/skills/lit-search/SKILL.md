---
name: lit-search
description: Literature search through the Web of Science and Scopus APIs, abstracts included, written to a CSV.
  Use whenever the user asks for a WoS or Scopus search, a literature sweep, or search strings run against those
  databases. Usage: /lit-search <topic or ready-made query> [wos|scopus]
  Example: /lit-search "boundary work" in decentralized organizations
---

# Literature search — Web of Science and Scopus

Runs `lit-search.py` in this folder. A WoS search goes to the **Web of Science API**, a Scopus search to the
**Scopus API** — never substitute OpenAlex, Google Scholar, a web search or your own knowledge for either. If
the API route fails, stop and report the failure in plain words; do not "help" with another source.

## The keys — never in the chat

- **Never read, print, cat, grep or copy anything in `.secrets/`**, and never ask the user to paste a key into
  the conversation. If the user offers one in the chat, decline and point to the setup below.
- The script finds the keys itself: environment, then `.secrets/*.env`, then a credential gateway (on Bob's
  server the gateway injects them; nothing to do there).
- **First use, or the preflight says a key is MISSING:** tell the user to open a terminal in the repo root and
  run, themselves:
  `bash .claude/skills/lit-search/setup-keys.sh`
  It asks for each missing key with hidden input, stores it in the gitignored `.secrets/` (mode 600), refuses
  if `.secrets/` is not gitignored, and tests both keys. Do not run it yourself — it needs a human at a
  terminal. Wait until the user says it is done, then run the preflight again.

## Step 1 — Preflight (every time)

```
.claude/skills/lit-search/lit-search.py --check
```

The last line is `READY` or `NOT READY`. On `NOT READY`, report its lines to the user and stop:
- egress outside the JKU range → the JKU VPN must be on (Scopus abstracts are IP-gated to the institution's network);
- `total=0` for WoS → the key authenticates but has no content entitlement (a library/plan question, not a code bug);
- a gateway message "holds no key" → the key has to be added to the server's credential gateway once.

## Step 2 — Build the query

- From a topic, draft the query in the database's own syntax and **show it to the user before running**:
  WoS `TS=(…)` (topic), `TI=`, `SO=`, `PY=`; Scopus `TITLE-ABS-KEY(…)`, `SRCTITLE(…)`, `PUBYEAR > n`.
- A query the user wrote is run exactly as given.
- Mode: `wos` when the user says WoS, or wants WoS citation counts (WoS search, abstracts from Scopus by DOI);
  `scopus` when the user says Scopus. If the user asks for both, run both and report them separately.
- Project recipes and journal filters, if present, are in `working/research/` (e.g. a `wos-search-recipe*.md`,
  a `wos-issn-filter.txt`) — read them before drafting.

## Step 3 — Run

```
.claude/skills/lit-search/lit-search.py --mode wos --query '<query>'
.claude/skills/lit-search/lit-search.py --mode scopus --query '<query>'
```

Default `--limit 500`; add `--out working/research/lit-search-<slug>-<YYYY-MM-DD>.csv` to name the file after
the topic. The script prints the CSV path on stdout and its progress and warnings on stderr.

## Step 4 — Report

- Records returned of total matches, how many with DOI and with abstract, and the CSV path.
- Repeat every ⚠ banner verbatim: **LIMIT REACHED** (offer the re-run with the `--limit` it names), **ZERO
  MATCHES**, **ABSTRACT LOOKUPS FAILED**, **EGRESS OUTSIDE THE JKU RANGE**.
- Then a short, ranked overview (WoS times-cited in mode `wos`) — triage from abstracts only. A paper is not a
  corpus fact until it has been read and digested through the project's own procedure.
