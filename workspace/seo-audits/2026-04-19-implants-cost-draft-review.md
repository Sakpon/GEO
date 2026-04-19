# SEO Review — draft dental-implants-cost-bangkok-2026 — 2026-04-19
Verdict: PASS-WITH-FIXES

## Checklist results
- Meta title: ⚠️ — H1/title "How Much Do Dental Implants Cost in Bangkok? A 2026 Price Guide" is 65 chars (over 60) and lacks brand. No explicit meta title field in frontmatter.
- Meta description: ⚠️ — Only present inside JSON-LD ("Transparent 2026 price guide..." = 110 chars). No frontmatter `meta_description` field; not guaranteed to render as SERP snippet.
- URL slug: ✅ — `dental-implants-cost-bangkok-2026` — lowercase, hyphenated, keyword-bearing, reasonable length.
- H1: ✅ — Single H1 present and contains primary keyword "dental implants cost" + "Bangkok".
- Heading hierarchy: ✅ — H1 → H2 → H3 (FAQ) flows cleanly, no skips.
- Primary keyword in first 100 words: ✅ — "dental implant in Bangkok typically costs" appears in opening sentence.
- Schema block: ⚠️ — BreadcrumbList, MedicalWebPage/Article, MedicalProcedure, FAQPage all present and well-formed. `reviewedBy`, `author`, `publisher.sameAs` still placeholders; `datePublished` (2026-04-21) is AFTER `dateModified` (2026-04-19) — invalid.
- Word count: ✅ — ~1,550 words, within 1,400–1,800 target.

## Must-fix (P0)
1. Add explicit `meta_title` and `meta_description` in frontmatter. Suggested: title "Dental Implants Cost in Bangkok 2026 | The Dent" (~49 chars); description "2026 Bangkok dental implant prices: single implant, All-on-4, Straumann vs Osstem, what's included. Book a free consultation at The Dent." (~148 chars).
2. Fix schema date inconsistency in the `MedicalWebPage/Article` block: `datePublished` 2026-04-21 is later than `dateModified` 2026-04-19. Set `datePublished` ≤ `dateModified`, or push `dateModified`/`lastReviewed` forward to match publish date.
3. Resolve all `<!-- CONFIRM -->` placeholders before publish — especially THB price ranges (appear 14+ times), doctor name/slug in both byline and JSON-LD `reviewedBy`/`author`, and `target_url` path (`/blog/` vs `/guides/`). Publishing with placeholders visible will tank trust signals.
4. Target URL path decision: frontmatter flags `/blog/` vs `/guides/`. BreadcrumbList schema hard-codes `/blog/`. Lock path before publish so canonical, breadcrumb, and internal links align.

## Should-fix (P1)
1. Internal links are thin: only two outbound internal links (`/en/services/dental-implants`, `/en/services/all-on-4`, `/en/book`). Brief typically requires 3–5. Add links from "implant brand" section to a brand comparison page if available, and from "safety / green flags" section to an About/Credentials page.
2. No inbound internal-link anchor plan noted. Flag to content-planner: update hub page (implants service page) and any existing "cost of dental work in Thailand" pillar to link here with anchor "dental implants cost in Bangkok".
3. Image alt text / hero image not specified in draft. Add image brief with descriptive alt including primary keyword (e.g., "Dental implant cost comparison chart — Bangkok 2026").
4. Add `publisher.sameAs` URLs (clinic social/GBP profiles) — currently placeholder array.
5. Consider adding `Organization` + `Dentist` schema via site-wide include if not already present; this page only carries page-level types.

## Passes
- Primary keyword placement: title, H1, first sentence, slug, and multiple H2s.
- Heading structure clean; FAQ section mirrors JSON-LD FAQPage entries 1:1 (good consistency signal).
- MedicalProcedure schema includes `howPerformed`, `preparation`, `followup` — matches approved pattern for service/medical content.
- `reviewedBy` + `lastReviewed` pattern followed for medical E-E-A-T (pending name fill-in).
- Keyword coverage: primary + all 8 secondary keywords appear naturally in body, tables, or FAQ.
- Comparison tables (brand, country, add-ons, timeline) are scannable and citation-friendly.
- No cannibalization risk detected against existing service pages — this is an informational/cost-intent page distinct from the transactional service URL.
