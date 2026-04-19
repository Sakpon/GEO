# Content Planner — Private Notebook

> Persistent memory for the `content-planner` agent.

## Topic cluster map

Maintained as a tree: one pillar per priority service, supporting articles below.

### Pillar: Dental Implants
- Pillar URL: _TBD — confirm `/en/services/dental-implants` and `/th/บริการ/รากฟันเทียม` (or equivalent) with client._
- Supporting articles:
  - EN — "How Much Do Dental Implants Cost in Bangkok? (2026 Guide)" — brief ready, W17 Tue
  - EN — All-on-4 cost & timeline (backlog)
  - EN — Straumann vs. Osstem vs. Hiossen brand comparison (backlog)
  - TH — Thai adaptation of 2026 cost guide (backlog, commission if EN performs)

### Pillar: Invisalign / Clear Aligners
- Pillar URL: _TBD_
- Supporting articles:
  - TH — "Invisalign vs จัดฟันเหล็ก: เลือกแบบไหนดีสำหรับคุณ" — planned, W17 Wed
  - EN — Invisalign treatment timeline for medical tourists (backlog)

### Pillar: Veneers / Cosmetic
- Pillar URL: _TBD_
- Supporting articles:
  - EN — "Porcelain vs Composite Veneers: Which Is Right for You?" — planned, W17 Thu

### Pillar: General Dentistry
- Pillar URL: _TBD_
- Supporting articles:
  - TH — "ขูดหินปูนเจ็บไหม? ใช้เวลานานแค่ไหน และควรทำบ่อยแค่ไหน" — planned, W17 Mon

### Pillar: Orthodontics (Braces)
- Pillar URL: _TBD — service-page refresh W17 Fri (TH)._
- Supporting articles:
  - _TBD_

## Keyword-to-URL registry

> One row per keyword. One URL per keyword. Prevents cannibalization.

| Keyword | Locale | Intent | SERP target | Assigned URL | Status |
|---|---|---|---|---|---|
| dental implants cost bangkok | EN | Commercial-investigation | Featured snippet + AI Overview + PAA | `/en/blog/dental-implants-cost-bangkok-2026` (proposed) | Brief ready |
| ขูดหินปูน เจ็บไหม | TH | Informational | PAA + AI Overview | _TBD_ | Planned |
| invisalign vs จัดฟันเหล็ก | TH | Commercial-investigation | Featured snippet (comparison table) | _TBD_ | Planned |
| porcelain vs composite veneers | EN | Commercial-investigation | Featured snippet + PAA | _TBD_ | Planned |
| จัดฟัน | TH | Commercial | Service page rank | existing TH pillar (refresh) | Planned |

## Editorial calendar index

Quarterly calendars live in `workspace/plans/calendar-YYYY-QN.md`. Weekly calendars by ISO week.

- `/home/user/GEO/workspace/plans/calendar-2026-W17.md` — Week of Apr 20–24, 2026. 5 items, 3 TH / 2 EN, all 5 clusters touched.

## Content-brief index

Briefs live in `workspace/plans/briefs/<slug>.md`.

- `/home/user/GEO/workspace/plans/briefs/dental-implants-cost-bangkok-2026.md` — W17 Tue, EN, Implants cluster. SEO/GEO sections pending expert fill-in.

## Prioritized backlog (top 10)

| Rank | Topic | Cluster | Business value | Search opp. | AI-citation opp. | Effort | Score |
|---|---|---|---|---|---|---|---|
| 1 | Dental Implants Cost Bangkok 2026 (EN) | Implants | 5 | 5 | 5 | 4 (new) | 19 |
| 2 | All-on-4 Cost & Timeline Bangkok (EN) | Implants | 5 | 4 | 5 | 4 | 18 |
| 3 | Invisalign vs Braces (TH) | Invisalign | 4 | 5 | 4 | 3 | 16 |
| 4 | Porcelain vs Composite Veneers (EN) | Veneers | 4 | 4 | 4 | 3 | 15 |
| 5 | Scaling / Cleaning FAQ (TH) | General | 3 | 5 | 4 | 2 (easy) | 14 |
| 6 | Orthodontics pillar refresh (TH) | Ortho | 4 | 4 | 3 | 2 (refresh) | 13 |
| 7 | Dental tourism guide — Thailand vs Turkey vs Mexico (EN) | Implants/tourism | 5 | 3 | 5 | 5 (research-heavy) | — |
| 8 | Invisalign treatment timeline for medical tourists (EN) | Invisalign | 4 | 3 | 4 | 3 | — |
| 9 | Smile design / digital workflow pillar (EN) | Veneers | 4 | 3 | 4 | 4 | — |
| 10 | Wisdom teeth extraction FAQ (TH) | General/surgery | 3 | 5 | 3 | 2 | — |

## Open strategic questions for the user

- [ ] Confirm priority order of service clusters (tentative: Implants > Invisalign > Veneers > General > Ortho).
- [ ] Are we publishing Thai-first and adapting to English, or vice versa, or producing both in parallel? This week uses parallel/balanced approach.
- [ ] Target publish cadence — planner assumed 5/week (1 per weekday). Confirm.
- [ ] Who approves content before publish? (clinical reviewer? marketing lead?)
- [ ] Which implant brands does the clinic actually stock? (blocks implant cost brief finalization)
- [ ] Which clear-aligner brands does the clinic offer? (blocks Invisalign comparison brief)
- [ ] Current live pricing — is there a single canonical pricing page we can link from commercial-investigation content?
- [ ] Is `/blog/` or `/guides/` the canonical path for EN long-form?
- [ ] Do we have doctor profile pages for byline links? (needed for YMYL trust signals)
- [ ] Is an `llms.txt` file already published? (geo-expert to confirm)

## Session log

**2026-04-19 — Week-17 plan produced.**
- Built `calendar-2026-W17.md` (5 items: Mon TH scaling-FAQ, Tue EN implant-cost GEO piece, Wed TH Invisalign-vs-braces, Thu EN veneers comparison, Fri TH orthodontics refresh). Locale 3 TH / 2 EN. Type mix: FAQ / GEO citation / comparison / pillar-supporting / refresh. Intent mix: 2 info, 2 commercial-investigation, 1 commercial.
- Selected Tue EN "Dental Implants Cost Bangkok 2026" as the sample brief for SEO + GEO expert review. Rationale: highest business value (AOV + medical tourism anchor), explicit GEO-citation design, and it stress-tests the brief template for future pieces.
- Brief drafted with SEO + GEO sections left as "PENDING: …" placeholders per instructions.
- Many `<!-- CONFIRM: ... -->` flags left in both deliverables — they must be resolved before content-creator starts drafting.
- Notebook now seeded with cluster map, keyword registry (5 entries), calendar index, brief index, and a top-10 backlog.

_Next sessions: after SEO/GEO reviewer fill-in, re-check brief for internal consistency and release to content-creator. Begin W18 plan once cluster priority is confirmed by client._
