# thedent.co.th — SEO & GEO Remediation Report and 90-Day Plan

**Prepared by:** SEO & GEO Agency (Agent Orchestra)
**Date:** 2026-04-19
**Client:** The Dent — Bangkok Dental Clinic
**Status:** Action required — site currently uncrawlable

---

## 1. Executive summary

A live audit of thedent.co.th on 2026-04-19 found that **the entire website is returning HTTP 403 (`x-deny-reason: host_not_allowed`) to all external clients**, including Googlebot and every major AI answer-engine crawler. The block sits at the CDN/WAF edge and affects the homepage, `www`, `robots.txt`, `sitemap.xml`, and `llms.txt`.

**What this means in plain terms:**

- Google cannot crawl or refresh the site. If this persists, ranked pages will drop out of the index.
- ChatGPT, Perplexity, Google AI Overviews, Gemini, and Claude cannot read the site at query time, so the clinic is excluded from AI-generated answers.
- Every other on-page or content issue is currently invisible behind this block — they cannot be diagnosed until crawlers can reach the site.

This is therefore a **two-stage program**: a short emergency phase to restore crawlability, followed by a structured 90-day build-out of SEO and GEO foundations once the site is reachable.

**The single most urgent action:** Have DevOps remove the `host_not_allowed` edge rule today and verify `curl -I https://thedent.co.th/` returns HTTP 200 for both a normal browser and a Googlebot user agent.

---

## 2. Current-state findings

### 2.1 Crawlability (CRITICAL)

| Resource | Status | Impact |
|---|---|---|
| `https://thedent.co.th/` | 403 `host_not_allowed` | Homepage uncrawlable |
| `https://www.thedent.co.th/` | 403 `host_not_allowed` | www variant uncrawlable |
| `https://thedent.co.th/robots.txt` | 403 | Google treats as "unreachable"; crawl slows/stops if >30 days |
| `https://thedent.co.th/sitemap.xml` | 403 | No URL discovery aid |
| `https://thedent.co.th/llms.txt` | 403 | No AI-engine site map; may not exist |

Diagnosis: an origin/edge host-allowlist (likely a CDN host rule, reverse-proxy `server_name`/`allowed_hosts`, or origin firewall) rejecting general traffic before any application logic runs. The block is indiscriminate, not bot-specific. TLS/HTTP2 and DNS (`210.246.201.242`) are healthy, so recovery should be immediate once the rule is corrected.

### 2.2 SEO impact

- **Indexation risk:** persistent 403s lead to deindexing; new/updated pages will not be discovered.
- **Measurement blocked:** PageSpeed Insights, Lighthouse, and any crawler-based audit (on-page, schema, internal links, Core Web Vitals) cannot run against a 403 origin.
- **Silent duration unknown:** the issue may have existed for weeks. Third-party uptime monitors that are allowlisted would not have caught it.

### 2.3 GEO / AI-visibility impact

A wholesale 403 is **citation extinction over time**:

- **T+0–4 weeks:** cached snapshots in Bing/Google/Common Crawl still surface; existing training data still references the site.
- **T+1–3 months:** caches expire; engines that re-verify before citing (Perplexity, ChatGPT browsing) silently drop the clinic.
- **T+6 months+:** next-generation model training corpora (fresh GPTBot/CCBot crawls) lack the site entirely; open-crawl competitor clinics take the citation slots.

When the site is unreachable, the only signals AI engines retain about the clinic are third-party: Google Business Profile, social pages, dental directories (DentaVox, WhatClinic, Dental Departures, Bookimed), review sites, and any Wikidata entry. If those are thin or inconsistent, the clinic's entity itself becomes ambiguous to LLMs.

### 2.4 What is already healthy

- HTTPS / HTTP-2 configured and negotiating cleanly.
- DNS resolves to a single clean A record — no split-horizon issues.
- The deny is fast and structured (`x-deny-reason` header), which makes diagnosis straightforward and recovery near-instant once corrected.

---

## 3. The 90-day plan

The plan is organized into four phases. Phase 0 is the unblock; Phases 1–3 are the build-out. Effort labels: **S** ≤1 day, **M** 2–5 days, **L** 1–3 weeks.

### Phase 0 — Emergency unblock (Days 0–7)

> Goal: site returns 200 to all crawlers; baseline measurement becomes possible.

