#!/usr/bin/env python3
"""
lit-search.py — literature search WITH abstracts via Web of Science, Scopus or OpenAlex.
The engine of the /lit-search skill (.claude/skills/lit-search/SKILL.md).
Started as a project script (2026-06); made a skill of the KW project template 2026-10-22.

Two modes:
  --mode wos     [Option A]  Web of Science (Starter API) search -> then enrich each
                             hit with the ABSTRACT from Scopus, matched by DOI.
                             WoS supplies the authoritative search + WoS times-cited;
                             Scopus supplies the abstract WoS Starter does not return.
  --mode scopus  [Option B]  Scopus-only search. Uses the COMPLETE view, which returns
                             the abstract + full author list INLINE (one call per 25).
                             Falls back to STANDARD view + per-DOI abstract retrieval
                             if COMPLETE is not entitled (announced on stderr).
  --mode openalex            OpenAlex search (free, no key needed): the query is matched against
                             title + abstract (quoted phrases, AND/OR/NOT); --filter adds raw
                             OpenAlex filters (e.g. publication_year:>2019). Sorted by citations.
  --mode all                 Combined search over every source that has a key here (OpenAlex always),
                             one query per source (--wos-query, --scopus-query, --openalex-query);
                             records merged by DOI (else title+year) into ONE CSV whose found_in
                             column says where each was found, with each source's citation count.
  --check                    Preflight only: where the keys come from, the egress IP,
                             and one tiny live call to each API. Run this first.

A WoS search always goes to the WoS API, a Scopus search always to the Scopus API, and
the script never switches source by itself: if an API fails, the run fails loudly.
OpenAlex runs only as --mode openalex. The skill uses it when chosen, or automatically
when NEITHER a WoS nor a Scopus key exists (preflight line OPENALEX ONLY) — never as a
silent substitute for a WoS/Scopus key that is there but failing.

Output: a UTF-8 CSV — default working/research/lit-search-<mode>-<date>.csv, relative
to the repo root — its rows ranked by citations per year (the highest count across the
sources, divided by the years since publication plus one; ties newer first), the rank and
cites_per_year columns saying so; then an OVERVIEW of the top 15 on stdout, each with the
start of its abstract, and the CSV path as stdout's last line.

KEYS — never hard-coded, never printed, never passed on the command line. Looked up in
this order, per service:
  1. the environment: WOS_STARTER_API_KEY, SCOPUS_API_KEY
  2. the gitignored files .secrets/clarivate-wos.env and .secrets/scopus-elsevier.env
     in the repo root (lines KEY=value) — written by setup-keys.sh in this folder
  3. a credential gateway: when neither exists and an HTTPS proxy is set (Bob's
     server container), the requests go out with a placeholder and the gateway
     injects the real key. Without a proxy and without a key, the run stops and
     names setup-keys.sh.
  OpenAlex needs no key. Without one, all users behind the same IP share one small
  free daily budget; an optional personal key (OPENALEX_API_KEY, .secrets/openalex.env,
  free at openalex.org/settings/api) gives its own budget. setup-keys.sh offers it too.

EXAMPLES (default --limit is 500; pass --limit only to change it):
  .claude/skills/lit-search/lit-search.py --check
  .claude/skills/lit-search/lit-search.py --mode wos \
      --query 'TS=("boundary work" AND (decentrali* OR "self-managing"))'
  .claude/skills/lit-search/lit-search.py --mode scopus \
      --query 'TITLE-ABS-KEY("boundary work" AND decentrali*)'

LIMIT FLAG: if a query has MORE matches than --limit, the run prints a loud
"LIMIT REACHED — RESULTS TRUNCATED" banner AND writes a sidecar <csv>.LIMIT-HIT.txt
next to the CSV (telling you the exact --limit needed to capture all). No silent truncation.

BOUNDARY CONDITION: Scopus content entitlement is IP-gated — the egress must be in the
JKU range 140.78.0.0/16 (JKU VPN, or the campus network). Off-range the Scopus calls may
return little/no content; the run warns when the egress is outside the range.
"""
import argparse, csv, ipaddress, json, os, sys, time, urllib.parse, urllib.request, urllib.error
from datetime import date
from pathlib import Path

WOS_BASE        = "https://api.clarivate.com/apis/wos-starter/v1/documents"
SCOPUS_SEARCH   = "https://api.elsevier.com/content/search/scopus"
SCOPUS_ABSTRACT = "https://api.elsevier.com/content/abstract/doi"
OPENALEX_WORKS  = "https://api.openalex.org/works"
JKU_RANGE       = ipaddress.ip_network("140.78.0.0/16")
GATEWAY_PLACEHOLDER = "gateway-managed"

