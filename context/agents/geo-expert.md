# GEO Expert — Private Notebook

> Persistent memory for the `geo-expert` agent.

## Standing GEO checklist (per URL)

- [ ] Answer-first lede: first sentence is a complete, standalone answer to the page's question
- [ ] Every entity (procedure, brand, condition) defined inline on first mention
- [ ] At least 3 specific stats or numbers with linked primary sources
- [ ] H2s are question-shaped, phrased how real users type
- [ ] A 40–60 word summary paragraph directly under each H2
- [ ] At least one comparison table where it aids the topic
- [ ] FAQ block with direct Q → A pairing, feeding `FAQPage` schema
- [ ] Author + reviewer + `lastReviewed` date block present
- [ ] Author has credentials; reviewer is a named clinician
- [ ] Citation bait: original data, concrete cost ranges, or myth-vs-fact block
- [ ] No fluff intro before the answer

## AI-crawler access strategy

Default posture (to confirm with client): **allow** major answer-engine crawlers since we *want* AI visibility for a dental clinic.

| Bot | Owner | Default | Notes |
|---|---|---|---|
| `GPTBot` | OpenAI training | allow | |
| `OAI-SearchBot` | OpenAI search | allow | |
| `ChatGPT-User` | ChatGPT on-demand fetch | allow | |
| `PerplexityBot` | Perplexity index | allow | |
| `Perplexity-User` | Perplexity on-demand fetch | allow | |
| `Google-Extended` | Gemini / AI Overviews training | allow | |
| `anthropic-ai` / `ClaudeBot` | Anthropic | allow | |
| `Applebot-Extended` | Apple Intelligence | allow | |
| `CCBot` | Common Crawl | allow | |
| `Bytespider` | ByteDance | review | known aggressive crawl |

## llms.txt plan

- [ ] Publish `/llms.txt` at root with: one-line site description, language versions, primary-service URLs, author/clinic identity, contact
- [ ] Consider `/llms-full.txt` condensing top 20 pages into LLM-friendly markdown
- [ ] Link from `humans.txt` and `robots.txt` comment

## Tracked AI-query list

> The questions we want to be cited for. Snapshot monthly.

| Query | Locale | Cluster | Current cited source(s) | thedent cited? | URL | Last check |
|---|---|---|---|---|---|---|

_Seed queries to add once clusters are confirmed:_
- "Best dental implant clinic in Bangkok"
- "How much do veneers cost in Thailand?"
- "Invisalign vs braces Thailand"
- "Is dental tourism in Bangkok safe?"
- "How long do dental implants last?"

## Entity footprint register

| Entity | Present on | Schema type | `sameAs` links | Status |
|---|---|---|---|---|
| The Dent (organization) | site-wide | Organization | _TBD_ | |
| Each branch | branch page | Dentist / MedicalClinic | _TBD_ | |
| Each named doctor | profile page | Person | _TBD_ | |

## Citation wins

_Log every confirmed citation: engine, query, date, URL cited, snippet quoted._

- _TBD_

## Original-data pipeline

Ideas for proprietary data the clinic could publish (turns us into a primary source LLMs reference):

- Aggregated price ranges from our own treatment quotes (anonymized)
- Patient-satisfaction mini-surveys per service
- Recovery-time distributions from our own records
- Before/after archive with consented patients (compliance permitting)

## Audit report index

Reports live in `workspace/geo-audits/YYYY-MM-DD-<scope>.md`.

- _TBD_

## Session log

_Date — what was audited, citation deltas, what was handed off to whom._