| # | Action | Owner | Effort | Done when |
|---|---|---|---|---|
| 0.1 | Locate and remove the `host_not_allowed` edge/WAF/origin rule | DevOps | S | `curl -I` returns 200 for browser + Googlebot + GPTBot UAs |
| 0.2 | Ensure `robots.txt` returns 200 (serve as static, outside gated path) | DevOps | S | robots.txt loads in browser |
| 0.3 | Ensure `sitemap.xml` returns 200 and is current | DevOps | S | sitemap loads; URL count matches live pages |
| 0.4 | Publish AI-bot-friendly `robots.txt` (allow major answer engines) | DevOps + GEO | S | bot allow rules live (template in geo-audit) |
| 0.5 | Publish initial `llms.txt` at root | GEO | S | llms.txt loads (template in geo-audit) |
| 0.6 | GSC: URL Inspection live test; resubmit sitemap; request indexing of homepage + top 10 pages | SEO | S | GSC shows successful fetch |
| 0.7 | Bing Webmaster Tools: submit sitemap (powers Copilot/ChatGPT retrieval) | SEO | S | Bing accepts sitemap |
| 0.8 | Add a synthetic Googlebot-UA probe to monitoring (external IP) | DevOps | S | alert fires on any future 403 |
| 0.9 | Establish baseline: full crawl audit + tracked-query battery across ChatGPT/Perplexity/AIO/Gemini/Claude | SEO + GEO | M | baseline reports saved |

**Phase 0 exit criteria:** all key URLs return 200; sitemap + robots + llms.txt live; GSC fetching successfully; baseline audits captured.

### Phase 1 — Technical & local foundations (Weeks 2–5)

> Goal: clean, indexable, schema-rich, locally optimized site. Now that crawlers can read it, fix what they find.

| # | Action | Owner | Effort |
|---|---|---|---|
| 1.1 | Full on-page audit now possible: titles, meta, H-structure, canonicals, hreflang TH↔EN, alt text | SEO | M |
| 1.2 | Fix canonical + hreflang pairing across all TH/EN equivalents | SEO + Dev | M |
| 1.3 | Core Web Vitals pass: LCP <2.5s, INP <200ms, CLS <0.1 on mobile (Thailand is mobile-first) | Dev | L |
| 1.4 | Deploy site-wide schema: `MedicalClinic`/`Dentist`, `Organization` + `sameAs`, `BreadcrumbList` | SEO + Dev | M |
| 1.5 | Per-service-page `MedicalProcedure` schema (`howPerformed`, `preparation`, `followup`) | SEO + Dev | M |
| 1.6 | Google Business Profile per branch: categories, services, hours, photos, Q&A; NAP consistency audit | SEO | M |
| 1.7 | Local citations cleanup across Thai + medical-tourism directories | SEO | M |
| 1.8 | Internal-link graph: eliminate orphan service pages; pillar↔supporting links | SEO + Content | M |
| 1.9 | Fix any `noindex`/`X-Robots-Tag` leakage; confirm clean response headers | Dev | S |

**Phase 1 exit criteria:** zero P0/P1 technical issues open; schema validates; CWV "Good"; GBP complete per branch; no orphan service pages.

### Phase 2 — E-E-A-T & content engine (Weeks 5–9)

> Goal: medical-grade trust signals + first wave of citation-shaped content.

| # | Action | Owner | Effort |
|---|---|---|---|
| 2.1 | Doctor profile pages with `Person` schema (credentials, `worksFor`, `sameAs`) | Content + SEO | M |
| 2.2 | Add reviewer byline + `reviewedBy` + visible `lastReviewed` date to all YMYL pages | Content | M |
| 2.3 | Confirm clinic facts (services, prices, brands stocked, branches) — unblocks content | Client | S |
| 2.4 | Publish priority-cluster pillar + supporting content (implants first) using the agency brief→draft→review→revise workflow | Planner→Creator→SEO+GEO | L |
| 2.5 | Convert top revenue pages to citation shape: answer-first lede, Q-shaped H2s, summary blocks, comparison tables, FAQ, myth-vs-fact, sourced stats | Creator + GEO | L |
| 2.6 | Wire `FAQPage` schema to every Q&A block | SEO + Dev | M |
| 2.7 | Begin Thai-language adaptations (native-speaker reviewed) of best-performing EN pieces | Creator | M |

