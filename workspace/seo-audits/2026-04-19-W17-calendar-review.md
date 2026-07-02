# SEO Audit — W17 Editorial Calendar Review — 2026-04-19

**Scope:** `/home/user/GEO/workspace/plans/calendar-2026-W17.md` (5 items, Apr 20–24).
**Reviewer:** seo-expert.
**Status:** Calendar is broadly sound. 1 P0 clarification, a handful of P1 refinements, and some keyword/intent gaps to flag to `content-planner`.

## Executive summary

The W17 line-up is well-balanced across clusters, intents, and locales, and the Tuesday implants piece is correctly prioritized as the high-value slot. Main risks are: (1) a potential cannibalization collision on the Friday orthodontics refresh vs. Wednesday's Invisalign comparison if the braces pillar also targets "Invisalign vs จัดฟันเหล็ก" style queries; (2) the Monday Thai FAQ needs a confirmed parent service page to link up to or it risks orphan status; (3) intent coverage is thin on pure transactional / local-pack queries for Bangkok this week — we lean heavily informational / comparison.

## P0 blockers (fix this week)

- **Confirm the parent service URL for the Monday "ขูดหินปูน" piece before draft begins.** The planner already flagged this as a CONFIRM. Without a pillar to link up to, the FAQ becomes an orphan and burns a crawl slot. If no pillar page exists, either (a) promote a pillar service page into the pipeline before the FAQ, or (b) refactor the Monday FAQ into a section of the pillar rather than a standalone URL.

## P1 high-impact (fix this sprint)

- **Cannibalization risk: Wed Invisalign comparison vs. Fri Orthodontics pillar refresh.** Both pieces are TH, both cover clear-aligner-vs-braces decision logic. The Friday pillar refresh must avoid targeting "Invisalign vs จัดฟันเหล็ก" and similar comparison queries — those belong exclusively to the Wed article. Recommend the Friday pillar link out to the Wed comparison for that decision, and scope the pillar to types/prices/process/duration only. Add an explicit "DO NOT TARGET" keyword list to the Friday brief when it is written.
- **Missing transactional / near-me intent coverage.** 4 of 5 items are informational or commercial-investigation; only Friday is commercial. For a clinic, at least one piece per week should target high-intent transactional queries ("ทันตแพทย์ใกล้ฉัน", "คลินิกทันตกรรม [district]", "dental clinic [BTS station]"). Propose adding a local-landing or branch-page refresh to W18 to balance.
- **EN/TH ratio versus priority clusters is off.** Implants, veneers, and Invisalign are all flagged in `optimization-goals.md` as heavy medical-tourism clusters, but only 2/5 items this week are EN. For tourism-heavy clusters we should run EN-first and commission TH adaptations, not the other way round. Recommend flipping the Wed Invisalign piece to EN-first (or dual-commission) in a future week — W17 is locked, but flag for W18 planning.
- **Thursday Porcelain vs Composite Veneers needs an explicit primary-keyword decision.** "Porcelain vs composite veneers" is a global query — Bangkok-intent is thin. If the goal is medical-tourism capture, the brief must add a Bangkok/Thailand geo-modifier in H2s ("in Bangkok", "in Thailand") and internal links to the veneers pillar. Otherwise the piece ranks globally but converts poorly.
- **Friday service-page refresh needs a scope lock.** Refreshes silently widen over time. Require the brief to list: (a) what URL changes, (b) what URL doesn't, (c) what net-new H2s are added, (d) whether the refresh keeps the existing URL (preferred) or changes it (requires 301). Slug changes on an established service page are a P0 risk — default to "no slug change."

## P2 improvements (quarterly)

- Add a "DO NOT TARGET" keyword column to the calendar template to make cannibalization prevention first-class.
- Add a "parent pillar URL" column so orphan risk is visible at a glance.
- Track SERP feature targets per slot (featured snippet vs. PAA vs. local pack vs. AI Overview) — it clarifies the structural requirements for each brief.

## Keyword & content gaps

- No piece this week covers **"dental implants thailand"** as a standalone query — the Tuesday piece targets the Bangkok-specific variant. Thailand-level query is a distinct medical-tourism entry point; log as a candidate for the pillar page or a near-future brief.
- No **branded comparison** piece ("The Dent vs [competitor]") — regulated, per compliance rules, so this is intentional; noting it so it doesn't get accidentally commissioned.
- No **cost/pricing** piece in TH — Thai locals also price-shop; a TH counterpart to Tuesday's EN implant cost guide should be scheduled (as the brief already flags for backlog).
- No **Invisalign cost** piece in either locale — high-AOV cluster without a cost entry point is a leak. Recommend adding to W18 or W19.

## Locale balance check

| Locale | Count | Clusters covered |
|---|---|---|
| TH | 3 | General, Invisalign, Orthodontics |
| EN | 2 | Implants, Veneers |

TH-skewed this week is defensible per planner rationale (local audience density), but for priority-1/2/3 clusters (implants, Invisalign, veneers) the medium-term split should target EN-first. Not a W17 change — a W18+ correction.

## Priority ordering sanity check

Current slot order: Mon General → Tue Implants → Wed Invisalign → Thu Veneers → Fri Ortho.

Placing the highest-value piece (Tuesday implants) early in the week is correct — leaves Wed/Thu/Fri for SEO/GEO re-reviews and any CMS turnaround without pushing the flagship piece to a low-traffic Friday publish. Keep.

## Handoff to content-planner

1. Lock the Monday piece's parent pillar URL before draft kickoff. If none exists, sequence a pillar before the FAQ.
2. Add explicit "DO NOT TARGET" keyword list to the Friday orthodontics refresh brief to prevent overlap with Wednesday.
3. Add Bangkok/Thailand geo-modifiers to the Thursday veneers brief's H2 plan and internal-link map.
4. Schedule for W18+: (a) TH implant cost counterpart, (b) Invisalign cost piece, (c) at least one local/branch-page refresh or transactional-intent piece.
5. Add "parent pillar URL" and "DO NOT TARGET keywords" columns to the calendar template.

## Handoff to content-creator (page-level)

- Sample brief (Tue implants) has its full SEO requirements in the brief itself — see `/home/user/GEO/workspace/plans/briefs/dental-implants-cost-bangkok-2026.md`.
- Other briefs: not yet written. This review does not pre-empt the per-brief SEO checklist; each will get one when it lands.

## Open blocks

- Keyword volumes / difficulty for all W17 items are planner estimates. Need Search Console access or a rank-tracker subscription to validate (tech-debt in notebook).
- GBP / branch-pages status unknown — limits our ability to prescribe local-intent pieces until the branch inventory is confirmed.