REPO_ROOT = Path(__file__).resolve().parents[3]          # <repo>/.claude/skills/lit-search/
SECRETS = {"WOS_STARTER_API_KEY": REPO_ROOT / ".secrets" / "clarivate-wos.env",
           "SCOPUS_API_KEY":      REPO_ROOT / ".secrets" / "scopus-elsevier.env",
           "OPENALEX_API_KEY":    REPO_ROOT / ".secrets" / "openalex.env"}

COLUMNS = ["mode", "rank", "title", "authors", "year", "journal", "volume", "issue",
           "pages", "doi", "times_cited", "times_cited_src", "cites_per_year",
           "abstract", "abstract_chars", "abstract_src", "record_id"]


# ----------------------------- keys -----------------------------
def _read_env_file(path, name):
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:].strip()
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return ""


def get_key(name):
    """Return (key, source). source is 'env', 'file', 'gateway' or '' (none). Never the value."""
    if os.environ.get(name):
        return os.environ[name], "env"
    v = _read_env_file(SECRETS[name], name)
    if v:
        return v, "file"
    if name != "OPENALEX_API_KEY" and (os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")):
        return GATEWAY_PLACEHOLDER, "gateway"
    return "", ""


def no_key_exit(name):
    sys.exit(f"{name} not found — not in the environment, not in {SECRETS[name].relative_to(REPO_ROOT)}, "
             f"and no credential gateway. Run in a terminal (not in the chat):\n"
             f"  bash .claude/skills/lit-search/setup-keys.sh")


# ----------------------------- http -----------------------------
def _get(url, headers, params=None, timeout=45, retries=2):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:      # rate-limited: back off
                time.sleep(2 + attempt * 3); continue
            body = e.read()[:400].decode("utf-8", "replace")
            if e.code == 429 and "openalex" in url:
                raise RuntimeError("HTTP 429: the free OpenAlex budget for this IP is used up for today — a "
                                   "personal OpenAlex key (setup-keys.sh) gives its own budget")
            if "credential_not_found" in body:           # the gateway has no key for this host
                host = urllib.parse.urlparse(url).hostname
                raise RuntimeError(f"HTTP {e.code}: the credential gateway holds no key for {host} — "
                                   f"it must be added there once (not in the chat)")
            if "access_restricted" in body:              # key is there, not attached to this agent
                host = urllib.parse.urlparse(url).hostname
                raise RuntimeError(f"HTTP {e.code}: the credential gateway holds a key for {host}, but it is "
                                   f"not attached to this agent — attach it in the gateway's admin UI")
            raise RuntimeError(f"HTTP {e.code}: {body[:200]}")
    raise RuntimeError("unreachable")


def egress_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=15) as r:
            return r.read().decode().strip()
    except Exception:
        return ""


def warn_if_off_jku(ip):
    try:
        inside = bool(ip) and ipaddress.ip_address(ip) in JKU_RANGE
    except ValueError:
        inside = False
    if not inside:
        bar = "=" * 70
        sys.stderr.write(f"\n{bar}\n⚠  EGRESS {ip or 'unknown'} IS OUTSIDE THE JKU RANGE 140.78.0.0/16 — Scopus may "
                         f"return few or no abstracts. Connect the JKU VPN and re-run.\n{bar}\n")
    return inside


# ----------------------------- Web of Science (Starter) -----------------------------
def wos_search(key, query, db, limit, sleep):
    headers = {"X-ApiKey": key, "Accept": "application/json"}
    hits, page, total = [], 1, 0
    while len(hits) < limit:
        per = min(50, limit - len(hits))
        data = _get(WOS_BASE, headers, {"db": db, "q": query, "limit": per, "page": page})
        batch = data.get("hits", []) or []
        total = (data.get("metadata", {}) or {}).get("total", total)
        if not batch:
            break
        hits.extend(batch)
        sys.stderr.write(f"  [wos] page {page}: +{len(batch)} (have {len(hits)}/{min(limit,total)} of {total})\n")
        if len(hits) >= total:
            break
        page += 1
        time.sleep(sleep)
    return hits[:limit], total


