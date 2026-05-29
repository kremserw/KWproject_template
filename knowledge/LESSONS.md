# LESSONS — Pitfalls & Guardrails

**Purpose**: A shared, git-versioned register of *failure-derived* lessons for running this
knowledge base — the things that go wrong, why, and the guardrail that prevents a repeat. Most memory
and session logs record what worked or what was decided; this file deliberately records what
**didn't**. Teams (like agents) get *robust* by storing pitfalls, not just successes.

**How to use**:
- Read this file at the start of any KB-maintenance or writing pass (the linter reads it; so should you).
- Each lesson follows a **Title / When it applies / Guardrail** schema, plus standard provenance tags.
- When a session hits a genuine trap (not a one-off typo — a *repeatable* mistake), add a lesson here
  via `/session-wrap` Step 1c.
- The **Won't-Fix Register** at the bottom closes the confidence loop: items the linter keeps flagging
  that have been consciously accepted as-is.

> The lessons below (L1–L8) are **portable process lessons** that apply to any knowledge-work project —
> they ship with the template. Add project-specific lessons beneath them as you go.

---

## L1 — Never guess specifics in derived/summary files

**When it applies**: writing any `_summary.md`, INDEX/ARTIFACTS entry, report, or memory that
restates facts from source files — names, statistics, titles, dates, figures.

**Guardrail**: grep the actual source files for the exact fact before writing it down. Do not
reconstruct specifics from memory or inference. Derived files inherit the authority of their sources —
so they must inherit the *facts*, verbatim. (Hallucinated names/figures in a summary can silently
mislead every future session that trusts it.)

---

## L2 — Denormalized facts drift across files

**When it applies**: any count, title, date, or status written into more than one file — e.g. a number
that appears in INDEX.md, ARTIFACTS.md, OPEN-QUESTIONS.md *and* a tracker.

**Guardrail**: prefer a single canonical home for each fact and *reference* it elsewhere rather than
copying it. Where duplication is unavoidable (dashboards), update **all** copies in the same edit and
let the linter's Consistency Check (Criterion 1) catch drift.

---

## L3 — The confidence loop must *close*, not just flag

**When it applies**: any claim tagged `*Verification: llm-derived*` or `*Confidence: single-source*`
that the linter keeps re-flagging session after session.

**Guardrail**: a flagged confidence item has exactly **three** legitimate exits — never "ignore it again":
1. **Verify** — find the source / confirm with the user, then upgrade the tag to `source-verified` or `user-confirmed`.
2. **Correct** — the claim was wrong; fix it.
3. **Won't-fix** — consciously accept it by adding a `*Resolution: accepted-as-is — <rationale> (Session N)*`
   line directly beneath the claim's tags, AND a row in the Won't-Fix Register below. The linter then stops re-flagging it.

Detection without closure is itself the failure — the linter escalates any item flagged ≥3× to a forced decision.

---

## L4 — No verbatim private correspondence in the repo *(privacy — opt-in)*

**When it applies**: processing any email or private message from a stakeholder into the KB. *(Keep this
lesson only if your project handles private correspondence; otherwise it can be removed.)*

**Guardrail**: never store verbatim private-correspondence content — neither as a quote in a KB file
nor as an original attachment. Paraphrase the substance; record provenance, not the words.

---

## L5 — `source-verified` is asserted, not earned

**When it applies**: tagging any file or claim `*Verification: source-verified*` — especially a
**file-level** header that then implicitly covers many sub-claims.

**Guardrail**: reserve `source-verified` for claims backed by a **retrievable artifact in
`knowledge/sources/`**. A file-level header silently launders confidence onto sub-claims whose backing
was never archived (or lives only in a gitignored cache — see L7). Prefer **per-section tags** where
confidence is mixed; downgrade web-scrape / live-URL / oral-source claims accordingly.

---

## L6 — An "UNSUPPORTED" flag means "not in `sources/`", not "fabricated"

**When it applies**: triaging any fact-check / lint finding that a claim is "unsupported", **before**
deleting or downgrading it.

**Guardrail**: the real backing often lives **outside `knowledge/sources/`** — in `knowledge/domain/`,
`working/research/`, a gitignored scrape cache, or an adjacent repo. **Never delete an "unsupported"
claim on a single grep** — search the whole repo first. An UNSUPPORTED verdict is a prompt to *find or
archive the source*, not proof of fabrication.

---

## L7 — Load-bearing scrapes must be archived into `sources/`, not left in a cache

**When it applies**: any figure whose only provenance is a live web scrape or a screenshot dropped in `inbox/`.

**Guardrail**: gitignored caches (e.g. `.firecrawl/`) are invisible to collaborators and to future
verification. When a scrape becomes load-bearing, write a dated text note into
`knowledge/sources/articles/` (or `official/`) capturing the figure + URL + date so the claim is
retrievable in-repo.

---

## L8 — Deep-research synthesis conflates adjacent sources — verify author/date/quote against the primary

**When it applies**: before treating any **author, publication date, or verbatim quote** that originates
in a deep-research report (`sources/deepresearch/*`) as `source-verified` — especially before citing it
externally.

**Guardrail**: the highest-risk llm-derived facts are not the *claims* but the *attributions*. A
deep-research model scanning an index page readily merges adjacent entries, so the title/thesis can be
right while the author/date/quote are wrong. **Fetch the primary page and confirm byline, date, and any
quoted sentence verbatim** before upgrading the tag. (Attribution-specific corollary of L5.)

---

## Won't-Fix Register

Confidence items the linter would otherwise re-flag forever, that have been consciously accepted as-is.
Each row must cite the file, the claim, the rationale, and the session that decided it. The linter
**skips** these.

| File | Claim | Rationale for accepting | Decided |
|------|-------|-------------------------|---------|
| _(none yet)_ | | | |

### Open carryovers awaiting a decision (NOT yet won't-fixed)

Confidence items still needing exit #1, #2, or #3 from L3 — listed here so they are visible outside the lint report.

- _(none yet)_
