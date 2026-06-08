# AIO Citation Probe

Measures how often **Google's AI Overview (AIO)** appears for high-intent dental
queries and how often **thedent.co.th** is cited in it — run each prompt N times
and report the **% of runs with an AIO** and the **% where The Dent is cited**,
with confidence intervals and week-over-week trends.

Data source: **SerpApi** (`google` + `google_ai_overview` engines),
queried with a **Thailand** locale (`location=Thailand, gl=th,
google_domain=google.co.th`) in Thai and English.

## Setup

```bash
pip install -r experiments/requirements.txt
export SERPAPI_API_KEY="your-key"      # required
```

Google AIO can't be read by a normal API, so SerpApi (or a similar SERP API) is
required. SerpApi's free plan (~100–250 searches/mo) covers a smoke test; the
full weekly cadence fits the $25/mo Starter (1,000 searches) thanks to the cost
optimizations below.

## Run from the CLI

```bash
cd experiments
python aio_citation_probe.py --smoke            # 1 prompt, 1 run (cheap sanity check)
python aio_citation_probe.py --tier core        # weekly core set
python aio_citation_probe.py                     # all prompts (asks to confirm cost)
python aio_citation_probe.py --tier full --n-runs 20 --yes   # monthly deep-dive
```

Outputs per run:
- `workspace/geo-audits/<date>-aio-citation-probe.xlsx` — primary Excel report
  (Summary · By prompt · Competitor SoV · Raw runs · Weekly trend)
- `workspace/geo-audits/<date>-aio-citation-probe.md` — condensed markdown
- `experiments/results/<date>-raw.jsonl` — per-run evidence
- `experiments/results/history.jsonl` — append-only log powering the trend view

## Run the web app (enter prompts → run → download)

```bash
cd experiments
SERPAPI_API_KEY=... python webapp.py      # http://localhost:8000  (PORT to change)
```

Behind **HTTP Basic Auth**. Credentials from env, defaulting to
`thedent` / `admin2026`:

```bash
export BASIC_AUTH_USERNAME=thedent
export BASIC_AUTH_PASSWORD=change-me
```

> **Security:** Basic Auth is unencrypted without HTTPS and the default password
> is weak — change `BASIC_AUTH_PASSWORD` before exposing this anywhere real.

The UI is mobile-first/responsive: enter prompts (one per line, optional
`| en` / `| th`), confirm the cost estimate, run as a background job with live
progress, view `/trends`, and download the Excel/Markdown.

## prompts.json

Single source of truth for the prompt set (max **30** prompts) and run knobs:

| key | meaning |
|---|---|
| `n_runs` | cap on runs per prompt |
| `min_runs` | floor before early-stopping can trigger |
| `ci_halfwidth_target` | stop a prompt once the 95% CI half-width ≤ this |
| `monthly_call_budget` | hard guard — runs that would exceed it are trimmed/skipped |
| `throttle_seconds` | delay between runs |
| `target_domain` | the domain we're checking for (thedent.co.th) |
| `defaults` | locale params applied to every prompt |
| `prompts[]` | `id`, `q`, `hl` (`en`/`th`), `tier` (`core`/`full`) |

> Thai prompt strings are first-draft and must be reviewed by a native speaker
> before relying on them (per `CLAUDE.md`).

## Cost optimization (built in)

- **Adaptive early-stopping** — stop once the citation-rate CI is tight enough.
- **2nd-call short-circuit** — only call `google_ai_overview` when AIO content
  isn't already inline and a `page_token` exists.
- **Tiered cadence** — `core` weekly (n_runs=10), `full` monthly (n_runs=20).
- **Hard `monthly_call_budget`** — never exceed your plan tier.

## Weekly automation

`.github/workflows/aio-weekly.yml` runs the `core` tier weekly (and `full` on
the 1st of the month) and commits the report + history. Add `SERPAPI_API_KEY`
as a GitHub Actions repository secret and ensure Actions can push to the branch.

## Deploying the web app to a public URL (e.g. audit.martics.co)

The web app is a Flask service, so it needs a host that can run Python/Docker.
A `Dockerfile`, `docker-compose.yml`, and `Caddyfile` (auto-HTTPS) are in the
repo root for a one-command deploy on any server with Docker.

On a server (VPS/VM) with Docker installed and ports 80 + 443 open:

1. **DNS:** add an `A` record `audit.martics.co` → the server's public IP.
   (If you prefer a CNAME to another host, point it there instead.)
2. **Run it:**
   ```bash
   git clone https://github.com/Sakpon/GEO.git && cd GEO
   git checkout claude/aio-summary-experiments-GJubb
   export SERPAPI_API_KEY=your_serpapi_key
   export BASIC_AUTH_PASSWORD=a_strong_password   # username defaults to "thedent"
   docker compose up -d --build
   ```
   Caddy automatically provisions a Let's Encrypt certificate, so the app is live
   at **https://audit.martics.co** within ~1 minute.

Notes:
- Edit the hostname in `Caddyfile` if you want a different subdomain.
- Reports and trend history persist in Docker named volumes across restarts.
- The container runs gunicorn with **one worker** on purpose — job progress is
  tracked in memory, so multiple workers wouldn't share job state.
- If `martics.co` is on shared hosting / WordPress / a static host that can't run
  Python, run this container on a small separate VPS and just point the
  `audit.martics.co` subdomain at that VPS.

## Accuracy

- Citation detection is deterministic (linked references only — not unlinked
  brand mentions in the AI prose).
- Rates carry **95% Wilson CIs**; weekly deltas inside the CI are flagged as
  noise.
- SerpApi is a de-personalized, country-level (Thailand) datacenter view — trust
  **trend direction + competitor share-of-voice** over the absolute %.
