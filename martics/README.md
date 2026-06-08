# martics · GEO Citation Tracker — MVP (Phases 0–2)

Thai-native **AI Share-of-Voice** + **URL-citation** tracker for brands being
discovered through AI answer engines (ChatGPT / Google AI Overview / Perplexity)
instead of Google blue links. Built on Cloudflare. First design partner:
[thedent.co.th](https://thedent.co.th).

This repo currently implements the **core pipeline (build-spec Phases 0–2)**:

| Phase | Status | What's here |
|---|---|---|
| **0 — Scaffold** | ✅ | D1 schema + migrations, Worker + Pages-style API, KV config var, Vite/React/Tailwind SPA |
| **1 — Pipeline proof (Perplexity)** | ✅ | `POST /api/run` → N rounds/prompt → Claude Sonnet parser → `runs` |
| **2 — Metrics + Dashboard** | ✅ | Aggregator → `metrics_daily` (SoV, citation rate, competitor SoV) → React dashboard w/ time-series |
| 3 — Google AIO engine | 🟫 stub | `engines/googleAio.ts` returns `engine_not_implemented` |
| 4 — ChatGPT engine | 🟫 stub | `engines/chatgpt.ts` returns `engine_not_implemented` |
| 5 — Fix-loop | 🟫 stub | `POST /api/fix` → 501 |
| 6 — White-label report | 🟫 stub | `GET /api/report/:brandId` → report-ready JSON payload |

> **Do not sell a Perplexity-only build.** Perplexity is the Phase-1 scaffold to
> prove the pipeline; Thai usage is low. The real-usage engines (Google AIO,
> ChatGPT) are Phase 3–4 and must ship before this goes to a paying client.

## Measurement model (spec §6)

AI answers are non-deterministic, so we **never measure binary**. Per
`prompt × engine × day` we fire `RUNS_PER_CYCLE` (default 5) rounds and compute
probabilities:

- **SoV** = rounds the brand was mentioned / N
- **Citation Rate** = rounds a brand **URL** was cited / N _(tracked separately from SoV)_
- **Avg Position** = mean ordinal of the brand among mentioned brands (1 = first)
- **Competitor SoV** = same, per competitor, matching Thai/English **aliases**

Metric math lives in `src/worker/metrics.ts` (pure, unit-tested in `tests/`).

## Architecture note — Worker, not Pages

The spec lists "Pages Functions", but Cloudflare **Pages has no cron**, and a
daily cron is a P0 requirement. This module is therefore a single **Cloudflare
Worker** that (a) serves the React SPA via the [Static Assets] binding, (b)
routes `/api/*` with [Hono], and (c) runs the daily cycle in a `scheduled`
handler. Same bindings the spec calls for (D1, KV), one deployable, cron
included.

```
Cron (daily 03:00 UTC) ─┐
POST /api/run ──────────┼─▶ runner: N rounds × engine ─▶ Perplexity API
                        │        └─▶ parser (Claude Sonnet, structured output) ─▶ runs (D1)
                        └─▶ aggregator ─▶ metrics_daily (D1)
GET /api/dashboard ─────────────────────▶ dashboard read-model ─▶ React SPA
```

## Layout

```
migrations/0001_init.sql     D1 schema (spec §8 + runs.status/error)
seeds/thedent.sql            sample brand + Thai prompts
src/worker/
  index.ts                   Worker entry: Hono fetch + scheduled() cron
  api.ts                     /api routes (spec §9)
  runner.ts                  N-round runner, per-run failure isolation
  parser.ts                  Claude Sonnet parser (structured outputs)
  aggregator.ts              writes metrics_daily
  metrics.ts                 pure SoV / citation / competitor math (tested)
  dashboard.ts               dashboard read-model
  engines/                   perplexity (live) + google_aio, chatgpt (stubs)
src/frontend/                Vite + React + Tailwind dashboard
tests/metrics.test.ts        acceptance-criteria unit tests
```

## API (spec §9)

| Method | Path | Notes |
|---|---|---|
| POST | `/api/brands` | create brand (+ client) with aliases & competitors |
| GET  | `/api/brands` | list brands |
| POST | `/api/prompts` | bulk-add Thai prompts (`{brand_id, prompts:[{text_th,intent}]}`) |
| GET  | `/api/prompts?brand_id=` | list prompts |
| POST | `/api/run` | run active prompts × active engines, then aggregate today |
| GET  | `/api/dashboard?brand_id=` | metrics + time-series + competitors + per-prompt |
| POST | `/api/fix` | 501 (Phase 5) |
| GET  | `/api/report/:brandId` | report-ready payload (Phase 6 PDF pending) |
| GET  | `/api/engines` | registered vs active engines |

## Local setup

```bash
cd martics
npm install

# 1. Create bindings, paste the IDs into wrangler.toml
wrangler d1 create martics
wrangler kv namespace create CONFIG

# 2. Migrate + seed (local)
npm run db:migrate:local
npm run db:seed:local

# 3. Secrets for local dev
cp .dev.vars.example .dev.vars   # fill in ANTHROPIC_API_KEY + PERPLEXITY_API_KEY

# 4. Build the SPA and run the Worker (serves API + UI on :8787)
npm run dev
```

For UI-only hot reload: `npm run dev:ui` (proxies `/api` to a separate
`wrangler dev`).

### Verify

```bash
npm run typecheck
npm test        # metric acceptance-criteria tests
```

## Config

- `RUNS_PER_CYCLE` (var) — N rounds per prompt×engine. Default 5.
- `ACTIVE_ENGINES` (var) — comma list the cron + `/api/run` execute. Default `perplexity`.
- `PARSER_MODEL` (var) — Claude model for the parser. Default `claude-sonnet-4-6`.
- Secrets: `ANTHROPIC_API_KEY`, `PERPLEXITY_API_KEY` (`wrangler secret put …`).

## Deploy

```bash
npm run deploy            # vite build + wrangler deploy
npm run db:migrate:remote
```

[Hono]: https://hono.dev
[Static Assets]: https://developers.cloudflare.com/workers/static-assets/