def wos_to_row(h):
    src   = h.get("source", {}) or {}
    names = (h.get("names", {}) or {}).get("authors", []) or []
    cites = h.get("citations", []) or []
    wos_c = next((c.get("count") for c in cites if c.get("db") == "WOS"), "")
    return {
        "title":  h.get("title", ""),
        "authors": "; ".join(a.get("displayName", "") for a in names),
        "year":   src.get("publishYear", ""),
        "journal": src.get("sourceTitle", ""),
        "volume": src.get("volume", ""),
        "issue":  src.get("issue", ""),
        "pages":  (src.get("pages", {}) or {}).get("range", ""),
        "doi":    (h.get("identifiers", {}) or {}).get("doi", ""),
        "times_cited": wos_c, "times_cited_src": "WoS" if wos_c != "" else "",
        "record_id": h.get("uid", ""),
    }


# ----------------------------- Scopus -----------------------------
def _scopus_desc(obj):
    """Pull a plaintext abstract from a coredata/entry dict's dc:description."""
    desc = obj.get("dc:description")
    if isinstance(desc, str):
        return desc.strip()
    if isinstance(desc, dict):                       # occasionally nested {abstract:{...}}
        return json.dumps(desc)[:4000]
    return ""


def scopus_abstract_by_doi(key, doi, sleep):
    if not doi:
        return ("", "")
    headers = {"X-ELS-APIKey": key, "Accept": "application/json"}
    try:
        data = _get(f"{SCOPUS_ABSTRACT}/{urllib.parse.quote(doi)}", headers,
                    {"httpAccept": "application/json"})
    except Exception as e:
        return ("", f"scopus-error:{str(e)[:50]}")
    core = (data.get("abstracts-retrieval-response", {}) or {}).get("coredata", {}) or {}
    time.sleep(sleep)
    txt = _scopus_desc(core)
    return (txt, "scopus-doi" if txt else "none")


def scopus_authors(entry):
    au = entry.get("author")
    if isinstance(au, list):
        return "; ".join(a.get("authname") or a.get("ce:indexed-name") or "" for a in au)
    return entry.get("dc:creator", "")               # STANDARD view: first author only


def scopus_search(key, query, limit, sleep, want_abstracts):
    headers = {"X-ELS-APIKey": key, "Accept": "application/json"}
    view = "COMPLETE"
    entries, start, total = [], 0, 0
    while len(entries) < limit:
        per = min(25, limit - len(entries))
        try:
            data = _get(SCOPUS_SEARCH, headers,
                        {"query": query, "count": per, "start": start, "view": view})
        except Exception as e:
            if view == "COMPLETE" and "credential gateway" not in str(e):
                sys.stderr.write(f"  [scopus] COMPLETE view unavailable ({str(e)[:60]}); "
                                 f"falling back to STANDARD + per-DOI abstracts\n")
                view = "STANDARD"; continue
            raise
        batch = (data.get("search-results", {}) or {}).get("entry", []) or []
        total = int((data.get("search-results", {}) or {}).get("opensearch:totalResults", total))
        if not batch or "error" in batch[0]:
            break
        entries.extend(batch)
        sys.stderr.write(f"  [scopus/{view}] start {start}: +{len(batch)} "
                         f"(have {len(entries)}/{min(limit,total)} of {total})\n")
        start += per
        if start >= total:
            break
        time.sleep(sleep)
    return entries[:limit], total, view


def scopus_to_row(e, view, key, sleep, want_abstracts):
    doi = e.get("prism:doi", "")
    abs = _scopus_desc(e); a_src = "scopus-complete" if abs_present(abs) else ""
    if want_abstracts and not abs and doi:           # STANDARD view -> retrieve by DOI
        abs, a_src = scopus_abstract_by_doi(key, doi, sleep)
    return {
        "title":  e.get("dc:title", ""),
        "authors": scopus_authors(e),
        "year":   (e.get("prism:coverDate", "") or "")[:4],
        "journal": e.get("prism:publicationName", ""),
        "volume": e.get("prism:volume", ""),
        "issue":  e.get("prism:issueIdentifier", ""),
        "pages":  e.get("prism:pageRange", ""),
        "doi":    doi,
        "times_cited": e.get("citedby-count", ""), "times_cited_src": "Scopus",
        "abstract": abs, "abstract_chars": len(abs), "abstract_src": a_src or "none",
        "record_id": e.get("eid", ""),
    }


def abs_present(x):
    return isinstance(x, str) and len(x) > 0


# ----------------------------- OpenAlex -----------------------------
def _oa_params(key, extra):
    if key:
        extra["api_key"] = key
    return extra


