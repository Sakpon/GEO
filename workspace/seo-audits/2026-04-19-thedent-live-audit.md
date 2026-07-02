# Live SEO Audit — thedent.co.th — 2026-04-19

## Sources fetched

- `GET https://thedent.co.th/` — HTTP/2 **403 Forbidden**, response header `x-deny-reason: host_not_allowed`, body 21 bytes (`text/plain`)
- `GET https://www.thedent.co.th/` — HTTP/2 **403**, same `x-deny-reason: host_not_allowed`
- `GET https://thedent.co.th/robots.txt` — HTTP/2 **403**, same deny reason
- `GET https://thedent.co.th/sitemap.xml` — HTTP/2 **403**, same deny reason
- Tested with three User-Agents: desktop Chrome (Win + macOS), and `Googlebot/2.1 (+http://www.google.com/bot.html)` — all 403
- DNS resolves to `210.246.201.242` (Thai hosting block); request did reach the origin and was rejected with a *content-bearing* deny header, not a network failure

**Conclusion of fetch step: no HTML, no head, no schema, no headings, no nav, no NAP, no sitemap, no robots directives could be retrieved.** The audit below pivots to what these signals themselves tell us.

## Snapshot

- **Title tag** — not observed in fetched HTML (server returned 403)
- **Meta description** — not observed in fetched HTML
- **Canonical** — not observed in fetched HTML
- **hreflang TH↔EN** — not observed in fetched HTML
- **Robots / indexability signals** — `robots.txt` itself returns 403. This means crawlers receive no Allow/Disallow guidance and likely cannot fetch any page either. If Googlebot is being treated like our test clients, the site is effectively **uncrawlable**.
- **Schema.org types detected** — not observed
- **H1** — not observed
- **H2/H3 hierarchy quality** — not observed
- **Navigation IA** — not observed (cannot enumerate services / location pages / content hub)
- **Internal link density** — not observed
- **Mobile / Core Web Vitals signals** — cannot be measured; PageSpeed Insights/Lighthouse will also fail against a 403 origin
- **Language switcher mechanics** — not observed
- **NAP visibility (Local SEO)** — not observed in HTML; needs verification against Google Business Profile separately
- **Sitemap / robots posture** — both blocked at HTTP layer with `x-deny-reason: host_not_allowed`. This header pattern is characteristic of an origin-side allowlist (host header or IP allowlist), not a standard WAF challenge. There was no JS challenge, no captcha, no 429 — straight 403.

## Top issues by priority

### P0 — must fix
1. **Site is returning HTTP 403 to unauthenticated external clients including Googlebot UA.** Header `x-deny-reason: host_not_allowed` indicates the origin (or a reverse proxy in front of it) has a host/IP allowlist that rejects general traffic. If Googlebot's crawl IPs are not on the allowlist, **the site will be deindexed or never indexed**. Verify immediately:
   - Search Console → URL Inspection → Test Live URL on `https://thedent.co.th/`. If it shows "Page fetch: Failed" or "Blocked due to access forbidden (403)", this is the same issue.
   - Search Console → Crawl Stats → look for spike in 403 responses.
   - Search Console → Pages report → look for "Blocked due to access forbidden (403)".
2. **`robots.txt` is unreachable (403).** Per Google's docs, a 403 on robots.txt is treated as "robots.txt unreachable" — if this persists >30 days, Google may slow or stop crawling the site entirely. Robots.txt MUST return 200 or 404, never 403/5xx.
3. **`sitemap.xml` is unreachable (403).** No sitemap = no discovery hint for new/updated URLs. Same fix as #2.
4. **Diagnose the origin policy.** Likely causes, in descending probability: (a) reverse-proxy `host_not_allowed` rule expecting a specific `Host:` header value that excludes the public hostname; (b) staging-style IP allowlist accidentally enabled on production; (c) a CDN / origin shield rule that whitelists only the CDN's egress IPs but DNS is now pointed direct-to-origin. Hosting/devops should check the web server (nginx/Apache) `server_name`/`allowed_hosts` config and any reverse proxy rules.

### P1 — high impact
1. Once the 403 is lifted, immediately re-submit `robots.txt` and `sitemap.xml` in Search Console and **request indexing** for the homepage and top 10 service pages.
2. Audit any third-party monitors (UptimeRobot, Pingdom) — they have likely been alerting on the same 403, and if they're allowlisted, this issue may have existed silently for weeks/months.
3. Add a synthetic Googlebot-UA probe to monitoring (curl with Googlebot UA from an external IP) to catch regressions early.
4. Once HTML is accessible, run the full on-page + schema audit — none of which can be done today.

### P2 — improvements
1. After remediation, log full response headers to confirm `Cache-Control`, `Server`, `Strict-Transport-Security`, and absence of `X-Robots-Tag: noindex` leakage.
2. Set up a recurring (weekly) automated audit that fetches with both Googlebot UA and a regular browser UA and diffs the responses — many sites cloak unintentionally.

## Quick wins (≤1 day each)

- Remove the `host_not_allowed` rule from the web server / reverse proxy config (most likely a one-line nginx `server_name`/`allow` change, or a Cloudflare WAF rule).
- Make `robots.txt` return 200 even before the rest of the site is fixed (it can be served as a static file outside the gated path).
- Make `sitemap.xml` return 200 once robots.txt is open.
- File a "Request indexing" in GSC for the homepage the moment crawl is restored.

## What's already good

- HTTPS is configured (HTTP/2 negotiates successfully, TLS handshake completes).
- DNS resolves cleanly to a single A record (`210.246.201.242`); no NXDOMAIN or split-horizon weirdness.
- The deny is fast and clean (no hang, no half-open connections) — so once the rule is corrected, recovery should be immediate.
- The server is returning a structured, debuggable header (`x-deny-reason: host_not_allowed`) rather than a generic 403 — that's actually helpful for diagnosis.
