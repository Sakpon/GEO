# Live GEO / AI-Visibility Audit — thedent.co.th — 2026-04-19

## Crawl access situation

**Observed state:** All requests to `https://thedent.co.th/` (root, www, `/robots.txt`, `/sitemap.xml`, `/llms.txt`) return **HTTP 403 Forbidden** with response header `x-deny-reason: host_not_allowed`. The block applies across user agents (normal browser UAs included) per the SEO agent's parallel finding and confirmed again here on `/llms.txt`. No `llms.txt` is reachable; we cannot even confirm whether one exists.

**Diagnosis:** This is not a `robots.txt` policy block — it is an edge/WAF/CDN host-allowlist rejection happening before any application logic. Almost certainly a misconfigured CDN host rule, a Cloudflare/Fastly "host not allowed" deny list, or an origin firewall whitelisting only specific Host headers. It is indiscriminate, not bot-specific.

**Implications by bot UA** (all currently blocked at the edge regardless of policy):
- **OpenAI:** `GPTBot` (training), `OAI-SearchBot` (search index), `ChatGPT-User` (live browsing for ChatGPT users) — all 403
- **Perplexity:** `PerplexityBot` (index), `Perplexity-User` (live retrieval at query time) — all 403
- **Google AI:** `Google-Extended` (AI training opt-in) and Googlebot itself — Google's main bot may still see cached snapshots, but fresh crawl is blocked
- **Anthropic:** `anthropic-ai`, `ClaudeBot`, `Claude-User`, `Claude-SearchBot` — all 403
- **Microsoft:** `Bingbot` (powers Copilot retrieval) — 403; this is critical because ChatGPT browsing leans on Bing
- **Apple:** `Applebot`, `Applebot-Extended` — 403
- **Other:** `CCBot` (Common Crawl, a major training corpus), `Bytespider`, `Meta-ExternalAgent`, `Diffbot`, `YouBot` — all 403

**Implications for retrieval at query time:**
- ChatGPT with browsing: cannot fetch our pages live; will fall back to Bing's stale cache or omit us
- Perplexity: `Perplexity-User` runs at query time per citation — a hard 403 means we are excluded from the citation candidate set in real time
- Google AI Overviews / Gemini: rely on Google's index; staleness will deepen and refreshes will fail
- Claude with web search: 403 = no citation possible

## Visibility implications (analysis)

A wholesale 403 is **citation-extinction over time**. The decay curve:
- **T+0–4 weeks:** Cached versions in Bing, Google, and Common Crawl still surface; existing AI training data already includes the site
- **T+1–3 months:** Search caches expire, AI engines that re-verify before citing (Perplexity, ChatGPT browsing) silently drop us
- **T+6+ months:** Next-generation model training corpora (built on fresh CCBot/GPTBot crawls) will lack us entirely; competitor clinics with open crawl will take our slot

**Brand mentions that may persist independent of our site:**
- Google Business Profile listings (if claimed and active)
- Facebook / Instagram pages
- Thai dental directories (DentaVox, WhatClinic, Dental Departures, Bookimed)
- Patient review sites (Google reviews, Trustpilot)
- Wikidata / Wikipedia (if entries exist — needs confirmation)
- YouTube / press mentions

These become the **only** signals AI engines can use about us. If those are thin or inconsistent, our entity itself becomes ambiguous to LLMs — "thedent" gets confused with generic dental terms or other clinics.

## Top GEO issues

### P0 — emergency (citation extinction risk)
1. **Site-wide 403 at edge** blocking all AI crawlers + search bots indiscriminately. This is the single dominant GEO failure right now.
2. **No `llms.txt`** discoverable (cannot exist or cannot be reached).
3. **Sitemap unreachable** — even if bots are allowed back, they have no discovery aid.

### P1 — high impact (do as soon as P0 is unblocked)
4. **Entity footprint unknown** — no confirmed Wikidata, no verified author/Person schema visible because site is unreachable
5. **`robots.txt` policy is undefined** for the modern AI bot fleet; current block is incidental, not strategic — once edge is fixed, we still need an explicit allow policy
6. **No verified author/medical-reviewer signals** in any externally cached content (per prior notebook context)

### P2 — improvements once crawl is restored
7. Answer-first ledes, FAQ schema, comparison tables, original cost data — all the standard GEO citation-bait work
8. `llms-full.txt` with condensed high-value content
9. Per-doctor `Person` schema with credentials and `sameAs`

## What to allow when the block is lifted

**Edge / WAF rule:** Remove `thedent.co.th` and `www.thedent.co.th` from the host-deny list. Verify both apex and `www` resolve and respond 200 to a plain `curl -I`. Confirm no Cloudflare "Under Attack" mode or bot-fight mode is blanket-blocking known bot UAs.

**Recommended `/robots.txt`** (clinic wants AI visibility):

```
User-agent: *
Allow: /
Sitemap: https://thedent.co.th/sitemap.xml

# AI answer-engine bots — explicitly allowed
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Perplexity-User
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: anthropic-ai
Allow: /
User-agent: Claude-User
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: CCBot
Allow: /
User-agent: Meta-ExternalAgent
Allow: /

# Block aggressive scrapers (optional)
User-agent: Bytespider
Disallow: /
```

**Recommended `/llms.txt`** (minimal v1):

```
# The Dent — Bangkok Dental Clinic

> Bilingual (TH/EN) dental clinic in Bangkok offering general,
> cosmetic, orthodontic, and implant dentistry.

## Core pages
- [Services](https://thedent.co.th/services): full treatment list with prices in THB
- [Doctors](https://thedent.co.th/doctors): credentialed staff profiles
- [Contact & Locations](https://thedent.co.th/contact)

## Treatment guides
- [Dental implants in Bangkok](https://thedent.co.th/services/implants)
- [Invisalign in Bangkok](https://thedent.co.th/services/invisalign)
- [Veneers](https://thedent.co.th/services/veneers)

## Policies
- Content is medically reviewed; reviewer credentials on each page
- Prices in THB; ranges reflect typical cases as of <date>
```

(Confirm exact URLs with the user before publishing.)

**Schema/entity work in parallel:**
- Claim/verify Google Business Profile
- File a Wikidata entry for the clinic (Organization + sameAs to GBP, LinkedIn, Facebook)
- Add `Dentist`/`MedicalClinic` schema to homepage with `medicalSpecialty`, `availableService`, `priceRange`
- Add `Person` schema for each doctor with credentials and `worksFor`

## Recovery sequence (this week)

1. **Day 0 (today):** DevOps confirms the `host_not_allowed` source (CDN edge rule? origin firewall? WAF rule?). Remove the deny entry. Test with `curl -I https://thedent.co.th/` and `curl -I -A "GPTBot" https://thedent.co.th/`.
2. **Day 0–1:** Publish corrected `robots.txt` (above) and ensure `sitemap.xml` returns 200.
3. **Day 1:** Publish initial `llms.txt` at root.
4. **Day 1–2:** Submit sitemap to Google Search Console + Bing Webmaster Tools; request re-indexing of top 10 commercial pages.
5. **Day 2–3:** Trigger Perplexity discovery by linking to key pages from active social posts (Perplexity follows social signals quickly).
6. **Day 3–5:** Run the tracked-query battery against ChatGPT, Perplexity, Google AI Overviews, Claude — establish a fresh baseline now that retrieval is possible.
7. **Day 5–7:** Hand off to `seo-expert` for indexation monitoring and to `content-planner` for the citation-bait brief queue (answer-first rewrites, FAQ schema, original cost data).
8. **Week 2+:** Begin P1/P2 work — entity footprint, author schema, structured comparison content.