def openalex_filter(query, extra_filter):
    f = "title_and_abstract.search:" + query.replace(",", " ")
    return f + ("," + extra_filter if extra_filter else "")


def openalex_search(key, query, extra_filter, limit, sleep):
    flt = openalex_filter(query, extra_filter)
    works, cursor, total = [], "*", 0
    while len(works) < limit and cursor:
        per = min(200, limit - len(works))
        data = _get(OPENALEX_WORKS, {"Accept": "application/json"},
                    _oa_params(key, {"filter": flt, "sort": "cited_by_count:desc",
                                     "per-page": per, "cursor": cursor}))
        meta = data.get("meta", {}) or {}
        total = meta.get("count", total) or 0
        batch = data.get("results", []) or []
        if not batch:
            break
        works.extend(batch)
        sys.stderr.write(f"  [openalex] +{len(batch)} (have {len(works)}/{min(limit,total)} of {total})\n")
        cursor = meta.get("next_cursor")
        time.sleep(sleep)
    return works[:limit], total


def openalex_abstract(inv):
    if not inv:
        return ""
    pos = [(i, w) for w, idx in inv.items() for i in idx]
    return " ".join(w for _, w in sorted(pos))


def openalex_to_row(w):
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    bib = w.get("biblio") or {}
    fp, lp = bib.get("first_page") or "", bib.get("last_page") or ""
    abs = openalex_abstract(w.get("abstract_inverted_index"))
    return {
        "title":  w.get("display_name") or w.get("title") or "",
        "authors": "; ".join(((a.get("author") or {}).get("display_name") or "")
                             for a in (w.get("authorships") or [])),
        "year":   w.get("publication_year", ""),
        "journal": src.get("display_name", ""),
        "volume": bib.get("volume") or "", "issue": bib.get("issue") or "",
        "pages":  f"{fp}-{lp}" if fp and lp else fp,
        "doi":    (w.get("doi") or "").replace("https://doi.org/", ""),
        "times_cited": w.get("cited_by_count", ""), "times_cited_src": "OpenAlex",
        "abstract": abs, "abstract_chars": len(abs), "abstract_src": "openalex" if abs else "none",
        "record_id": (w.get("id") or "").replace("https://openalex.org/", ""),
    }


# ----------------------------- ranking and overview -----------------------------
# One order for every mode, the CSV's rank column and the overview alike (Waldemar's choice, 2026-10-22): recency and
# relevance together -- the highest citation count across the record's sources, divided by the years since publication
# plus one, most first; ties newer first; a record without a year or a count after every scored one, by its count.
OVERVIEW_TOP, OVERVIEW_EXCERPT = 15, 350
CITE_COLUMNS = ("times_cited", "cited_wos", "cited_scopus", "cited_openalex")


def _whole(v):
    try:
        return int(str(v).strip())
    except ValueError:
        return -1


def cites_per_year(row, this_year):
    """(score or None, year, highest count): None when the record has no count or no year."""
    count = max(_whole(row.get(c, "")) for c in CITE_COLUMNS)
    year = _whole(row.get("year", ""))
    if count < 0 or year < 1:
        return None, year, count
    return count / (max(0, this_year - year) + 1), year, count


def rank_rows(rows, this_year=None):
    """rows sorted in place in the ranking above, each given its rank and its cites_per_year."""
    this_year = this_year or date.today().year
    scored = [(cites_per_year(r, this_year), i, r) for i, r in enumerate(rows)]

    def order(x):
        (score, year, count), i, _ = x
        return (0, -score, -year, i) if score is not None else (1, -count, -year, i)
    scored.sort(key=order)
    rows[:] = [r for _, _, r in scored]
    for n, ((score, _, _), _, r) in enumerate(scored, 1):
        r["rank"] = n
        r["cites_per_year"] = f"{score:.2f}" if score is not None else ""
    return rows


def _flat(v, n):
    """A cell on one line: control characters dropped, whitespace collapsed, at most n characters."""
    return " ".join("".join(c if c.isprintable() else " " for c in str(v if v is not None else "")).split())[:n]


