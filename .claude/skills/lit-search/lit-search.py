#!/usr/bin/env python3
"""
lit-search.py — literature search WITH abstracts via Web of Science and Scopus.
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
  --check                    Preflight only: where the keys come from, the egress IP,
                             and one tiny live call to each API. Run this first.

A WoS search always goes to the WoS API, a Scopus search always to the Scopus API.
There is no fallback to any other source (OpenAlex, web search): if an API fails,
the run fails loudly.

Output: a UTF-8 CSV — default working/research/lit-search-<mode>-<date>.csv, relative
to the repo root.

KEYS — never hard-coded, never printed, never passed on the command line. Looked up in
this order, per service:
  1. the environment: WOS_STARTER_API_KEY, SCOPUS_API_KEY
  2. the gitignored files .secrets/clarivate-wos.env and .secrets/scopus-elsevier.env
     in the repo root (lines KEY=value) — written by setup-keys.sh in this folder
  3. a credential gateway: when neither exists and an HTTPS proxy is set (Bob's
     server container), the requests go out with a placeholder and the gateway
     injects the real key. Without a proxy and without a key, the run stops and
     names setup-keys.sh.

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
JKU_RANGE       = ipaddress.ip_network("140.78.0.0/16")
GATEWAY_PLACEHOLDER = "gateway-managed"

REPO_ROOT = Path(__file__).resolve().parents[3]          # <repo>/.claude/skills/lit-search/
SECRETS = {"WOS_STARTER_API_KEY": REPO_ROOT / ".secrets" / "clarivate-wos.env",
           "SCOPUS_API_KEY":      REPO_ROOT / ".secrets" / "scopus-elsevier.env"}

COLUMNS = ["mode", "rank", "title", "authors", "year", "journal", "volume", "issue",
           "pages", "doi", "times_cited", "times_cited_src",
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
    if os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"):
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
    if not (wos_key and sc_key):
        print("Missing key(s): run in a terminal (not in the chat): bash .claude/skills/lit-search/setup-keys.sh")
    print("READY" if ok else "NOT READY")
    return 0 if ok else 1


# ----------------------------- main -----------------------------
def main():
    ap = argparse.ArgumentParser(description="WoS/Scopus literature search with abstracts.")
    ap.add_argument("--check", action="store_true", help="preflight: keys, egress IP, one live call per API")
    ap.add_argument("--mode", choices=["wos", "scopus"])
    ap.add_argument("--query", help="raw query in the chosen DB's syntax")
    ap.add_argument("--limit", type=int, default=500,
                    help="max records to return (default 500); a loud flag + sidecar "
                         "file fire automatically if the query has MORE matches than this")
    ap.add_argument("--db", default="WOS", help="WoS database (default WOS)")
    ap.add_argument("--no-abstracts", action="store_true", help="skip abstract fetching")
    ap.add_argument("--sleep", type=float, default=0.3, help="politeness delay between calls")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    if args.check:
        sys.exit(check())
    if not (args.mode and args.query):
        ap.error("--mode and --query are required (or --check)")

    want_abs = not args.no_abstracts
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
    print(out)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:          # an API refused: one loud line, no traceback
        sys.exit(f"FAILED: {e}")
