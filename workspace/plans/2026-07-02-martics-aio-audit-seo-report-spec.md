---
title: "Martics /admin/aio-audit — Comprehensive SEO Report: Product Spec"
version: "1.0 draft"
date: 2026-07-02
scope: "Turn the existing admin AIO-audit page into a full SEO report: on-demand snapshot audits + scheduled rank tracking, per-device positions, organic traffic, AI-Overview visibility, competitors, and auto-recommendations."
audience: "Martics engineering team (implementation-ready)"
---

# Martics — `/admin/aio-audit` Comprehensive SEO Report

## 0. Summary

This spec turns the current AIO-audit admin page into a comprehensive SEO report. The core user flow: a user enters a **target website** + a list of **targeted keywords** (+ country / language / optional location + device set), runs an audit, and receives a report covering **keyword position per device (desktop vs mobile)**, **organic traffic to the target site**, AI-Overview visibility, competitor comparison, and prioritized recommendations. Tracked keywords are re-checked on a schedule so the report also shows position history and traffic trends.

**Confirmed data sources**

| Need | Source | Works for |
|---|---|---|
| Per-device SERP positions, keyword metrics (volume/CPC/difficulty), SERP features incl. AI Overviews | Third-party SERP API — **DataForSEO recommended** (§7.1) | Any domain |
| Real organic traffic (sessions, users, conversions, landing pages) | **GA4 Data API** via OAuth | Owned/connected properties only |
| Estimated organic traffic | Derived: `volume × CTR-curve(position)` (§4.2) | Any domain (incl. competitors) |

> Google Search Console is intentionally **not** used. Estimated traffic covers any domain; measured GA4 traffic covers connected properties. The two are shown side by side and never blended into one number.

**Audit input object:** `target_domain` + `keywords[]` + `country`, `language`, optional `location` (city/region), `devices` (`desktop`, `mobile`, or both — default both), `schedule` (`off` / `daily` / `weekly`).

**Report sections:** §1 KPI overview · §2 Keyword rankings table · §3 Position history/trends · §4 Organic traffic · §5 Competitors · §6 AI Visibility ("AIO") · §7 Recommendations · §8 Data architecture · §9 UI layout · §10 Phased roadmap.

---

## 1. Report KPIs / Health-Score Overview

Rendered as a KPI card row at the top of the report. Every card shows: current value, delta vs previous snapshot, sparkline over last N snapshots.

**Conventions (used throughout)**
- `pos(k, d, t)` = organic position of `target_domain` for keyword `k`, device `d`, snapshot `t`. **Organic position** = rank among organic results only (`rank_group` in DataForSEO terms), not absolute pixel/SERP position. If the domain does not appear within fetched depth (top 100), `pos = NULL` ("not ranking").
- `K` = set of tracked keywords in the audit; `|K|` = count.
- `NR_PENALTY = 101` — value substituted for `NULL` positions in averages that must include non-ranking keywords (always disclose in tooltip).

| # | KPI | Formula | Notes |
|---|-----|---------|-------|
| 1 | **Avg position (desktop)** | `AVG(pos(k, desktop, t))` over keywords where `pos IS NOT NULL` | Show `n/|K|` ranking count next to it, e.g. "7.4 (31/50 ranking)". Do not mix penalty values here. |
| 2 | **Avg position (mobile)** | Same, `d = mobile` | Card shows both side-by-side + gap: `avg_mobile − avg_desktop` (positive = worse on mobile). |
| 3 | **Keywords in Top 3** | `COUNT(k WHERE pos(k,d,t) ≤ 3)` | Per device; respects the global device toggle (§9). |
| 4 | **Keywords in Top 10** | `COUNT(k WHERE pos ≤ 10)` | " |
| 5 | **Keywords in Top 100** | `COUNT(k WHERE pos IS NOT NULL)` | Equivalent to "ranking at all" given depth=100. |
| 6 | **Estimated organic traffic /mo** | `Σ over k: search_volume(k) × CTR(pos(k,d,t), d)`; `CTR(NULL) = 0` | CTR curve in §4.2. Per device; "combined" = `0.35 × desktop_est + 0.65 × mobile_est` (device split configurable per market, default 65% mobile). |
| 7 | **Share of Voice (SoV)** | `Σ_k volume(k)·CTR(pos(k,d,t), d) ÷ Σ_k volume(k)·CTR(1, d) × 100%` | Estimated traffic as a % of what ranking #1 for every tracked keyword would yield. Range 0–100%. Reused per competitor (§5). |
| 8 | **Visibility Index** (secondary; feeds health score) | `Σ_k weight(pos) ÷ |K| × 100`; weight: 1→1.0, 2–3→0.85, 4–5→0.60, 6–10→0.35, 11–20→0.15, 21–100→0.05, NULL→0 | Volume-agnostic complement to SoV (which is dominated by head terms). |
| 9 | **Real organic sessions (30d)** | GA4: sessions where `sessionDefaultChannelGroup = "Organic Search"`, last 30 complete days | Only when a GA4 property is connected; otherwise card shows "Connect GA4" CTA. |
| 10 | **Health score (0–100)** | `0.35·SoV + 0.35·VisibilityIndex + 0.15·Top10Rate + 0.15·MomentumScore` | `Top10Rate = Top10 ÷ |K| × 100`. `MomentumScore = 50 + clamp(Σ volume-weighted position changes, −50, +50)`. First snapshot: Momentum = 50. Bands: 0–39 Poor / 40–69 Fair / 70–100 Good. |