def print_overview(rows, combined):
    """The overview the report gives (SKILL.md Step 4), on stdout in rank order: the top records, each with year,
    counts, cites per year, title, journal, DOI and the start of its abstract."""
    top = rows[:OVERVIEW_TOP]
    print(f"OVERVIEW the top {len(top)} of {len(rows)} records by citations per year (the highest count across the "
          f"sources, divided by the years since publication plus one), most first; ties newer first -- triage from "
          f"abstracts only; the CSV holds them all")
    for r in top:
        if combined:
            cites = " · ".join(f"{c[6:]} {_flat(r.get(c), 12)}" for c in CITE_COLUMNS[1:] if _flat(r.get(c), 12))
        else:
            cites = f"cited {_flat(r.get('times_cited'), 12)}" if _flat(r.get("times_cited"), 12) else ""
        head = f"[{_flat(r.get('found_in'), 40)}] " if combined else ""
        rate = f"{float(r['cites_per_year']):.1f}/yr" if r.get("cites_per_year") else "no score"
        print(f"  {r['rank']}. {head}{_flat(r.get('year'), 4) or '?'} · {cites or 'no count'} · {rate} · "
              f"{_flat(r.get('title'), 200)} -- {_flat(r.get('journal'), 80)} · doi {_flat(r.get('doi'), 80) or 'none'}")
        a = _flat(r.get("abstract"), OVERVIEW_EXCERPT + 1)
        print("     abstract: " + ((a[:OVERVIEW_EXCERPT] + "...") if len(a) > OVERVIEW_EXCERPT else (a or "none")))


# ----------------------------- combined (--mode all) -----------------------------
COMBINED_COLUMNS = ["rank", "found_in", "n_sources", "title", "authors", "year", "journal", "volume",
                    "issue", "pages", "doi", "cited_wos", "cited_scopus", "cited_openalex", "cites_per_year",
                    "abstract", "abstract_chars", "abstract_src", "wos_id", "scopus_id", "openalex_id"]
SOURCE_LABEL = {"wos": "WoS", "scopus": "Scopus", "openalex": "OpenAlex"}


def _merge_key(r):
    doi = (r.get("doi") or "").strip().lower()
    if doi:
        return "doi:" + doi
    title = "".join(ch for ch in (r.get("title") or "").lower() if ch.isalnum())
    return f"t:{title}:{r.get('year', '')}"


def combine(per_source):
    """per_source: {src: [rows]} -> merged rows, one per work."""
    merged = {}
    for src in ("wos", "scopus", "openalex"):
        for r in per_source.get(src, []):
            k = _merge_key(r)
            m = merged.get(k)
            if m is None:
                m = merged[k] = {c: "" for c in COMBINED_COLUMNS}
                m["_src"] = []
                for c in ("title", "authors", "year", "journal", "volume", "issue", "pages", "doi"):
                    m[c] = r.get(c, "")
            m["_src"].append(src)
            m[f"cited_{src}"] = r.get("times_cited", "")
            m[f"{src}_id"] = r.get("record_id", "")
            for c in ("authors", "journal", "volume", "issue", "pages", "doi"):
                if not m[c] and r.get(c):
                    m[c] = r[c]
            if not abs_present(m["abstract"]) and abs_present(r.get("abstract")):
                m["abstract"], m["abstract_src"] = r["abstract"], r.get("abstract_src", "")
    rows = list(merged.values())
    for m in rows:
        m["found_in"] = "; ".join(SOURCE_LABEL[s] for s in m["_src"])
        m["n_sources"] = len(m["_src"])
        m["abstract_chars"] = len(m["abstract"] or "")
        if not m["abstract_src"]:
            m["abstract_src"] = "none"
    return rows


