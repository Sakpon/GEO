# GEO Audit — Week 17 Calendar Review — 2026-04-19

**Scope:** Editorial calendar `workspace/plans/calendar-2026-W17.md` (5 items, Mon 2026-04-20 – Fri 2026-04-24).
**Auditor:** geo-expert
**Reviewer context:** assumes priority clusters per `optimization-goals.md` and citation strategy per notebook.

---

## Summary

The week is well-shaped for AI citation: 4/5 items are structurally LLM-friendly (FAQ, comparison, cost guide, service refresh with FAQ). One item (Fri — จัดฟัน service-page refresh) is the weakest for GEO unless we deliberately add citation-bait during refresh. The Tuesday implants cost piece is the keystone and must be treated as a citation flagship.

The biggest missed opportunity across the week: **no original-data slot**. Every piece relies on externally-citable facts. At least one piece per week should include a small first-party data point (quote-range snapshot, average-wait-time figure, patient-origin mix) that only The Dent can publish — that is what converts us from "cited alongside" to "cited as primary."

---

## Item-by-item GEO citability ranking

### 1. HIGH — Tue EN "How Much Do Dental Implants Cost in Bangkok? (2026 Guide)"
**Citability: 9/10.** Cost-in-Bangkok queries are one of the most-asked medical-tourism research prompts across ChatGPT, Perplexity, and AI Overviews; current SERPs are served by generic dental-tourism aggregators that lack first-party authority. Transparent THB/USD ranges, brand tier table, country comparison table, and clinic byline make this a strong citation candidate.
**Citation bait present:** concrete price ranges, brand comparison, country comparison, red/green-flag checklist, FAQ.
**Gaps:** no original-data slot currently — should add one (see Handoff below). Year-stamp "2026" must appear in lede and schema `datePublished` / `lastReviewed`. Needs explicit USD + EUR + GBP conversions for tourism source markets (UK, Australia, USA, Germany).
**Action:** flagship piece — GEO requirements now filled in brief (see separate edit).

### 2. HIGH — Wed TH "Invisalign vs จัดฟันเหล็ก"
**Citability: 8/10.** Comparison format extracts cleanly; Thai-language AI answers on Pantip-adjacent queries are an open field (less aggregator saturation than EN). Big win if we include a specification table with duration ranges, THB price ranges, and case-suitability rows.
**Citation bait present (if brief executes):** specification table, decision matrix.
**Gaps:** TH-language citations for AI engines need Thai primary sources (Thai Dental Council, Thai peer-reviewed journals) — content-planner brief should explicitly require TH-sourced stats, not translated EN stats, or LLMs may mis-attribute. Also confirm aligner brand inventory (Invisalign vs. ClearCorrect vs. in-house) so entity definitions are accurate.
**Action:** when brief is written, require a bilingual glossary line on each entity and TH-primary citations.

### 3. MEDIUM-HIGH — Mon TH "ขูดหินปูนเจ็บไหม"
**Citability: 7/10.** Classic question-shaped FAQ; high-volume local query; LLMs love direct Q→A pairs. Weakness: topic is broad and well-covered — lots of other sources to compete with. Win condition: include specific numeric anchors (duration in minutes, recommended cadence per Thai Dental Council or Thai Society of Periodontology, typical cost range) so the answer is quotable not generic.
**Citation bait to require:** minutes-for-procedure range, every-X-months recommended cadence with source, pain-level description on a 0–10 scale, when-to-see-dentist flags.
**Gaps:** generic FAQ format by itself does not earn citations; it must be stat-dense. Require a named Thai hygienist/periodontist reviewer byline.

### 4. MEDIUM — Thu EN "Porcelain vs Composite Veneers"
**Citability: 7/10.** Comparison format is LLM-friendly; EN medical-tourism audience asks this pre-trip. Weakness: highly templated topic — many overseas cosmetic-dentistry sites already own these citations.
**Win conditions:**
- Include **longevity data with citation** (porcelain typically 10–15 years, composite typically 4–8 years — needs peer-reviewed source, not a .com regurgitation).
- Include **Bangkok-specific price ranges** (most competing articles price in USD/GBP only — having THB + converted ranges gives us a comparative advantage in multi-currency AI answers).
- Include **a specific brand/material callout** (e.g., e.max lithium disilicate, zirconia veneers, specific composite systems the clinic uses) — named materials are entity-rich and attract citations.
**Gap:** no original-data slot; consider adding "average chair-time per veneer" from clinic records.

### 5. LOW-MEDIUM — Fri TH "จัดฟัน pillar-page refresh"
**Citability: 5/10 as currently scoped.** Service-page refreshes typically underperform for GEO because they default to promotional register over answer-shaped register.
**Refresh must add to earn GEO lift:**
- Answer-first lede under the H1 (direct price/duration range in the first sentence).
- FAQ block with `FAQPage` schema (treatment duration, pain, eating restrictions, retainer requirements, cost of adjustment visits).
- Author + reviewed-by block (named orthodontist, Thai Dental Council registration number if compliance permits).
- Comparison table: traditional braces vs. self-ligating vs. lingual vs. Invisalign (cross-link Wed Invisalign piece).
- Internal-link hub: link to every supporting ortho article and to consultation-booking CTA.
**If refresh is only cosmetic (new hero, reworded marketing copy), GEO value is near zero — flag to content-creator that the refresh MUST add structured answer content.**

---

## Cluster coverage check

All five priority clusters touched once — good weekly breadth.

