# AIO Citation Audit — Build Reference (Cloudflare Pages)

> Single-file reference for rebuilding the **Google AI Overview (AIO) citation
> audit page** in another repository deployed on **Cloudflare Pages**. Copy the
> code blocks below into the indicated paths, set the environment variables, and
> deploy. This document is self-contained — no other files are required.

---

## 1. What it does

A small web app that measures **how often Google's AI Overview cites a target
domain** (default `thedent.co.th`) for a list of high-intent search prompts, and
which competitors get cited instead.

- Enter up to 30 prompts (one per line; `| en` or `| th` sets the language).
- For each prompt it runs N samples against Google AIO and reports:
  - **AIO trigger rate** — % of runs where an AI Overview appeared.
  - **Target citation rate** — % of runs where the target domain was cited,
    with a 95% Wilson confidence interval.
  - **Competitor share-of-voice** — every other cited domain, tallied.
- Exports results to **Excel** (SheetJS) and **CSV**.
- The whole project sits behind **HTTP Basic Auth** at the edge.

## 2. Architecture

```
repo-root/
├── index.html                 # static UI (place anywhere; root => https://domain/)
└── functions/                 # MUST be at the repo root for Cloudflare Pages
    ├── _middleware.js          # Basic Auth gate for the whole project
    └── api/aio.js              # POST /api/aio  -> server-side SerpApi probe
```

**Why a serverless function (not a pure HTML file)?** Google AIO can't be read
by a normal API, so the app uses **SerpApi**. Calling SerpApi from the browser
would (a) expose the API key and (b) fail CORS. The Cloudflare Pages Function
calls SerpApi at the edge with the key kept as a project **secret**, and returns
only the parsed result to the page.

## 3. Data source & key implementation notes

These are the non-obvious details that make it work — keep them if you rewrite it:

- **Provider:** SerpApi. Two engines:
  - `engine=google` for the search (NOT `google_search` — that returns HTTP 400).
  - `engine=google_ai_overview` for the follow-up fetch.
- **Two-step AIO flow:** the first `google` response may contain the AI Overview
  inline (`ai_overview.text_blocks`), OR only a short-lived `ai_overview.page_token`
  (expires ~1 min). If only a token is present, immediately make a second call to
  `engine=google_ai_overview&page_token=...` to get `ai_overview.references`.
  Skip the second call when content is already inline (saves an API credit).
- **AIO present?** True if `text_blocks` exist OR a `page_token` is present.
- **Citation check:** collect hostnames from `ai_overview.references[].link`
  (fallback `url`/`source`), strip `www.`, and match the target domain or any
  subdomain of it. Counts **linked references only** — not unlinked brand
  mentions in the AI prose.
- **Locale (critical for a Thailand business):** query as
  `location=Thailand`, `gl=th`, `google_domain=google.co.th`. Set `no_cache=true`
  so each run is a fresh sample (AIO is stochastic).
- **Stats:** report rates with a 95% **Wilson** score interval (good for small N
  proportions). Treat week-over-week deltas inside the CI as noise.
- **Cost:** each prompt-run is 1–2 SerpApi calls. Show a worst-case estimate
  (`prompts × runs × 2`) and require a confirm before running.

## 4. Environment variables (set on the Cloudflare Pages project)

| Variable | Required | Default | Notes |
|---|---|---|---|
| `SERPAPI_API_KEY` | yes | — | Mark as a **secret**. |
| `BASIC_AUTH_USERNAME` | no | `thedent` | Login user. |
| `BASIC_AUTH_PASSWORD` | no | `admin2026` | **Change before going live.** Basic Auth is unencrypted without HTTPS (Cloudflare provides HTTPS). |

## 5. Deploy / import steps

1. Copy `index.html` into the target repo (root → served at `/`, or `audit/index.html` → `/audit/`).
2. Copy the **`functions/` folder to the repo root** (Pages requires it there).
   - `functions/api/aio.js` → endpoint `/api/aio`.
   - `functions/_middleware.js` → gates the whole project.
3. In Cloudflare dashboard → Pages project → Settings → Environment variables,
   add the variables from section 4.
4. Push / `wrangler pages deploy` → live on the existing domain.
5. Local preview: `SERPAPI_API_KEY=... wrangler pages dev .`

> If `/api/aio` or `functions/` already exist in that repo, merge/rename rather
> than overwrite. To protect only this page (not the whole site), drop
> `_middleware.js` and use **Cloudflare Access** on the audit path instead.

## 6. Limits