def run_combined(args):
    want_abs = not args.no_abstracts
    wos_key, wos_src = get_key("WOS_STARTER_API_KEY")
    sc_key, sc_src = get_key("SCOPUS_API_KEY")
    oa_key, _ = get_key("OPENALEX_API_KEY")
    queries = {"wos": args.wos_query, "scopus": args.scopus_query, "openalex": args.openalex_query}
    keys = {"wos": wos_key, "scopus": sc_key, "openalex": True}
    plan, skipped = [], []
    for s in ("wos", "scopus", "openalex"):
        if not keys[s]:
            skipped.append(f"{SOURCE_LABEL[s]} (no key)")
        elif not queries[s]:
            skipped.append(f"{SOURCE_LABEL[s]} (no query given)")
        else:
            plan.append(s)
    if not plan:
        sys.exit("--mode all: no source to search (each needs its key and its --<source>-query)")
    if sc_key and want_abs:
        warn_if_off_jku(egress_ip())
    per_source, totals, failed = {}, {}, []
    for s in plan:
        try:
            if s == "wos":
                sys.stderr.write(f"WoS search: {queries[s]!r} (limit {args.limit})\n")
                hits, totals[s] = wos_search(wos_key, queries[s], args.db, args.limit, args.sleep)
                per_source[s] = [wos_to_row(h) for h in hits]
            elif s == "scopus":
                sys.stderr.write(f"Scopus search: {queries[s]!r} (limit {args.limit})\n")
                entries, totals[s], view = scopus_search(sc_key, queries[s], args.limit, args.sleep, want_abs)
                per_source[s] = [scopus_to_row(e, view, sc_key, args.sleep, False) for e in entries]
            else:
                sys.stderr.write(f"OpenAlex search: {queries[s]!r} filter {args.filter or '-'} (limit {args.limit})\n")
                works, totals[s] = openalex_search(oa_key, queries[s], args.filter, args.limit, args.sleep)
                per_source[s] = [openalex_to_row(w) for w in works]
        except RuntimeError as e:
            failed.append(f"{SOURCE_LABEL[s]}: {e}")
            sys.stderr.write(f"  [{s}] FAILED — {e}\n")
    rows = combine(per_source)
    n_err = 0
    if want_abs and sc_key:                       # fill missing abstracts from Scopus by DOI
        for m in rows:
            if not abs_present(m["abstract"]) and m["doi"]:
                m["abstract"], m["abstract_src"] = scopus_abstract_by_doi(sc_key, m["doi"], args.sleep)
                m["abstract_chars"] = len(m["abstract"])
                n_err += str(m["abstract_src"]).startswith("scopus-error")
    rank_rows(rows)

    out = Path(args.out) if args.out else \
        REPO_ROOT / "working" / "research" / f"lit-search-all-{date.today().isoformat()}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COMBINED_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for m in rows:
            w.writerow({k: m.get(k, "") for k in COMBINED_COLUMNS})

    bar = "=" * 70
    sys.stderr.write(f"\nDONE: {len(rows)} distinct works -> {out}\n")
    for s in plan:
        if s in per_source:
            sys.stderr.write(f"  {SOURCE_LABEL[s]}: {len(per_source[s])} of {totals[s]} matches\n")
    combos = {}
    for m in rows:
        combos[m["found_in"]] = combos.get(m["found_in"], 0) + 1
    for c, n in sorted(combos.items(), key=lambda x: -x[1]):
        sys.stderr.write(f"  found in {c}: {n}\n")
    sys.stderr.write(f"  with DOI: {sum(1 for m in rows if m['doi'])}/{len(rows)} | "
                     f"with abstract: {sum(1 for m in rows if abs_present(m['abstract']))}/{len(rows)}\n")
    if skipped:
        sys.stderr.write(f"  not searched: {', '.join(skipped)}\n")
    if failed:
        sys.stderr.write(f"\n{bar}\n⚠  SOURCE FAILED — the combined result is missing it:\n  " +
                         "\n  ".join(failed) + f"\n{bar}\n")
    if n_err:
        sys.stderr.write(f"\n{bar}\n⚠  {n_err} ABSTRACT LOOKUPS FAILED at Scopus (abstract_src scopus-error:… in the "
                         f"CSV). The records are there, their abstracts are not.\n{bar}\n")
    marker = Path(str(out) + ".LIMIT-HIT.txt")
    cut = [s for s in per_source if totals[s] > len(per_source[s])]
    if cut:
        msg = "LIMIT REACHED — RESULTS TRUNCATED: " + "; ".join(
            f"{SOURCE_LABEL[s]} returned {len(per_source[s])} of {totals[s]}" for s in cut) + \
            f". Re-run with --limit {max(totals[s] for s in cut)} (or higher) to capture all of them."
        sys.stderr.write(f"\n{bar}\n⚠  {msg}\n{bar}\n")
        marker.write_text(msg + "\n\n" + "\n".join(f"{s}: {queries[s]}" for s in plan) +
                          f"\nlimit: {args.limit}\ncsv:   {out}\n", encoding="utf-8")
        sys.stderr.write(f"  flag file written: {marker}\n")
    elif marker.exists():
        marker.unlink()
    print_overview(rows, combined=True)
    print(out)