**Deltas vs previous snapshot.** Each card computes `Δ = current − previous_snapshot` (previous = most recent prior snapshot of the same target with the **same device + location settings**; on settings change the delta is suppressed with tooltip "tracking settings changed"). Sign coloring: for position metrics **lower is better** (green when Δ < 0); for counts/traffic/SoV higher is better. The date-range selector (§9) also allows delta vs "N days ago" — pick the snapshot closest to `today − N` (tolerance ±2 days daily, ±4 weekly).

---

## 2. Keyword Rankings Table

One row per keyword, with both devices shown in the same row (per-device columns) — the desktop↔mobile comparison is a core feature. Field-source notation uses DataForSEO endpoint paths; SerpApi equivalents noted where materially different.

| # | Column | Type / format | Definition & threshold | Source |
|---|---|---|---|---|
| 1 | Keyword | string | Tracked phrase; click → keyword detail drawer (trend chart §3.1 + SERP snapshot). | `keywords.phrase` |
| 2 | Position (desktop) | int 1–100 or "—" | Best organic position of `target_domain`; if multiple URLs rank, take best and store others (feeds §7-R7). | Organic SERP (`serp/google/organic/...`, `device=desktop`): first `items[]` with `type="organic"` and matching `domain` → `rank_group`. SerpApi: `organic_results[].position`. |
| 3 | Position (mobile) | int 1–100 or "—" | Same, `device=mobile`. | Same endpoint, `device=mobile` — a **separate API call** (both devices = 2 SERP requests/check). |
| 4 | Device gap flag | badge | `gap = pos_mobile − pos_desktop` (NULL→101). **Flag when `|gap| ≥ 5`, or one device top-10 while the other is >20 / not ranking.** Badge e.g. "📱 −7"; orange = mobile worse, blue = desktop worse. | Derived (cols 2–3). |
| 5 | Ranking URL | URL (path) | URL holding best position, per device; tooltip shows both if they differ (feeds §7-R7). | `items[].url` of matched item. SerpApi: `organic_results[].link`. |
| 6 | Search volume | int | Monthly searches for the audit's country/language; refresh monthly. | DataForSEO Labs `keyword_overview` → `keyword_info.search_volume`. SerpApi has none (see §7.1). |
| 7 | CPC | currency (2dp) | Google Ads top-of-page CPC. | `keyword_info.cpc`. |
| 8 | Keyword difficulty | int 0–100 + chip | Vendor difficulty. Chip: 0–29 green, 30–59 yellow, 60–100 red. | DataForSEO Labs `bulk_keyword_difficulty`. |
| 9 | SERP features | icon list | Features present per device: AI Overview, featured snippet, local pack, PAA, images, video, shopping, sitelinks, top ads. Filled icon = **owned by target**. Persisted in `serp_features` (§8.3). | `items[].type` values (`ai_overview`, `featured_snippet`, `local_pack`, `people_also_ask`, …). |
| 10 | Change vs last check | signed int + arrow | `prev_pos − current_pos` per device (positive = improved). States: `NEW`, `LOST`, `—` (first check). | Derived from `rank_snapshots`. |
| 11 | Est. traffic | int | `volume × CTR(pos, device)` (§4.2); basis follows device toggle. | Derived. |
| 12 | AIO | badge | AI-Overview state for this keyword (see §6.3). | Derived from `aio_observation`. |
| 13 | Keyword group | tag(s) | Optional user label for filtering. | `keywords.group_label`. |

**Behaviors:** default sort = volume desc; sortable on every column; filters per §9; sticky header; CSV export of filtered view; 500-row cap with virtual scroll.

---

## 3. Position History / Trends

### 3.1 Per-keyword trend chart (detail drawer)
- Line chart, X = snapshot date, Y = position, **Y-axis inverted** (1 at top); linear 1–20, compressed 21–100.
- Two series: desktop (solid), mobile (dashed), toggleable via legend.
- "Not ranking" = line break + hollow marker on the 100 line, tooltip "Not in top 100".
- Tooltip: date, position per device, ranking URL — annotate when the ranking URL **changed** between snapshots (URL flip = cannibalization signal).
- v1.1: user event annotations ("published new page", "migration").
- Data: `rank_snapshots WHERE keyword_id = ? AND date BETWEEN range`.

### 3.2 Aggregate position-distribution chart
Stacked area (stacked bar for weekly) over time. Buckets per snapshot date and device:

| Bucket | Rule | Color |
|---|---|---|
| Top 3 | `pos ≤ 3` | dark green |
| 4–10 | `4 ≤ pos ≤ 10` | green |
| 11–20 | `11 ≤ pos ≤ 20` | yellow |
| 21–100 | `21 ≤ pos ≤ 100` | orange |
| Not ranking | `pos IS NULL` | gray |

Y = keyword count with a %-mode toggle (100% stacked). Respects the device toggle; **Both** renders two small-multiple charts side by side (never average the two devices — that hides the gap we sell). Buckets computed at read time from `rank_snapshots`; add a materialized daily rollup only if query time exceeds ~500 ms. Keyword-group and date-range filters apply.

---

## 4. Organic Traffic

Two clearly labeled layers in one panel: **"Measured (GA4)"** and **"Estimated (rank-based)"**. Never blend them into one number.

### 4.1 Layer A — Real GA4 data (connected properties only)
Applies when the target has a linked GA4 property (OAuth in §8.2). Pulled nightly into `traffic_daily`.

