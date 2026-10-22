---
name: lit-search
description: Literature search through the Web of Science, Scopus or OpenAlex APIs, abstracts included, written to a CSV.
  Use whenever the user asks for a WoS, Scopus or OpenAlex search, a literature sweep, or search strings run against
  those databases. Usage: /lit-search <topic or ready-made query> [wos|scopus|openalex]
  Example: /lit-search "boundary work" in decentralized organizations
---

# Literature search — Web of Science, Scopus, OpenAlex

Runs `lit-search.py` in this folder. A WoS search goes to the **Web of Science API**, a Scopus search to the
**Scopus API**, an OpenAlex search to the **OpenAlex API** — never Google Scholar, a web search or your own
knowledge instead.

## Which source

- The user names one (WoS, Scopus, OpenAlex) → that one.
- The user names none, or several → **combined search** (`--mode all`) over every source available here
  (READY: all three): one integrated CSV, records merged by DOI, the `found_in` column saying where each was
  found ("WoS; Scopus; OpenAlex", "WoS", …), each source's citation count in its own column. Report it as one
  result, saying per record where it was found.
- **Preflight says `OPENALEX ONLY`** (no WoS and no Scopus key in this setup) → use OpenAlex automatically,
  whatever was asked, and say so plainly in the first line of the report: "Searched OpenAlex — no WoS/Scopus
  keys here."
- A WoS or Scopus key that **exists but fails** (`NOT READY`) is not that case: report the failure and stop. Do
  not switch to OpenAlex unless the user then asks for it.

## The keys — never in the chat

- **Never read, print, cat, grep or copy anything in `.secrets/`**, and never ask the user to paste a key into
  the conversation. If the user offers one in the chat, decline and point to the setup below.
- The script finds the keys itself: environment, then `.secrets/*.env`, then a credential gateway (on Bob's
  server the gateway injects them; nothing to do there). OpenAlex needs no key; an optional personal one gives
  its own daily budget instead of the one shared by everyone behind the same IP.
- **To add keys** (first use, or the preflight says a key is MISSING and the user has one): tell the user to open
  a terminal in the repo root and run, themselves:
  `bash .claude/skills/lit-search/setup-keys.sh`
  It asks for each missing key with hidden input (Enter skips), stores it in the gitignored `.secrets/`
  (mode 600), refuses if `.secrets/` is not gitignored, and tests the keys. Do not run it yourself — it needs a
  human at a terminal. Wait until the user says it is done, then run the preflight again. Someone without
  WoS/Scopus keys does not need it at all.

## Step 1 — Preflight (every time)

```
.claude/skills/lit-search/lit-search.py --check
```

The last line is `READY`, `OPENALEX ONLY …` or `NOT READY`. On `NOT READY`, report its lines and stop:
- egress outside the JKU range → the JKU VPN must be on (Scopus abstracts are IP-gated to the institution's network);
- `total=0` for WoS → the key authenticates but has no content entitlement (a library/plan question, not a code bug);
- a gateway message "holds no key" / "not attached" → the key has to be added or attached in the server's
  credential gateway once.

## Step 2 — Build the query

- From a topic, draft the query in the database's own syntax and **show it to the user before running**:
  - WoS `TS=(…)` (topic), `TI=`, `SO=`, `PY=`;
  - Scopus `TITLE-ABS-KEY(…)`, `SRCTITLE(…)`, `PUBYEAR > n`;
  - OpenAlex: `--query` is matched against title + abstract (`"quoted phrases"`, `AND`, `OR`, `NOT`, stemmed);
    years, journals etc. go in `--filter` as raw OpenAlex filters, e.g. `publication_year:>2019`,
    `primary_location.source.issn:0001-8392|1537-5390`, `type:article`.
- A query the user wrote is run exactly as given.
- Mode `wos` gives WoS citation counts (WoS search, abstracts from Scopus by DOI); `scopus` Scopus counts;
  `openalex` OpenAlex's own counts. OpenAlex matching is looser — say so when reporting, and prefer narrow phrases.
- Combined: draft all three and show them together; they should ask the same question (same phrase, same years).
- Project recipes and journal filters, if present, are in `working/research/` (e.g. a `wos-search-recipe*.md`,
  a `wos-issn-filter.txt`) — read them before drafting.

## Step 3 — Run

```
.claude/skills/lit-search/lit-search.py --mode wos --query '<query>'
.claude/skills/lit-search/lit-search.py --mode scopus --query '<query>'
.claude/skills/lit-search/lit-search.py --mode openalex --query '<query>' [--filter '<filters>']
.claude/skills/lit-search/lit-search.py --mode all --wos-query '<q>' --scopus-query '<q>' \
    --openalex-query '<q>' [--filter '<filters>']
```

In `--mode all`, a source without a key or without a query is skipped and named on stderr ("not searched: …");
a source that fails is reported in a ⚠ SOURCE FAILED banner and the rest still run.

Default `--limit 500` (OpenAlex: the most-cited first); add `--out working/research/lit-search-<slug>-<YYYY-MM-DD>.csv`
to name the file after the topic. The script ranks the records by citations per year — the highest citation count
across the sources, divided by the years since publication plus one; ties newer first; a record without a year or a
count last — and writes the CSV in that order (its `rank` and `cites_per_year` columns). On stdout it prints an
OVERVIEW of the top 15 in that order, each with the start of its abstract, and the CSV path as the last line; its
progress and warnings go to stderr.

## Step 4 — Report

- Which source was searched, records returned of total matches, how many with DOI and with abstract, the CSV path.
  Combined: the distinct works, the per-source counts and the "found in …" breakdown the script prints. A record
  found in one source only is often a coverage or year-boundary difference (online-first vs. issue year), not a
  unique find — say so before calling anything unique.
- Repeat every ⚠ banner verbatim: **LIMIT REACHED** (offer the re-run with the `--limit` it names), **ZERO
  MATCHES**, **ABSTRACT LOOKUPS FAILED**, **SOURCE FAILED**, **EGRESS OUTSIDE THE JKU RANGE**.
- Then the ranked overview, from the script's OVERVIEW and in its order (by citations per year, in every mode; "found
  in" is shown but does not rank) — one line a record with your triage from its abstract; never re-sort it, and never
  read the whole CSV for it. A paper is not a corpus fact until it has been read and digested through the project's
  own procedure.