# ----------------------------- preflight -----------------------------
def check():
    """One line per fact; exit 0 only if both APIs answered with content."""
    ok = True
    ip = egress_ip()
    print(f"egress IP: {ip or 'unknown'} ({'inside' if warn_if_off_jku(ip) else 'OUTSIDE'} JKU 140.78.0.0/16)")
    wos_key, wos_src = get_key("WOS_STARTER_API_KEY")
    sc_key, sc_src = get_key("SCOPUS_API_KEY")
    print(f"WoS key: {wos_src or 'MISSING'} | Scopus key: {sc_src or 'MISSING'}")
    if wos_key:
        try:
            d = _get(WOS_BASE, {"X-ApiKey": wos_key, "Accept": "application/json"},
                     {"db": "WOS", "q": "TS=(organizational routines)", "limit": 1, "page": 1})
            total = (d.get("metadata", {}) or {}).get("total", 0)
            print(f"WoS Starter: OK, test query total={total}")
            if not total:
                ok = False
                print("WoS Starter: total=0 — the key authenticates but sees no records "
                      "(no content entitlement on this key; ask the library which Starter plan it carries)")
        except Exception as e:
            ok = False; print(f"WoS Starter: FAILED — {e}")
    else:
        ok = False
    if sc_key:
        try:
            d = _get(SCOPUS_SEARCH, {"X-ELS-APIKey": sc_key, "Accept": "application/json"},
                     {"query": 'TITLE-ABS-KEY("organizational routines")', "count": 1, "view": "COMPLETE"})
            sr = d.get("search-results", {}) or {}
            e = (sr.get("entry") or [{}])[0]
            print(f"Scopus: OK, test query total={sr.get('opensearch:totalResults')}, "
                  f"COMPLETE-view abstract {'present' if _scopus_desc(e) else 'MISSING'}")
            if not _scopus_desc(e):
                ok = False
        except Exception as e:
            ok = False; print(f"Scopus: FAILED — {e}")
    else:
        ok = False
    oa_key, oa_src = get_key("OPENALEX_API_KEY")
    oa_ok = True
    try:
        d = _get(OPENALEX_WORKS, {"Accept": "application/json"},
                 _oa_params(oa_key, {"filter": 'title_and_abstract.search:"organizational routines"',
                                     "per-page": 1, "select": "id"}))
        print(f"OpenAlex: OK ({'own key' if oa_key else 'no key, shared free budget'}), "
              f"test query total={(d.get('meta') or {}).get('count')}")
    except Exception as e:
        oa_ok = False; print(f"OpenAlex: FAILED — {e}")
    if not (wos_key and sc_key):
        print("Missing key(s): run in a terminal (not in the chat): bash .claude/skills/lit-search/setup-keys.sh")
    if ok:
        print("READY")
        return 0
    if not wos_key and not sc_key and oa_ok:
        print("OPENALEX ONLY — no WoS and no Scopus key here; searches go to OpenAlex")
        return 0
    print("NOT READY")
    return 1