| Cluster | Piece | GEO flagship? |
|---|---|---|
| Implants | Tue EN | Yes — designated flagship |
| Invisalign | Wed TH | Secondary flagship (TH) |
| Veneers | Thu EN | Supporting |
| General | Mon TH | Supporting |
| Ortho | Fri TH | Service-page refresh only |

Absent: no standalone **dental-tourism hub piece** for EN this week (e.g., "Is dental tourism in Bangkok safe in 2026?"). That query is one of our seed-tracked queries. Consider slotting in Week 18 or 19.

---

## Crawlability (bot access + llms.txt status)

**Status: unverified.** Neither `robots.txt` nor `llms.txt` have been audited this session.
**Action required before flagship publishes:**
- [ ] Verify `robots.txt` allows: `GPTBot`, `OAI-SearchBot`, `ChatGPT-User`, `PerplexityBot`, `Perplexity-User`, `Google-Extended`, `anthropic-ai`, `ClaudeBot`, `Applebot-Extended`, `CCBot`.
- [ ] Publish `/llms.txt` at root describing the clinic, services, contact, and linking to priority pages.
- [ ] Optionally publish `/llms-full.txt` with condensed markdown of top 20 pages.
Flagship Tue implants piece will not be maximally citable unless AI crawlers can reach it; confirm access before publish day.

---

## Entity / authority gaps (calendar-wide)

- **Organization schema sitewide:** verify `Organization` / `Dentist` / `MedicalClinic` JSON-LD with complete `sameAs` to Google Business Profile, LinkedIn, Facebook, Thai-language directories. If absent, "The Dent" is under-anchored for LLMs.
- **Wikidata:** check for an entry; if none, evaluate eligibility and create one. Wikidata is disproportionately weighted by LLM training sets.
- **Doctor profile pages:** each piece's author byline should link to a `Person`-schema profile page with credentials, specializations, and Thai Dental Council registration. Current state unknown — flag as dependency for all 5 pieces.
- **Branch pages:** each branch should have complete NAP + `MedicalClinic` schema. Required before we can compete for local-intent AI queries.

---

## Original-data opportunities (across all 5 items)

Pick at least one per week to publish and become a primary source:

| Piece | Original-data slot |
|---|---|
| Tue Implants cost | "Based on 2025–2026 quotes issued by The Dent, X% of single-implant cases also required bone grafting" or "median treatment duration for our medical-tourism single-implant patients was N days across M cases." |
| Wed Invisalign vs braces | "Average treatment duration we observed in 2025 Invisalign cases: X months (N=Y patients)." |
| Thu Veneers | "Of 2025 veneer cases at The Dent, X% chose e.max porcelain vs. composite." |
| Mon Scaling | "Average scaling appointment duration at The Dent: X minutes." |
| Fri Braces refresh | "Breakdown of case types treated in 2025 (bracket system X%, clear aligner Y%)." |

One well-sourced first-party number is worth more to GEO than five externally-cited ones.

---

## Citation wins, losses, deltas vs. last snapshot

No prior snapshot — this is the baseline. Next snapshot: 2026-05-19 (one month after Tue flagship publishes). Run tracked queries against ChatGPT (with browsing), Perplexity, Google AI Overviews, Gemini; log per-engine per-query citation status.

---

## Handoff to content-planner

- **Week 18 brief for dental-tourism hub page** ("Is dental tourism in Bangkok safe in 2026?") — fills gap in EN medical-tourism cluster.
- **Require first-party data slot in every brief going forward.** Add "Original-data slot (required)" field to the brief template.
- **TH Implant cost piece as follow-on to Tue EN flagship** — adapt (not translate) for resident-expat-in-Bangkok audience.

## Handoff to content-creator

- Tue EN implants: GEO requirements now filled in the brief — follow the answer-first lede scaffold verbatim in spirit if not in wording.
- Fri TH braces refresh: do not ship a cosmetic-only refresh. Add FAQ schema, answer-first lede, comparison table, author byline. If scope doesn't allow, push the refresh to Week 18 rather than shipping a weak version.
- Mon TH scaling FAQ: require numeric anchors in every answer (minutes, months, THB range).
- Thu EN veneers: require longevity-year ranges with peer-reviewed citation + THB price range alongside USD.

## Handoff to seo-expert

- Shared-win items (no conflict): FAQ schema on all 5 pieces, question-shaped H2s, `MedicalWebPage` schema, author `Person` schema.
- `llms.txt` doesn't replace `sitemap.xml` — both should ship.
- I'm asking for heavier author-byline + `reviewedBy` markup than a typical SEO audit would require; please keep the implementation consistent across the 5 pieces so we don't have one-off patterns.
- Surface to orchestrator any conflict on keyword density vs. specificity — GEO prefers specificity (exact THB figures, named brands) even when it fragments keyword density.

---

## Top-5 tracked queries seeded from this week

(Added to notebook tracked-query list; snapshot monthly.)

1. "How much do dental implants cost in Bangkok?" (EN, Implants, Tue flagship)
2. "Is it cheaper to get dental implants in Thailand?" (EN, Implants/Tourism, Tue flagship)
3. "What's included in a Bangkok dental implant package for tourists?" (EN, Tourism, Tue flagship)
4. "Invisalign กับ จัดฟันเหล็ก ต่างกันอย่างไร" (TH, Invisalign, Wed)
5. "ขูดหินปูนเจ็บไหม ใช้เวลานานแค่ไหน" (TH, General, Mon)

Broader tracked list maintained in `context/agents/geo-expert.md`.