**GA4 Data API `runReport` requests:**
- **Report 1 — daily organic totals:** dims `date`, `sessionDefaultChannelGroup`; metrics `sessions`, `totalUsers`, `engagedSessions`, `engagementRate`, `conversions`/`keyEvents` (prefer `keyEvents` on newer API versions); filter `sessionDefaultChannelGroup = "Organic Search"`; dateRange last 90 days on first sync (backfill up to 13 months on demand), then rolling last 3 days nightly (GA4 data is not final for ~48 h — re-upsert D-1..D-3).
- **Report 2 — landing-page breakdown:** dims `date`, `landingPagePlusQueryString` (strip query string on ingest; keep raw in debug column), `sessionDefaultChannelGroup`; metrics `sessions`, `totalUsers`, `conversions`/`keyEvents`; cap top 1,000 landing pages/day by sessions.
- **Report 3 (optional):** add dim `sessionSource` filtered to organic to split google / bing / other.

**UI:** daily organic-sessions line chart, range totals + delta vs prior equal-length period, landing-page table (page, sessions, users, conversions, Δ%). Where a landing page matches a **ranking URL** from §2, show a link icon cross-referencing the keywords ranking with that URL. Batch the 2–3 reports per property via `batchRunReports` (GA4 Core quotas are generous for nightly pulls).

### 4.2 Layer B — Estimated traffic (any domain)
`est_traffic(k, d) = search_volume(k) × CTR(pos(k,d), d)`; domain total = Σ over keywords. Also computed for competitors (§5).

**Reference CTR curve** (industry-composite; stored as editable config table `ctr_curves` — treat as approximate defaults):

| Position | Desktop CTR | Mobile CTR |
|---|---|---|
| 1 | 32.0% | 26.0% |
| 2 | 15.5% | 13.5% |
| 3 | 9.5% | 9.0% |
| 4 | 6.5% | 6.0% |
| 5 | 4.5% | 4.3% |
| 6 | 3.5% | 3.3% |
| 7 | 2.8% | 2.7% |
| 8 | 2.3% | 2.3% |
| 9 | 2.0% | 2.0% |
| 10 | 1.8% | 1.8% |
| 11 | 1.6% | 1.5% |
| 12 | 1.4% | 1.3% |
| 13 | 1.2% | 1.2% |
| 14 | 1.1% | 1.1% |
| 15 | 1.0% | 1.0% |
| 16 | 0.9% | 0.9% |
| 17 | 0.8% | 0.8% |
| 18 | 0.7% | 0.75% |
| 19 | 0.65% | 0.7% |
| 20 | 0.6% | 0.65% |
| 21–30 | 0.4% | 0.45% |
| 31–100 | 0.15% | 0.2% |

**Documented assumptions ("About this estimate" tooltip):**
1. All-intents composite; branded queries skew far higher at #1 (often 50%+); AI-Overview / heavy-ad SERPs skew lower.
2. Volume = monthly country-level average from Google Ads data (rounded, seasonal).
3. No SERP-feature dampening in v1. **v1.1:** multiply CTR by 0.7 when an AI Overview or featured snippet is present and not owned (config flag, default off).
4. Covers the tracked keyword set only — label the number "Est. traffic from tracked keywords".
5. Mobile tail (11+) slightly fatter than desktop; figures approximate.

**Calibration (connected properties):** show `calibration_ratio = GA4 organic sessions (30d) ÷ estimated monthly traffic` as a footnote ("estimates run ~1.8× low for this site"). Do not auto-adjust in v1.

---

## 5. Competitors

No user input — competitors are **derived from the SERPs already fetched**.

**Derivation.** For the latest snapshot, over all tracked keywords and both devices: (1) collect every organic result's registrable domain (eTLD+1) from positions 1–20; (2) exclude `target_domain` + a configurable ignore-list (`wikipedia.org`, `youtube.com`, `facebook.com`, `amazon.*`, `reddit.com`, `quora.com`, `pinterest.*` — toggle "show big platforms"); (3) score `overlap_count = COUNT(DISTINCT keyword WHERE domain in top 20)`; (4) rank desc, take **top 10** into `competitors`.

**Metrics per competitor (comparison table):**

| Column | Formula |
|---|---|
| Keyword overlap | `overlap_count`, `overlap_pct = overlap_count ÷ |K| × 100%` |
| Avg position (desktop / mobile) | `AVG(pos_c(k,d))` where competitor ranks (positions come from the same stored SERP items — **zero extra API cost**) |
| Keywords in top 3 / top 10 | counts, per device |
| Share of Voice | §1 KPI-7 formula with `pos_c` — comparable bar chart: target vs top-5 |
| Est. traffic (tracked set) | §4.2 with `pos_c` |
| Head-to-head | `wins = COUNT(k WHERE pos_target < pos_c)`, `losses = COUNT(k WHERE pos_c < pos_target)` (NULL loses to any rank) → "You lead 18 / trail 27" |

**Per-device comparison view.** Grouped bar chart: for top-5 competitors + target, avg position desktop vs mobile side by side. Clicking a competitor filters the rankings table (§2) to keywords where it ranks, adding its position (desktop/mobile) and `Δ vs you`. **Mobile-specialist flag:** competitor whose `avg_pos_mobile ≤ avg_pos_desktop − 3` gets a "strong on mobile" badge (feeds §7-R12).

---

## 6. AI Visibility ("AIO")

The distinctive angle of the AIO-audit page: whether tracked keywords trigger Google **AI Overviews** and whether the target domain is cited. Section renders after §2 rankings, before §5 competitors visually; device toggle at the top, consistent with the rest of the report.

### 6.1 What we capture
For every keyword × geo × language × device on every crawl, record one `aio_observation`:

| Field | Type | Description |
|---|---|---|
| `keyword_id`, `crawl_id`, `device` | FK / enum | Identity |
| `aio_present` | bool | SERP contains an AI Overview block |
| `aio_state` | enum(`full`,`collapsed_generate`,`error`,`none`) | AIO may require a second fetch or fail (§6.4) |
| `aio_position` | int? | Absolute position of AIO block (`rank_absolute`); usually 1 |
| `aio_text` | text? | Answer text (first ~5 KB; full payload in blob storage) |
| `target_cited` | bool | Target domain appears in citations (matching §6.5) |
| `target_citation_positions` | int[] | 1-based indexes of target citations in the ordered list |
| `target_citation_count`, `total_citation_count` | int | Counts |
| `raw_payload_ref` | string | Pointer to raw SERP-API JSON (retain ≥ 13 months) |

Child table `aio_citation(id, observation_id, position, url, domain, registrable_domain, title, source_name, snippet)`. `position` = order of appearance in the provider's references array — the best available proxy since Google exposes no official citation ranking (document this in a UI tooltip).

### 6.2 Provider payload shapes
**DataForSEO (primary):** `POST /v3/serp/google/organic/live/advanced` (or `task_post`+`task_get/advanced` for scheduled batches). AI Overview arrives as an item in `tasks[0].result[0].items[]` with `"type": "ai_overview"`, containing `ai_overview_element` items whose `references[]` hold `{source, domain, url, title, text}`. Adapter rules: merge references from per-element **and** any top-level `references[]`, preserving first-seen order, dedupe by exact `url`; if `asynchronous_ai_overview: true`, resolve with `load_async_ai_overview: true` in the task POST (extra cost/latency — per-report setting, default **on**); an `ai_overview` item with empty `items` → `aio_present=true`, `aio_state='collapsed_generate'`.

**SerpApi (alternative adapter):** `GET /search?engine=google` returns an `ai_overview` object — either inline (`text_blocks[]` with `reference_indexes[]` + `references[]`) or token-only (`page_token` requiring an immediate follow-up `engine=google_ai_overview` call; **token expires in ~1 min**, so the second fetch must be synchronous inside the same job and is separately billed — factor 2× cost for token-case keywords). Citation position = `references[].index` (0-based → store 1-based); persist `reference_indexes` (claim-level attribution) for R-AIO4 and future "which sentence cites you" UI.

> ⚠️ **Schema-stability caveat.** Field names above match current (2026-07) DataForSEO v3 / SerpApi docs, but both vendors revise SERP-feature schemas several times a year. Adapters must: tolerate unknown sibling fields; **log-and-alert on validation failure rather than dropping the observation**; pin a schema version per crawl. Build behind the same `SerpProvider` interface as §8.1.

### 6.3 States & edge cases

| Situation | Handling |
|---|---|
| No AIO block | `aio_present=false`, `aio_state='none'` |
| AIO stub / "generate" button | `aio_present=true`, `aio_state='collapsed_generate'`, citations empty — **counts toward trigger rate** (still displaces clicks) but **excluded from citation-position stats**; shown as "AIO (uncrawled)" |
| Second fetch fails / token expired | `aio_state='error'`; retry once with fresh base search; else keep `aio_present=true`, empty citations, mark degraded |
| AIO flickers between crawls | Expected (Google A/B tests heavily); metrics use per-crawl values; trend chart smooths with 7-day rolling window |
| Same domain cited multiple times | `target_citation_count` counts all; `target_cited` is boolean; citation-share metrics use boolean per keyword |

### 6.4 Domain matching
Normalize both target and citation URLs to **registrable domain** (public-suffix list; `www.thedent.co.th` → `thedent.co.th`). Match: `citation.registrable_domain == target.registrable_domain`. Store full URL to also report which page got cited. Competitors matched the same way.

### 6.5 Metrics (computed per crawl, rolled into `aio_metrics_daily`)
Let `K` = tracked keyword×device pairs under the current device filter (default "all devices", each pair once).

- **M1 — AIO trigger rate** = `|{k : aio_present(k)}| / |K|`. Sub-metric `aio_crawled_rate` = share of triggered AIOs with `state='full'` (data-quality, tooltip only).
- **M2 — Citation share (target)**: `K_aio = {k : aio_present ∧ state='full'}`; `citation_share = |{k ∈ K_aio : target_cited}| / |K_aio|`. Denominator = keywords with a **readable** AIO. If `|K_aio|=0` display "—", not 0%.
- **M3 — Weighted citation share** = `Σ_{k∈K_aio} 1/min(target_citation_positions(k)) ÷ |K_aio|` (rewards earlier citation).
- **M4 — Avg citation position** = mean over `{k : target_cited}` of `min(target_citation_positions(k))`.
- **M5 — Competitor citation share** = M2 with a competitor domain substituted. **Share of voice** = `Σ_{k∈K_aio} citation_count(d,k) ÷ Σ_{k∈K_aio} total_citation_count(k)`.
- **M6 — Trend deltas** for M1–M5 vs previous / 7d / 30d / report-start; on keyword-set change compute deltas on the **intersection** and badge "keyword set changed".
- **M7 — Opportunity count** = `|{k∈K_aio : ¬target_cited ∧ organic_rank(target,k) ≤ 10}|` (feeds R-AIO1).