**Phase 2 exit criteria:** doctor profiles live with schema; all YMYL pages carry reviewer signals; one full citation-optimized pillar published per top cluster; sample implant-cost guide finalized and live.

### Phase 3 — Entity footprint, GEO scale & measurement (Weeks 9–13)

> Goal: LLMs reliably recognize and cite the clinic; durable measurement loop established.

| # | Action | Owner | Effort |
|---|---|---|---|
| 3.1 | File Wikidata entry (Organization + `sameAs` to GBP, LinkedIn, FB, IG) | GEO | M |
| 3.2 | Consistent entity profile across DentaVox, WhatClinic, Dental Departures, Bookimed | GEO + Marketing | M |
| 3.3 | Publish `llms-full.txt` with condensed high-value content | GEO | M |
| 3.4 | Original-data asset (e.g. anonymized 2025 price ranges / brand mix) as primary-source citation bait | GEO + Client | M |
| 3.5 | Drive Perplexity/AIO discovery via social signals to key pages | Marketing | S |
| 3.6 | Monthly tracked-query battery (top 20 questions, TH+EN) → measure citation share | GEO | M |
| 3.7 | Quarterly roadmap: convert audit deltas into the next content calendar | Planner | M |

**Phase 3 exit criteria:** Wikidata + directory entity consistency live; `llms-full.txt` published; first original-data asset live; monthly AI-citation tracking running with a baseline-vs-now delta.

---

## 4. KPIs & checkpoints

| Metric | Baseline (today) | Day 30 target | Day 60 target | Day 90 target |
|---|---|---|---|---|
| Crawlable URLs (HTTP 200) | ~0% (403) | 100% | 100% | 100% |
| Pages indexed (GSC) | Unknown / decaying | Recovering | Back to pre-block + new | Growth trend |
| Service pages with valid schema | Unknown | Core types live | All service pages | All pages |
| Branches with complete GBP | TBD | Audited | Complete | Optimized + posting |
| YMYL pages with reviewer signals | ~0 | Template live | 50% | 100% |
| Citation-optimized pillars published | 0 (1 draft) | 1 | 3 | 5 (one per cluster) |
| AI-citation share (tracked queries) | ~0 (unreachable) | Baseline set | First citations | Measurable share |
| Core Web Vitals (mobile) | Unmeasurable | Measured | Improving | All "Good" |

**Review cadence:** weekly status during Phase 0–1; bi-weekly during Phase 2–3. Monthly KPI report to client.

---

## 5. Dependencies & risks

| Dependency / risk | Impact | Mitigation |
|---|---|---|
| DevOps access to CDN/WAF/origin config | Blocks everything | Escalate today; Phase 0 cannot start without it |
| Client confirmation of services/prices/brands/branches | Blocks content (Phase 2) | Collect in week 1 in parallel with Phase 0 |
| Search Console + GA4 access | Blocks measurement | Request access now |
| Thai native-speaker review capacity | Blocks TH publishing | Identify reviewer in week 1 |
| Doctor credentials + photos for bylines | Blocks E-E-A-T | Collect during Phase 1 |
| The 403 recurs after fix (config not durable) | Re-extinction | Synthetic Googlebot probe (0.8) + static robots.txt |

---

## 6. Immediate next actions (this week)

1. **DevOps:** remove the `host_not_allowed` edge rule; verify 200 for browser + Googlebot + GPTBot. *(today)*
2. **DevOps + GEO:** publish corrected `robots.txt`, `sitemap.xml`, and `llms.txt`. *(Day 0–1)*
3. **SEO:** resubmit sitemap and request reindexing in GSC + Bing. *(Day 1–2)*
4. **Client:** start compiling confirmed services, prices, implant/aligner brands, branch list, and doctor credentials. *(week 1)*
5. **SEO + GEO:** capture baseline crawl audit + AI tracked-query battery once the site is reachable. *(Day 3–5)*

---

## Appendix — source audits

- `workspace/seo-audits/2026-04-19-thedent-live-audit.md` — full SEO findings + diagnostics
- `workspace/geo-audits/2026-04-19-thedent-live-audit.md` — AI-bot impact + ready-to-paste `robots.txt` and `llms.txt` templates + 7-day recovery sequence
- `workspace/content/en/dental-implants-cost-bangkok-2026.md` — sample citation-optimized draft (template for Phase 2)
- `workspace/plans/calendar-2026-W17.md` — example weekly editorial calendar
