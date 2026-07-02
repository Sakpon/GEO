# GEO Review — draft dental-implants-cost-bangkok-2026 — 2026-04-19
Verdict: PASS-WITH-FIXES

## GEO checklist (bullets, one line each)
- Answer-first lede (complete, standalone, specific): PASS — opening sentence delivers THB range, USD equivalent, 50–70% delta, and price drivers in one self-contained claim. Strong citation bait once CONFIRM placeholders resolve.
- Entities defined inline on first mention: PASS — "dental implant", "All-on-4", "All-on-6", "osseointegration", "CBCT" all defined; minor gap: "abutment" used in tables and lede before any inline definition.
- 40–60 word summary under each H2: MIXED — most H2s lead with a tight summary paragraph, but "Key takeaways" and "Myth vs fact" skip the summary; "How long will I need to stay" summary is borderline too long.
- Stat/number density with source markers: WEAK — numbers are dense but nearly every one is a `<!-- CONFIRM -->` or `<!-- SOURCE NEEDED -->` placeholder. Until resolved, LLMs cannot cite this page confidently.
- Comparison tables present: PASS — four tables (component, brand, add-ons, country). Country table is a strong citation-bait asset.
- FAQ Q&A block (8+ pairs): PASS — exactly 8 pairs, mirrored in JSON-LD FAQPage.
- Myth-vs-fact block: PASS — 4 myths with direct rebuttals; format is LLM-friendly.
- Author + lastReviewed block: PARTIAL — structure is correct (byline top + "About this guide" bottom + `lastReviewed` in schema), but doctor name, slug, and credentials are all placeholders.
- JSON-LD schema usable: PASS on structure (MedicalWebPage, MedicalProcedure, FAQPage, BreadcrumbList, `lastReviewed`, `reviewedBy`). Will not validate until name/URL/sameAs placeholders are filled.
- Citation-bait elements (original-data slot, price ranges, country comparison): PARTIAL — country table and brand-tier table are excellent; no original clinic-data nugget (e.g. "X% of our 2025 implant cases used Straumann") to distinguish from competitors.

## Must-fix for citation-worthiness (P0)
1. Resolve every `<!-- CONFIRM -->` THB range and every `<!-- SOURCE NEEDED -->` benchmark before publish. A price guide with bracketed placeholders cannot be cited. Highest priority: lede THB range, country-comparison table rows (UK/US/AU/DE), All-on-4 per-arch range in body and FAQ answer.
2. Fill the reviewer identity end-to-end: byline under H1, "About this guide" paragraph, `reviewedBy.name`, `reviewedBy.url`, `author.name`, `author.url`, `publisher.sameAs`. Named-expert review is a primary LLM trust signal.
3. Hard-code the THB ranges into the FAQPage JSON-LD answers (currently already written as THB 45,000–90,000 and THB 380,000–650,000 — confirm these match the body once CONFIRM values resolve; any mismatch will poison the schema).
4. Add a one-line inline definition of "abutment" at first mention in the lede or the component table footnote (e.g. "abutment — the connector between fixture and crown"). Currently used 11+ times without definition.

## Should-fix (P1)
1. Add a short original-data sentence under "How do implant brands affect the price in Thailand?" — e.g. share The Dent's own brand-mix share for 2025 implant placements. This is the single biggest citation-bait upgrade available.
2. Add a 40–60 word summary paragraph directly under the "Myth vs fact" H2 and under "Key takeaways" so every section has an extractable lede block.
3. In the country-comparison table, convert the non-USD rows (GBP, AUD, EUR) to a USD column as well so LLMs can extract a single normalized axis.
4. Replace `<!-- SOURCE NEEDED -->` placeholders with actual linked primary sources (NHS, ADA HPI, ADA Australia Fees Survey, KZBV) — inline hyperlinks give LLMs an attribution path and strengthen retrieval.
5. Add 1–2 sentences on implant survival rates (10-year survival %) with a named study (e.g. ITI or JOMI meta-analysis) — high-value quoteable stat currently missing.
6. Confirm `datePublished` (currently 2026-04-21) is not in the future relative to publish date; LLM retrievers flag future dates as low-trust.

## Passes
- Answer-first lede structure is exactly the shape Perplexity and AI Overviews extract.
- Question-shaped H2s align with real user queries and map cleanly to the FAQ.
- Four well-structured tables give LLMs row-level facts to quote.
- Green-flag / red-flag lists are ideal citation bait for "is it safe" queries.
- Myth-vs-fact block directly answers the "too cheap to be real" objection that dominates this query cluster.
- Schema graph (MedicalWebPage + MedicalProcedure + FAQPage + Breadcrumb) is comprehensive and correctly cross-referenced via `@id`.
