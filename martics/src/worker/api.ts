import { Hono } from "hono";
import { aggregateBrandDay } from "./aggregator";
import { getBrand, getPrompt, listActivePrompts } from "./db";
import { ENGINE_NAMES } from "./engines";
import { runPromptEngine, type RunSummary } from "./runner";
import { activeEngines, type Env } from "./types";
import { newId, nowISO, todayUTC } from "./util";
import { buildDashboard } from "./dashboard";

export const api = new Hono<{ Bindings: Env }>();

// --- Brands ----------------------------------------------------------------
api.post("/brands", async (c) => {
  const body = await c.req.json().catch(() => ({}));
  const { name, domain } = body as { name?: string; domain?: string };
  if (!name || !domain) {
    return c.json({ error: "name and domain are required" }, 400);
  }

  let clientId: string = body.client_id;
  if (!clientId) {
    clientId = newId();
    await c.env.DB.prepare("INSERT INTO clients (id, name, logo_url, created_at) VALUES (?, ?, ?, ?)")
      .bind(clientId, body.client_name || name, body.logo_url ?? null, nowISO())
      .run();
  }

  const brandId = newId();
  await c.env.DB.prepare(
    `INSERT INTO brands (id, client_id, name, domain, aliases_json, competitors_json, created_at)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
  )
    .bind(
      brandId,
      clientId,
      name,
      domain,
      JSON.stringify(body.aliases ?? []),
      JSON.stringify(body.competitors ?? []),
      nowISO(),
    )
    .run();

  return c.json({ id: brandId, client_id: clientId, name, domain }, 201);
});

api.get("/brands", async (c) => {
  const { results } = await c.env.DB.prepare(
    "SELECT id, client_id, name, domain FROM brands ORDER BY created_at DESC",
  ).all();
  return c.json({ brands: results ?? [] });
});

// --- Prompts ---------------------------------------------------------------
api.post("/prompts", async (c) => {
  const body = await c.req.json().catch(() => ({}));
  const brandId: string = body.brand_id;
  if (!brandId) return c.json({ error: "brand_id is required" }, 400);

  // Accept either { prompts: [{text_th,intent}] } or a single { text_th, intent }.
  const incoming: { text_th: string; intent?: string }[] = Array.isArray(body.prompts)
    ? body.prompts
    : body.text_th
      ? [{ text_th: body.text_th, intent: body.intent }]
      : [];

  if (incoming.length === 0) return c.json({ error: "no prompts provided" }, 400);

  const created: { id: string; text_th: string; intent: string }[] = [];
  for (const p of incoming) {
    if (!p.text_th?.trim()) continue;
    const id = newId();
    const intent = p.intent || "informational";
    await c.env.DB.prepare(
      "INSERT INTO prompts (id, brand_id, text_th, intent, active, created_at) VALUES (?, ?, ?, ?, 1, ?)",
    )
      .bind(id, brandId, p.text_th.trim(), intent, nowISO())
      .run();
    created.push({ id, text_th: p.text_th.trim(), intent });
  }

  return c.json({ created, count: created.length }, 201);
});

api.get("/prompts", async (c) => {
  const brandId = c.req.query("brand_id");
  if (!brandId) return c.json({ error: "brand_id is required" }, 400);
  const { results } = await c.env.DB.prepare(
    "SELECT id, text_th, intent, active FROM prompts WHERE brand_id = ? ORDER BY created_at",
  )
    .bind(brandId)
    .all();
  return c.json({ prompts: results ?? [] });
});

// --- Run (manual trigger; cron uses the same code path) --------------------
api.post("/run", async (c) => {
  const body = await c.req.json().catch(() => ({}));
  const brandId: string = body.brand_id;
  if (!brandId) return c.json({ error: "brand_id is required" }, 400);

  const brand = await getBrand(c.env, brandId);
  if (!brand) return c.json({ error: "brand not found" }, 404);

  const prompts = body.prompt_id
    ? [await getPrompt(c.env, body.prompt_id)].filter(Boolean)
    : await listActivePrompts(c.env, brandId);
  if (prompts.length === 0) return c.json({ error: "no active prompts" }, 400);

  const engines: string[] = Array.isArray(body.engines) && body.engines.length
    ? body.engines
    : activeEngines(c.env);

  const summaries: RunSummary[] = [];
  for (const prompt of prompts) {
    for (const engine of engines) {
      summaries.push(await runPromptEngine(c.env, brand, prompt!, engine));
    }
  }

  const date = todayUTC();
  const metricsWritten = await aggregateBrandDay(c.env, brand, date);

  return c.json({
    brand_id: brandId,
    date,
    engines,
    runs: summaries,
    metrics_written: metricsWritten,
  });
});

// --- Dashboard -------------------------------------------------------------
api.get("/dashboard", async (c) => {
  const brandId = c.req.query("brand_id");
  if (!brandId) return c.json({ error: "brand_id is required" }, 400);
  const brand = await getBrand(c.env, brandId);
  if (!brand) return c.json({ error: "brand not found" }, 404);
  return c.json(await buildDashboard(c.env, brand));
});

// --- Fix-loop (Phase 5 — P1, scaffolded) -----------------------------------
api.post("/fix", (c) =>
  c.json(
    {
      error: "not_implemented",
      message: "Fix-loop (Claude gap analysis ภาษาไทย) ships in Phase 5.",
    },
    501,
  ),
);

// --- White-label report (Phase 6 — P1, scaffolded) -------------------------
api.get("/report/:brandId", async (c) => {
  const brand = await getBrand(c.env, c.req.param("brandId"));
  if (!brand) return c.json({ error: "brand not found" }, 404);
  const dashboard = await buildDashboard(c.env, brand);
  return c.json({
    ...dashboard,
    scaffold: true,
    message: "White-label PDF export ships in Phase 6. Payload below is report-ready.",
    client_logo_url: null,
  });
});

// --- Meta ------------------------------------------------------------------
api.get("/engines", (c) =>
  c.json({ registered: ENGINE_NAMES, active: activeEngines(c.env) }),
);