- **Stateless** — no week-over-week trend storage here. To add trends, persist
  each run's aggregates to **Cloudflare KV or D1** from `api/aio.js` (or a new
  `api/save` function) and render history on the page.
- **Approximation** — SerpApi is a de-personalized, country-level (Thailand)
  datacenter view, not a specific logged-in user. Trust **trend direction +
  competitor share-of-voice** over the absolute %.
- **Thai prompts** should be reviewed by a native speaker.

---

## 7. Source code

### `index.html`

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Dent · AIO Citation Audit</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
<style>
  :root{--teal:#0f766e;--teal-d:#0b5650;--ink:#1f2937;--muted:#6b7280;
        --line:#e5e7eb;--bg:#f8fafc;--green:#dcfce7;--red:#fee2e2;--r:10px}
  *{box-sizing:border-box}
  body{margin:0;font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
       color:var(--ink);background:var(--bg)}
  .top{display:flex;justify-content:space-between;align-items:center;gap:12px;
       padding:12px 16px;background:var(--teal);color:#fff;position:sticky;top:0;z-index:5}
  .top b{font-weight:700}
  .wrap{max-width:920px;margin:0 auto;padding:16px}
  h1{font-size:1.4rem;margin:.4em 0}h2{font-size:1.1rem;margin-top:1.4em}
  .muted{color:var(--muted);font-size:.9rem}.err{color:#b91c1c}
  code{background:#eef2ff;padding:1px 5px;border-radius:4px;font-size:.85em}
  .card{background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:16px;margin:14px 0}
  label{display:block;font-weight:600;margin:10px 0 4px}
  textarea,input[type=number]{width:100%;padding:12px;font-size:16px;border:1px solid var(--line);
       border-radius:8px;font-family:inherit}
  textarea{resize:vertical;min-height:150px}
  .grid2{display:grid;grid-template-columns:1fr;gap:12px}
  .est{display:block;padding:12px;background:#f1f5f9;border-radius:8px}
  .chk{display:flex;align-items:center;gap:8px;font-weight:400;margin:14px 0}
  .chk input{width:20px;height:20px}
  .btn{display:inline-block;padding:12px 18px;min-height:44px;border-radius:8px;border:1px solid var(--teal);
       color:var(--teal);background:#fff;font-weight:600;cursor:pointer;text-align:center}
  .btn.primary{background:var(--teal);color:#fff}.btn.primary:hover{background:var(--teal-d)}
  .btn:disabled{opacity:.5;cursor:not-allowed}
  .bar{background:var(--line);border-radius:999px;height:12px;overflow:hidden;margin:10px 0}
  .bar>i{display:block;background:var(--teal);height:100%;width:0;transition:width .3s}
  .scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--line);border-radius:var(--r)}
  table{width:100%;border-collapse:collapse;font-size:.9rem}
  th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
  thead th{background:var(--teal);color:#fff}
  td.hit{background:var(--green);font-weight:700}td.miss{background:var(--red)}
  .foot{color:var(--muted);font-size:.8rem;text-align:center;padding:24px 16px}
  .actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
  @media(min-width:620px){.grid2{grid-template-columns:1fr 1fr}h1{font-size:1.7rem}}
</style>
</head>
<body>
<header class="top"><b>The Dent · AIO Audit</b><span class="muted" style="color:#d1faf5">Cloudflare edition</span></header>
<main class="wrap">
  <h1>Run an AIO citation audit</h1>
  <p class="muted">Measures how often Google's AI Overview cites
    <strong>thedent.co.th</strong> for each prompt (Thailand locale). One prompt
    per line; add <code>| en</code> or <code>| th</code> to set the language.</p>

  <div class="card">
    <label for="prompts">Prompts</label>
    <textarea id="prompts">Best dental implant clinic in Bangkok | en
คลินิกรากฟันเทียมที่ดีที่สุดในกรุงเทพ | th
How much do veneers cost in Thailand? | en
Invisalign vs braces Thailand | en
Is dental tourism in Bangkok safe? | en</textarea>
    <p class="muted" id="count"></p>
    <div class="grid2">
      <div><label for="nruns">Runs per prompt</label>
        <input id="nruns" type="number" inputmode="numeric" min="1" max="30" value="3"></div>
      <div><label>Estimated max API calls</label><output id="est" class="est">—</output></div>
    </div>
    <label class="chk"><input type="checkbox" id="confirm"> I understand this spends SerpApi credits.</label>
    <div class="actions"><button id="run" class="btn primary">Run audit</button></div>
  </div>

  <div id="progress" class="card" style="display:none">
    <p id="plabel">Working…</p><div class="bar"><i id="pfill"></i></div>
  </div>

  <div id="results" style="display:none">
    <h2>Results</h2>
    <p id="overall" class="muted"></p>
    <div class="scroll"><table id="ptable">
      <thead><tr><th>Prompt</th><th>Lang</th><th>Runs</th><th>AIO rate</th>
        <th>The Dent rate (95% CI)</th><th>Top cited domains</th></tr></thead>
      <tbody></tbody></table></div>
    <h2>Competitor share of voice</h2>
    <div class="scroll"><table id="ctable">
      <thead><tr><th>Domain</th><th>Times cited</th><th>Is The Dent?</th></tr></thead>
      <tbody></tbody></table></div>
    <div class="actions">
      <button id="xlsx" class="btn primary">Download Excel</button>
      <button id="csv" class="btn">Download CSV</button>
    </div>
  </div>
</main>
<footer class="foot">De-personalized Thailand datacenter view via SerpApi · trust trends over absolute %</footer>

<script>
const $=s=>document.querySelector(s), TARGET="thedent.co.th";
function parsePrompts(t){
  return t.split("\n").map(l=>l.trim()).filter(Boolean).map((l,i)=>{
    let hl="en",q=l;
    if(l.includes("|")){const p=l.split("|");const tail=p[p.length-1].trim().toLowerCase();
      if(tail==="en"||tail==="th"){hl=tail;q=p.slice(0,-1).join("|").trim();}}
    return {id:`p${i+1}-${hl}`,q,hl};});
}
function wilson(s,n){if(!n)return[0,1];const z=1.96,p=s/n,d=1+z*z/n;
  const c=(p+z*z/(2*n))/d,m=z*Math.sqrt((p*(1-p)+z*z/(4*n))/n)/d;
  return[Math.max(0,c-m),Math.min(1,c+m)];}
const pct=x=>Math.round(x*100)+"%";
function update(){
  const lines=$("#prompts").value.split("\n").map(s=>s.trim()).filter(Boolean);
  const n=Math.max(1,parseInt($("#nruns").value||"1",10));
  $("#est").textContent=(lines.length*n*2)+" (worst case)";
  $("#count").textContent=lines.length+" / 30 prompts";
  $("#count").className=lines.length>30?"muted err":"muted";
}
$("#prompts").addEventListener("input",update);$("#nruns").addEventListener("input",update);update();

let LAST=null;
async function runOne(p){
  const r=await fetch("/api/aio",{method:"POST",headers:{"content-type":"application/json"},
    body:JSON.stringify({q:p.q,hl:p.hl})});
  if(!r.ok)throw new Error("API "+r.status);
  return r.json();
}
$("#run").addEventListener("click",async()=>{
  if(!$("#confirm").checked){alert("Please confirm the cost first.");return;}
  const prompts=parsePrompts($("#prompts").value);
  if(!prompts.length){alert("Enter at least one prompt.");return;}
  if(prompts.length>30){alert("Max 30 prompts.");return;}
  const nruns=Math.max(1,Math.min(30,parseInt($("#nruns").value||"1",10)));
  $("#run").disabled=true;$("#results").style.display="none";$("#progress").style.display="block";
  const total=prompts.length*nruns;let done=0,calls=0;
  const rows=[],comp={};
  for(const p of prompts){
    let aio=0,td=0,runs=0;const doms={};
    for(let i=0;i<nruns;i++){
      $("#plabel").textContent=`${p.id} — run ${i+1}/${nruns}`;
      try{const res=await runOne(p);calls+=res.calls||0;runs++;
        if(res.aio_present){aio++;(res.domains||[]).forEach(d=>{doms[d]=(doms[d]||0)+1;comp[d]=(comp[d]||0)+1;});}
        if(res.thedent_cited)td++;
      }catch(e){runs++;}
      done++;$("#pfill").style.width=(100*done/total)+"%";
    }
    const ci=wilson(td,runs),top=Object.entries(doms).sort((a,b)=>b[1]-a[1]).slice(0,3);
    rows.push({...p,runs,aio,td,aioRate:aio/runs,tdRate:td/runs,ci,top});
  }
  LAST={rows,comp,calls,nruns,date:new Date().toISOString().slice(0,10)};
  render(LAST);
  $("#progress").style.display="none";$("#run").disabled=false;
});

function render(d){
  const tb=$("#ptable tbody");tb.innerHTML="";
  let R=0,A=0,T=0;
  d.rows.forEach(r=>{R+=r.runs;A+=r.aio;T+=r.td;
    const tr=document.createElement("tr");
    tr.innerHTML=`<td>${esc(r.q)}</td><td>${r.hl}</td><td>${r.runs}</td>
      <td>${pct(r.aioRate)}</td>
      <td class="${r.tdRate>0?'hit':'miss'}">${pct(r.tdRate)} (${pct(r.ci[0])}–${pct(r.ci[1])})</td>
      <td>${r.top.map(x=>esc(x[0])+" ("+x[1]+")").join(", ")||"—"}</td>`;
    tb.appendChild(tr);});
  const ci=wilson(T,R);
  $("#overall").innerHTML=`Overall AIO trigger rate <b>${pct(A/R)}</b> · `+
    `The Dent citation rate <b>${pct(T/R)}</b> (95% CI ${pct(ci[0])}–${pct(ci[1])}) · `+
    `${d.calls} SerpApi calls`;
  const cb=$("#ctable tbody");cb.innerHTML="";
  Object.entries(d.comp).sort((a,b)=>b[1]-a[1]).forEach(([dom,n])=>{
    const isT=dom===TARGET||dom.endsWith("."+TARGET);
    const tr=document.createElement("tr");
    tr.innerHTML=`<td class="${isT?'hit':''}">${esc(dom)}</td><td>${n}</td><td>${isT?'YES':''}</td>`;
    cb.appendChild(tr);});
  $("#results").style.display="block";
}
function esc(s){return String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));}

function rowsForExport(d){
  const head=["Prompt","Lang","Runs","AIO rate %","The Dent rate %","CI low %","CI high %","Top cited domains"];
  const body=d.rows.map(r=>[r.q,r.hl,r.runs,Math.round(r.aioRate*100),Math.round(r.tdRate*100),
    Math.round(r.ci[0]*100),Math.round(r.ci[1]*100),r.top.map(x=>x[0]+" ("+x[1]+")").join("; ")]);
  return[head,...body];
}
$("#xlsx").addEventListener("click",()=>{
  if(!LAST)return;const wb=XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb,XLSX.utils.aoa_to_sheet(rowsForExport(LAST)),"By prompt");
  const comp=[["Domain","Times cited","Is The Dent?"],
    ...Object.entries(LAST.comp).sort((a,b)=>b[1]-a[1]).map(([d2,n])=>
      [d2,n,(d2===TARGET||d2.endsWith("."+TARGET))?"YES":""])];
  XLSX.utils.book_append_sheet(wb,XLSX.utils.aoa_to_sheet(comp),"Competitor SoV");
  XLSX.writeFile(wb,`${LAST.date}-aio-citation-audit.xlsx`);
});
$("#csv").addEventListener("click",()=>{
  if(!LAST)return;const csv=rowsForExport(LAST).map(r=>r.map(c=>`"${String(c).replace(/"/g,'""')}"`).join(",")).join("\n");
  const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));
  a.download=`${LAST.date}-aio-citation-audit.csv`;a.click();
});
</script>
</body>
</html>

```

### `functions/api/aio.js`

```js
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

```

### `functions/_middleware.js`

```js
// Edge HTTP Basic Auth gate for the whole Pages project (the page + /api/*).
// Credentials come from environment variables, defaulting to thedent/admin2026.
// Set BASIC_AUTH_USERNAME / BASIC_AUTH_PASSWORD on the Pages project and change
// the password before going live.

function unauthorized() {
  return new Response("Authentication required.", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="The Dent AIO Audit"' },
  });
}

// Constant-time-ish string compare.
function safeEqual(a, b) {
  if (a.length !== b.length) return false;
  let out = 0;
  for (let i = 0; i < a.length; i++) out |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return out === 0;
}

export async function onRequest(context) {
  const { request, env, next } = context;
  const user = env.BASIC_AUTH_USERNAME || "thedent";
  const pass = env.BASIC_AUTH_PASSWORD || "admin2026";

  const header = request.headers.get("Authorization") || "";
  if (!header.startsWith("Basic ")) return unauthorized();

  let decoded = "";
  try {
    decoded = atob(header.slice(6));
  } catch {
    return unauthorized();
  }
  const idx = decoded.indexOf(":");
  const u = decoded.slice(0, idx);
  const p = decoded.slice(idx + 1);
  if (!safeEqual(u, user) || !safeEqual(p, pass)) return unauthorized();

  return next();
}

```
