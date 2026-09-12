# Source Digest — Locked Template (Layer 1)

Standard structure for every per-source **digest** under `knowledge/sources/<type>/`. A digest is the
**stable, faithful, lens-neutral substrate** that all later work reads *instead of* the original.

Lock this file at the start of a project and stop re-deciding the shape per document. What makes a
digest worth the effort is that it is the same shape every time.

**Design rules**
- **The digest is the reading surface; the original is the lookup surface.** Write it so the original
  almost never has to be opened — and so that when it does, the note says why.
- Faithful, located, verbatim where the wording matters — NOT an interpretive summary. Everything is
  non-interpretive EXCEPT the fenced "Open hooks (our notes)" section.
- Evolving cross-source synthesis does NOT live here. It lives in `knowledge/domain/<slug>.md` (and,
  for a literature project, a Layer-2 matrix under `working/planning/`). The digest is stable; the
  synthesis is disposable and gets rewritten as the lens changes.
- One digest per source. Long enough that the original is not needed; short enough to read in one
  sitting. Fidelity over coverage.
- Where the original ends up is a project decision — `inbox/processed/` (this template's default) or
  co-located with its digest in `knowledge/sources/<type>/` if the project versions its corpus.
  **Decide once, write it into the pointer line below, and keep `.gitignore` consistent with it.**

---

## Schema

Sections marked `[academic]` or `[institutional]` are genre-specific: keep the ones your sources
actually are, delete the rest at setup. Everything unmarked is common to both.

```
# <Authors Year | Body / Sender> — <Full title | what it is, D Month YYYY>

*Source: inbox-file (<original-filename>)*
*Verification: [source-verified | llm-derived]*
*Confidence: [single-source | corroborated]*
*Pages refer to: <printed page numbers | PDF page index>*        [academic]

**Original: `<inbox/processed/… | knowledge/sources/<type>/…>`**
<One sentence: when is the original worth opening? e.g. "Worth opening to quote the decisions
verbatim — the wording is what matters." / "Nothing in it beyond this note.">

> **Orientation (1–2 sentences):** what this source is and its central move.

## What it is / Coordinates
Genre, date, provenance, and the people it involves.
- [academic] **Authors / Year / Venue** · **Type & method** (conceptual → mode of theorizing;
  empirical → design, setting, data, sample, analysis) · **Theoretical lineage** · **Core constructs**
- [institutional] Document genre (protocol, email, board paper, regulation, deck), its own
  self-description in quotes if it carries one, date/time, place or channel, sender and recipients or
  participants BY NAME, and its stated purpose

## The substance
The body of the note, organised by the source's own structure — not by an imposed scheme. Faithful
and non-interpretive. Quote verbatim and locate the quote wherever the wording will be argued over;
paraphrase plainly where the source merely reports. For a contested matter, an explicit
"arguments for / arguments against" split is usually truer than a merged summary.

## Construct definitions (verbatim where definitional)    [academic]
- **<construct>** — "<verbatim definition>" (p.N). *(gloss if needed)*

## Claims ledger    [academic: "Claims / propositions" (conceptual) or "Findings" (empirical)]
| # | Claim / finding (faithful, non-interpretive) | Location | Anchor quote |
|---|---|---|---|

## Typology / framework      [academic — conceptual papers that offer one; render it explicitly]
- dimension / type → verbatim defining basis (p.N)

## Process model / mechanisms    [academic — where the source offers one]
- stage / component → faithful description (+ verbatim label) (p.N)

## Episode / vignette bank       [academic — empirical sources]
- **<short episode name>** — what happens + what it demonstrates (p.N) — "<anchor quote>"

## Decisions as recorded         [institutional — omit if the document records none]
What was decided, in the document's own terms, numbered as it numbers them. Record a dissent by name
if the document does — that it was recorded at all is evidence.

## Action items as recorded      [institutional — omit if the document records none]
| Who | What | Until |
|---|---|---|

## People and bodies touched     [institutional — when the source introduces or repositions someone]
Names, roles, and what this source adds. Cross-link to the project's actor register; do not duplicate
it here.

## Quote bank (located, lens-neutral)
- `[tag]` "<verbatim>" (<p.N | § | agenda item | paragraph>)

## Engagements (the scholarly conversation)    [academic]
- **Builds on / extends:**  · **Contests / departs from:**

## Scope & boundary conditions / Reliability
Where the claims hold, and the limitations the source states itself. How the document came to exist
(peer-reviewed, recording-based minutes, auto-generated transcript, forwarded mail) and what that
implies about its accuracy. Explicitly: **what cannot be known from this source alone.** This section
is what stops a convenient sentence from being treated as established.

## Open hooks (our notes)    [the ONLY interpretive section]
Candidate links to the project's question, argument, or upcoming decisions, and to other sources.
Clearly marked as our reading, never blended into "The substance".

## See Also
- `[[path]]` — the domain/foundations file(s) this feeds
- `[[path]]` — related digests in the same folder, with one clause saying how they relate
```

---

## Fidelity rules (non-negotiable)
- Quotes VERBATIM and actually present in the original. Never invent, never paraphrase inside quote
  marks. If unsure of the exact wording, paraphrase plainly WITHOUT quotes and tag "(paraphrase)".
- Locate every quote: page, `§`, agenda item, or paragraph — whatever the source offers. A quote
  nobody can find again is not a quote.
- [academic] Page anchors = the source's printed page numbers; declare at the top if you fall back to
  the PDF index. Verify author/year/venue against the title page, never against the filename.
- [institutional] Verify sender, date and body against the document's own header, never against the
  filename.
- Re-locate each quote before finalising, to confirm wording and position.
- Keep interpretation OUT of every section except "Open hooks".
- `source-verified` is earned only because the archived original backs every claim. Use `llm-derived`
  where the content was generated rather than recorded.
- If the source contradicts something already in `knowledge/`, say so under Reliability — do not
  silently resolve it, and do not edit the other file from inside this one.

## Naming & placement
- Slug: `firstauthor-year-keyword` for academic sources, `YYYY-MM-DD-<topic>` for dated documents;
  lowercase, hyphens. The digest goes in the `knowledge/sources/<type>/` folder matching its type.
- After writing: append a row to that folder's `_summary.md` Contents table, and integrate the durable
  content into the relevant `knowledge/domain/<slug>.md`. **The digest is not the synthesis.**