### 6.6 Report UI (AI Visibility section)
- **KPI cards (row of 4):** AIO Trigger Rate (M1) · Your Citation Share (M2, tooltip explains denominator) · Avg Citation Position (M4, inverted color: down = good, "—" if never cited) · AIO Opportunities (M7, anchors to filtered recommendations).
- **Rankings-table columns (added to §2):** **AIO** badge (`—` none · `AIO` gray triggered-not-cited · `AIO ✓` green cited · `AIO ?` dashed collapsed/error; filter facets "Has AIO / Cited / Not cited") and **AIO Cite #** (`#2 of 8`). Row-expand drawer: AIO answer text (first ~400 chars, "show full"), full ordered citation list with favicon/domain/title/link (target highlighted, competitors flagged), per-crawl present/cited sparkline.
- **Competitor citation-share comparison:** horizontal bar per domain (target pinned first) for M5, SoV as secondary bar/toggle; table beneath (domain · citation share · SoV · # keywords cited · avg citation position · Δ30d). Cap 10; auto-detected = top-N by citation frequency across `K_aio`, excluding the ubiquitous-domain ignore-list (wikipedia/youtube/reddit/quora), configurable.
- **Trend chart:** lines for M1 and M2 (competitor shares togglable dashed), 7-day rolling toggle, annotations on keyword-set and provider-schema changes. Empty state (<2 crawls): "Trend appears after your second scheduled crawl."
- **Empty/degraded:** no keyword triggers AIO → single informational card; adapter errors >20% of a crawl → "AI Overview data is partial for this crawl" banner + affected-metric badges.

---

## 7. Auto-Generated Recommendations

Rule engine runs after each snapshot. Each rule emits `{rule_id, severity, entity_ref, message, evidence}`. Severity `high|medium|low`. Dedupe by `(rule_id, entity)`; carry `status` (new / persisting / resolved / dismissed / snoozed) across snapshots; auto-resolving a condition records a "win" in the report changelog.

### 7.1 SEO / ranking rules

| ID | Rule | Condition | Recommendation | Severity |
|---|---|---|---|---|
| R1 | Mobile gap | `pos_mobile − pos_desktop ≥ 5` (or desktop top-10 while mobile >20/NULL) ∧ volume ≥ 100 | "**{kw}** ranks #{pd} desktop but #{pm} mobile. Check mobile Core Web Vitals, intrusive interstitials, mobile rendering of `{url}`." | high |
| R2 | Desktop gap | inverse of R1 | "**{kw}** performs better on mobile (#{pm}) than desktop (#{pd}). Review desktop layout/UX of `{url}`." | medium |
| R3 | Striking distance (page 2) | `11 ≤ best_pos ≤ 20` ∧ volume ≥ 100 | "**{kw}** sits at #{pos} — page 2. Refresh `{url}`: expand depth, add 2–3 internal links with this anchor, update freshness. Highest-leverage win." | high |
| R4 | Top-3 push | `4 ≤ best_pos ≤ 10` ∧ volume ≥ 500 | "**{kw}** is top-10 (#{pos}) but not top-3. CTR triples at #3. Improve title/meta CTR, add FAQ/schema, earn 1–2 links to `{url}`." | medium |
| R5 | High-volume not ranking | `pos IS NULL` both devices ∧ volume ≥ 1000 | "No top-100 ranking for **{kw}** ({vol}/mo). Create dedicated content, or verify indexation of the intended page." | high |
| R6 | Lost ranking | prev `pos ≤ 20`, current NULL or dropped ≥ 20 | "**{kw}** dropped from #{prev} to {cur}. Check `{url}` for deindexation, redirects/404, or SERP shake-up." | high |
| R7 | Cannibalization | ≥ 2 target URLs in top 20 for same keyword+device, or ranking URL flipped ≥ 2× in last 5 snapshots | "Two URLs compete for **{kw}**: `{url1}` (#{p1}) and `{url2}` (#{p2}). Consolidate: canonical target, 301/de-optimize the other, fix internal anchors." | medium |
| R8 | Snippet / AIO opportunity | SERP has `featured_snippet`/`ai_overview` not owned ∧ target `pos ≤ 10` | "**{kw}**: {feature} owned by {owner}. You rank #{pos} — restructure `{url}` with a 40–60-word direct answer + list/table." | medium |
| R9 | Zero-click warning | AI Overview + owned position ≥ 4 ∧ volume ≥ 500 | "**{kw}** SERP has an AI Overview; expect suppressed CTR at #{pos}. Prioritize AIO-free keywords for traffic, or target citation." | low |
| R10 | Low difficulty, unexploited | KD ≤ 30 ∧ (`pos > 10` or NULL) ∧ volume ≥ 100 | "**{kw}** is low-difficulty (KD {kd}) but you rank {pos}. Quick win: publish/upgrade a focused page." | medium |
| R11 | Weak CTR vs rank (GA4 only) | ranking URL top-5 for keywords ≥ 2000 volume, but GA4 landing-page sessions < 30% of estimated | "`{url}` ranks well but GA4 shows only {sess} organic sessions/mo vs ~{est} expected. Rewrite title/meta; check rich-result eligibility." | medium |
| R12 | Competitor momentum | competitor SoV Δ ≥ +5 pts between snapshots, or newly top-3 on ≥ 3 tracked keywords | "**{competitor}** gained {Δ} SoV since {date} (now leads on {n} of your keywords). Review their pages on: {list}." | low |

### 7.2 AI-visibility rules (route R-AIO3 to the content-planning queue)

| ID | Condition | Recommendation | Sev |
|---|---|---|---|
| R-AIO1 | `aio_present ∧ ¬target_cited ∧ organic_rank ≤ 10 ∧ ∃ competitor cited` | "**{kw}** triggers an AI Overview citing {competitor} (#{pos}); you rank #{organic_rank} but aren't cited. On `{your_url}`: add a 40–60-word direct answer in the first paragraph under a question-phrased H2, add `FAQPage` schema, include one sourced fact the AIO lacks. Compare vs `{competitor_cited_url}`." | high |
| R-AIO2 | `target_cited ∧ min(citation_position) ≥ 4 ∧ total_citations ≥ 5` | "You're cited at #{pos} of {total} for **{kw}**. On `{cited_url}`: move the answer sentence above the fold, tighten to one self-contained claim with a concrete figure, refresh `dateModified`." | medium |
| R-AIO3 | `aio_present ∧ ¬target_cited ∧ organic_rank > 20 / unranked` | "**{kw}** triggers an AI Overview but you have no ranking page. Create one: question-shaped headings, answer-first lede, comparison table / numbered steps, author byline, visible dates. Cited domains to study: {top_3_cited_urls}." | medium |
| R-AIO4 | `target_cited ∧ cited_url ≠ best_organic_url` | "The AI Overview cites `{cited_url}` but your ranking page is `{organic_url}`. Consolidate: internal-link the two, move the quotable block onto the page you want cited (or canonicalize)." | medium |
| R-AIO5 | `target_cited (prev/last 14d) ∧ ¬target_cited (current) ∧ aio_present (current)` | "You lost your AI Overview citation for **{kw}** (last seen {date}, #{old_pos}). Now cited: {new_domains}. Diff their answer text vs yours; re-add the specific claim the AIO used to quote." + notification | high |
| R-AIO6 | ≥ 3 keywords in a cluster trigger AIOs ∧ cluster citation share < account share ∧ ranking pages lack FAQ/Q&A structure | "The '{cluster}' cluster triggers AIOs on {n} keywords but your citation share is {x}% vs {y}% overall. Add a 4–6 question FAQ block (`FAQPage` schema) to each ranking page: {query_list}." | medium |

**Ordering.** UI groups by severity desc, then by `volume × |position opportunity|` desc. Cross-severity priority for the featured list: `R-AIO5 > R5/R6/R1 > R-AIO1 > R4/R-AIO4 > R3 > R-AIO2 > R-AIO6 > R-AIO3`. Each item has Dismiss / Snooze(30d), persisted per target.

---

## 8. Data Architecture

### 8.1 SERP API choice — DataForSEO vs SerpApi

| Criterion | DataForSEO | SerpApi |
|---|---|---|
| Per-device (desktop/mobile) | Yes — `device` param on all Google SERP endpoints | Yes — `device=desktop\|mobile\|tablet` |
| Cost per 1k Google SERP checks (approx., mid-2026 — **verify before contract**) | ~$0.60/1k standard queue, ~$1.20/1k priority, ~$2.00/1k live; pay-as-you-go, $50 min | Subscription: $75/mo=5k (~$15/1k), $150/mo=15k (~$10/1k); no rollover |
| Batching | Native: up to 100 tasks/POST, async retrieve or pingback webhooks | One search/request; parallel HTTP + throughput caps; no batch queue |
| Keyword metrics (volume/CPC/difficulty) | Yes — Keywords Data + Labs (one vendor) | **No** — SERPs only; needs a second vendor |
| Localization | country + language + granular `location_code`/coords | domain/gl/hl + `location` (uule) |
| Latency | async queue (minutes) for scheduled; live mode for on-demand | real-time (~2–5 s) |

**Recommendation: DataForSEO.** (1) ~10–25× cheaper at tracking scale — 100 keywords × 2 devices × 30 days = 6,000 checks/mo ≈ **$3.60** standard vs ≈ **$75+** on SerpApi; (2) task batching + webhooks map onto the scheduler (§8.4); (3) single vendor also supplies volume/CPC/KD (SerpApi forces a second integration); (4) use **live mode** ($2/1k) for the "Run audit now" path so first results render in seconds, **standard queue** for scheduled re-checks. Build behind a `SerpProvider` interface (`fetchSerp(keyword, device, locale) → NormalizedSerp`) so SerpApi stays a drop-in fallback. *(Pricing approximate, verified July 2026 — see Sources.)*

### 8.2 GA4 integration
- **OAuth 2.0 (web flow):** scope `analytics.readonly`; store `refresh_token` encrypted (KMS / AES-256 at rest) in `ga4_connections`; access tokens in memory only.
- **Connect flow:** "Connect GA4" on a target → Google consent → `accountSummaries.list` → user picks a property → store `property_id` linked to `audit_target_id`. One property per target; a Google account may back many targets.
- **Nightly pull (03:00 target TZ):** per connection, `batchRunReports` (§4.1); upsert `traffic_daily` keyed `(property_id, date, landing_page, channel_group)`; re-upsert last 3 days. Backoff/resume on 429/`RESOURCE_EXHAUSTED`; after 3 consecutive failed nights set `status=error` + banner + re-auth CTA.

### 8.3 Data model (PostgreSQL)

```sql
audit_targets (
  id uuid PK, domain text NOT NULL,          -- registrable domain, lowercased
  country_code char(2) NOT NULL, language_code char(2) NOT NULL,
  location_name text NULL, location_code int NULL,   -- resolved SERP location_code
  devices text[] NOT NULL DEFAULT '{desktop,mobile}',
  schedule text NOT NULL DEFAULT 'weekly',   -- 'off'|'daily'|'weekly'
  serp_depth int NOT NULL DEFAULT 100,
  ga4_connection_id uuid NULL FK,
  created_by uuid FK, created_at timestamptz, archived_at timestamptz NULL
)
keywords (
  id uuid PK, audit_target_id uuid FK NOT NULL, phrase text NOT NULL,
  group_label text NULL, search_volume int NULL, cpc numeric(8,2) NULL,
  currency char(3) NULL, difficulty smallint NULL,
  metrics_fetched_at timestamptz NULL, is_active bool DEFAULT true,
  UNIQUE (audit_target_id, phrase)
)
rank_snapshots (                             -- keyword × device × date; INSERT-ONLY
  id bigserial PK, keyword_id uuid FK NOT NULL, device text NOT NULL,
  checked_at timestamptz NOT NULL, check_date date NOT NULL,
  position smallint NULL,                    -- best organic rank_group; NULL = not in depth
  ranking_url text NULL,
  additional_positions jsonb NULL,           -- [{position,url}] other target URLs (cannibalization)
  serp_task_id text NULL, raw_serp_ref text NULL,   -- S3 key, 90-day lifecycle
  UNIQUE (keyword_id, device, check_date)
)
serp_features (
  id bigserial PK, rank_snapshot_id bigint FK NOT NULL,
  feature_type text NOT NULL,                -- 'ai_overview','featured_snippet','local_pack',...
  owned_by_target bool NOT NULL DEFAULT false, owner_domain text NULL,
  feature_position smallint NULL
)
aio_observation (                            -- AI Overview per keyword × device × crawl
  id bigserial PK, keyword_id uuid FK NOT NULL, rank_snapshot_id bigint FK NOT NULL,
  device text NOT NULL, aio_present bool NOT NULL,
  aio_state text NOT NULL,                   -- 'full'|'collapsed_generate'|'error'|'none'
  aio_position smallint NULL, aio_text text NULL,
  target_cited bool NOT NULL DEFAULT false,
  target_citation_positions int[] NULL, target_citation_count int DEFAULT 0,
  total_citation_count int DEFAULT 0, raw_payload_ref text NULL,
  UNIQUE (keyword_id, device, rank_snapshot_id)
)
aio_citation (
  id bigserial PK, observation_id bigint FK NOT NULL, position int NOT NULL,
  url text, domain text, registrable_domain text, title text,
  source_name text, snippet text NULL
)
traffic_daily (
  id bigserial PK, audit_target_id uuid FK NOT NULL, property_id text NOT NULL,
  date date NOT NULL, landing_page text NOT NULL DEFAULT '(total)',
  sessions int, total_users int, engaged_sessions int, conversions numeric(12,2),
  channel_group text NOT NULL DEFAULT 'Organic Search', pulled_at timestamptz,
  UNIQUE (property_id, date, landing_page, channel_group)
)
competitors (                                -- recomputed per snapshot
  id bigserial PK, audit_target_id uuid FK NOT NULL, snapshot_date date NOT NULL,
  domain text NOT NULL, overlap_count int NOT NULL,
  avg_pos_desktop numeric(5,1) NULL, avg_pos_mobile numeric(5,1) NULL,
  top3_count int, top10_count int, sov_pct numeric(5,2), est_traffic int,
  UNIQUE (audit_target_id, snapshot_date, domain)
)
recommendations (
  id bigserial PK, audit_target_id uuid FK, snapshot_date date,
  rule_id text, severity text, entity_ref jsonb, message text, evidence jsonb,
  status text DEFAULT 'new', snoozed_until date NULL,
  UNIQUE (audit_target_id, rule_id, (entity_ref::text))
)
ga4_connections (
  id uuid PK, google_account_email text, property_id text,
  refresh_token_enc bytea, status text, last_pull_at timestamptz, created_at timestamptz
)
```
Indexes: `rank_snapshots (keyword_id, device, check_date DESC)`; `traffic_daily (audit_target_id, date)`; `serp_features (rank_snapshot_id)`; `aio_observation (keyword_id, device)`; partial `keywords (audit_target_id) WHERE is_active`.

### 8.4 Scheduler design
- **On-demand ("Run now"):** enqueue `audit_run` → DataForSEO **live** SERP calls (parallelism 10, retry ×2 w/ jitter) for keywords × devices → if keyword metrics stale (>30 days) fire volume/CPC/KD tasks → write `rank_snapshots` + `serp_features` + `aio_observation` → recompute competitors + KPIs + AIO metrics + recommendations → status `queued → fetching (x/y) → computing → ready` via SSE/websocket. Max 1 concurrent on-demand run per target.
- **Scheduled re-checks:** per-target `schedule` (daily 05:00 UTC / weekly Mondays). Batch job posts ≤ 100 tasks per `task_post` on the **standard queue** with a `pingback_url`; webhook receiver fetches via `task_get`, validates, writes snapshots. Sweep at +2 h re-polls `tasks_ready`; unresolved at +6 h retried once, then the (keyword, device, date) cell is `missed` (chart gap, never interpolated).
- **Snapshot immutability:** `rank_snapshots` / `serp_features` / `aio_observation` are **insert-only** (DB trigger raises on UPDATE). On `(keyword_id, device, check_date)` collision, first-write-wins (an on-demand run the same day as a scheduled one doesn't overwrite). Corrections via superadmin-only tombstone flag, never mutation.
- **Monthly job (1st):** refresh volume/CPC/difficulty for active keywords.
- **Cost guardrail:** per-target monthly SERP-call budget (default 10,000); scheduler pauses the target + banner when exceeded.

---

## 9. UI Layout — `/admin/aio-audit`

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Audit: example.com ▾    [Run audit now]  Schedule: Weekly ▾   Last: Jul 1 ✓  │
│ Country: TH ▾  Lang: th ▾  Location: Bangkok ▾        [⚙ Edit keywords (48)] │
├──────────────────────────────────────────────────────────────────────────────┤
│ GLOBAL FILTER BAR                                                            │
│ Device: [ Desktop | Mobile | Both ]   Date range: [Last 30d ▾]               │
│ Keyword group: [All ▾]   Compare to: [Previous snapshot ▾]                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ KPI CARD ROW                                                                 │
│ ┌Health 72 ▲4┐ ┌Avg pos D 8.2 / M 11.4 ▲┐ ┌Top3 6 ▲1┐ ┌Top10 19 ▲3┐          │
│ ┌Est. traffic 4.2k/mo ▲12%┐ ┌SoV 17.3% ▲1.1┐  (+ GA4 sessions card if conn.) │
├──────────────────────────────────────────────────────────────────────────────┤
│ AI VISIBILITY CARD ROW (§6.6)                                                │
│ ┌AIO trigger 41% ▲3┐ ┌Your citation share 22% ▲2┐ ┌Avg cite # 2.4 ▼┐ ┌Opps 7┐│
├───────────────────────────────────┬──────────────────────────────────────────┤
│ POSITION DISTRIBUTION (stacked     │ TRAFFIC PANEL (tabs)                     │
│ area, buckets §3.2, device toggle) │ [GA4 measured] [Estimated]               │
│                                    │ line chart + totals + Δ; landing-page    │
│                                    │ mini-table; "Connect GA4" CTA empty state│
├───────────────────────────────────┴──────────────────────────────────────────┤
│ RANKINGS TABLE (§2 + §6.3 AIO columns)                                       │
│ [Search kw…] [Pos: All|Top3|Top10|11–20|21–100|Not ranking ▾]                │
│ [Movement: All|Improved|Dropped|New|Lost ▾] [Feature ▾] [AIO: Has|Cited ▾]   │
│ [⚑ Device-gap only] [Export CSV]                                             │
│ kw | posD | posM | gap | URL | vol | CPC | KD | features | AIO | Δ | est.trf  │
│ (row click → drawer: trend chart §3.1, SERP snapshot, AIO answer + citations)│
├───────────────────────────────────┬──────────────────────────────────────────┤
│ COMPETITORS (§5) + AIO citation    │ RECOMMENDATIONS (§7)                     │
│ share (§6.6): SoV bar you vs top 5 │ grouped by severity; count badges        │
│ table: domain|overlap|avgD|avgM|   │ each: message + evidence chips +         │
│ top10|SoV|est.trf|cite-share|H2H   │ [View keywords] [Dismiss] [Snooze]       │
│ (row click → filters rankings tbl) │ filter: severity, rule type, status      │
└───────────────────────────────────┴──────────────────────────────────────────┘
```

**Interaction rules**
- **Device toggle is global:** `Desktop`/`Mobile` re-bases every card, chart, and the table's Δ/est-traffic columns; `Both` shows dual columns + small-multiple charts.
- **Date range** (7d/30d/90d/custom) drives trend charts, GA4 panel, and the KPI comparison snapshot; "Compare to" overrides the delta baseline.
- All filters serialize to the URL query string (shareable admin links).
- First-run: setup checklist (keywords added → locale set → run audit); charts render after ≥ 2 snapshots.
- Snapshot in progress: KPI skeletons + "fetching 96/126 SERPs".
- Export: full-report **PDF** (KPI rows + distribution chart + top-50 table + recommendations) and per-table **CSV**; shareable white-label client link (roadmap Phase 3).

---

## 10. Phased Roadmap

**Phase 1 — MVP (input → snapshot report).** Schema + DataForSEO `SerpProvider` + on-demand run + rankings table with per-device positions + estimated traffic (§4.2) + KPI row.

**Phase 2 — Tracking & GA4.** Scheduler (daily/weekly re-checks, immutable snapshots) + deltas + position-history/trend charts (§3) + GA4 OAuth + measured-traffic panel (§4.1) + recommendations engine (§7.1).

**Phase 3 — AI visibility, competitors, exports.** AI-Overview capture + AIO metrics/UI (§6) + AIO recommendations (§7.2) + competitor derivation & comparison (§5) + PDF export + white-label share link.

**Phase 4 — Future (not scoped here).**
- **ChatGPT / Perplexity / Gemini citation tracking** via a scheduled **prompt battery**: 1–3 question variants per keyword, run monthly through each engine's API with grounding enabled (OpenAI Responses `web_search`, Gemini Search grounding, Perplexity `citations[]`), parsed with the §6.4 matching pipeline. Answers are non-deterministic — sample n=3 and report citation *frequency*, not booleans. Use official APIs only (no consumer-UI scraping). Build-vs-buy spike first (Profound / Otterly / DataForSEO LLM-response endpoints).
- **llms.txt check:** fetch `/llms.txt` + `/llms-full.txt`, validate structure (llmstxt.org), plus a robots.txt **AI-bot matrix** (GPTBot, OAI-SearchBot, PerplexityBot, ClaudeBot, Google-Extended, CCBot, Bytespider — allow/deny). Cheap, high demo value.
- **Answer-shaped-content scoring:** per ranking URL, a 0–100 heuristic (answer in first 2 sentences via query↔lede embedding similarity, question-shaped headings, tables/lists/FAQ schema, byline + dates, stat density). Surfaces beside organic rank; feeds R-AIO1/R-AIO3. Batch the LLM call, cache by content hash.

---

## Sources (pricing/payload figures — approximate, checked July 2026; verify before contract)
- DataForSEO SERP API pricing — https://dataforseo.com/apis/serp-api/pricing
- DataForSEO pricing update note — https://dataforseo.com/update/important-serp-api-remains-fully-operational-pricing-update
- DataForSEO AI Overview SERP feature — https://dataforseo.com/serp-feature/ai-overview
- DataForSEO — scraping AI Overviews guide — https://dataforseo.com/help-center/how-to-scrape-google-ai-overviews-with-serp-api
- SerpApi plans & pricing — https://serpapi.com/pricing
- SerpApi Google AI Overview API — https://serpapi.com/google-ai-overview-api
- SERP API pricing comparison 2026 — https://www.proxies.sx/blog/cheapest-serp-api-comparison-2026
