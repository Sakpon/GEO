import { Hono } from "hono";
import { api } from "./api";
import { aggregateBrandDay } from "./aggregator";
import { listActivePrompts, listBrandsWithActivePrompts } from "./db";
import { runPromptEngine } from "./runner";
import { activeEngines, type Env } from "./types";
import { todayUTC } from "./util";

const app = new Hono<{ Bindings: Env }>();

app.route("/api", api);

// Everything that isn't /api is the React SPA, served from the ASSETS binding.
// (run_worker_first = true means the Worker sees every request first.)
app.all("*", (c) => c.env.ASSETS.fetch(c.req.raw));

/** Daily cron: run every active prompt × active engine, then aggregate. */
async function runDailyCycle(env: Env): Promise<void> {
  const engines = activeEngines(env);
  const brands = await listBrandsWithActivePrompts(env);
  const date = todayUTC();

  for (const brand of brands) {
    const prompts = await listActivePrompts(env, brand.id);
    for (const prompt of prompts) {
      for (const engine of engines) {
        // Per-run failures are isolated inside runPromptEngine; a thrown error
        // here (e.g. brand-level) must not abort the rest of the cycle.
        try {
          await runPromptEngine(env, brand, prompt, engine);
        } catch (e) {
          console.error(`cycle error brand=${brand.id} prompt=${prompt.id} engine=${engine}:`, e);
        }
      }
    }
    await aggregateBrandDay(env, brand, date);
  }
}

export default {
  fetch: app.fetch,
  scheduled(_event: ScheduledController, env: Env, ctx: ExecutionContext) {
    ctx.waitUntil(runDailyCycle(env));
  },
} satisfies ExportedHandler<Env>;
