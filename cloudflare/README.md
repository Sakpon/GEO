# AIO Citation Audit — Cloudflare Pages edition

A self-contained audit page you can drop into any repo deployed on **Cloudflare
Pages**. It measures how often Google's AI Overview cites **thedent.co.th** and
shows competitor share-of-voice, with Excel/CSV export — all behind a login.

## What's in here

```
cloudflare/
├── index.html                 # the audit UI (single static file; Excel export via SheetJS CDN)
└── functions/
    ├── _middleware.js         # HTTP Basic Auth gate for the whole project
    └── api/aio.js             # server-side SerpApi probe (keeps the API key secret)
```

Why the function? A pure HTML file can't call SerpApi safely — the key would be
exposed in the browser and SerpApi blocks browser CORS. The Pages Function runs
the call at the edge with the key kept as a Cloudflare secret.

## Import into your Cloudflare repo

1. **Copy the files** into the repo that serves your Cloudflare site:
   - Put `index.html` where you want the page (site root → `https://yourdomain/`,
     or e.g. `audit/index.html` → `https://yourdomain/audit/`).
   - Copy the **`functions/`** folder to the **repo root** (Cloudflare Pages
     requires it at the project root; `functions/api/aio.js` becomes the
     `/api/aio` endpoint, and `_middleware.js` gates everything).

2. **Set environment variables** on the Pages project
   (Cloudflare dashboard → your Pages project → Settings → Environment variables):
   - `SERPAPI_API_KEY` — your SerpApi key (mark it as a **secret**).
   - `BASIC_AUTH_USERNAME` — optional, defaults to `thedent`.
   - `BASIC_AUTH_PASSWORD` — **set a strong value** (default is `admin2026`).

3. **Deploy** — push to the repo (or run `wrangler pages deploy`). Cloudflare
   builds and serves it on your existing domain. Visit the page, log in, run an
   audit, download the Excel.

> If you already have a `functions/` folder in that repo, just merge these files
> in (rename `aio.js`/its path if `/api/aio` is taken). The `_middleware.js`
> gates the **whole** project — if you only want to protect this page, move the
> auth check into `functions/api/aio.js` and a small inline check on the page
> instead, or use **Cloudflare Access** on just the audit path.

## Local preview (optional)

```bash
npm i -g wrangler
cd cloudflare
SERPAPI_API_KEY=your_key wrangler pages dev .
```

## Notes & limits

- **Stateless:** this edition runs synchronously in the browser and has **no
  week-over-week trend storage** (that lives in the Python tool in `experiments/`,
  which persists `history.jsonl`). If you want trends here too, store results in
  Cloudflare KV/D1 from the function — ask and I'll add it.
- **Locale:** queries run as `location=Thailand, gl=th, google_domain=google.co.th`.
- **Accuracy:** counts linked AIO references only; de-personalized country-level
  view — trust trend direction and competitor share-of-voice over the absolute %.
- **Thai prompts** are first-draft — have a native speaker review them.
- **Cost:** each prompt-run is 1–2 SerpApi calls; the page shows a worst-case
  estimate and requires a confirm before running.