# ----------------------------- main -----------------------------
def main():
    ap = argparse.ArgumentParser(description="WoS/Scopus/OpenAlex literature search with abstracts.")
    ap.add_argument("--check", action="store_true", help="preflight: keys, egress IP, one live call per API")
    ap.add_argument("--mode", choices=["wos", "scopus", "openalex", "all"])
    ap.add_argument("--query", help="raw query in the chosen DB's syntax")
    ap.add_argument("--limit", type=int, default=500,
                    help="max records to return (default 500); a loud flag + sidecar "
                         "file fire automatically if the query has MORE matches than this")
    ap.add_argument("--db", default="WOS", help="WoS database (default WOS)")
    ap.add_argument("--filter", default="", help="openalex only: extra raw OpenAlex filters, comma-separated")
    ap.add_argument("--wos-query", default="", help="--mode all: the WoS query")
    ap.add_argument("--scopus-query", default="", help="--mode all: the Scopus query")
    ap.add_argument("--openalex-query", default="", help="--mode all: the OpenAlex query")
    ap.add_argument("--no-abstracts", action="store_true", help="skip abstract fetching")
    ap.add_argument("--sleep", type=float, default=0.3, help="politeness delay between calls")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    if args.check:
        sys.exit(check())
    if args.mode == "all":
        return run_combined(args)
    if not (args.mode and args.query):
        ap.error("--mode and --query are required (or --check, or --mode all with per-source queries)")

    want_abs = not args.no_abstracts
    if args.mode == "openalex":
        oa_key, oa_src = get_key("OPENALEX_API_KEY")
        sys.stderr.write(f"OpenAlex search: {args.query!r} filter {args.filter or '-'} (limit {args.limit}; "
                         f"{'own key' if oa_key else 'no key'})\n")
        works, total = openalex_search(oa_key, args.query, args.filter, args.limit, args.sleep)
        rows = []
        for i, w in enumerate(works, 1):
            r = openalex_to_row(w); r["mode"] = "openalex"; r["rank"] = i
            rows.append(r)
        return finish(args, rows, total)
    wos_key, wos_src = get_key("WOS_STARTER_API_KEY")
    scopus_key, sc_src = get_key("SCOPUS_API_KEY")
    if args.mode == "wos" and not wos_key:
        no_key_exit("WOS_STARTER_API_KEY")
    if (args.mode == "scopus" or (args.mode == "wos" and want_abs)) and not scopus_key:
        no_key_exit("SCOPUS_API_KEY")
    sys.stderr.write(f"keys: WoS from {wos_src or '-'}, Scopus from {sc_src or '-'}\n")
    if args.mode == "scopus" or want_abs:
        warn_if_off_jku(egress_ip())

    rows = []
    if args.mode == "wos":
        sys.stderr.write(f"WoS search: {args.query!r} (limit {args.limit})\n")
        hits, total = wos_search(wos_key, args.query, args.db, args.limit, args.sleep)
        for i, h in enumerate(hits, 1):
            r = wos_to_row(h); r["mode"] = "wos"; r["rank"] = i
            if want_abs:
                r["abstract"], r["abstract_src"] = scopus_abstract_by_doi(scopus_key, r["doi"], args.sleep)
            else:
                r["abstract"], r["abstract_src"] = "", "skipped"
            r["abstract_chars"] = len(r["abstract"])
            rows.append(r)
    else:
        sys.stderr.write(f"Scopus search: {args.query!r} (limit {args.limit})\n")
        entries, total, view = scopus_search(scopus_key, args.query, args.limit, args.sleep, want_abs)
        for i, e in enumerate(entries, 1):
            r = scopus_to_row(e, view, scopus_key, args.sleep, want_abs)
            r["mode"] = "scopus"; r["rank"] = i
            rows.append(r)
    return finish(args, rows, total)


def finish(args, rows, total):
    rank_rows(rows)
    out = Path(args.out) if args.out else \
        REPO_ROOT / "working" / "research" / f"lit-search-{args.mode}-{date.today().isoformat()}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLUMNS})

    n_abs = sum(1 for r in rows if abs_present(r.get("abstract")))
    n_doi = sum(1 for r in rows if r.get("doi"))
    n_err = sum(1 for r in rows if str(r.get("abstract_src", "")).startswith("scopus-error"))
    sys.stderr.write(f"\nDONE: {len(rows)} records (of {total} total matches) -> {out}\n")
    sys.stderr.write(f"  with DOI: {n_doi}/{len(rows)} | with abstract: {n_abs}/{len(rows)}\n")
    bar = "=" * 70
    if total == 0:
        sys.stderr.write(f"\n{bar}\n⚠  ZERO MATCHES. Check the query syntax first; if a query that must match "
                         f"also returns 0, run --check (a WoS key without content entitlement looks exactly "
                         f"like this).\n{bar}\n")
    if n_err:
        sys.stderr.write(f"\n{bar}\n⚠  {n_err} ABSTRACT LOOKUPS FAILED at Scopus (abstract_src scopus-error:… in the "
                         f"CSV). The records are there, their abstracts are not.\n{bar}\n")

    # ---- automatic LIMIT-HIT flag: fire whenever the query has MORE matches than we returned ----
    marker = Path(str(out) + ".LIMIT-HIT.txt")
    truncated = total > len(rows)
    if truncated:
        msg = (f"LIMIT REACHED — RESULTS TRUNCATED: returned {len(rows)} of {total} matching "
               f"records; {total - len(rows)} more exist. Re-run with --limit {total} (or higher) "
               f"to capture all of them.")
        sys.stderr.write(f"\n{bar}\n⚠  {msg}\n{bar}\n")
        with open(marker, "w", encoding="utf-8") as mf:
            mf.write(msg + f"\n\nmode:  {args.mode}\nquery: {args.query}\nlimit: {args.limit}\n"
                           f"total: {total}\nreturned: {len(rows)}\ncsv:   {out}\n")
        sys.stderr.write(f"  flag file written: {marker}\n")
    elif marker.exists():
        marker.unlink()   # clear a stale flag from an earlier truncated run to the same path
    print_overview(rows, combined=False)
    print(out)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:          # an API refused: one loud line, no traceback
        sys.exit(f"FAILED: {e}")
