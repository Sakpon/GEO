// Cloudflare Pages Function: POST /api/aio
// Runs one Google AI Overview probe via SerpApi (server-side, so the API key
// stays secret) and reports whether thedent.co.th is cited.
//
// Body: { q: string, hl?: "en"|"th", gl?, location?, google_domain? }
// Requires the SERPAPI_API_KEY environment variable / secret on the Pages project.

const TARGET = "thedent.co.th";

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

function host(value) {
  if (!value) return "";
  let v = value.trim();
  if (!v.includes("//")) v = "//" + v;
  try {
    let h = new URL(v).hostname.toLowerCase();
    return h.startsWith("www.") ? h.slice(4) : h;
  } catch {
    return "";
  }
}

function refsToDomains(aio) {
  const refs = (aio && aio.references) || [];
  const set = new Set();
  for (const r of refs) {
    const h = host(r.link || r.url || r.source || "");
    if (h) set.add(h);
  }
  return [...set];
}

async function serpapi(params, key) {
  const u = new URL("https://serpapi.com/search");
  for (const [k, v] of Object.entries(params)) u.searchParams.set(k, v);
  u.searchParams.set("api_key", key);
  const r = await fetch(u.toString());
  return r;
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const key = env.SERPAPI_API_KEY;
  if (!key) return json({ error: "SERPAPI_API_KEY is not configured" }, 500);

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "invalid JSON body" }, 400);
  }
  const q = (body.q || "").trim();
  if (!q) return json({ error: "missing 'q'" }, 400);

  const params = {
    engine: "google",
    q,
    location: body.location || "Thailand",
    gl: body.gl || "th",
    hl: body.hl || "en",
    google_domain: body.google_domain || "google.co.th",
    no_cache: "true",
  };

  let calls = 0;
  let r1;
  try {
    r1 = await serpapi(params, key);
  } catch (e) {
    return json({ error: "network_error", calls }, 502);
  }
  calls++;
  if (!r1.ok) {
    let msg = `HTTP ${r1.status}`;
    try { msg += ": " + ((await r1.json()).error || ""); } catch {}
    return json({ error: msg, calls }, 200);
  }
  const d1 = await r1.json();
  const aio = d1.ai_overview || {};
  const hasInline = Array.isArray(aio.text_blocks) && aio.text_blocks.length > 0;
  const pageToken = aio.page_token;
  const aioPresent = hasInline || !!pageToken;
  let domains = hasInline ? refsToDomains(aio) : [];

  // Second call only when content isn't inline but a token exists.
  if (!hasInline && pageToken) {
    try {
      const r2 = await serpapi({ engine: "google_ai_overview", page_token: pageToken }, key);
      calls++;
      if (r2.ok) domains = refsToDomains((await r2.json()).ai_overview || {});
    } catch { /* leave domains empty */ }
  }

  const thedent = domains.some((h) => h === TARGET || h.endsWith("." + TARGET));
  return json({ aio_present: aioPresent, thedent_cited: thedent, domains, calls });
}
