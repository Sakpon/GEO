# SEO Expert — Private Notebook

> Persistent memory for the `seo-expert` agent.

## Standing on-page checklist (canonical)

For every published URL:

- [ ] Title tag: primary keyword + brand, ≤ 60 chars
- [ ] Meta description: ≤ 155 chars, keyword, CTA
- [ ] H1 unique, contains primary keyword
- [ ] Heading hierarchy: no skipped levels
- [ ] URL slug: short, lowercase, hyphenated, keyword-bearing
- [ ] Canonical tag points to self (unless intentional alias)
- [ ] hreflang set for TH ↔ EN pair
- [ ] At least 3 descriptive internal links in
- [ ] At least 3 contextual internal links out
- [ ] At least 1 authoritative outbound citation for any medical claim
- [ ] All images: descriptive alt text, lazy-loaded, modern format
- [ ] Schema markup: `MedicalWebPage` or `MedicalProcedure` where applicable + `BreadcrumbList`
- [ ] CWV (LCP < 2.5s, INP < 200ms, CLS < 0.1) validated on mobile
- [ ] No orphan status — linked from pillar and at least one sibling

## Approved schema patterns

> JSON-LD snippets that have passed validator and reviewer. Paste into `content-creator` briefs.

### Organization + LocalBusiness (site-wide) — TBD
### Dentist (per branch) — TBD
### MedicalProcedure (per service page) — TBD
### MedicalWebPage + Article (per blog post) — TBD
### FAQPage — TBD
### BreadcrumbList — TBD

## Keyword universe

> Growing master list. Merge with `content-planner`'s registry weekly to ensure alignment.

| Keyword | Locale | Volume | Difficulty | Intent | Notes |
|---|---|---|---|---|---|

## Competitor SERP observations

_Who's outranking us, for what, and why (format, depth, authority, backlinks)._

- _TBD_

## Tech debt register

| Issue | Severity | Found | Assigned | Fixed |
|---|---|---|---|---|

## Audit report index

Reports live in `workspace/seo-audits/YYYY-MM-DD-<scope>.md`.

- _TBD_

## Tools / access notes

- Search Console: _pending access_
- GA4: _pending access_
- Rank tracker: _TBD_
- PageSpeed Insights API: public, no auth
- Schema Markup Validator: https://validator.schema.org/

## Session log

_Date — what was audited, top findings, what was handed off and to whom._
