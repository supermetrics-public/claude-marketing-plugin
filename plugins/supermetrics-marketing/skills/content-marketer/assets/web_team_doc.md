# Web team fix doc template

The structured Google Doc the content marketer sends to the web/dev team. Web teams get a lot of "please fix" requests; the ones that get prioritized are the ones that read like a clear checklist with effort estimates and business impact, not like a complaint.

---

# Landing page fix list — [Period]

**Why this doc exists:** [N] pages in our top traffic are converting below benchmark or losing visitors via bounce. Estimated impact if fixed: ~[X] additional conversions per [month/quarter]. This doc is prioritized — fix the high-priority items first.

**Owner:** [Content marketing manager name]
**Web team contact:** [Name]
**Target completion:** [Date]

---

## How to read this doc

Each page below lists:
- **Page URL** — the page to fix
- **Current state** — what the data shows
- **Proposed fixes** — specific changes to make (not "make it better" — actual things to ship)
- **Estimated dev effort** — S/M/L (the content team's rough estimate; web team will refine)
- **Expected impact** — best-guess conversion lift if the fixes ship

If a proposed fix is wrong because of context the content team doesn't have (e.g. an A/B test running, a legal constraint, a known infrastructure issue), leave a comment and we'll revisit.

---

## High-priority pages

### 1. [Page URL]
**Current state:**
- Sessions/month: [N]
- Bounce rate: [X]%
- Avg time on page: [Y] seconds
- Conversion rate: [Z]%
- Estimated lost conversions per month: ~[N]

**Proposed fixes:**
1. [Specific fix — e.g. "Move the primary CTA above the fold. Currently it sits below a 600px hero image and only ~15% of mobile users scroll to it."]
2. [Specific fix]
3. [Specific fix]

**Estimated dev effort:** [S / M / L]
**Expected conversion rate lift:** [target %, e.g. "from 0.4% to ~1.5%"]

---

### 2. [Page URL]
[Same structure]

---

## Medium-priority pages

[Same structure, shorter detail per page]

---

## Low-priority pages

[A simple table is fine here — these are batched for whenever there's bandwidth]

| Page | Sessions | Issue | Proposed fix | Effort |
|---|---|---|---|---|
| [URL] | [N] | [Brief] | [Brief] | [S/M/L] |

---

## Cross-cutting observations

[A section for patterns across multiple pages — e.g. "Most underperformers share a mobile form layout issue: fields are too small and submit buttons fall below the viewport on small screens. A site-wide fix to the form component would address ~8 of these pages at once."]

---

## What we'll measure post-fix

- For each page fixed, we'll re-measure 30 days post-deploy and report back on conversion rate change
- Pages where the fix produced <50% of the expected lift will be reopened for a second round of analysis

---

## Tone notes

- Web teams care about scope and effort. The S/M/L estimate is more important than the marketing context.
- "Make the CTA more prominent" is not a fix. "Change the CTA button background from #EEEEEE to the primary brand orange (#FF6B35) and move it above the fold" is a fix.
- Pages where the content marketer can't propose a specific fix should go in a separate "needs investigation" section. Don't pad the high-priority list with vague items.
- The cross-cutting observations section is the most valuable part of the doc for the web team. A single component-level fix that addresses eight pages beats eight individual page fixes.
- The "what we'll measure post-fix" section closes the loop. Web teams that ship fixes and never hear what happened stop prioritizing marketing's requests.
